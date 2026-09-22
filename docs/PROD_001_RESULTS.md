# PROD_001: Held-Out Replication -- Results

N=199 (100 Python-target/100 achieved minus overlap guard, 99 Java + 100
Python -> counts below use the actual per-cell N_attempted=99/100).
Pre-registration: `docs/PROD_001_PREREGISTRATION.md` (H-Pilot, decision rule,
frozen scope -- written and committed before this run).

## Full diagnostic table

| Detector | Language | Family | N_att | N_appl | N_valid | N_base_ok | MeanΔ | MedianΔ | Flips | Induced Error Rate |
|---|---|---|---|---|---|---|---|---|---|---|
| DroidDetect-Base | Java | control_flow | 99 | 18 | 17 | 14 | 0.0039 | 0.0000 | 2 | 0.0714 |
| DroidDetect-Base | Java | formatting | 99 | 64 | 64 | 54 | -0.1197 | -0.0047 | 13 | **0.2407** |
| DroidDetect-Base | Java | lexical_rename | 99 | 83 | 83 | 71 | 0.0054 | 0.0000 | 4 | 0.0282 |
| DroidDetect-Base | Python | control_flow | 100 | 26 | 26 | 26 | -0.0015 | 0.0000 | 1 | 0.0385 |
| DroidDetect-Base | Python | formatting | 100 | 95 | 94 | 83 | -0.2760 | -0.0088 | 32 | **0.3494** |
| DroidDetect-Base | Python | lexical_rename | 100 | 82 | 81 | 73 | -0.0028 | 0.0000 | 6 | 0.0411 |
| LLMSniffer | Java | control_flow | 99 | 18 | 17 | 4 | 0.0233 | 0.0247 | 5 | 0.0000 |
| LLMSniffer | Java | formatting | 99 | 64 | 64 | 24 | 0.0092 | 0.0119 | 13 | 0.0833 |
| LLMSniffer | Java | lexical_rename | 99 | 83 | 83 | 35 | 0.0094 | 0.0085 | 5 | 0.0000 |
| LLMSniffer | Python | control_flow | 100 | 26 | 26 | 15 | 0.0065 | 0.0060 | 2 | 0.0000 |
| LLMSniffer | Python | formatting | 100 | 95 | 94 | 62 | 0.0036 | 0.0004 | 8 | **0.0645** |
| LLMSniffer | Python | lexical_rename | 100 | 82 | 81 | 52 | 0.0072 | 0.0056 | 1 | 0.0192 |

Full row-level data: `artifacts/prod001_detector_scores.jsonl`. Transform log
with `d_text`/`d_token`/`d_ast`: `artifacts/prod001_transform_log.jsonl`.
C0 baseline: `artifacts/prod001_c0_baseline.jsonl`.

## Pre-registered decision rule evaluation

From `docs/PROD_001_PREREGISTRATION.md`: H-Pilot is treated as replicated if
DroidDetect-Base x Python x formatting's Induced Error Rate is (a) comparable
in magnitude to the pilot's ~38.5%, (b) visibly larger than DroidDetect-Base's
other two Python families, and (c) visibly larger than LLMSniffer's Induced
Error Rate on the same cell. All three conditions hold:

- (a) 34.9% vs. pilot's 38.5% -- same order of magnitude, N=83 baseline-correct
  samples vs. the pilot's N=13.
- (b) 34.9% vs. 3.85% (control_flow) and 4.11% (lexical_rename) -- roughly
  8-9x higher within the same detector/language.
- (c) 34.9% (DroidDetect-Base) vs. 6.45% (LLMSniffer) on the identical
  Python-formatting cell -- roughly 5.4x higher.

**Verdict: H-Pilot is replicated at production scale (N=199).**

## Signature-region check

Rows satisfying `d_text>0, d_token<=5, d_ast==0, |delta_score|>=0.3` (the
PILOT_004 forensic signature: near-zero lexical/structural change, large
detector-score swing): **30 rows total, all 30 attributed to DroidDetect-Base,
zero to LLMSniffer.** Full list in the run log / regenerable from
`artifacts/prod001_detector_scores.jsonl` with the same filter. Most are
`formatting`, but several are `lexical_rename` (including one Java case with
delta=+0.99), and deltas run in both directions -- consistent with the
PILOT_004 interpretation boundary (decision-boundary instability, not
directional "AI signal decay").

## Observation outside the pre-registered scope (exploratory, not part of H-Pilot)

DroidDetect-Base's Java-formatting cell shows the same qualitative pattern
(IER=24.1% vs. 7.1%/2.8% for its other two Java families) even though H-Pilot
only named Python. This is noted as an exploratory addition, not something
this pre-registration confirms -- a separate hypothesis would need its own
pre-registration to claim it formally.

## What this does and does not license

- It licenses treating "cosmetic transformations can induce disproportionate,
  detector-specific decision-boundary instability" as a real, replicated
  phenomenon at N=199, not just a 15-sample artifact.
- It does NOT license claiming a population-level Induced Error Rate (34.9%
  is this sample's estimate, no confidence interval or significance test has
  been computed), and does NOT license claiming this is unique to formatting
  vs. lexical_rename in general (the Java lexical_rename signature-region
  cases show the same signature can occur there too, just less frequently in
  this sample).
- Per the pre-registration's decision rule, the next step is: expand the
  detector panel and introduce the richer transformation ladder. That is a
  scope decision for the next checkpoint, not executed automatically here.
