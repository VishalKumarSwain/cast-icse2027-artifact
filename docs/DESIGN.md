# AIHUMAN — Attribution Half-Life Study

Target: ICSE NIER 2027.

## Working title
"When Does AI-Generated Code Stop Looking AI? Toward Measuring the Attribution
Persistence of Machine-Generated Programs Under Code Evolution"

## Core reframe
Not: "classify code as Human / AI / Hybrid."
Instead: "measure how detector-visible AI-attribution signal persists or decays
as AI-generated code undergoes realistic, controlled human-like modification."

Detector output `P_D(AI | C_i)` is **attribution confidence**, not a claim about
true percentage authorship. Provenance of `C_0` is fixed and known; only the
detector's belief is being measured as `C_0` is transformed.

## Research questions
- RQ1 (decay): how does detector confidence decay as a function of edit distance /
  AST distance, per transformation family?
- RQ2 (perturbation sensitivity): what is the minimum perturbation needed to flip
  predicted label, per family/detector/language? (**Minimum Flip Perturbation**, not
  "FlipPoint" — see terminology below)
- RQ3 (signal persistence): which feature families (lexical / AST-structural /
  semantic-complexity) predict decay best, per transformation family?
- RQ4 (cross-detector agreement): do heterogeneous detectors fail at the same
  transformations, or is fragility detector-specific?

## Terminology (locked)
- **Independent experiment** (main): each transformation applied directly to `C_0`
  in isolation, at low/high intensity. Metric: **Minimum Flip Perturbation (MFP)**.

  MFP_D(C, F) = min over T in family F of { d(C, T(C)) : label_D(T(C)) != label_D(C) }

  where `d` is token/AST/edit distance appropriate to the family.

- **Chained experiment** (secondary, ~20% of samples): ordered sequential
  transformations `C_0 -> C_1 -> ... -> C_k`. Metric: **FlipPoint** (a true ordered
  stage index) and **ConfidenceDecay_D(C_i) = p_0 - p_i**.

- **AttributionHalfLife**: `min{i : p_i <= 0.5 * p_0}` — reported ONLY for detectors
  with genuinely calibrated probabilistic output. For logit-only detectors, report
  raw-score delta + flip point instead; do not force a normalization.

## Transformation families x intensity
| Family | Low | High | Tooling |
|---|---|---|---|
| Lexical | rename 1 identifier | rename all identifiers | libcst / tree-sitter rewrite |
| Formatting | formatter normalization | (single level) | black / google-java-format |
| Local structural | 1 extract-method/local rewrite | 3+ local rewrites | scripted AST refactor |
| Control-flow | 1 equivalent rewrite (for<->while, if-else<->guard) | multiple | scripted rewrite rules |
| Semantic-preserving (deep) | low AST-edit-distance rewrite | high AST-edit-distance | scripted + validation gate |
| Semantic-changing | small bugfix/logic change | larger logic change | mutation tooling (mutmut/PIT) or paired human-fix data |
| Extension | one bounded added feature | — | templated / paired human continuation |

Applied independently to `C_0` by default (isolates type from amount). A ~20%
stratified subset also gets the chained, ordered version.

## Semantic-preservation validation gate
- Must parse/compile.
- **Correction after Droid schema audit (2026-09-19): Droid retains NO problem IDs
  or test cases** — columns are only `Code, Generator, Generation_Mode, Source,
  Language, Sampling_Params, Rewriting_Params, Label, Model_Family`. Even for
  TACO/LeetCode/CodeForces/AtCoder-sourced rows, there is no official test suite
  attached. Plan revised: semantic-preserving transforms are validated by
  **differential execution against self-generated inputs** (lightweight fuzzing:
  random/boundary inputs harvested from the code's own literal constants and
  simple type-directed generation), not official tests. Parse/compile-only
  validation is the pilot-stage floor; execution-based diffing is added once the
  pilot proves the input-generation approach works on real samples.
- Semantic-changing transforms validated only for "still runs," not output-equivalence
  (behavior change is intended there).
- Failed/non-compiling transforms are discarded and logged with reason + rate
  reported in the paper, not hidden.

## Seed corpus
**DroidCollection** (`project-droid/DroidCollection` on HF, EMNLP 2025).
- `datasets.load_dataset("project-droid/DroidCollection")`
- Confirmed by direct schema audit (2026-09-19, docs/droid_audit.json):
  train/dev/test = 846598/105824/105826 rows. Fields: Code, Generator,
  Generation_Mode, Source, Language, Sampling_Params, Rewriting_Params, Label
  (actually 4 distinct string values observed: HUMAN_GENERATED,
  MACHINE_GENERATED, MACHINE_REFINED, MACHINE_GENERATED_ADVERSARIAL),
  Model_Family. Languages present: Python, Java, C++, C, C#, JavaScript, Go.
  **No problem-id or test-case fields exist** (see validation-gate note below).
- Start with **Python + Java** subset only (mature AST tooling for both).
- ~150-200 seed programs per language stratified across generator/model families
  and human controls (~300-400 `C_0` total for the main study).
- Note: Droid's own "Machine-Refined" class + `Rewriting_Params` is adjacent to our
  ladder but is a fixed, opaque-to-us transformation — cite as related work we
  differentiate from, not a substitute for our controlled ladder. Worth a secondary
  check as an external validation set later.
- License not explicit on dataset card -> treated as research-use for now; confirm
  before any redistribution of derived artifacts.

## Detector panel (revised after Phase 0 audit)
1. **LLMSniffer** (GraphCodeBERT + supervised contrastive learning) — supersedes
   GPTSniffer (reports GPTSniffer's numbers as a baseline already). Static/trained
   family. Repo: github.com/mahirlabibdihan/llmsniffer, weights on HF
   (`mahirlabibdihan/LLMSniffer`). No explicit repo license file -> research-use only,
   no redistribution of their weights/data.
2. **DroidDetect-Base** (`project-droid/DroidDetect-Base`, Apache 2.0, ModernBERT-based,
   4-class: Human/AI/Machine-Refined/Adversarial). Hybrid-aware SOTA baseline,
   HF `pipeline("text-classification", ...)`.
3. **Fast-DetectGPT-for-code** (zero-shot, conditional probability curvature,
   adapted from ICLR 2024 Fast-DetectGPT using a compact open code LLM as scorer,
   e.g. starcoderbase-1b — exact size pinned during pilot based on MIG memory budget).
4. *(secondary, not load-bearing)* LLM-as-judge, fixed prompt/temperature-0, on a
   stratified subsample only. Core RQ1-4 conclusions must hold without it.

Outstanding checks before pilot close:
- Confirm LLMSniffer's output head is a probability vs. logit-only.
- Confirm which Droid `Source` subsets retain runnable test cases at row level.
- Pin Fast-DetectGPT scorer model size against MIG 3g.40gb budget.

## Artifact schema (per transformed sample x detector row)
sample_id, original_provenance, language, generator/model_origin,
transformation_family, transformation_operator, intensity, edit_distance,
token_distance, AST_distance, complexity_delta, semantic_validation,
detector, raw_score, calibrated_P(AI) [if meaningful], predicted_label.

## Contribution statement (for the paper)
1. A reproducible transformation-ladder methodology for measuring persistence of
   AI-code attribution signal under controlled code evolution.
2. Attribution-decay and minimum-flip-perturbation measurements across
   heterogeneous detectors, transformation families, languages, and generator
   origins.
3. A signal-persistence analysis of which observable code characteristics survive
   which degree/type of modification.

Central thesis: AI-code detection should not be evaluated only on pristine
generated code; it must also be evaluated on how attribution signal survives
realistic code evolution. Hybrid human-AI code produces a continuum of observable
attribution signal that categorical Human/AI/Hybrid labels fail to represent —
but detector confidence is attribution confidence, not literal authorship
percentage.

## Compute environment
- DGX A100 (shared, multi-user), remote at [redacted-internal-ip].
- Allocated MIG partition: `MIG-80f109f6-aa75-51f9-9909-42ad8029df93` (3g.40gb,
  physically on GPU 2). Always pin `CUDA_VISIBLE_DEVICES` to this UUID.
- Project code lives at `~/Vishresearch/AIHUMAN` on the remote (root disk, small,
  git-tracked).
- Large artifacts (venv, HF cache, checkpoints) live on the bigdata mount
  (`/data/aihuman/`, 675GB free)
  and are symlinked into the project dir as `.venv`, `data`, `checkpoints` — root
  disk on the DGX is at 98% capacity, do not write large files there.
- Auth: password-based per-session (SSH key install was blocked by auto-mode
  persistence guardrail; user chose to keep password auth rather than override).

## Status
- [x] Phase 0 feasibility audit (dataset + detector panel verified reproducible)
- [x] DGX environment provisioned: MIG slice confirmed, venv + storage layout live
- [x] Torch + core deps installed in venv, CUDA confirmed pinned to MIG slice
- [x] PILOT_001 (`scripts/transform_pilot.py`) — 30 C0 seeds, 3 transformations,
      regex/javac-based validation. Result: 35/90 OK, but exposed two protocol
      defects rather than measuring anything real yet:
      1. javac-as-validity-predicate wrongly marked most Java C0 fragments
         invalid (Droid Java rows are often function/class fragments, not
         standalone compilation units).
      2. Python control-flow used string-splice, had an indentation bug, and
         conflated "operator not applicable" with "transform failed."
      Verdict: REVISE. Outputs preserved untouched at
      `artifacts/pilot_transform_log.jsonl` / `artifacts/transformed/` as
      evidence of why the validation protocol changed below.
- [x] PILOT_002 (`scripts/transform_pilot_v2.py`) — fixes both defects:
      - Java: tiered, source-kind-aware validation
        (STANDALONE_VALID > WRAPPER_VALID > STRUCTURAL_ONLY > PARSE_INVALID).
        tree-sitter structural parse and javac compile are tracked as
        separate fields (`c0_parse_valid` vs `c0_native_compile_valid` vs
        `c0_wrapped_compile_valid`); a synthetic wrapper class is used only
        as a validation instrument and is never written as detector input
        (kept in `artifacts/java_wrappers_v2/`, separate from
        `artifacts/transformed_v2/`).
      - Python: control-flow rewrite reimplemented in libcst (CST-node
        replacement, not string-splicing) — removes the indentation defect.
      - Three-outcome status model throughout: `SUCCESS` /
        `NOT_APPLICABLE` (operator's pattern not present in this sample --
        not a failure) / `VALIDATION_FAILED` (transform applied, result
        failed the validation gate) / `TRANSFORM_ERROR` (implementation bug;
        should be ~0).
      - Reports `ApplicabilityRate = N_applicable / N_attempted` and
        `TransformationSuccessRate = N_valid / N_applicable` separately,
        never conflated into one "success rate."
      Result: ApplicabilityRate=0.61, TransformationSuccessRate=0.98 (54/55),
      0 TRANSFORM_ERROR. Java C0 validation_status distribution across the
      pilot: STRUCTURAL_ONLY=27, STANDALONE_VALID=12, WRAPPER_VALID=6, zero
      PARSE_INVALID. Verdict: **PILOT GO** on transformation/validation
      mechanics. Logs at `artifacts/pilot_transform_log_v2.jsonl`.
- [ ] Wire in first two detectors (LLMSniffer, DroidDetect-Base) on the
      PILOT_002 C0 + transformed set; produce the first C0-vs-transformed
      raw-score table.
- [ ] Protocol freeze
- [ ] Full pipeline scale-up (~300-400 seeds, full transformation ladder)
