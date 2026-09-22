"""PILOT_004: apply the FROZEN PILOT_002 transformation/validation logic to
the new held-out C0 manifest. No changes to transformation or validation
functions -- only I/O paths differ, per the instruction to reuse the
frozen PILOT_002 implementations exactly.
"""
import json
import os
import sys

sys.path.insert(0, "scripts")
from transform_pilot_v2 import (  # noqa: E402  (frozen, imported not modified)
    TRANSFORMS,
    AST_COUNTERS,
    validate_python,
    validate_java,
    JAVA_WRAPPER_TEMPLATE_VERSION,
)

MANIFEST_PATH = "artifacts/pilot_manifest_v2.jsonl"
OUT_DIR = "artifacts/transformed_v3"
WRAPPER_DIR = "artifacts/java_wrappers_v3"
LOG_PATH = "artifacts/pilot_transform_log_v3.jsonl"


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(WRAPPER_DIR, exist_ok=True)
    rows = [json.loads(l) for l in open(MANIFEST_PATH, encoding="utf-8")]

    logs = []
    for row in rows:
        lang = row["language"]
        sid = row["sample_id"]
        code0 = row["code"]
        source = row["source"]

        if lang == "Python":
            c0_valid, c0_err = validate_python(code0)
            c0_meta = {"c0_valid": c0_valid, "c0_valid_error": c0_err}
        else:
            jv = validate_java(code0, sid, source)
            wrapper_path = None
            if jv["wrapper_used"] and jv["wrapper_code"]:
                wrapper_path = f"{WRAPPER_DIR}/{sid}__c0_wrapper.java"
                with open(wrapper_path, "w", encoding="utf-8") as f:
                    f.write(jv["wrapper_code"])
            c0_meta = {k: v for k, v in jv.items() if k != "wrapper_code"}
            c0_meta["wrapper_path"] = wrapper_path

        base_ast = AST_COUNTERS[lang](code0)

        for family, fn in TRANSFORMS[lang].items():
            log = {
                "sample_id": sid,
                "dataset": row["dataset"],
                "dataset_split": row["dataset_split"],
                "language": lang,
                "label": row["label"],
                "model_family": row["model_family"],
                "source": source,
                "transformation_family": family,
                "intensity": "low",
                **c0_meta,
            }
            try:
                new_code, err = fn(code0)
            except Exception as e:
                new_code, err = None, f"TRANSFORM_ERROR: {e}"

            if new_code is None:
                status = "NOT_APPLICABLE" if (err or "").startswith("NOT_APPLICABLE") else "TRANSFORM_ERROR"
                log.update({"status": status, "error": err})
                logs.append(log)
                continue

            if lang == "Python":
                t_valid, t_err = validate_python(new_code)
                status = "SUCCESS" if t_valid else "VALIDATION_FAILED"
                log["transform_valid"] = t_valid
                log["transform_valid_error"] = t_err
            else:
                tjv = validate_java(new_code, sid + "_t", source)
                tier_order = {"PARSE_INVALID": 0, "STRUCTURAL_ONLY": 1, "WRAPPER_VALID": 2, "STANDALONE_VALID": 3}
                c0_tier = tier_order.get(c0_meta.get("validation_status"), 0)
                t_tier = tier_order.get(tjv["validation_status"], 0)
                status = "SUCCESS" if t_tier >= c0_tier and t_tier >= 1 else "VALIDATION_FAILED"
                t_wrapper_path = None
                if tjv["wrapper_used"] and tjv["wrapper_code"]:
                    t_wrapper_path = f"{WRAPPER_DIR}/{sid}__{family}_wrapper.java"
                    with open(t_wrapper_path, "w", encoding="utf-8") as f:
                        f.write(tjv["wrapper_code"])
                log["transform_parse_valid"] = tjv["c0_parse_valid"]
                log["transform_native_compile_valid"] = tjv["c0_native_compile_valid"]
                log["transform_wrapper_used"] = tjv["wrapper_used"]
                log["transform_wrapped_compile_valid"] = tjv["c0_wrapped_compile_valid"]
                log["transform_wrapper_path"] = t_wrapper_path
                log["transform_validation_status"] = tjv["validation_status"]

            out_ext = "py" if lang == "Python" else "java"
            out_path = f"{OUT_DIR}/{sid}__{family}.{out_ext}"
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(new_code)

            new_ast = AST_COUNTERS[lang](new_code) if status == "SUCCESS" else None
            import difflib

            def token_distance(a, b):
                ta, tb = a.split(), b.split()
                sm = difflib.SequenceMatcher(a=ta, b=tb, autojunk=False)
                matches = sum(bl.size for bl in sm.get_matching_blocks())
                return max(len(ta), len(tb)) - matches

            def char_edit_distance(a, b):
                sm = difflib.SequenceMatcher(a=a, b=b, autojunk=False)
                matches = sum(bl.size for bl in sm.get_matching_blocks())
                return max(len(a), len(b)) - matches

            log.update(
                {
                    "status": status,
                    "output_path": out_path,
                    "token_distance": token_distance(code0, new_code),
                    "char_edit_distance": char_edit_distance(code0, new_code),
                    "ast_node_count_c0": base_ast,
                    "ast_node_count_transformed": new_ast,
                    "ast_node_count_delta": (new_ast - base_ast) if (base_ast is not None and new_ast is not None) else None,
                }
            )
            logs.append(log)

    with open(LOG_PATH, "w", encoding="utf-8") as f:
        for log in logs:
            f.write(json.dumps(log, ensure_ascii=False) + "\n")

    from collections import Counter

    attempted = len(logs)
    applicable = sum(1 for l in logs if l["status"] != "NOT_APPLICABLE")
    success = sum(1 for l in logs if l["status"] == "SUCCESS")
    print(f"attempted={attempted} applicable={applicable} success={success}")
    print(f"ApplicabilityRate={applicable/attempted:.2f} TransformationSuccessRate={(success/applicable if applicable else 0):.2f}")
    print(Counter((l["language"], l["transformation_family"], l["status"]) for l in logs))


if __name__ == "__main__":
    main()
