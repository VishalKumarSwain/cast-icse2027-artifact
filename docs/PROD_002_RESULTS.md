# PROD_002: Cross-Detector Replication -- Results

Same 199 C0 seeds and same PROD_001 transformed artifacts as PROD_001/frozen
protocol (`docs/PROD_002_PROTOCOL.md`). Third detector (DetectCodeGPT) added
per the K=50/threshold=2.931 frozen configuration
(`docs/DETECTCODEGPT_KCONVERGENCE_RESULTS.md`,
`docs/DETECTCODEGPT_CALIBRATION_RESULTS.md`).

## Full table

| Detector | Language | Family | N_valid | Baseline_correct | MeanΔ | MedianΔ | Flips | Induced Error Rate |
|---|---|---|---|---|---|---|---|---|
| DetectCodeGPT | Java | control_flow | 17 | 11 | 0.0002 | 0.1307 | 3 | 0.1818 |
| DetectCodeGPT | Java | formatting | 64 | 36 | 0.2182 | 0.1979 | 11 | 0.1667 |
| DetectCodeGPT | Java | lexical_rename | 83 | 48 | 0.1538 | 0.1671 | 16 | 0.1667 |
| DetectCodeGPT | Python | control_flow | 26 | 14 | 0.0528 | 0.0679 | 8 | **0.5000** |
| DetectCodeGPT | Python | formatting | 94 | 48 | 0.0788 | -0.0083 | 24 | 0.2500 |
| DetectCodeGPT | Python | lexical_rename | 81 | 43 | -0.0118 | 0.1152 | 19 | 0.3023 |
| DroidDetect-Base | Java | control_flow | 17 | 14 | 0.0039 | 0.0000 | 2 | 0.0714 |
| DroidDetect-Base | Java | formatting | 64 | 54 | -0.1197 | -0.0047 | 13 | 0.2407 |
| DroidDetect-Base | Java | lexical_rename | 83 | 71 | 0.0054 | 0.0000 | 4 | 0.0282 |
| DroidDetect-Base | Python | control_flow | 26 | 26 | -0.0015 | 0.0000 | 1 | 0.0385 |
| DroidDetect-Base | Python | formatting | 94 | 83 | -0.2760 | -0.0088 | 32 | **0.3494** |
| DroidDetect-Base | Python | lexical_rename | 81 | 73 | -0.0028 | 0.0000 | 6 | 0.0411 |
| LLMSniffer | Java | control_flow | 17 | 4 | 0.0233 | 0.0247 | 5 | 0.0000 |
| LLMSniffer | Java | formatting | 64 | 24 | 0.0092 | 0.0119 | 13 | 0.0833 |
| LLMSniffer | Java | lexical_rename | 83 | 35 | 0.0094 | 0.0085 | 5 | 0.0000 |
| LLMSniffer | Python | control_flow | 26 | 15 | 0.0065 | 0.0060 | 2 | 0.0000 |
| LLMSniffer | Python | formatting | 94 | 62 | 0.0036 | 0.0004 | 8 | 0.0645 |
| LLMSniffer | Python | lexical_rename | 81 | 52 | 0.0072 | 0.0056 | 1 | 0.0192 |

Full row-level data: `artifacts/prod002_detector_scores.jsonl`.

## Calibration-quality context (must be read alongside the table, not after)

- LLMSniffer: 90% in-domain sanity accuracy
- DroidDetect-Base: 87.5% reconstruction-verification accuracy
- **DetectCodeGPT: 60% calibration accuracy on an independent dev-split set
  -- near chance for a binary task.** Its Induced Error Rates above are
  **not on equal footing** with the other two detectors' numbers. A
  near-chance classifier will show elevated flip rates simply because many
  of its predictions sit close to an uninformative decision boundary, not
  necessarily because of genuine cosmetic-transformation sensitivity. This
  caveat is load-bearing for the interpretation below, not a footnote.

## Answering the RQ4 question this experiment was designed for

**"Is DroidDetect-Base's formatting-fragility pattern detector-specific, or
does it generalize across detector families?"**

**It does not clearly generalize as the same pattern.** Three distinct
behaviors, not one:

1. **LLMSniffer**: uniformly the most stable detector across every cell in
   this table (max Induced Error Rate 8.3%, most cells at or near 0%). No
   family stands out as disproportionately fragile for this detector.
2. **DroidDetect-Base**: formatting is clearly and specifically the fragile
   family *within this detector* -- 34.9% (Python) / 24.1% (Java) vs. 2.8-7.1%
   for its other two families. This replicates PILOT_004/PROD_001.
3. **DetectCodeGPT**: elevated instability across the board, but **not
   concentrated in formatting** the way DroidDetect-Base's is -- its worst
   cell is Python **control_flow** (50.0% IER, on a small N=14
   baseline-correct subset), not formatting (25.0%). Given its near-chance
   calibration, this pattern is at least as plausibly generic classifier
   noise as it is a genuine transformation-sensitivity signal, and the two
   are not distinguishable from this table alone.

**Conclusion for RQ4**: the evidence points toward "different detector
architectures exhibit substantially different attribution stability
patterns under the same transformations" (heterogeneous fragility) rather
than "cosmetic formatting is universally the fragile transformation
family." DroidDetect-Base's specific formatting-fragility finding from
PILOT_004/PROD_001 is real and replicated within that detector, but it is
**not** evidence of a general "formatting breaks code-AI-detectors"
phenomenon -- it is evidence that *this detector* has that specific
weakness, which is itself the more interesting and precise claim for the
paper.

## What is NOT claimed here

- Not claiming DetectCodeGPT's high Python-control_flow IER (50%) is a
  genuine transformation-sensitivity finding -- the calibration caveat above
  applies directly to it, and N=14 baseline-correct samples in that cell is
  small.
- Not claiming this is a complete cross-detector picture -- GPTSniffer and
  CodeGPTSensor/+ remain `INTEGRATION_FAILED` (no released checkpoints, see
  `docs/PROD_002_PROTOCOL.md`), so this is a 3-detector, 3-method-family
  comparison, not 5.
- Not re-running any signature-region (d_text>0, d_token small, d_ast=0,
  |delta|>>0) forensic check across all three detectors yet -- that is a
  natural next analysis before finalizing the PROD_003 (transformation
  ladder expansion) scope, not done automatically here.
