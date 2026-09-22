"""PROD_004 step 2: score canon(C0) and canon(T) for the 50 non-identical
residual pairs with LLMSniffer + DroidDetect-Base. DetectCodeGPT scored
separately (isolated venv) via prod004_score_residual_detectcodegpt.py.
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
    llmsniffer_ckpt = contracts["llmsniffer"]["checkpoint"]

    llm_det = LLMSnifferDetector(llmsniffer_ckpt)
    droid_det = DroidDetectDetector(droid_ckpt, pooling=chosen_pooling)

    pairs = [json.loads(l) for l in open("artifacts/prod004_canonicalized_pairs.jsonl", encoding="utf-8")]
    residual = [p for p in pairs if not p["identical"]]

    manifest_labels = {json.loads(l)["sample_id"]: json.loads(l)["label"] for l in open("artifacts/pilot_manifest_prod001.jsonl", encoding="utf-8")}

    def score_all(code, language):
        r_llm = llm_det.score(code, language)
        r_droid = droid_det.score(code, language)
        return r_llm["raw_score"], r_droid["raw_score"]

    results = []
    for p in residual:
        sid, lang = p["sample_id"], p["language"]
        llm0_raw, droid0_full = score_all(p["canon0"], lang)
        llmt_raw, droidt_full = score_all(p["canont"], lang)
        true_idx = DROID_LABEL_NAMES.index(manifest_labels[sid])
        droid0 = droid0_full[true_idx]
        droidt = droidt_full[true_idx]
        results.append(
            {
                "sample_id": sid, "language": lang,
                "LLMSniffer_s0": llm0_raw, "LLMSniffer_sT": llmt_raw, "LLMSniffer_delta_canon": llmt_raw - llm0_raw,
                "DroidDetect-Base_s0": droid0, "DroidDetect-Base_sT": droidt, "DroidDetect-Base_delta_canon": droidt - droid0,
            }
        )

    with open("artifacts/prod004_residual_scores_llm_droid.jsonl", "w") as f:
        for r in results:
            f.write(json.dumps(r, default=str) + "\n")
    print(f"scored {len(results)} residual pairs (LLMSniffer + DroidDetect-Base)")


if __name__ == "__main__":
    main()
