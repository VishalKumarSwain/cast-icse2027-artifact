# DetectCodeGPT threshold calibration -- results

Protocol: `docs/DETECTCODEGPT_PROTOCOL.md`. Calibration set: 40 samples
(20 HUMAN_GENERATED, 20 machine-labeled) from Droid's **dev** split --
disjoint by construction (different split, not just different seed) from
every test-split sample used in PILOT_004, PROD_001, and the K-convergence
study. K frozen at 50 per `docs/DETECTCODEGPT_KCONVERGENCE_RESULTS.md`.

## Result

- **Frozen threshold: s > 2.931 -> predicted AI**
- **Calibration accuracy: 60.0%** (24/40)
- Full per-sample scores: `artifacts/detectcodegpt_calibration_scores.jsonl`

This threshold is frozen and will not be re-tuned after seeing PROD_002
results, per protocol.

## Honest assessment: this is weak discriminative performance

60% accuracy on a balanced binary task is barely above the 50% chance
baseline. Raw scores for HUMAN_GENERATED and machine-labeled samples heavily
overlap (both range roughly 1-5 in this sample), rather than forming
separable clusters. This must be disclosed as a limitation of this
detector's integration, not smoothed over.

**Plausible contributing factors** (not adjudicated here, listed for future
reference, none of them justify going back to retune the frozen protocol
now):

1. Our masking/perturbation scheme is a documented deviation from the
   paper's exact approach (see `docs/PROD_002_PROTOCOL.md`) -- we use
   generic word-span masking rather than their identifier-targeted masking
   (`pct_identifiers_masked=0.75` in their default config specifically
   targets identifiers, which we did not replicate; ours masks arbitrary
   word spans at `pct_words_masked=0.5` instead).
2. CodeLlama-7b-hf's log-likelihood behavior on Droid's specific code
   distribution (competitive programming snippets, function fragments, etc.)
   may differ from the corpora (CodeSearchNet/TheVault) the original paper
   validated against.
3. General reimplementation gap -- this is our own reconstruction of the
   DetectGPT/NPR-family statistic for code, not the paper's original
   pipeline verbatim.

## What this means for PROD_002

Per `docs/DETECTCODEGPT_PROTOCOL.md`, the raw statistic `s_50` and its
sample-level delta (`delta_score = s_T - s_0`) are preserved and remain the
primary analysis object regardless of threshold quality -- the
attribution-stability analysis (RQ1/RQ4) does not depend on this threshold
being a good binary classifier. However, any PROD_002 result that depends on
DetectCodeGPT's *predicted label* / flip count (as opposed to its raw score
delta) must be reported alongside this 60% calibration accuracy, and
interpreted as weak-instrument evidence, not a well-calibrated detector on
par with LLMSniffer (90% in-domain sanity) or DroidDetect-Base (87.5%
reconstruction-verification accuracy).

This is itself a legitimate PROD_002 finding worth keeping: not every
detector family integrates equally well from public artifacts, and that
variability is part of the answer to "how detector-specific is attribution
stability," not noise to average away.
