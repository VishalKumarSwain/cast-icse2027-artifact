# PILOT_004 forensic drill-down: DroidDetect-Base x Python x formatting

Frozen diagnostic record. Written under the original PILOT_002/PILOT_003
distance-metric definitions, before any metric changes. Source data:
`artifacts/pilot004_detector_scores.jsonl`, `artifacts/pilot_transform_log_v3.jsonl`,
`artifacts/pilot_manifest_v2.jsonl`. Analysis script:
`scripts/forensic_droid_python_formatting.py`.

## 1. Why this analysis was triggered

The PILOT_004 diagnostic table showed one cell with a striking mean/median
gap:

- DroidDetect-Base x Python x formatting: N=15, mean Delta=-0.3039,
  median Delta=-0.0034, 6/15 raw label flips.

A mean roughly two orders of magnitude larger in absolute value than the
median, on a transformation family expected to be one of the weakest
("cosmetic") in the ladder, is exactly the kind of anomaly that needs
forensic inspection before any interpretation.

## 2. Forensic findings

Sorting the 15 pairs by Delta = sT - s0 ascending shows the distribution is
highly concentrated, not diffuse:

- 4-5 samples show very large negative score changes (Delta between -1.00
  and -0.63).
- The remaining ~10 samples are approximately unchanged (|Delta| <= 0.02,
  most exactly 0.0000).

Baseline-correct-only analysis (the methodologically cleaner count, per the
distinction between "flips among samples the detector already had wrong"
and "flips among samples it had right"):

- 13/15 samples were baseline-correct (`y_hat_D(C0) == y_true`).
- **5 of those 13 changed predicted label after formatting** (raw flip count
  was 6/15; one flip was on a sample that was already baseline-incorrect and
  is excluded from this cleaner count).

## 3. Confound checks

- **Truncation**: the two truncated samples in this cell
  (`c0_test_57740d795db9`, `c0_test_e840db674e2e`) show *small* deltas
  (-0.1086, -0.0222).
  The five largest collapses are all non-truncated (`truncated_c0=False`,
  `truncated_t=False`). Truncation / tokenization-window effects do not
  explain the large-magnitude cases.
- **AST structure**: `ast_node_count_delta = 0` for every one of the five
  largest-collapse samples. Formatting did not change program structure by
  this measure.
- **Token distance (whitespace-split metric, as originally defined)**: 0, 4,
  0, 0, 2 for the five largest-collapse samples — near-zero by this metric.
- **What actually changed, by manual source inspection**: indentation-width
  normalization (e.g. 8-space method-body indent renormalized to 4-space),
  insertion of a PEP8 blank line between statements, and string-quote
  normalization (`'...'` to `"..."`). All cosmetic by inspection; none alter
  control flow, statement structure, or identifiers.

## 4. Cross-detector observation

LLMSniffer, scored on the identical 15-sample Python-formatting cell: mean
Delta=+0.013, median Delta=+0.0040, 0 flips.

This is preliminary evidence of **detector-specific sensitivity** to the
same nominal transformation family, on the same inputs. It is not, on its
own, a general conclusion about LLMSniffer's robustness or DroidDetect-Base's
fragility -- N=15 is a pilot-scale observation.

## 5. Interpretation boundary

PILOT_004 does not support interpreting these cases simply as decay of an
"AI signal." Formatting-induced prediction instability occurred for both
provenance classes, including correctly classified `HUMAN_GENERATED`
samples (3 of the 5 largest-collapse cases carry that label, moving from a
confident correct human prediction toward a different predicted class after
a blank-line insertion or quote-style change). The observed phenomenon is
therefore more accurately characterized as **preliminary decision-boundary
instability under cosmetic source-code transformations**, not as directional
"AI signal decay." Any future write-up of this cell must preserve that
distinction.

## 6. Metric defect discovered

The whitespace-split `token_distance` used throughout PILOT_002-PILOT_004 is
**insensitive to indentation-width changes and blank-line insertion/removal**
by construction (splitting on whitespace discards exactly the characters
those edits change). It registered near-zero distance (0, 4, 0, 0, 2) for
transformations that a human would clearly see as visually significant and
that were sufficient to flip detector predictions. This metric must be
replaced before protocol freeze -- see follow-up plan below.

## Frozen diagnostic sample set

These 5 sample IDs are the forensic evidence set for this cell. They must
NOT be used as a tuning target for future transformation or metric design --
they are a diagnostic record, not an objective to reproduce:

- `c0_test_33781209d435` (HUMAN_GENERATED, Delta=-1.0000, flip=True)
- `c0_test_8f4aace61f34` (HUMAN_GENERATED, Delta=-1.0000, flip=True)
- `c0_test_bd14d6d27732` (HUMAN_GENERATED, Delta=-0.9999, flip=True)
- `c0_test_3aa1bb91de4a` (MACHINE_REFINED, Delta=-0.7960, flip=True)
- `c0_test_e134f4294cf7` (HUMAN_GENERATED, Delta=-0.6281, flip=True)

## Status and next steps

This is a pilot-scale (N=15) observation, not a result. Sequence going
forward, per methodology decision: write this report -> commit -> improve
and freeze distance metrics (see below) -> re-verify metrics on PILOT_004
WITHOUT re-running or changing detector outputs -> define the production
manifest -> scale the held-out experiment and test whether this effect
replicates.

### Planned metric fix (not yet implemented)

Replace the single collapsed `token_distance` with three explicitly distinct
measures, since this finding shows formatting can legitimately have nonzero
distance at one level and zero at another:

- `d_text`: raw textual/character-level distance (captures presentation-level
  changes such as indentation width and blank lines).
- `d_token`: lexical/token-stream distance using Python's `tokenize` module
  (retains INDENT/DEDENT/NEWLINE/NL, operators, strings, names -- unlike the
  current whitespace-split metric, this will register indentation and
  blank-line changes as real token-stream edits).
- `d_AST`: structural distance (existing AST-node-count-delta measure,
  possibly refined further later).

Hierarchy: Textual -> Lexical -> Structural -> Behavioral. A formatting
transformation can legitimately show `d_text > 0` and `d_AST = 0`
simultaneously -- that is the correct representation of what this cell
demonstrated, not a bug to eliminate.

### Research framing (not changed by this finding)

This result does not pivot the research question. It sharpens it: under the
umbrella of "how persistent and stable are code-attribution decisions under
controlled software evolution, and is that stability detector-specific,"
there are now two candidate phenomena to distinguish at production scale --
**attribution confidence decay** and **decision-boundary instability** -- and
the two may not coincide. The production experiment is designed to
distinguish them, not to reproduce this specific pilot cell.
