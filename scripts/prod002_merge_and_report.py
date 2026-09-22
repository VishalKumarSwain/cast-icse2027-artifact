"""PROD_002: merge DetectCodeGPT scores with the existing frozen PROD_001
LLMSniffer/DroidDetect-Base scores into one diagnostic table across all
three detectors. DetectCodeGPT's weak calibration (60% on its independent
dev-split calibration set, see docs/DETECTCODEGPT_CALIBRATION_RESULTS.md) is
flagged explicitly in the output, not averaged away.
"""
import json
import statistics
from collections import defaultdict

prod001_rows = [json.loads(l) for l in open("artifacts/prod001_detector_scores.jsonl", encoding="utf-8")]
detectcodegpt_rows = [json.loads(l) for l in open("artifacts/prod002_detectcodegpt_scores.jsonl", encoding="utf-8")]

all_rows = prod001_rows + detectcodegpt_rows
with open("artifacts/prod002_detector_scores.jsonl", "w") as f:
    for r in all_rows:
        f.write(json.dumps(r, default=str) + "\n")

groups = defaultdict(list)
for r in all_rows:
    groups[(r["detector"], r["language"], r["transformation_family"])].append(r)

DETECTOR_CALIBRATION_NOTE = {
    "LLMSniffer": "90% in-domain sanity accuracy (GPTSniffer Java test set)",
    "DroidDetect-Base": "87.5% reconstruction-verification accuracy (Droid dev-split subset)",
    "DetectCodeGPT": "60% calibration accuracy on independent dev-split set -- NEAR CHANCE, weak instrument, see docs/DETECTCODEGPT_CALIBRATION_RESULTS.md",
}

print("\nDetector\tLanguage\tFamily\tN_valid\tBaseline_correct\tMeanD\tMedianD\tFlips\tInducedErrorRate")
table_rows = []
for (det, lang, fam), rs in sorted(groups.items()):
    deltas = [r["delta_score"] for r in rs if r.get("delta_score") is not None]
    base_ok = [r for r in rs if r.get("baseline_correct")]
    induced_errors = sum(1 for r in base_ok if r.get("flip_among_baseline_correct"))
    ier = (induced_errors / len(base_ok)) if base_ok else None
    mean_d = statistics.mean(deltas) if deltas else None
    median_d = statistics.median(deltas) if deltas else None
    flips = sum(1 for r in rs if r.get("flip"))
    row = [det, lang, fam, len(rs), len(base_ok), mean_d, median_d, flips, ier]
    table_rows.append(row)
    print("\t".join(str(x) for x in row))

with open("artifacts/prod002_diagnostic_table.csv", "w") as f:
    f.write("detector,language,family,n_valid,n_baseline_correct,mean_delta,median_delta,flips,induced_error_rate\n")
    for row in table_rows:
        f.write(",".join(str(x) for x in row) + "\n")

print("\nDetector calibration-quality notes (read alongside the table above):")
for det, note in DETECTOR_CALIBRATION_NOTE.items():
    print(f"  {det}: {note}")
