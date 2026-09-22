# PROD_001: Held-Out Replication -- Pre-registration

Written and committed BEFORE running PROD_001. Not to be edited after results
are seen; any post-hoc changes belong in a separate follow-up note, not here.

## Hypothesis under test (H-Pilot)

**H-Pilot**: Cosmetic formatting transformations can induce prediction
instability in DroidDetect-Base on held-out Python code despite minimal
structural change, whereas LLMSniffer exhibits comparatively different
sensitivity under the same transformations.

This is the pilot-generated hypothesis from PILOT_004
(`docs/PILOT_004_FORENSIC_FORMATTING.md`), not a claim it will replicate.
PROD_001 exists to test whether it survives a larger held-out sample --
nothing about the transformation, detector, or analysis code is allowed to
change based on the outcome.

## What is frozen for this run

- **Transformations**: the three already validated in PILOT_002/PILOT_004 --
  lexical rename, formatting, control-flow. No structural refactoring,
  semantic transformations, extensions, or additional intensity levels.
- **Detectors**: LLMSniffer + DroidDetect-Base only, same checkpoints, same
  pooling/label-permutation choice loaded from
  `artifacts/pilot003_detector_contracts.json`. No GPTSniffer/CodeGPTSensor/
  DetectCodeGPT addition at this stage.
- **Distance metrics**: the new `d_text` / `d_token` / `d_ast` from
  `scripts/distances.py`, verified against PILOT_004 in commit `9026bcb`.
- **Corpus**: Droid's held-out **test** split only (same split PILOT_004
  used), disjoint sample_ids from PILOT_004's 30-seed manifest.

## Manifest design

- **N = 200 seeds**: 100 Python + 100 Java.
- Within each language, stratified across `HUMAN_GENERATED` /
  `MACHINE_GENERATED` / `MACHINE_REFINED`, and within the two machine labels,
  stratified as evenly as possible across available `Model_Family` values.
- Fixed seed, distinct from PILOT_002 (20260919) and PILOT_004 (20260920).
- Exact sample_ids recorded in `artifacts/pilot_manifest_prod001.jsonl` and
  provenance in `docs/pilot_manifest_prod001_provenance.md`.

## What will be calculated

Per detector x language x transformation family:
- `N_attempted`, `N_applicable`, `N_valid` (SUCCESS), `N_baseline_correct`
- score-delta distribution (mean, median, min/max)
- label-flip counts (raw, and among baseline-correct only)
- **Induced Error Rate** = (# baseline-correct samples that became incorrect
  after transformation) / (# baseline-correct samples). This is the
  production-scale analogue of PILOT_004's 5/13 (~38.5%) DroidDetect-Base x
  Python x formatting cell -- that pilot number is a hypothesis to test
  against, not an established population estimate.
- Detector-change vs. distance-metric relationship, specifically flagging
  the region `d_text > 0, d_token small, d_ast ~= 0` combined with
  `|delta_score| >> 0` -- the signature PILOT_004's forensic cases showed.

## Decision rule (fixed before seeing results)

- If DroidDetect-Base x Python x formatting shows a comparable
  Induced Error Rate at N=100 Python seeds (order-of-magnitude similar to
  the pilot's ~38.5%, and visibly larger than DroidDetect-Base's other two
  Python transformation families, and visibly larger than LLMSniffer's
  Induced Error Rate on the same cell) -> treat H-Pilot as replicated at
  production scale. Next step: expand detector panel (GPTSniffer/
  CodeGPTSensor/DetectCodeGPT) and introduce the richer transformation
  ladder.
- If it does not replicate (rate drops toward the other cells' baseline, or
  the detector-specific contrast disappears) -> PILOT_004 remains exploratory
  pilot evidence. Keep the broader attribution-persistence research question;
  do not build the paper around formatting fragility specifically.

No other outcome-contingent branching is pre-registered here.
