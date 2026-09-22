"""Re-verify distance metrics on PILOT_004's existing transformed artifacts,
WITHOUT re-running transformations or detectors. Reads the frozen
artifacts/pilot_transform_log_v3.jsonl + artifacts/pilot_manifest_v2.jsonl,
adds d_text and d_token (language-aware) alongside the existing
ast_node_count_delta, writes a new augmented file. The original log is left
untouched.
"""
import json
import sys

sys.path.insert(0, "scripts")
from distances import d_text, d_token

manifest = {json.loads(l)["sample_id"]: json.loads(l) for l in open("artifacts/pilot_manifest_v2.jsonl", encoding="utf-8")}
transform_log = [json.loads(l) for l in open("artifacts/pilot_transform_log_v3.jsonl", encoding="utf-8")]

out_rows = []
for row in transform_log:
    row = dict(row)
    if row["status"] != "SUCCESS":
        row["d_text"] = None
        row["d_token_v2"] = None
        out_rows.append(row)
        continue

    sid = row["sample_id"]
    lang = row["language"]
    code0 = manifest[sid]["code"]
    code_t = open(row["output_path"], encoding="utf-8").read()

    row["d_text"] = d_text(code0, code_t)
    row["d_token_v2"] = d_token(code0, code_t, lang)
    row["old_whitespace_token_distance"] = row.get("token_distance")
    out_rows.append(row)

with open("artifacts/pilot_transform_log_v3_distances.jsonl", "w", encoding="utf-8") as f:
    for row in out_rows:
        f.write(json.dumps(row, ensure_ascii=False, default=str) + "\n")

# Focused re-check on the forensic set: DroidDetect-Base x Python x formatting
print("Python formatting rows: old_whitespace_token_distance vs new d_text / d_token_v2 / ast_node_count_delta")
for row in out_rows:
    if row["language"] == "Python" and row["transformation_family"] == "formatting" and row["status"] == "SUCCESS":
        print(
            f"{row['sample_id']:24} old_tok={row['old_whitespace_token_distance']:>4}  "
            f"d_text={row['d_text']:>4}  d_token_v2={row['d_token_v2']:>4}  "
            f"ast_delta={row['ast_node_count_delta']}"
        )
