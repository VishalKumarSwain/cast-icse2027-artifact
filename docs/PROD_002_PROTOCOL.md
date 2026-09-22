# PROD_002: Cross-Detector Replication -- Protocol

Written and committed BEFORE running any new detector, per methodology
decision: detector selection and integration-status calls are made before
seeing any results on our corpus, not after.

## What stays frozen from PROD_001

- Same 199 C0 seeds (`artifacts/pilot_manifest_prod001.jsonl`)
- Same transformed artifacts (`artifacts/prod001_transform_log.jsonl`,
  `artifacts/transformed_prod001/`)
- Same `d_text` / `d_token` / `d_ast` distance metrics
- Same validation logic
- No new transformation families or intensities introduced here (that is
  PROD_003's job)

**Only variable changed: detector panel.**

## Candidate detectors and verified integration status

Three candidates were proposed, each checked against its actual public
repository BEFORE any integration attempt:

### 1. GPTSniffer (original, CodeBERT-based) -- **INTEGRATION_FAILED**

- Repo: `github.com/MDEGroup/GPTSniffer`
- Checked: full repo file tree for any `.bin`/`.pt`/`.pth`/`.ckpt`/
  `.safetensors` checkpoint file. **None found.** The repository ships
  training/evaluation code (`GPTSniffer/gptsniffer.py`) and the paper's
  dataset materials, but not a released trained model.
- Note: our existing LLMSniffer detector already trains on and reports
  against the GPTSniffer *dataset* using a different architecture
  (GraphCodeBERT, not CodeBERT) -- that is not a substitute for the original
  paper's own CodeBERT-based checkpoint, and is not represented as one.
- Disposition: would require training a CodeBERT classifier from scratch on
  the GPTSniffer dataset ourselves. That is a materially different task from
  "integrate a released detector" -- it introduces our own training
  decisions (hyperparameters, epochs, seed) as a new confound, and is out of
  scope for this checkpoint. **Recorded as INTEGRATION_FAILED, not silently
  substituted.**

### 2. CodeGPTSensor / CodeGPTSensor+ -- **INTEGRATION_FAILED**

- Repo: `github.com/doriscullen/CodeGPTSensor`
- Checked: repo tree and README. Ships `model.py` / `run.py` (UniXcoder-based,
  contrastive-learning training script) and `dataset.zip`, but the
  `models_output/` directory is explicitly empty ("Models will be saved
  here") -- **no released trained checkpoint.** README's own usage
  instructions start from `--do_train`, 20 epochs, no pretrained weights
  path.
- CodeGPTSensor+ (the adversarially-trained, MIST-augmented variant) is
  described in the paper but no separate released checkpoint was found
  either.
- Disposition: same reasoning as GPTSniffer -- training from scratch would
  introduce new confounds and is out of scope here. **Recorded as
  INTEGRATION_FAILED.**

### 3. DetectCodeGPT -- **CONDITIONAL GO (heavier integration than LLMSniffer/DroidDetect-Base)**

- Repo: `github.com/YerbaPage/DetectCodeGPT` (ICSE 2025, MIT license)
- This is a **zero-shot** method (perturbation-based naturalness/log-rank
  discrepancy, in the DetectGPT/DetectLLM-NPR family) -- no trained
  classifier checkpoint is needed, which is exactly why it survives this
  screen when the other two don't.
- Contract, as shipped in `code-detection/main.py`'s default config:
  - `base_model_name`: `codellama/CodeLlama-7b-hf` (scores log-likelihood /
    log-rank of the code under this model)
  - `mask_filling_model_name`: `Salesforce/codet5p-770m` (generates masked-
    span perturbations of the input)
  - `n_perturbation_list`: 50 perturbations per sample (paper default)
  - `pct_words_masked`: 0.5, `pct_identifiers_masked`: 0.75, `span_length`: 2
  - Output: an unnormalized statistic (log-rank / log-likelihood
    discrepancy under perturbation), **not a probability** -- no shipped
    decision threshold; the paper calibrates thresholds per-dataset. We will
    calibrate a threshold empirically on our own C0 baseline set and record
    that explicitly as our own calibration, not the paper's.
  - Supported languages: language-agnostic in principle (works on any code
    CodeLlama can score), validated by the paper on Python/Java-adjacent
    corpora (CodeSearchNet, TheVault).
- **Planned deviation from the paper's exact setup** (to keep compute
  tractable on our MIG slice and sample count): reduce perturbations per
  sample from 50 to a smaller number (to be fixed before running, not tuned
  after seeing scores) and use the simpler log-rank/log-likelihood
  perturbation-discrepancy formula directly rather than the full NPR
  ensemble machinery in their repo. This is a genuine reproduction of the
  DetectGPT/DetectCodeGPT *family* of statistic, not a byte-for-byte
  reproduction of their exact experimental pipeline -- documented here as a
  deviation, not hidden.
- Resource cost, disclosed before running: CodeLlama-7b-hf (~13GB in fp16)
  plus CodeT5p-770m (~1.5GB) need to be downloaded and held on the MIG
  slice's 40GB budget alongside GraphCodeBERT/ModernBERT already loaded --
  feasible but the first genuinely heavy download/compute step in this
  project so far. Estimated scoring cost: on the order of tens of minutes to
  ~1-2 hours for ~800 score() calls (199 C0 + ~600 transformed artifacts)
  depending on perturbation count chosen.

## What counts as successful integration (pre-registered, per detector)

- **Checkpoint/model loads without error**, matching a documented
  architecture (as done for DroidDetect-Base's reconstruction).
- **Sanity check against a small labeled set disjoint from PROD_001/PILOT_004**
  reaches non-trivial accuracy (same bar as PILOT_003: informally, well above
  chance for the label cardinality involved).
- **Reproducible score() contract**: same code in -> same score out, with
  truncation/perturbation-count logged per call the same way LLMSniffer and
  DroidDetect-Base already log truncation.
- Failing any of the above -> `INTEGRATION_FAILED`, recorded, not patched by
  changing the corpus or silently dropping the detector from the writeup.

## Net panel for PROD_002

- LLMSniffer (frozen from PROD_001)
- DroidDetect-Base (frozen from PROD_001)
- DetectCodeGPT (new; zero-shot, log-rank/log-likelihood perturbation
  discrepancy family, per contract above)
- GPTSniffer: **INTEGRATION_FAILED**, excluded, reason on record above
- CodeGPTSensor/CodeGPTSensor+: **INTEGRATION_FAILED**, excluded, reason on
  record above

This changes PROD_002 from a planned 5-detector comparison to a 3-detector
one. That is reported as a finding about panel feasibility, not adjusted by
substituting untrained models to hit a target count.
