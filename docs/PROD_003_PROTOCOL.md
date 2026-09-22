# PROD_003: Deeper Transformations -- Protocol

Written and committed BEFORE implementing either new transformation family
or seeing any detector behavior on them. Per methodology decision, this is
intended to be the last major experiment before final analysis/writeup --
no further detector or transformation expansion planned after this.

## What stays frozen

- Same 199 C0 seeds (`artifacts/pilot_manifest_prod001.jsonl`)
- Same three detectors, same frozen contracts (LLMSniffer, DroidDetect-Base,
  DetectCodeGPT @ K=50, threshold=2.931)
- Same validation system (`validate_python`/`validate_java` from
  `transform_pilot_v2.py`, Java's tiered STANDALONE/WRAPPER/STRUCTURAL_ONLY
  validation)
- Same `d_text` / `d_token` / `d_ast` distance metrics
- Same three-outcome status model: SUCCESS / NOT_APPLICABLE /
  VALIDATION_FAILED / TRANSFORM_ERROR, same Applicability/Success rate
  reporting discipline

**Only variable changed: two new transformation families, each at LOW and
HIGH intensity where technically defensible.**

## New transformation families

### 1. Local structural refactoring

- **Operator**: extract-method. Identify one eligible contiguous statement
  block inside a function body (Python: `ast`/`libcst` block of >=3
  statements not containing a `return`/`yield` that would complicate
  extraction; Java: an analogous contiguous statement block inside a method
  body via tree-sitter). Extract it into a new private helper
  function/method, replace the original block with a call to it.
- **LOW intensity**: exactly one extraction, applied to the first eligible
  block found (deterministic, seed-independent selection rule: first
  eligible block in source order).
- **HIGH intensity**: extract every eligible block found (up to a cap of 3,
  to avoid degenerate over-fragmentation of small functions), each into its
  own helper.
- **Applicability rule**: NOT_APPLICABLE if no eligible block exists (e.g.
  function body too short, or entirely control-flow with no
  extractable straight-line block).
- **Validation**: same tiered validation as existing families
  (parse/compile at or above the C0's own tier). This is a structural
  rewrite, not claimed behavior-preserving beyond "still parses/compiles" --
  see semantic-preservation note below.

### 2. Deeper semantic-preserving rewrite

- **Operator**: a composed rewrite that changes AST shape substantially
  while intending to preserve input-output behavior: for Python, a
  combination of (a) converting straightforward accumulator loops to
  equivalent comprehensions where syntactically safe, or the reverse
  (comprehension to explicit loop) when no comprehension is present, plus
  (b) boolean-expression rewriting (De Morgan's-law-equivalent restructuring
  of one compound conditional, if present). For Java, an analogous
  composed rewrite: loop-form conversion (for<->enhanced-for where
  applicable) plus one boolean-expression restructuring.
- **LOW intensity**: apply only the loop-form conversion (part a/first
  operator in the pair), if applicable.
- **HIGH intensity**: apply both composed rewrites (loop-form conversion AND
  boolean restructuring) where both are applicable; if only one is
  applicable, HIGH degrades to the same result as LOW for that sample (not
  NOT_APPLICABLE -- partial applicability is recorded, not treated as
  failure).
- **Applicability rule**: NOT_APPLICABLE if neither sub-rewrite pattern is
  present in the sample.

## Semantic-equivalence validation (the harder requirement for these two families)

Per the original design's validation-gate plan (`docs/DESIGN.md`), and
consistent with the correction already recorded there (Droid ships no test
cases): semantic-preservation for these two families is checked by
**differential execution on self-generated inputs**, not official tests:

1. Must parse/compile at or above the C0's own validation tier (same gate as
   existing families).
2. Where the sample is a complete, runnable unit (determined the same way
   the existing Java tiered validator distinguishes STANDALONE from
   fragment sources) AND has an unambiguous entry point (a `main`-like
   function/method, or a single top-level function taking primitive/string
   arguments): generate up to 5 lightweight input probes (boundary values
   and literals harvested from the code's own constants), run C0 and T(C0),
   compare stdout/return value. Mismatch -> `VALIDATION_FAILED`, logged with
   the actual diverging output, not silently discarded.
3. Where no unambiguous entry point exists (the common case for Droid's
   function-fragment samples): validation degrades to "parses/compiles at or
   above C0's tier" only, and this degradation is recorded explicitly per
   row (`semantic_check: "STRUCTURAL_ONLY_NO_ENTRY_POINT"` vs
   `semantic_check: "DIFFERENTIAL_EXECUTION_PASSED"` vs
   `"DIFFERENTIAL_EXECUTION_FAILED"`). This limitation is disclosed in the
   paper's threats-to-validity section, not hidden -- a meaningful fraction
   of samples will not get true behavioral verification.

## Metrics (unchanged from PROD_001/PROD_002)

Per detector x language x transformation family x intensity: N_attempted,
N_applicable, N_valid, N_baseline_correct, delta-score distribution
(median/p90/max, per PROD_002F's within-detector-only comparison
discipline), flips, flips_among_baseline_correct / Induced Error Rate, and
the same detector-relative signature-region check from PROD_002F.

## Central question

As modifications become deeper (formatting -> lexical -> control-flow ->
local structural -> deep semantic-preserving), do LLMSniffer,
DroidDetect-Base, and DetectCodeGPT retain the three distinct stability
profiles established in PROD_002F (stable/Pattern-C-noise; localized
Pattern A; diffuse Pattern B), or does the ordering/character change as
transformations move from cosmetic toward structural?

## After PROD_003

No further transformation families, detectors, languages, semantic-changing
mutations, feature extensions, or telemetry are planned for this NIER study.
Next steps after PROD_003's results are: final statistical analysis,
figures, threats-to-validity writeup, manuscript. Any further expansion
(the full original transformation ladder, additional detector families,
human telemetry) is deferred to a "Future Work" section, not executed here.
