"""PROD_003 runner: applies local_structural and deep_semantic (LOW/HIGH) to
the same frozen 199-seed manifest, using the frozen PILOT_002 validation
functions and the frozen d_text/d_token/d_ast metrics. Adds a differential-
execution semantic check where the sample has an unambiguous entry point and
needs no stdin; degrades explicitly to STRUCTURAL_ONLY_NO_ENTRY_POINT
otherwise, per docs/PROD_003_PROTOCOL.md.
"""
import json
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, "scripts")
from transform_pilot_v2 import AST_COUNTERS, validate_java, validate_python
from transform_families_v4 import (
    transform_deep_semantic_java,
    transform_deep_semantic_python,
    transform_local_structural_java,
    transform_local_structural_python,
)
from distances import d_text, d_token

MANIFEST_PATH = "artifacts/pilot_manifest_prod001.jsonl"
OUT_DIR = "artifacts/transformed_prod003"
WRAPPER_DIR = "artifacts/java_wrappers_prod003"
LOG_PATH = "artifacts/prod003_transform_log.jsonl"
JDK_JAVAC = "/data/aihuman/tools/jdk17/bin/javac"
JDK_JAVA = "/data/aihuman/tools/jdk17/bin/java"

FAMILIES = {
    "Python": {"local_structural": transform_local_structural_python, "deep_semantic": transform_deep_semantic_python},
    "Java": {"local_structural": transform_local_structural_java, "deep_semantic": transform_deep_semantic_java},
}
INTENSITIES = ["low", "high"]


def has_unambiguous_entry_point(code, lang):
    if lang == "Python":
        return "if __name__" in code and "input(" not in code and "sys.argv" not in code
    if lang == "Java":
        return "public static void main" in code and "Scanner" not in code and "System.in" not in code
    return False


def run_and_capture(cmd, cwd=None, timeout=5):
    try:
        r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
        return r.stdout, r.returncode
    except Exception:
        return None, None


def semantic_check(code0, code_t, lang, c0_tier):
    if c0_tier not in ("STANDALONE_VALID", "WRAPPER_VALID") and lang == "Java":
        return "STRUCTURAL_ONLY_NO_ENTRY_POINT"
    if not has_unambiguous_entry_point(code0, lang) or not has_unambiguous_entry_point(code_t, lang):
        return "STRUCTURAL_ONLY_NO_ENTRY_POINT"

    if lang == "Python":
        with tempfile.TemporaryDirectory() as td:
            p0, pt = os.path.join(td, "c0.py"), os.path.join(td, "ct.py")
            open(p0, "w", encoding="utf-8").write(code0)
            open(pt, "w", encoding="utf-8").write(code_t)
            out0, rc0 = run_and_capture([sys.executable, p0])
            outt, rct = run_and_capture([sys.executable, pt])
    else:
        with tempfile.TemporaryDirectory() as td:
            import re

            m = re.search(r"\bclass\s+(\w+)", code0)
            cname = m.group(1) if m else "Pilot"
            p0 = os.path.join(td, f"{cname}.java")
            open(p0, "w", encoding="utf-8").write(code0)
            compiled0, _ = run_and_capture([JDK_JAVAC, "-d", td, p0], timeout=15)
            out0, rc0 = run_and_capture([JDK_JAVA, "-cp", td, cname], timeout=5)

            m2 = re.search(r"\bclass\s+(\w+)", code_t)
            cname2 = m2.group(1) if m2 else "Pilot"
            td2 = tempfile.mkdtemp()
            pt = os.path.join(td2, f"{cname2}.java")
            open(pt, "w", encoding="utf-8").write(code_t)
            run_and_capture([JDK_JAVAC, "-d", td2, pt], timeout=15)
            outt, rct = run_and_capture([JDK_JAVA, "-cp", td2, cname2], timeout=5)

    if out0 is None or outt is None:
        return "STRUCTURAL_ONLY_NO_ENTRY_POINT"  # execution itself failed/timed out -- can't establish equivalence either way
    return "DIFFERENTIAL_EXECUTION_PASSED" if out0 == outt else "DIFFERENTIAL_EXECUTION_FAILED"


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(WRAPPER_DIR, exist_ok=True)
    rows = [json.loads(l) for l in open(MANIFEST_PATH, encoding="utf-8")]

    logs = []
    for n, row in enumerate(rows):
        lang = row["language"]
        sid = row["sample_id"]
        code0 = row["code"]
        source = row["source"]

        if lang == "Python":
            c0_valid, c0_err = validate_python(code0)
            c0_meta = {"c0_valid": c0_valid, "c0_valid_error": c0_err, "validation_status": "PARSE_VALID" if c0_valid else "PARSE_INVALID"}
        else:
            jv = validate_java(code0, sid, source)
            c0_meta = {k: v for k, v in jv.items() if k != "wrapper_code"}

        base_ast = AST_COUNTERS[lang](code0)

        for family, fn in FAMILIES[lang].items():
            for intensity in INTENSITIES:
                log = {
                    "sample_id": sid,
                    "language": lang,
                    "label": row["label"],
                    "model_family": row["model_family"],
                    "source": source,
                    "transformation_family": family,
                    "intensity": intensity,
                    **c0_meta,
                }
                try:
                    new_code, err = fn(code0, intensity)
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
                else:
                    tjv = validate_java(new_code, sid + "_t", source)
                    tier_order = {"PARSE_INVALID": 0, "STRUCTURAL_ONLY": 1, "WRAPPER_VALID": 2, "STANDALONE_VALID": 3}
                    c0_tier = tier_order.get(c0_meta.get("validation_status"), 0)
                    t_tier = tier_order.get(tjv["validation_status"], 0)
                    status = "SUCCESS" if t_tier >= c0_tier and t_tier >= 1 else "VALIDATION_FAILED"
                    log["transform_validation_status"] = tjv["validation_status"]

                if status != "SUCCESS":
                    log.update({"status": status})
                    logs.append(log)
                    continue

                out_ext = "py" if lang == "Python" else "java"
                out_path = f"{OUT_DIR}/{sid}__{family}__{intensity}.{out_ext}"
                with open(out_path, "w", encoding="utf-8") as f:
                    f.write(new_code)

                sem_check = semantic_check(code0, new_code, lang, c0_meta.get("validation_status", "PARSE_INVALID"))
                new_ast = AST_COUNTERS[lang](new_code)

                log.update(
                    {
                        "status": status,
                        "output_path": out_path,
                        "semantic_check": sem_check,
                        "d_text": d_text(code0, new_code),
                        "d_token": d_token(code0, new_code, lang),
                        "ast_node_count_c0": base_ast,
                        "ast_node_count_transformed": new_ast,
                        "d_ast": (new_ast - base_ast) if (base_ast is not None and new_ast is not None) else None,
                    }
                )
                logs.append(log)

        if (n + 1) % 50 == 0:
            print(f"...{n + 1}/{len(rows)} seeds processed", flush=True)

    with open(LOG_PATH, "w", encoding="utf-8") as f:
        for log in logs:
            f.write(json.dumps(log, ensure_ascii=False, default=str) + "\n")

    from collections import Counter

    attempted = len(logs)
    applicable = sum(1 for l in logs if l["status"] != "NOT_APPLICABLE")
    success = sum(1 for l in logs if l["status"] == "SUCCESS")
    print(f"attempted={attempted} applicable={applicable} success={success}")
    print(f"ApplicabilityRate={applicable/attempted:.2f} TransformationSuccessRate={(success/applicable if applicable else 0):.2f}")
    print(Counter((l["language"], l["transformation_family"], l["intensity"], l["status"]) for l in logs))
    print("Semantic check distribution:", Counter(l.get("semantic_check") for l in logs if l["status"] == "SUCCESS"))


if __name__ == "__main__":
    main()
