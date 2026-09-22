"""DetectCodeGPT threshold calibration, per docs/DETECTCODEGPT_PROTOCOL.md.
Calibration set is drawn from Droid's DEV split (not test), so it cannot
collide with any test-split sample used by PILOT_004/PROD_001/the
K-convergence study by construction. Threshold is frozen here and never
re-tuned after seeing PROD_002 results.
"""
import json

from datasets import load_dataset, DownloadConfig

import sys
sys.path.insert(0, "scripts")
from detectcodegpt import DetectCodeGPTDetector

N_PER_LABEL = 20  # ~40 total, binary human vs machine (matching DetectCodeGPT's framing)
CHOSEN_K = 50  # frozen from the K-convergence study


def build_calibration_sample():
    dl_config = DownloadConfig(cache_dir="data/hf_cache")
    ds = load_dataset("project-droid/DroidCollection", split="dev", download_config=dl_config)
    ds = ds.filter(lambda r: r["Language"] in ("Python", "Java"), num_proc=4)

    human, machine = [], []
    for row in ds:
        if row["Label"] == "HUMAN_GENERATED" and len(human) < N_PER_LABEL:
            human.append(row)
        elif row["Label"] in ("MACHINE_GENERATED", "MACHINE_REFINED") and len(machine) < N_PER_LABEL:
            machine.append(row)
        if len(human) >= N_PER_LABEL and len(machine) >= N_PER_LABEL:
            break
    return human + machine


def main():
    rows = build_calibration_sample()
    print(f"calibration set: {len(rows)} rows ({sum(1 for r in rows if r['Label']=='HUMAN_GENERATED')} human, "
          f"{sum(1 for r in rows if r['Label']!='HUMAN_GENERATED')} machine)")

    det = DetectCodeGPTDetector()

    scored = []
    for row in rows:
        perturbations = det.generate_perturbations(row["Code"], n=CHOSEN_K)
        s = det.score_at_k(row["Code"], perturbations, CHOSEN_K)
        binary_label = "HUMAN" if row["Label"] == "HUMAN_GENERATED" else "AI"
        scored.append({"label": row["Label"], "binary_label": binary_label, "language": row["Language"], "score": s})
        print(row["Language"], row["Label"], s)

    with open("artifacts/detectcodegpt_calibration_scores.jsonl", "w") as f:
        for r in scored:
            f.write(json.dumps(r, default=str) + "\n")

    valid = [r for r in scored if r["score"] is not None]
    scores_sorted = sorted(set(r["score"] for r in valid))
    candidate_thresholds = scores_sorted + [scores_sorted[-1] + 1] if scores_sorted else [0.0]

    # convention: score > threshold -> predicted AI (higher curvature-discrepancy statistic
    # is the direction associated with machine-generated text/code in this method family)
    best_thresh, best_acc = None, -1
    for t in candidate_thresholds:
        correct = sum(1 for r in valid if (("AI" if r["score"] > t else "HUMAN") == r["binary_label"]))
        acc = correct / len(valid) if valid else 0
        if acc > best_acc:
            best_acc, best_thresh = acc, t

    result = {"n": len(valid), "chosen_k": CHOSEN_K, "frozen_threshold": best_thresh, "calibration_accuracy": best_acc}
    with open("artifacts/detectcodegpt_calibration_result.json", "w") as f:
        json.dump(result, f, indent=2, default=str)
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
