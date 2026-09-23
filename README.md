# CAST: Code Attribution Stability Testing -- Artifact

This repository contains the scripts, frozen result artifacts, and protocol/results
documentation for "CAST: Testing the Attribution Stability of AI-Generated-Code
Detectors Under Controlled Source Transformations." It supports two parallel paper
submissions built from the same experiments: an ICSE 2027 NIER submission and an
ISEC 2027 Regular-paper submission (both manuscripts are included under `paper/`).

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
- `paper/` -- both manuscript sources (`CAST_ICSE2027_NIER.tex` for the ICSE
  2027 NIER track, `CAST_ISEC2027.tex` for the ISEC 2027 Regular-paper track),
  their compiled PDFs, and figures.

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
```

All three scripts operate only on the frozen JSONL/CSV artifacts already
included in this repository; no GPU or model download is required for this
reproduction path. It regenerates every number and figure reported in the
paper directly from frozen data, with no manual editing step in between.

## Model checkpoints

Detector checkpoints and cached HF models are not included (multi-GB, third-party
artifacts). `docs/env_snapshot.json` records the environment and checkpoint
provenance used for the reported results.
