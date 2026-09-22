# DetectCodeGPT K-convergence study -- results

Protocol: `docs/DETECTCODEGPT_PROTOCOL.md`. N=25 held-out samples, disjoint
from PILOT_004 (30) and PROD_001 (199), Droid test split. Nested-K design
(K=5/10/20 computed as prefixes of the same K=50 perturbation draw per
sample, not independent redraws).

## Implementation note (before the results, since it affects them)

The first implementation looped one perturbation-fill `generate()` call at a
time with `max_new_tokens=256` (oversized for ~2-word masked spans) and one
log-likelihood forward pass at a time. This made the study impractically
slow (>15 min for a single sample with no completion after 24 minutes of
CPU time) and was killed before producing any numbers. It was replaced with
a batched implementation (all K perturbations mask-filled in one batched
`generate()` call, all K+1 log-likelihoods scored in one batched forward
pass, `max_new_tokens` reduced to a per-mask budget) before any convergence
number was computed. This is an engineering fix, not a change to the
statistic or the protocol -- `s_K` is defined identically before and after.

## Results

| K | n | rho_vs_k50 | median_abs_diff | relative_deviation | mean_runtime_sec | passes_rule |
|---|---|---|---|---|---|---|
| 5 | 25 | 0.786 | 1.134 | 0.889 | 0.556 | **False** |
| 10 | 25 | 0.870 | 0.678 | 0.531 | 1.004 | **False** |
| 20 | 25 | 0.905 | 0.518 | 0.406 | 1.904 | **False** |
| 50 | 25 | 1.000 | 0.000 | 0.000 | 4.775 | True (reference) |

Full per-sample scores: `artifacts/detectcodegpt_kconv_results.jsonl`.
Full report: `artifacts/detectcodegpt_kconv_report.json`.

## Decision (per the predeclared rule, not adjusted after seeing this table)

Rule: smallest K in {5,10,20,50} with rho>=0.95 AND relative_deviation<=0.10,
else K=50.

None of K=5/10/20 clear either threshold -- K=20 comes closest
(rho=0.905, relative_deviation=0.406) but is not close to either bound.

**CHOSEN K = 50.**

## Consequence for PROD_002

K=50 was expected to be the expensive choice; the batching fix makes it
tractable regardless (4.78 sec/sample mean at K=50, after the fix). For
PROD_002's full scoring pass (199 C0 + the existing ~600 successful
transformed artifacts from PROD_001, ~800 score() calls total), this
projects to roughly 60-70 minutes of DetectCodeGPT scoring -- acceptable.

No perturbation-count approximation is used in PROD_002; every DetectCodeGPT
score is computed at the paper's own K=50.
