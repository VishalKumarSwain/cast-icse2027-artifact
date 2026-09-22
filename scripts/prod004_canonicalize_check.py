"""PROD_004 step 1 (CPU-only, cheap): canonicalize all formatting-family
SUCCESS rows from PROD_001, check how many pairs become byte-identical.
Determines the actual scoring workload before spending any GPU time.
"""
import json
import sys

sys.path.insert(0, "scripts")
from canonicalize import canonicalize

manifest = {json.loads(l)["sample_id"]: json.loads(l) for l in open("artifacts/pilot_manifest_prod001.jsonl", encoding="utf-8")}
transform_log = [json.loads(l) for l in open("artifacts/prod001_transform_log.jsonl", encoding="utf-8")]
formatting_rows = [r for r in transform_log if r["status"] == "SUCCESS" and r["transformation_family"] == "formatting"]

results = []
for row in formatting_rows:
    sid = row["sample_id"]
    lang = row["language"]
    code0 = manifest[sid]["code"]
    code_t = open(row["output_path"], encoding="utf-8").read()
    canon0 = canonicalize(code0, lang)
    canont = canonicalize(code_t, lang)
    identical = (canon0 is not None and canon0 == canont)
    results.append({"sample_id": sid, "language": lang, "canon0": canon0, "canont": canont, "identical": identical})

with open("artifacts/prod004_canonicalized_pairs.jsonl", "w", encoding="utf-8") as f:
    for r in results:
        f.write(json.dumps(r, ensure_ascii=False, default=str) + "\n")

n = len(results)
n_identical = sum(1 for r in results if r["identical"])
n_py = sum(1 for r in results if r["language"] == "Python")
n_java = n - n_py
n_py_identical = sum(1 for r in results if r["language"] == "Python" and r["identical"])
n_java_identical = sum(1 for r in results if r["language"] == "Java" and r["identical"])
n_canon_failed = sum(1 for r in results if r["canon0"] is None or r["canont"] is None)

print(f"total formatting SUCCESS rows: {n} (Python={n_py}, Java={n_java})")
print(f"byte-identical after canonicalization: {n_identical}/{n} (Python={n_py_identical}/{n_py}, Java={n_java_identical}/{n_java})")
print(f"canonicalization failed (needs fresh scoring anyway, but flagged): {n_canon_failed}")
print(f"non-identical pairs needing fresh detector scoring: {n - n_identical}")
