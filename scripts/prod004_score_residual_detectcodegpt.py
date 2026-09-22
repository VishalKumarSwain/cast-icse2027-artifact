"""PROD_004 step 2b: score canon(C0)/canon(T) for the 50 residual pairs with
DetectCodeGPT (frozen K=50). Runs in .venv_detectcodegpt.
"""
import functools
import json
import time

import sys
sys.path.insert(0, "scripts")
from detectcodegpt import DetectCodeGPTDetector

print = functools.partial(print, flush=True)
CHOSEN_K = 50


def main():
    det = DetectCodeGPTDetector()
    pairs = [json.loads(l) for l in open("artifacts/prod004_canonicalized_pairs.jsonl", encoding="utf-8")]
    residual = [p for p in pairs if not p["identical"]]

    results = []
    for n, p in enumerate(residual):
        sid = p["sample_id"]
        t0 = time.time()
        pert0 = det.generate_perturbations(p["canon0"], n=CHOSEN_K)
        s0 = det.score_at_k(p["canon0"], pert0, CHOSEN_K)
        pertt = det.generate_perturbations(p["canont"], n=CHOSEN_K)
        sT = det.score_at_k(p["canont"], pertt, CHOSEN_K)
        elapsed = time.time() - t0
        results.append(
            {
                "sample_id": sid, "language": p["language"],
                "DetectCodeGPT_s0": s0, "DetectCodeGPT_sT": sT,
                "DetectCodeGPT_delta_canon": (sT - s0) if (s0 is not None and sT is not None) else None,
            }
        )
        print(f"{n + 1}/{len(residual)} sid={sid} elapsed={elapsed:.1f}s")

    with open("artifacts/prod004_residual_scores_detectcodegpt.jsonl", "w") as f:
        for r in results:
            f.write(json.dumps(r, default=str) + "\n")
    print(f"done: {len(results)} scored")


if __name__ == "__main__":
    main()
