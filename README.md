# CAST: Code Attribution Stability Testing -- Artifact

This repository contains the scripts, frozen result artifacts, and protocol/results
documentation for "CAST: Testing the Attribution Stability of AI-Generated-Code
Detectors Under Controlled Source Transformations," submitted to ISEC 2027 (Regular
paper track). It contains no author identity, institution, or personal information.

The GitHub repository additionally includes the manuscript source under `paper/`,
for reviewer convenience during double-blind review; a code+data-only archival
bundle (no `paper/`) is attached to this repo's GitHub Release for permanent
archival (e.g. on Zenodo), separate from the venue submission itself.

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
- `paper/` -- the manuscript source (`CAST_ISEC2027.tex`), compiled PDF,
  bibliography, and figures.

## Dataset

Experiments use the held-out test split of DroidCollection
(https://huggingface.co/datasets/project-droid/DroidCollection), not redistributed
here; see `docs/droid_audit.json` and `docs/DESIGN.md` for how the split and
manifests were constructed.

## Reproducing the tables and figures

**Option A -- Docker (recommended, zero setup):**

```
docker build -t cast-reproduce .
docker run --name cast-run cast-reproduce
docker cp cast-run:/artifact/artifacts/final_tables ./out
docker rm cast-run
```

`./out` will contain every regenerated CSV/Markdown table and PNG figure.
`docker cp` is used instead of a `-v` volume mount because volume-mount path
translation is unreliable across Windows/macOS/Linux shells; this exact
sequence was verified to work during artifact preparation.

**Option B -- local Python:**

```
pip install -r requirements-reproduce.txt
python scripts/final_tables.py             # rebuilds artifacts/final_tables/*.csv
python scripts/make_figures.py             # rebuilds artifacts/final_tables/figures/*.png
python scripts/reviewer_round2_analysis.py # rebuilds table7-10 (confusion matrices,
                                            # flip direction, saturation, distance correlation)
python scripts/significance_tests.py     # Fisher exact test (58.0% vs 5.2%)
python scripts/confound_analysis.py       # length / edit-size confound analysis, accuracy check, table13
```

All of these scripts operate only on the frozen JSONL/CSV artifacts already
included in this repository; no GPU or model download is required for this
reproduction path. It regenerates every number and figure reported in the
paper directly from frozen data, with no manual editing step in between.

## Model checkpoints

Detector checkpoints and cached HF models are not included (multi-GB, third-party
artifacts). `docs/env_snapshot.json` records the environment and checkpoint
provenance used for the reported results.
