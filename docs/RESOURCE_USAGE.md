# Compute resource usage

Recorded for the paper's reproducibility / experimental-setup section.
Figures below are measured, not estimated, except where marked.

## Hardware

- DGX A100 node (shared, multi-user), remote.
- Allocated slice: **1x MIG 3g.40gb partition** (physically one slice of an
  80GB A100), pinned via `CUDA_VISIBLE_DEVICES` for every run. All detector
  inference and model downloads in this study ran on this single partition
  -- no multi-GPU parallelism was used or needed.
- Host: 128 CPU cores, 503GB RAM (not a bottleneck at any point; all
  workloads were GPU- or single-core-bound).

## Software environment

- Two isolated Python 3.10 venvs on the same box:
  - Main venv (`torch 2.11.0+cu128`, `transformers 5.17.0`): LLMSniffer,
    DroidDetect-Base, all transformation/validation/distance code.
  - Isolated venv (`transformers==4.41.2`, pinned): DetectCodeGPT only,
    required because the main venv's `transformers` build had a library bug
    loading CodeT5p-770m's tokenizer (see `docs/DETECTCODEGPT_PROTOCOL.md`
    implementation note) -- kept separate rather than downgrading the main
    venv and risking the already-working detectors.
- Portable JDK 17 + google-java-format, installed without root (no JDK was
  present on the shared host at all, only a JRE).
- Full environment snapshot (pip freeze, torch/CUDA versions, git commit):
  `docs/env_snapshot.json`.

## Model checkpoints and storage footprint

| Model | Role | Size on disk |
|---|---|---|
| microsoft/graphcodebert-base + LLMSniffer head | detector | ~1.4MB metadata (weights in shared blob store) |
| answerdotai/ModernBERT-base + DroidDetect-Base head | detector | ~2.2MB metadata (weights in shared blob store) |
| codellama/CodeLlama-7b-hf (fp16) | DetectCodeGPT base scorer | ~13GB |
| Salesforce/codet5p-770m (fp16) | DetectCodeGPT mask-filler | ~1.4GB |
| DroidCollection (test split used) | seed corpus | 105,826 rows, loaded via `datasets`, cached as Arrow |

**Total bigdata-mount footprint for this project: ~35GB** (19GB HF model
cache incl. the CodeLlama-7B blob, 15GB across both venvs, 0.5GB JDK/
google-java-format tooling, <1.5GB pip cache/artifacts/repos). This is
deliberately kept off the shared host's home-directory disk (which was at
98% capacity at project start) via symlinks into the shared `/media/bigdata`
mount.

## Wall-clock / compute time by phase (measured)

| Phase | Measured time | Note |
|---|---|---|
| DGX provisioning (venv, JDK, storage layout) | ~15 min | one-time |
| Droid dataset audit + schema check | ~2 min | |
| PILOT_001/002 (30 seeds, 3 families) transform+validate | <1 min each | CPU-only (parsing/compiling, no model inference) |
| PILOT_003/004 detector integration + scoring (30 seeds x 2 detectors) | ~5 min | includes GraphCodeBERT/ModernBERT load |
| PROD_001 transformation pass (199 seeds x 3 families) | ~4 min | CPU-only |
| PROD_001 detector scoring (199 seeds + ~600 transforms x 2 detectors) | <10 min | models stayed loaded |
| DetectCodeGPT K-convergence study (25 seeds x K in {5,10,20,50}) | ~3 min | **after** fixing an initial sequential-generation implementation bug that made this step >15 min/sample and impractical; batched version brought it to ~5s/sample at K=50 |
| DetectCodeGPT calibration (40 dev-split seeds, K=50) | ~4 min | |
| **DetectCodeGPT PROD_002 full scoring (199 baseline + 365 transformed = 564 score() calls, K=50)** | **5.69 GPU-hours** (measured: sum of per-call elapsed time = 20,470.5s) | **by far the dominant compute cost of the entire study**; mean 36.3s/call, driven by 50 sequential mask-filling + scoring passes per call; also required a mid-run fix for a pathological slowdown on long files (uncapped mask count on long inputs produced multi-thousand-token generation calls before the fix -- see `docs/DETECTCODEGPT_PROTOCOL.md`/commit `c234922`) |
| PROD_003 transformation pass (199 seeds x 2 new families x 2 intensities) | ~5 min | CPU/javac-bound; low yield (35/796 SUCCESS) since these families' safe-applicability patterns are rare in Droid's fragment-heavy composition |

**Total GPU-hours for this study, dominated by one phase**: approximately
**6 GPU-hours on a single 40GB MIG partition**, of which **~5.7 hours (95%)
is the DetectCodeGPT scoring pass alone**. Every other detector
integration/scoring step combined (LLMSniffer + DroidDetect-Base, across all
of PILOT_003/004 and PROD_001/002) totals well under 30 minutes of GPU time.

## Implication for the paper

This is worth stating explicitly in a limitations/reproducibility section:
**zero-shot perturbation-based detectors (the DetectGPT/DetectCodeGPT
family) are dramatically more expensive to run than trained classifier
detectors (LLMSniffer, DroidDetect-Base) at the same sample count** -- roughly
two orders of magnitude in this study (5.7 GPU-hours for 564 calls vs.
single-digit minutes for the same-scale scoring with the other two
detectors). Any future scale-up of the detector panel or sample size should
budget compute accordingly, and this cost/benefit tradeoff (DetectCodeGPT's
weak 60% calibration accuracy for ~2 orders of magnitude more compute) is
itself a finding relevant to detector-panel design for future studies in
this space.
