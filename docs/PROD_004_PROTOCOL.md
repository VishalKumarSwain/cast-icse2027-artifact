# PROD_004: Canonicalization Probe -- Protocol

Written before running. Uses only the existing frozen formatting-family
SUCCESS samples from PROD_001 (`artifacts/prod001_transform_log.jsonl`) and
the same three frozen detectors. No new dataset, detector, language, or
transformation family.

## Question

DroidDetect-Base's formatting Induced Error Rate (34.9% Python, 24.1% Java)
is the study's strongest single result. Is it driven by formatting/
whitespace presentation specifically? If a canonicalizer collapses C0 and
T(C0) to the same whitespace/comment/quote-invariant representation, does
the instability shrink?

## Canonicalizer definition (fixed before running)

Reuses this study's existing tokenizers (`scripts/distances.py`) rather than
introducing new tooling:

- **Python**: `tokenize.generate_tokens`, keep only NAME/OP/NUMBER/STRING/
  keyword tokens (drop COMMENT/NL/NEWLINE/INDENT/DEDENT/ENCODING/ENDMARKER),
  normalize every STRING token's quote character to `"`, join with single
  spaces.
- **Java**: tree-sitter leaf tokens (as in `distances.py::_java_token_stream`),
  drop `comment`/`line_comment`/`block_comment` leaf nodes, join remaining
  leaf text with single spaces.

Two inputs differing only in indentation, blank lines, comments, or quote
style canonicalize to an **identical** string. Two inputs differing in
actual token content (renamed identifiers, reordered statements) do not.

## Sample set

All formatting-family SUCCESS rows from PROD_001
(`artifacts/prod001_transform_log.jsonl`, N=94 Python + 64 Java = 158). No
resampling, no new draw.

## Procedure

1. For each of the 158 rows: compute `canon(C0)` and `canon(T)` per the
   definition above.
2. Score `canon(C0)` and `canon(T)` with all three frozen detectors (same
   contracts as PROD_002 -- LLMSniffer, DroidDetect-Base, DetectCodeGPT
   K=50/threshold=2.931). These are fresh scores (the canonicalized text is
   different from either raw C0 or raw T, so no prior score can be reused).
3. Compute `delta_canon = score(canon(T)) - score(canon(C0))` per detector,
   per sample.
4. Compare the distribution of `|delta_canon|` against the ALREADY-FROZEN
   `|delta_score|` from PROD_002's formatting rows for the same sample_ids,
   per detector.

## Metric

For each detector x language: median/mean `|delta_canon|` vs. median/mean
`|delta_score|` (original, PROD_002), and the fraction of `canon(C0) ==
canon(T)` exactly (byte-identical after canonicalization -- expected for
samples whose ONLY formatting change was indentation/blank-lines/comments,
which trivially forces `delta_canon = 0` for those rows by construction, not
as evidence of anything -- these rows are reported separately from rows
where canonicalization leaves a residual textual difference, e.g. from
quote-style changes our canonicalizer doesn't fully normalize, or genuine
token-level changes).

## Decision rule (fixed before seeing results)

- If DroidDetect-Base's `|delta_canon|` distribution collapses toward the
  other detectors' typically-small scale (order of magnitude smaller median
  than its original PROD_002 formatting `|delta_score|`) -- support for
  "formatting/whitespace presentation specifically drives the instability."
- If `|delta_canon|` remains large even for byte-identical canonical pairs
  (impossible by construction -- flag as a bug, not a finding) or for
  near-identical canonical pairs -- instability is not purely a whitespace-
  presentation artifact.

## After this: freeze all experiments

No further detectors, languages, samples, transformation families, or
probes planned. Next steps after PROD_004: final statistics across all
phases, final tables update, figures, threats-to-validity, manuscript.
