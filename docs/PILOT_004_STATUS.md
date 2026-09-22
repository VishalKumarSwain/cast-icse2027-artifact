# PILOT_004

**Status: GO** (first clean preliminary diagnostic table)

## Chain so far
- PILOT_001 -> found validation/transformation problems
- PILOT_002 -> fixed methodology, transformation pipeline validated
- PILOT_003 -> detector contracts validated, found train-split contamination
- PILOT_004 -> held-out seeds (Droid **test** split, used directly, no
  dev fallback needed), frozen PILOT_002 transformations, frozen PILOT_003
  detector contracts (pooling=cls, label permutation=identity)

## What changed vs PILOT_003
- C0 manifest rebuilt from Droid's **test** split (`artifacts/pilot_manifest_v2.jsonl`,
  seed 20260920, distinct from PILOT_002's train-split seed 20260919).
  Provenance recorded in `docs/pilot_manifest_v2_provenance.md`.
- Transformation/validation logic untouched (imported directly from
  `transform_pilot_v2.py`, not reimplemented) -- `scripts/transform_pilot_v3.py`
  only changes I/O paths.
- Detector contracts untouched -- `scripts/pilot004_run.py` loads pooling
  choice and label permutation from `artifacts/pilot003_detector_contracts.json`
  rather than re-searching.
- Every row now carries `dataset`, `dataset_version`, `dataset_split`,
  `sample_id`, `detector_training_overlap` (conservative values
  `NO_KNOWN_OVERLAP` for both detectors here -- see reasoning in
  `scripts/pilot004_run.py` and `docs/PILOT_003_STATUS.md`; never claiming
  bare `NO_OVERLAP` since neither training corpus was independently audited).

## Result: contamination signal is gone
DroidDetect-Base `baseline_correct` is no longer 100% in every cell (PILOT_003
symptom). PILOT_004 values: Java control_flow 2/2, formatting 8/10,
lexical_rename 11/13; Python control_flow 4/4, formatting 13/15,
lexical_rename 12/14 -- varied and plausible, consistent with genuine
(non-memorized) detection performance.

## Transformation mechanics reproduced stably on a new draw
ApplicabilityRate=0.66, TransformationSuccessRate=0.98 (58/59) -- consistent
with PILOT_002's 0.61/0.98, confirming the frozen transformation logic
behaves the same way on an independent sample of seeds.

## Diagnostic table (primitive: Delta score + flips only, no half-life/decay-curve analysis yet)
See `artifacts/pilot004_diagnostic_table.csv` / `artifacts/pilot004_detector_scores.jsonl`.

| Detector | Language | Family | N_valid | Baseline_correct | MeanDelta | MedianDelta | Flips |
|---|---|---|---|---|---|---|---|
| DroidDetect-Base | Java | control_flow | 2 | 2 | -0.0053 | -0.0053 | 0 |
| DroidDetect-Base | Java | formatting | 10 | 8 | -0.0845 | -0.0010 | 1 |
| DroidDetect-Base | Java | lexical_rename | 13 | 11 | -0.0038 | 0.0000 | 0 |
| DroidDetect-Base | Python | control_flow | 4 | 4 | -0.0210 | 0.0000 | 0 |
| DroidDetect-Base | Python | formatting | 15 | 13 | -0.3039 | -0.0034 | 6 |
| DroidDetect-Base | Python | lexical_rename | 14 | 12 | -0.0359 | 0.0000 | 1 |
| LLMSniffer | Java | control_flow | 2 | 0 | +0.0388 | +0.0388 | 0 |
| LLMSniffer | Java | formatting | 10 | 3 | +0.0136 | +0.0140 | 2 |
| LLMSniffer | Java | lexical_rename | 13 | 4 | +0.0097 | +0.0099 | 3 |
| LLMSniffer | Python | control_flow | 4 | 4 | +0.0024 | +0.0048 | 0 |
| LLMSniffer | Python | formatting | 15 | 9 | +0.0130 | +0.0040 | 0 |
| LLMSniffer | Python | lexical_rename | 14 | 9 | +0.0107 | +0.0081 | 0 |

## Deliberately not done yet
- No half-life computation, no significance testing, no scaling to 300-400
  seeds. This table is for checking whether the measurement system behaves
  coherently, per the frozen protocol.
