"""PROD_002: score DetectCodeGPT (frozen K=50, frozen threshold=2.931) over
the same 199 C0 seeds + the same PROD_001 successful transformations used by
LLMSniffer/DroidDetect-Base. Runs in .venv_detectcodegpt.
"""
import functools
import json
import time

import sys
sys.path.insert(0, "scripts")
from detectcodegpt import DetectCodeGPTDetector

print = functools.partial(print, flush=True)  # stdout is fully buffered when redirected to a
                                                # file -- without flush=True, progress prints are
                                                # invisible until the buffer fills or exit

CHOSEN_K = 50
FROZEN_THRESHOLD = 2.931085010288198  # from docs/DETECTCODEGPT_CALIBRATION_RESULTS.md


def predicted_label(score):
    if score is None:
        return None
    return "AI" if score > FROZEN_THRESHOLD else "HUMAN"


def provenance_binary(label):
    return "HUMAN" if label == "HUMAN_GENERATED" else "AI"


def main():
    det = DetectCodeGPTDetector()

    manifest = {json.loads(l)["sample_id"]: json.loads(l) for l in open("artifacts/pilot_manifest_prod001.jsonl", encoding="utf-8")}
    transform_log = [json.loads(l) for l in open("artifacts/prod001_transform_log.jsonl", encoding="utf-8")]
    success_rows = [r for r in transform_log if r["status"] == "SUCCESS"]

    baseline = {}
    for n, (sid, row) in enumerate(manifest.items()):
        t0 = time.time()
        perturbations = det.generate_perturbations(row["code"], n=CHOSEN_K)
        s0 = det.score_at_k(row["code"], perturbations, CHOSEN_K)
        elapsed = time.time() - t0
        pred = predicted_label(s0)
        correct = (pred == provenance_binary(row["label"])) if pred is not None else None
        baseline[sid] = {"sample_id": sid, "language": row["language"], "label": row["label"], "s0": s0, "pred0": pred, "baseline_correct": correct}
        print(f"baseline {n + 1}/{len(manifest)} sid={sid} code_len={len(row['code'])} elapsed={elapsed:.1f}s")

    with open("artifacts/prod002_detectcodegpt_c0_baseline.jsonl", "w") as f:
        for sid, entry in baseline.items():
            f.write(json.dumps(entry, default=str) + "\n")

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
                "detector": "DetectCodeGPT",
                "baseline_correct": b["baseline_correct"],
                "s0": b["s0"],
                "sT": sT,
                "delta_score": (sT - b["s0"]) if (sT is not None and b["s0"] is not None) else None,
                "flip": (predT != b["pred0"]) if (predT is not None and b["pred0"] is not None) else None,
                "flip_among_baseline_correct": (b["baseline_correct"] and predT != b["pred0"]) if (b["baseline_correct"] is not None and predT is not None and b["pred0"] is not None) else None,
                "d_text": row.get("d_text"),
                "d_token": row.get("d_token"),
                "d_ast": row.get("d_ast"),
            }
        )
        print(f"transformed {n + 1}/{len(success_rows)} sid={sid} family={row['transformation_family']} code_len={len(code_t)} elapsed={elapsed:.1f}s")

    with open("artifacts/prod002_detectcodegpt_scores.jsonl", "w") as f:
        for r in results:
            f.write(json.dumps(r, default=str) + "\n")

    print(f"done: {len(baseline)} baseline, {len(results)} transformed scored")


if __name__ == "__main__":
    main()
