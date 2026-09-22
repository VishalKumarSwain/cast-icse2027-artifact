"""PROD_001: score the 200-seed manifest + frozen transformations with the
frozen PILOT_003 detector contracts. Computes Induced Error Rate per
detector x language x transformation family, and reports detector-change
against the new d_text/d_token/d_ast metrics, specifically flagging the
PILOT_004 signature region (d_text>0, d_token small, d_ast~=0, |delta|>>0).
"""
import json
import statistics
from collections import defaultdict

import sys
sys.path.insert(0, "scripts")
from detectors import LLMSnifferDetector, DroidDetectDetector

DROID_LABEL_NAMES = ["HUMAN_GENERATED", "MACHINE_GENERATED", "MACHINE_REFINED", "MACHINE_GENERATED_ADVERSARIAL"]
DETECTOR_OVERLAP = {"LLMSniffer": "NO_KNOWN_OVERLAP", "DroidDetect-Base": "NO_KNOWN_OVERLAP"}


def provenance_binary(label):
    return "HUMAN" if label == "HUMAN_GENERATED" else "AI"


def main():
    with open("artifacts/pilot003_detector_contracts.json") as f:
        contracts = json.load(f)

    llmsniffer_ckpt = contracts["llmsniffer"]["checkpoint"]
    droid_ckpt = contracts["droiddetect_base"]["checkpoint"]
    chosen_pooling = contracts["droiddetect_base"]["chosen_pooling"]
    chosen_perm = tuple(contracts["droiddetect_base"]["chosen_label_permutation"])

    llm_det = LLMSnifferDetector(llmsniffer_ckpt)
    droid_det = DroidDetectDetector(droid_ckpt, pooling=chosen_pooling)
    droid_perm_applied = [DROID_LABEL_NAMES[chosen_perm[i]] for i in range(4)]

    def score_all(code, language):
        out = {"LLMSniffer": llm_det.score(code, language)}
        r = droid_det.score(code, language)
        raw_idx = droid_det.label_names.index(r["predicted_label"])
        r["predicted_label_mapped"] = droid_perm_applied[raw_idx]
        out["DroidDetect-Base"] = r
        return out

    manifest = [json.loads(l) for l in open("artifacts/pilot_manifest_prod001.jsonl", encoding="utf-8")]
    transform_log = [json.loads(l) for l in open("artifacts/prod001_transform_log.jsonl", encoding="utf-8")]
    success_rows = [r for r in transform_log if r["status"] == "SUCCESS"]

    baseline = {}
    for n, row in enumerate(manifest):
        sid = row["sample_id"]
        scores = score_all(row["code"], row["language"])
        entry = {"sample_id": sid, "language": row["language"], "label": row["label"], "scores": {}}
        for det_name, r in scores.items():
            if det_name == "LLMSniffer":
                correct = r["predicted_label"] == provenance_binary(row["label"])
            else:
                correct = r["predicted_label_mapped"] == row["label"]
            entry["scores"][det_name] = {**r, "baseline_correct": correct, "detector_training_overlap": DETECTOR_OVERLAP[det_name]}
        baseline[sid] = entry
        if (n + 1) % 50 == 0:
            print(f"...baseline {n + 1}/{len(manifest)}")

    with open("artifacts/prod001_c0_baseline.jsonl", "w") as f:
        for sid, entry in baseline.items():
            f.write(json.dumps(entry, default=str) + "\n")

    joined_rows = []
    for n, row in enumerate(success_rows):
        sid = row["sample_id"]
        lang = row["language"]
        code_t = open(row["output_path"], encoding="utf-8").read()
        t_scores = score_all(code_t, lang)
        base_entry = baseline[sid]
        for det_name, t_r in t_scores.items():
            b_r = base_entry["scores"][det_name]
            if det_name == "LLMSniffer":
                s0, sT = b_r["raw_score"], t_r["raw_score"]
                flip = b_r["predicted_label"] != t_r["predicted_label"]
            else:
                true_idx = DROID_LABEL_NAMES.index(row["label"])
                model_idx_for_true = chosen_perm.index(true_idx)
                s0 = b_r["raw_score"][model_idx_for_true]
                sT = t_r["raw_score"][model_idx_for_true]
                flip = b_r.get("predicted_label_mapped") != t_r.get("predicted_label_mapped")
            joined_rows.append(
                {
                    "sample_id": sid,
                    "language": lang,
                    "label": row["label"],
                    "transformation_family": row["transformation_family"],
                    "detector": det_name,
                    "baseline_correct": b_r["baseline_correct"],
                    "s0": s0,
                    "sT": sT,
                    "delta_score": (sT - s0) if (s0 is not None and sT is not None) else None,
                    "flip": flip,
                    "flip_among_baseline_correct": flip and b_r["baseline_correct"],
                    "d_text": row.get("d_text"),
                    "d_token": row.get("d_token"),
                    "d_ast": row.get("d_ast"),
                }
            )
        if (n + 1) % 100 == 0:
            print(f"...transformed scoring {n + 1}/{len(success_rows)}")

    with open("artifacts/prod001_detector_scores.jsonl", "w") as f:
        for r in joined_rows:
            f.write(json.dumps(r, default=str) + "\n")

    groups = defaultdict(list)
    for r in joined_rows:
        groups[(r["detector"], r["language"], r["transformation_family"])].append(r)

    # also compute N_attempted / N_applicable directly from the transform log
    attempt_counts = defaultdict(lambda: [0, 0, 0])  # attempted, applicable, valid(success)
    for r in transform_log:
        key = (r["language"], r["transformation_family"])
        attempt_counts[key][0] += 1
        if r["status"] != "NOT_APPLICABLE":
            attempt_counts[key][1] += 1
        if r["status"] == "SUCCESS":
            attempt_counts[key][2] += 1

    print("\nDetector\tLanguage\tFamily\tN_att\tN_appl\tN_valid\tN_base_ok\tMeanD\tMedianD\tFlips\tInducedErrorRate")
    table_rows = []
    for (det, lang, fam), rs in sorted(groups.items()):
        n_att, n_appl, n_valid = attempt_counts[(lang, fam)]
        deltas = [r["delta_score"] for r in rs if r["delta_score"] is not None]
        base_ok = [r for r in rs if r["baseline_correct"]]
        induced_errors = sum(1 for r in base_ok if r["flip_among_baseline_correct"])
        ier = (induced_errors / len(base_ok)) if base_ok else None
        mean_d = statistics.mean(deltas) if deltas else None
        median_d = statistics.median(deltas) if deltas else None
        flips = sum(1 for r in rs if r["flip"])
        row = [det, lang, fam, n_att, n_appl, n_valid, len(base_ok), mean_d, median_d, flips, ier]
        table_rows.append(row)
        print("\t".join(str(x) for x in row))

    with open("artifacts/prod001_diagnostic_table.csv", "w") as f:
        f.write("detector,language,family,n_attempted,n_applicable,n_valid,n_baseline_correct,mean_delta,median_delta,flips,induced_error_rate\n")
        for row in table_rows:
            f.write(",".join(str(x) for x in row) + "\n")

    # signature region: d_text>0, d_token small (<=5), d_ast==0, |delta|>=0.3
    print("\nSignature-region rows (d_text>0, d_token<=5, d_ast==0, |delta|>=0.3):")
    sig_count = 0
    for r in joined_rows:
        if (
            r["d_text"] is not None and r["d_text"] > 0
            and r["d_token"] is not None and r["d_token"] <= 5
            and r["d_ast"] == 0
            and r["delta_score"] is not None and abs(r["delta_score"]) >= 0.3
        ):
            sig_count += 1
            print(r["sample_id"], r["detector"], r["language"], r["transformation_family"], r["delta_score"], r["d_text"], r["d_token"])
    print(f"total signature-region rows: {sig_count}")


if __name__ == "__main__":
    main()
