"""Post-hoc fix for a reviewer-caught construct-validity gap: DroidDetect-Base's
IER (Table I / prod001_run.py) was computed from 4-way predicted_label_mapped
flips, so a flip between MACHINE_GENERATED and MACHINE_REFINED counted as an
"error" even though the human-vs-AI verdict never changed. This script re-scores
the 365 already-transformed PROD_001 files (frozen artifacts, no new sampling)
with the frozen DroidDetect-Base checkpoint/permutation, collapses both the
baseline and transformed predictions to HUMAN/AI, and reports the corrected
2-class IER next to the original 4-class one so the two can be compared directly.
"""
import json
import statistics
import sys
from collections import defaultdict

sys.path.insert(0, "scripts")
from detectors import DroidDetectDetector

DROID_LABEL_NAMES = ["HUMAN_GENERATED", "MACHINE_GENERATED", "MACHINE_REFINED", "MACHINE_GENERATED_ADVERSARIAL"]


def provenance_binary(label):
    return "HUMAN" if label == "HUMAN_GENERATED" else "AI"


def wilson_ci(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    half = (z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5)) / denom
    return (max(0.0, center - half), min(1.0, center + half))


def main():
    with open("artifacts/pilot003_detector_contracts.json") as f:
        contracts = json.load(f)
    droid_ckpt = contracts["droiddetect_base"]["checkpoint"]
    chosen_pooling = contracts["droiddetect_base"]["chosen_pooling"]
    chosen_perm = tuple(contracts["droiddetect_base"]["chosen_label_permutation"])
    droid_perm_applied = [DROID_LABEL_NAMES[chosen_perm[i]] for i in range(4)]

    droid_det = DroidDetectDetector(droid_ckpt, pooling=chosen_pooling)

    def mapped_label(code, language):
        r = droid_det.score(code, language)
        raw_idx = droid_det.label_names.index(r["predicted_label"])
        return droid_perm_applied[raw_idx]

    baseline = {r["sample_id"]: r for r in (json.loads(l) for l in open("artifacts/prod001_c0_baseline.jsonl", encoding="utf-8"))}

    transform_log = [json.loads(l) for l in open("artifacts/prod001_transform_log.jsonl", encoding="utf-8")]
    success_rows = [r for r in transform_log if r["status"] == "SUCCESS"]

    out_rows = []
    for n, row in enumerate(success_rows):
        sid = row["sample_id"]
        base_entry = baseline[sid]
        b_droid = base_entry["scores"]["DroidDetect-Base"]
        b_mapped_4 = b_droid["predicted_label_mapped"]
        b_mapped_2 = provenance_binary(b_mapped_4)
        baseline_correct_2class = b_mapped_2 == provenance_binary(row["label"])

        code_t = open(row["output_path"], encoding="utf-8").read()
        t_mapped_4 = mapped_label(code_t, row["language"])
        t_mapped_2 = provenance_binary(t_mapped_4)

        flip_4class = b_mapped_4 != t_mapped_4
        flip_2class = b_mapped_2 != t_mapped_2

        out_rows.append({
            "sample_id": sid,
            "language": row["language"],
            "label": row["label"],
            "transformation_family": row["transformation_family"],
            "baseline_correct_4class": b_droid["baseline_correct"],
            "baseline_correct_2class": baseline_correct_2class,
            "baseline_pred_4class": b_mapped_4,
            "transformed_pred_4class": t_mapped_4,
            "flip_4class": flip_4class,
            "flip_2class": flip_2class,
            "flip_among_baseline_correct_4class": flip_4class and b_droid["baseline_correct"],
            "flip_among_baseline_correct_2class": flip_2class and baseline_correct_2class,
            "intra_ai_churn_only": flip_4class and not flip_2class,
        })
        if (n + 1) % 100 == 0:
            print(f"...{n + 1}/{len(success_rows)}", flush=True)

    with open("artifacts/prod001_droiddetect_2class_reclassified.jsonl", "w") as f:
        for r in out_rows:
            f.write(json.dumps(r, default=str) + "\n")

    groups = defaultdict(list)
    for r in out_rows:
        groups[(r["language"], r["transformation_family"])].append(r)

    print("\nLang\tFamily\tn(4cls-correct)\tIER_4class\tn(2cls-correct)\tIER_2class\tIntra-AI-churn-only flips")
    csv_rows = []
    total_churn_only = 0
    for (lang, fam), rs in sorted(groups.items()):
        base_ok_4 = [r for r in rs if r["baseline_correct_4class"]]
        induced_4 = sum(1 for r in base_ok_4 if r["flip_among_baseline_correct_4class"])
        ier_4 = (induced_4 / len(base_ok_4)) if base_ok_4 else None

        base_ok_2 = [r for r in rs if r["baseline_correct_2class"]]
        induced_2 = sum(1 for r in base_ok_2 if r["flip_among_baseline_correct_2class"])
        ier_2 = (induced_2 / len(base_ok_2)) if base_ok_2 else None

        churn_only = sum(1 for r in base_ok_4 if r["intra_ai_churn_only"])
        total_churn_only += churn_only

        lo4, hi4 = wilson_ci(induced_4, len(base_ok_4))
        lo2, hi2 = wilson_ci(induced_2, len(base_ok_2))
        print(f"{lang}\t{fam}\t{len(base_ok_4)}\t{ier_4:.3f} [{lo4:.3f},{hi4:.3f}]\t{len(base_ok_2)}\t{ier_2:.3f} [{lo2:.3f},{hi2:.3f}]\t{churn_only}")
        csv_rows.append([lang, fam, len(base_ok_4), induced_4, ier_4, lo4, hi4, len(base_ok_2), induced_2, ier_2, lo2, hi2, churn_only])

    with open("artifacts/final_tables/table5_droiddetect_2class_reclassification.csv", "w") as f:
        f.write("language,family,n_4class_correct,induced_4class,ier_4class,ci_lo_4class,ci_hi_4class,n_2class_correct,induced_2class,ier_2class,ci_lo_2class,ci_hi_2class,intra_ai_churn_only_flips\n")
        for row in csv_rows:
            f.write(",".join(str(x) for x in row) + "\n")

    print(f"\nTotal intra-AI-churn-only flips (MACHINE_GENERATED<->MACHINE_REFINED, no human-vs-AI change) among 4-class-baseline-correct programs: {total_churn_only}")
    print("Wrote artifacts/prod001_droiddetect_2class_reclassified.jsonl and artifacts/final_tables/table5_droiddetect_2class_reclassification.csv")


if __name__ == "__main__":
    main()
