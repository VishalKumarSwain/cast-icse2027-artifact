"""PROD_003: merge all three detectors' scores on the 35 SUCCESS rows and
report a diagnostic table with N shown explicitly per cell -- most cells
here are N=1 to N=12, so no cell is treated as a population estimate.
"""
import json
import statistics
from collections import defaultdict

rows_a = [json.loads(l) for l in open("artifacts/prod003_llmsniffer_droiddetect_scores.jsonl", encoding="utf-8")]
rows_b = [json.loads(l) for l in open("artifacts/prod003_detectcodegpt_scores.jsonl", encoding="utf-8")]
all_rows = rows_a + rows_b

with open("artifacts/prod003_detector_scores.jsonl", "w") as f:
    for r in all_rows:
        f.write(json.dumps(r, default=str) + "\n")

groups = defaultdict(list)
for r in all_rows:
    groups[(r["detector"], r["language"], r["transformation_family"], r["intensity"])].append(r)

print(f"{'Detector':16} {'Lang':8} {'Family':16} {'Intensity':10} {'N':>3} {'BaseOK':>6} {'MeanD':>8} {'MedianD':>8} {'Flips':>6}")
for key, rs in sorted(groups.items()):
    det, lang, fam, intensity = key
    deltas = [r["delta_score"] for r in rs if r.get("delta_score") is not None]
    base_ok = sum(1 for r in rs if r.get("baseline_correct"))
    flips = sum(1 for r in rs if r.get("flip"))
    mean_d = statistics.mean(deltas) if deltas else None
    median_d = statistics.median(deltas) if deltas else None
    n = len(rs)
    print(f"{det:16} {lang:8} {fam:16} {intensity:10} {n:>3} {base_ok:>6} "
          f"{(f'{mean_d:.4f}' if mean_d is not None else 'NA'):>8} "
          f"{(f'{median_d:.4f}' if median_d is not None else 'NA'):>8} {flips:>6}")

print("\nNOTE: N ranges from 1 to 12 per cell here -- these are individual data")
print("points / small illustrative samples, not population estimates. Compare")
print("against PROD_001/PROD_002's N=17-94 per cell for the earlier families.")
