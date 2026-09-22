"""PILOT_003: detector integration.

Step 1: establish detector contracts (see scripts/detectors.py docstrings).
Step 2: sanity-check each detector against KNOWN labels disjoint from our
         pilot manifest, before trusting it on C0/transformed scoring.
Step 3: C0 sanity check -- score every C0 seed, split into S_all vs
         S_baseline_correct (detector already agrees with provenance).
Step 4: score every SUCCESS transformation from PILOT_002 with the SAME
         frozen detector config, join by sample_id + family + intensity +
         detector, log truncation fields throughout.
Step 5: emit the primitive diagnostic table only (Delta score, flips) --
        no half-life / decay-curve analysis yet.
"""
import itertools
import json
import statistics
from collections import defaultdict

import torch
from datasets import load_dataset, DownloadConfig
from huggingface_hub import hf_hub_download

import sys
sys.path.insert(0, "scripts")
from detectors import LLMSnifferDetector, DroidDetectDetector

HF_CACHE = "data/hf_cache"


# ---------------------------------------------------------------------------
# Sanity check A: LLMSniffer on GPTSniffer's own Java test set (in-domain)
# ---------------------------------------------------------------------------

def sanity_check_llmsniffer(detector):
    from huggingface_hub import list_repo_files

    files = list_repo_files("mahirlabibdihan/GPTSniffer", repo_type="dataset")
    test_files = [f for f in files if f.startswith("test/")][:20]
    correct, total = 0, 0
    for fpath in test_files:
        label = int(fpath.split("/")[-1].split("_")[0])
        local = hf_hub_download("mahirlabibdihan/GPTSniffer", fpath, repo_type="dataset")
        code = open(local, encoding="utf-8", errors="replace").read()
        result = detector.score(code, "Java")
        pred = 1 if result["predicted_label"] == "AI" else 0
        correct += int(pred == label)
        total += 1
    acc = correct / total if total else 0.0
    return {"n": total, "accuracy": acc}


# ---------------------------------------------------------------------------
# Sanity check B: DroidDetect-Base pooling + label-order disambiguation on a
# Droid dev-split subset (disjoint from our pilot manifest, which is drawn
# from the train split).
# ---------------------------------------------------------------------------

def sanity_check_droiddetect(checkpoint_path, n_per_label=6):
    dl_config = DownloadConfig(cache_dir=HF_CACHE)
    dev = load_dataset("project-droid/DroidCollection", split="dev", download_config=dl_config)

    wanted_labels = ["HUMAN_GENERATED", "MACHINE_GENERATED", "MACHINE_REFINED", "MACHINE_GENERATED_ADVERSARIAL"]
    picked = []
    counts = {l: 0 for l in wanted_labels}
    for row in dev:
        lbl = row["Label"]
        if lbl in wanted_labels and counts[lbl] < n_per_label and row["Language"] in ("Python", "Java"):
            picked.append(row)
            counts[lbl] += 1
        if all(c >= n_per_label for c in counts.values()):
            break

    results = {}
    for pooling in ["cls", "mean"]:
        det = DroidDetectDetector(checkpoint_path, pooling=pooling)
        true_labels, pred_indices = [], []
        for row in picked:
            r = det.score(row["Code"], row["Language"])
            true_labels.append(row["Label"])
            pred_indices.append(det.label_names.index(r["predicted_label"]))

        best_acc, best_perm = 0.0, None
        for perm in itertools.permutations(range(4)):
            mapped = [wanted_labels[perm[i]] for i in pred_indices]
            acc = sum(int(a == b) for a, b in zip(mapped, true_labels)) / len(true_labels)
            if acc > best_acc:
                best_acc, best_perm = acc, perm

        results[pooling] = {
            "n": len(picked),
            "best_accuracy_under_best_label_permutation": best_acc,
            "inferred_label_permutation": best_perm,
            "load_report": det._load_report,
        }
    return results, picked


# ---------------------------------------------------------------------------
# Main PILOT_003 run
# ---------------------------------------------------------------------------

def provenance_binary(label):
    return "HUMAN" if label == "HUMAN_GENERATED" else "AI"


def main():
    llmsniffer_ckpt = hf_hub_download("mahirlabibdihan/LLMSniffer", "gptsniffer.pth")
    droid_ckpt = hf_hub_download("project-droid/DroidDetect-Base", "pytorch_model.bin")

    print("=== Loading LLMSniffer ===")
    llm_det = LLMSnifferDetector(llmsniffer_ckpt)
    print("=== Sanity check: LLMSniffer on GPTSniffer Java test set (in-domain) ===")
    llm_sanity = sanity_check_llmsniffer(llm_det)
    print(llm_sanity)

    print("=== Sanity check: DroidDetect-Base pooling + label-order search ===")
    droid_sanity, _ = sanity_check_droiddetect(droid_ckpt)
    print(json.dumps(droid_sanity, indent=2, default=str))

    chosen_pooling = max(droid_sanity, key=lambda p: droid_sanity[p]["best_accuracy_under_best_label_permutation"])
    chosen_acc = droid_sanity[chosen_pooling]["best_accuracy_under_best_label_permutation"]
    chosen_perm = droid_sanity[chosen_pooling]["inferred_label_permutation"]
    print(f"Chosen DroidDetect-Base config: pooling={chosen_pooling}, accuracy={chosen_acc:.2f}, label_perm={chosen_perm}")

    contract = {
        "llmsniffer": {
            "checkpoint": llmsniffer_ckpt,
            "encoder": "microsoft/graphcodebert-base",
            "training_domain_language": "Java",
            "max_length": 512,
            "calibrated": False,
            "in_domain_sanity_check": llm_sanity,
        },
        "droiddetect_base": {
            "checkpoint": droid_ckpt,
            "encoder": "answerdotai/ModernBERT-base (reconstructed, no published modeling code)",
            "max_length": 512,
            "calibrated": False,
            "pooling_sanity_check": droid_sanity,
            "chosen_pooling": chosen_pooling,
            "chosen_label_permutation": chosen_perm,
            "chosen_accuracy_on_dev_subset": chosen_acc,
        },
    }
    with open("artifacts/pilot003_detector_contracts.json", "w") as f:
        json.dump(contract, f, indent=2, default=str)

    if chosen_acc < 0.4:
        print("!!! DroidDetect-Base reconstruction does not clear a basic sanity bar "
              "(accuracy < 0.4 under best label permutation). Recording as INCOMPATIBLE, "
              "not forcing it into the panel. Skipping DroidDetect scoring for PILOT_003.")
        use_droiddetect = False
    else:
        use_droiddetect = True

    droid_label_names = ["HUMAN_GENERATED", "MACHINE_GENERATED", "MACHINE_REFINED", "MACHINE_GENERATED_ADVERSARIAL"]
    droid_perm_applied = [droid_label_names[chosen_perm[i]] for i in range(4)]  # index i (raw model idx) -> true label name
    droid_det = DroidDetectDetector(droid_ckpt, pooling=chosen_pooling) if use_droiddetect else None

    manifest = [json.loads(l) for l in open("artifacts/pilot_manifest.jsonl", encoding="utf-8")]
    transform_log = [json.loads(l) for l in open("artifacts/pilot_transform_log_v2.jsonl", encoding="utf-8")]
    success_rows = [r for r in transform_log if r["status"] == "SUCCESS"]

    def score_all(code, language):
        out = {}
        out["LLMSniffer"] = llm_det.score(code, language)
        if use_droiddetect:
            r = droid_det.score(code, language)
            raw_idx = droid_det.label_names.index(r["predicted_label"])
            r["predicted_label_mapped"] = droid_perm_applied[raw_idx]
            out["DroidDetect-Base"] = r
        return out

    baseline = {}
    for row in manifest:
        sid = row["sample_id"]
        scores = score_all(row["code"], row["language"])
        entry = {"sample_id": sid, "language": row["language"], "label": row["label"], "scores": {}}
        for det_name, r in scores.items():
            if det_name == "LLMSniffer":
                correct = (r["predicted_label"] == provenance_binary(row["label"]))
            else:
                correct = (r["predicted_label_mapped"] == row["label"])
            entry["scores"][det_name] = {**r, "baseline_correct": correct}
        baseline[sid] = entry

    with open("artifacts/pilot003_c0_baseline.jsonl", "w") as f:
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
                # track probability mass on the sample's own true-provenance class
                true_idx = droid_label_names.index(row["label"])
                model_idx_for_true = chosen_perm.index(true_idx) if true_idx in chosen_perm else None
                s0 = b_r["raw_score"][model_idx_for_true] if model_idx_for_true is not None else None
                sT = t_r["raw_score"][model_idx_for_true] if model_idx_for_true is not None else None
                flip = b_r.get("predicted_label_mapped") != t_r.get("predicted_label_mapped")
            joined_rows.append(
                {
                    "sample_id": sid,
                    "language": lang,
                    "label": row["label"],
                    "transformation_family": row["transformation_family"],
                    "intensity": row["intensity"],
                    "detector": det_name,
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

    with open("artifacts/pilot003_detector_scores.jsonl", "w") as f:
        for r in joined_rows:
            f.write(json.dumps(r, default=str) + "\n")

    # --- diagnostic table: Detector x Language x Family -> N valid, baseline-correct, mean/median delta, flips ---
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

    with open("artifacts/pilot003_diagnostic_table.csv", "w") as f:
        f.write("detector,language,family,n_valid,baseline_correct,mean_delta,median_delta,flips\n")
        for row in table_rows:
            f.write(",".join(str(x) for x in row) + "\n")


if __name__ == "__main__":
    main()
