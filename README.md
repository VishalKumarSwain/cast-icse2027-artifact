# CAST: Code Attribution Stability Testing -- Artifact

This repository contains the scripts, frozen result artifacts, protocol/results
documentation, and the manuscript for the ICSE 2027 NIER submission "CAST: Testing
the Attribution Stability of AI-Generated-Code Detectors Under Controlled Source
Transformations."

This repository is anonymized for double-blind review. It contains no author
identity, institution, or personal information.

## Contents

- `scripts/` -- all experiment scripts: manifest construction, transformation
  families, distance metrics, detector wrappers, scoring, canonicalization,
  final-table and figure generation.
- `artifacts/` -- frozen experiment outputs (JSONL score files, transformation
  logs, diagnostic tables, `final_tables/` with the CSVs and figures the paper's
  tables and plots are built from).
- `docs/` -- pre-registration and results write-ups for each experiment phase
  (PILOT_003/004, PROD_001-004), the DetectCodeGPT calibration/convergence
  studies, and environment snapshot.
- `paper/` -- the manuscript source (`CAST_ICSE2027_NIER.tex`), compiled PDF,
  bibliography, and figures.

## Dataset

Experiments use the held-out test split of DroidCollection
(https://huggingface.co/datasets/project-droid/DroidCollection), not redistributed
here; see `docs/droid_audit.json` and `docs/DESIGN.md` for how the split and
manifests were constructed.

## Reproducing the tables and figures

```
python scripts/final_tables.py     # rebuilds artifacts/final_tables/*.csv
python scripts/make_figures.py     # rebuilds artifacts/final_tables/figures/*.png
```

Both operate only on the frozen JSONL artifacts already included in this
repository; no GPU or model download is required to regenerate the paper's
tables and figures from them.

## Model checkpoints

Detector checkpoints and cached HF models are not included (multi-GB, third-party
artifacts). `docs/env_snapshot.json` records the environment and checkpoint
provenance used for the reported results.
