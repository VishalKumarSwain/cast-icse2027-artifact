"""PROD_003: score DetectCodeGPT on the 35 SUCCESS rows only, reusing the
frozen C0 baseline scores already computed in PROD_002 (same 199 seeds,
same K=50/threshold=2.931 contract). Runs in .venv_detectcodegpt.
"""
import functools
import json
import time

import sys
sys.path.insert(0, "scripts")
from detectcodegpt import DetectCodeGPTDetector

print = functools.partial(print, flush=True)

CHOSEN_K = 50
FROZEN_THRESHOLD = 2.931085010288198


def predicted_label(score):
    if score is None:
        return None
    return "AI" if score > FROZEN_THRESHOLD else "HUMAN"


def main():
    det = DetectCodeGPTDetector()

    baseline = {json.loads(l)["sample_id"]: json.loads(l) for l in open("artifacts/prod002_detectcodegpt_c0_baseline.jsonl", encoding="utf-8")}
    transform_log = [json.loads(l) for l in open("artifacts/prod003_transform_log.jsonl", encoding="utf-8")]
    success_rows = [r for r in transform_log if r["status"] == "SUCCESS"]

    results = []
    for n, row in enumerate(success_rows):
        sid = row["sample_id"]
        code_t = open(row["output_path"], encoding="utf-8").read()
        t0 = time.time()
        perturbations_t = det.generate_perturbations(code_t, n=CHOSEN_K)
        sT = det.score_at_k(code_t, perturbations_t, CHOSEN_K)
        elapsed = time.time() - t0
        predT = predicted_label(sT)
        b = baseline[sid]
        results.append(
            {
                "sample_id": sid,
                "language": row["language"],
                "label": row["label"],
                "transformation_family": row["transformation_family"],
                "intensity": row["intensity"],
                "detector": "DetectCodeGPT",
                "baseline_correct": b["baseline_correct"],
                "s0": b["s0"],
                "sT": sT,
                "delta_score": (sT - b["s0"]) if (sT is not None and b["s0"] is not None) else None,
                "flip": (predT != b["pred0"]) if (predT is not None and b["pred0"] is not None) else None,
                "d_text": row.get("d_text"),
                "d_token": row.get("d_token"),
                "d_ast": row.get("d_ast"),
                "semantic_check": row.get("semantic_check"),
            }
        )
        print(f"{n + 1}/{len(success_rows)} sid={sid} family={row['transformation_family']} intensity={row['intensity']} elapsed={elapsed:.1f}s")

    with open("artifacts/prod003_detectcodegpt_scores.jsonl", "w") as f:
        for r in results:
            f.write(json.dumps(r, default=str) + "\n")
    print(f"done: {len(results)} scored")


if __name__ == "__main__":
    main()
