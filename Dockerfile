# Reproduces every table and figure in the CAST paper from the frozen
# result artifacts already checked into this repository -- no GPU and no
# model download required. This covers scripts/final_tables.py and
# scripts/make_figures.py, i.e. the "Functional" reproduction path
# described in the paper's Artifact Availability Statement.
#
# It does NOT run the detector-scoring scripts themselves (detectors.py,
# detectcodegpt.py and the scripts that call them), since those require
# downloading third-party model checkpoints (GraphCodeBERT, ModernBERT,
# CodeLlama-7B, CodeT5p-770M) and, for DetectCodeGPT, a GPU. Those
# checkpoints' exact versions and provenance are recorded in
# docs/env_snapshot.json; see the README for how to obtain and run them.
#
# Build:  docker build -t cast-reproduce .
# Run:    docker run --name cast-run cast-reproduce
#         docker cp cast-run:/artifact/artifacts/final_tables ./out
#         docker rm cast-run
#         (regenerated tables/figures land in ./out on the host; `docker cp`
#         is used instead of a volume mount because -v path translation is
#         unreliable across Windows/macOS/Linux shells -- verified during
#         artifact preparation)

FROM python:3.10-slim

WORKDIR /artifact

COPY requirements-reproduce.txt .
RUN pip install --no-cache-dir -r requirements-reproduce.txt

COPY scripts/final_tables.py scripts/final_tables.py
COPY scripts/make_figures.py scripts/make_figures.py
COPY scripts/reviewer_round2_analysis.py scripts/reviewer_round2_analysis.py
COPY scripts/significance_tests.py scripts/significance_tests.py
COPY scripts/confound_analysis.py scripts/confound_analysis.py
COPY artifacts/ artifacts/

CMD ["sh", "-c", "python scripts/final_tables.py && python scripts/make_figures.py && python scripts/reviewer_round2_analysis.py && python scripts/significance_tests.py && python scripts/confound_analysis.py && echo 'Regenerated tables/figures are in artifacts/final_tables/'"]
