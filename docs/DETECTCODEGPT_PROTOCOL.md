# DetectCodeGPT integration: K-convergence + calibration protocol

Written and committed BEFORE downloading CodeLlama-7b-hf / CodeT5p-770m or
running anything. Locks the perturbation count and the calibration procedure
as methodological decisions, not runtime settings tuned after seeing scores.

## Why this exists

DetectCodeGPT's published configuration uses K=50 perturbations per sample.
Silently using a smaller K to save compute would let a reviewer reasonably
ask whether any observed instability comes from our approximation of the
method rather than from DetectCodeGPT itself. This protocol fixes the
acceptance rule for a smaller K, and the calibration procedure, before
either is run.

## Statistic

Following the DetectGPT/DetectLLM-NPR family DetectCodeGPT extends: for code
`c`, generate `K` masked-span perturbations `c~_1 ... c~_K` via the mask-
filling model, score log-likelihood (or log-rank) of `c` and each `c~_i`
under the base scoring model, and compute

  s_K(c) = (LL(c) - mean_i LL(c~_i)) / std_i LL(c~_i)

(the DetectGPT z-score form; larger positive values indicate the base model
finds the original less "curved" relative to its perturbed neighborhood --
the direction associated with machine-generated text/code in this family of
methods).

**Nested-perturbation design** (this is the key methodological choice that
makes the K-comparison clean): generate the full K=50 perturbation set ONCE
per sample with a fixed seed, then compute s_K for K in {5, 10, 20, 50} using
the first K perturbations of that same set as a prefix. This isolates the
effect of perturbation COUNT from perturbation-sample variance -- s_5, s_10,
s_20 are literally computed from subsets of the same s_50 perturbation draw,
not independent redraws.

## K-convergence study design

- **Sample**: 25 held-out C0 seeds from Droid's **test** split, drawn with a
  NEW fixed seed disjoint from every sample_id already used in PILOT_004 (30)
  and PROD_001 (199). Recorded before running.
- **Procedure**: for each of the 25 samples, generate 50 perturbations once,
  compute s_K for K in {5, 10, 20, 50}, record runtime per K.
- **Metrics against the K=50 reference**, computed across the 25 samples:
  - Spearman rank correlation rho(s_K, s_50)
  - Relative deviation: median(|s_K - s_50|) / std(s_50 across the 25 samples)
  - Wall-clock runtime per sample at each K

## Predeclared acceptance rule (fixed now, not after seeing results)

Choose the smallest K in {5, 10, 20, 50} such that BOTH:

  rho(s_K, s_50) >= 0.95
  median(|s_K - s_50|) / std(s_50) <= 0.10

If no K < 50 satisfies both conditions, use K=50 (the paper's own default)
and accept the runtime cost. This rule is fixed before the convergence study
runs; the acceptance thresholds (0.95, 0.10) are not adjusted after seeing
the data.

## Threshold calibration (kept independent of PROD_002's evaluation set)

DetectCodeGPT ships no universal decision threshold -- the paper calibrates
per-dataset. Calibrating on the same 199 C0 samples used for PROD_002's
evaluation would contaminate that evaluation (the threshold would be fit to
exactly the data whose baseline accuracy we then report).

- **Calibration set**: ~40 samples drawn from Droid's **dev** split (a
  different split entirely from the test split used by PILOT_004/PROD_001/
  the K-convergence study -- not just a different seed, so there is no
  possibility of sample_id collision by construction), stratified across
  HUMAN_GENERATED vs. the machine labels collapsed to a binary AI class
  (matching DetectCodeGPT's binary human-vs-machine framing).
- **Procedure**: compute s_K (at the frozen K from the convergence study) on
  the calibration set, sweep a threshold on `s_K`, pick the threshold
  maximizing accuracy on this calibration set only, freeze it.
- **This threshold is never re-tuned after seeing PROD_002 results.**

## What is preserved regardless of threshold quality

The raw statistic `s_K` (and per-sample `delta_score = s_T - s_0`) is
preserved for every C0 and transformed sample regardless of calibration
quality. The core attribution-stability analysis (score deltas, and flips
computed against the frozen threshold) does not depend entirely on the
calibrated cutoff being well-chosen -- `delta_score` remains informative even
if the threshold itself turns out to be a weak binary decision boundary.

## Frozen sequence

1. Implement DetectCodeGPT wrapper (`scripts/detectcodegpt.py`)
2. Contract sanity check (small labeled subset, disjoint from the
   convergence and calibration sets)
3. K-convergence study (25 samples, K in {5,10,20,50}, predeclared rule above)
4. Choose K per the rule -- record the chosen K and why
5. Calibrate threshold on the independent dev-split set -- freeze it
6. Only then run PROD_002 on the frozen 199 C0 + existing transformations,
   comparing all three detectors (LLMSniffer, DroidDetect-Base,
   DetectCodeGPT)

GPTSniffer and CodeGPTSensor/+ remain `INTEGRATION_FAILED` per
`docs/PROD_002_PROTOCOL.md` -- not trained from scratch for this study, since
that would introduce a new experimental dimension (our own training-data
selection and reproduction fidelity) outside this project's scope.
