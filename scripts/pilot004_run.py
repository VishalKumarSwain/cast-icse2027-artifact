"""PILOT_004: score the held-out C0 manifest + its PILOT_002-frozen
transformations with the PILOT_003-frozen detector contracts (no re-running
of pooling/label-permutation search -- that was already established and is
loaded from artifacts/pilot003_detector_contracts.json).

Adds explicit provenance/overlap fields to every row:
  dataset, dataset_version, dataset_split, sample_id, detector_training_overlap
using the conservative values KNOWN_OVERLAP / NO_KNOWN_OVERLAP / UNKNOWN.
"""
import json
import statistics
from collections import defaultdict

from huggingface_hub import hf_hub_download

import sys
sys.path.insert(0, "scripts")
from detectors import LLMSnifferDetector, DroidDetectDetector

DROID_LABEL_NAMES = ["HUMAN_GENERATED", "MACHINE_GENERATED", "MACHINE_REFINED", "MACHINE_GENERATED_ADVERSARIAL"]

# Conservative, evidence-based overlap calls (see PILOT_003_STATUS.md):
#  - LLMSniffer: trained on GPTSniffer/Whodunit, distinct named datasets from
#    DroidCollection -> no known overlap, though full corpora not independently verified.
#  - DroidDetect-Base: trained on DroidCollection; PILOT_004 draws C0 from Droid's
#    held-out test/dev split specifically to avoid the train-split contamination
#    found in PILOT_003 -> no known overlap for THIS split, conditional on Droid's
#    own train/test separation being honored during DroidDetect-Base's training
#    (not independently verified -- hence NO_KNOWN_OVERLAP, not NO_OVERLAP).
DETECTOR_OVERLAP = {
    "LLMSniffer": "NO_KNOWN_OVERLAP",
    "DroidDetect-Base": "NO_KNOWN_OVERLAP",
}


def provenance_binary(label):
    return "HUMAN" if label == "HUMAN_GENERATED" else "AI"


def main():
    with open("artifacts/pilot003_detector_contracts.json") as f:
        contracts = json.load(f)

    llmsniffer_ckpt = contracts["llmsniffer"]["checkpoint"]
    droid_ckpt = contracts["droiddetect_base"]["checkpoint"]
    chosen_pooling = contracts["droiddetect_base"]["chosen_pooling"]
    chosen_perm = tuple(contracts["droiddetect_base"]["chosen_label_permutation"])

    print(f"Reusing frozen contracts: LLMSniffer ckpt={llmsniffer_ckpt}")
    print(f"Reusing frozen contracts: DroidDetect-Base ckpt={droid_ckpt} pooling={chosen_pooling} perm={chosen_perm}")

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

    manifest = [json.loads(l) for l in open("artifacts/pilot_manifest_v2.jsonl", encoding="utf-8")]
    transform_log = [json.loads(l) for l in open("artifacts/pilot_transform_log_v3.jsonl", encoding="utf-8")]
    success_rows = [r for r in transform_log if r["status"] == "SUCCESS"]

    baseline = {}
    for row in manifest:
        sid = row["sample_id"]
        scores = score_all(row["code"], row["language"])
        entry = {
            "sample_id": sid,
            "dataset": row["dataset"],
            "dataset_version": row["dataset_version"],
            "dataset_split": row["dataset_split"],
            "language": row["language"],
            "label": row["label"],
            "scores": {},
        }
        for det_name, r in scores.items():
            if det_name == "LLMSniffer":
                correct = r["predicted_label"] == provenance_binary(row["label"])
            else:
                correct = r["predicted_label_mapped"] == row["label"]
            entry["scores"][det_name] = {**r, "baseline_correct": correct, "detector_training_overlap": DETECTOR_OVERLAP[det_name]}
        baseline[sid] = entry

    with open("artifacts/pilot004_c0_baseline.jsonl", "w") as f:
        for sid, entry in baseline.items():
            f.write(json.dumps(entry, default=str) + "\n")

    joined_rows = []
    for row in success_rows:
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
                    "dataset": row["dataset"],
                    "dataset_split": row["dataset_split"],
                    "language": lang,
                    "label": row["label"],
                    "transformation_family": row["transformation_family"],
                    "intensity": row["intensity"],
                    "detector": det_name,
                    "detector_training_overlap": DETECTOR_OVERLAP[det_name],
                    "baseline_correct": b_r["baseline_correct"],
                    "s0": s0,
                    "sT": sT,
                    "delta_score": (sT - s0) if (s0 is not None and sT is not None) else None,
                    "flip": flip,
                    "c0_truncated": b_r["truncated"],
                    "t_truncated": t_r["truncated"],
                    "c0_input_tokens": b_r["input_tokens"],
                    "t_input_tokens": t_r["input_tokens"],
                }
            )

    with open("artifacts/pilot004_detector_scores.jsonl", "w") as f:
        for r in joined_rows:
            f.write(json.dumps(r, default=str) + "\n")

    groups = defaultdict(list)
    for r in joined_rows:
        groups[(r["detector"], r["language"], r["transformation_family"])].append(r)

    print("\nDetector\tLanguage\tFamily\tN_valid\tBaseline_correct\tMeanDelta\tMedianDelta\tFlips")
    table_rows = []
    for (det, lang, fam), rs in sorted(groups.items()):
        deltas = [r["delta_score"] for r in rs if r["delta_score"] is not None]
        n_valid = len(rs)
        baseline_correct = sum(1 for r in rs if r["baseline_correct"])
        flips = sum(1 for r in rs if r["flip"])
        mean_d = statistics.mean(deltas) if deltas else None
        median_d = statistics.median(deltas) if deltas else None
        row = [det, lang, fam, n_valid, baseline_correct, mean_d, median_d, flips]
        table_rows.append(row)
        print("\t".join(str(x) for x in row))

    with open("artifacts/pilot004_diagnostic_table.csv", "w") as f:
        f.write("detector,language,family,n_valid,baseline_correct,mean_delta,median_delta,flips\n")
        for row in table_rows:
            f.write(",".join(str(x) for x in row) + "\n")


if __name__ == "__main__":
    main()
