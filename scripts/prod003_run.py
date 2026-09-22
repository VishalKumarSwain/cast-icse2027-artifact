"""PROD_003: score LLMSniffer + DroidDetect-Base on the 35 SUCCESS rows from
transform_prod003.py. Reuses the frozen C0 baseline scores already computed
in PROD_001/PROD_002 (same 199 seeds, same detector contracts) rather than
rescoring C0 -- only the new transformed artifacts need fresh scores.
"""
import json

import sys
sys.path.insert(0, "scripts")
from detectors import LLMSnifferDetector, DroidDetectDetector

DROID_LABEL_NAMES = ["HUMAN_GENERATED", "MACHINE_GENERATED", "MACHINE_REFINED", "MACHINE_GENERATED_ADVERSARIAL"]


def main():
    with open("artifacts/pilot003_detector_contracts.json") as f:
        contracts = json.load(f)
    droid_ckpt = contracts["droiddetect_base"]["checkpoint"]
    chosen_pooling = contracts["droiddetect_base"]["chosen_pooling"]
    chosen_perm = tuple(contracts["droiddetect_base"]["chosen_label_permutation"])
    llmsniffer_ckpt = contracts["llmsniffer"]["checkpoint"]

    llm_det = LLMSnifferDetector(llmsniffer_ckpt)
    droid_det = DroidDetectDetector(droid_ckpt, pooling=chosen_pooling)
    droid_perm_applied = [DROID_LABEL_NAMES[chosen_perm[i]] for i in range(4)]

    baseline = {json.loads(l)["sample_id"]: json.loads(l) for l in open("artifacts/prod001_c0_baseline.jsonl", encoding="utf-8")}
    transform_log = [json.loads(l) for l in open("artifacts/prod003_transform_log.jsonl", encoding="utf-8")]
    success_rows = [r for r in transform_log if r["status"] == "SUCCESS"]

    def score_all(code, language):
        out = {"LLMSniffer": llm_det.score(code, language)}
        r = droid_det.score(code, language)
        raw_idx = droid_det.label_names.index(r["predicted_label"])
        r["predicted_label_mapped"] = droid_perm_applied[raw_idx]
        out["DroidDetect-Base"] = r
        return out

    results = []
    for row in success_rows:
        sid = row["sample_id"]
        code_t = open(row["output_path"], encoding="utf-8").read()
        t_scores = score_all(code_t, row["language"])
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
            results.append(
                {
                    "sample_id": sid,
                    "language": row["language"],
                    "label": row["label"],
                    "transformation_family": row["transformation_family"],
                    "intensity": row["intensity"],
                    "detector": det_name,
                    "baseline_correct": b_r["baseline_correct"],
                    "s0": s0,
                    "sT": sT,
                    "delta_score": (sT - s0) if (s0 is not None and sT is not None) else None,
                    "flip": flip,
                    "d_text": row.get("d_text"),
                    "d_token": row.get("d_token"),
                    "d_ast": row.get("d_ast"),
                    "semantic_check": row.get("semantic_check"),
                }
            )

    with open("artifacts/prod003_llmsniffer_droiddetect_scores.jsonl", "w") as f:
        for r in results:
            f.write(json.dumps(r, default=str) + "\n")
    print(f"scored {len(results)} rows ({len(success_rows)} transformed samples x 2 detectors)")


if __name__ == "__main__":
    main()
