"""Exploratory (labeled as such, not a new method): what do the samples that
show up in BOTH DroidDetect-Base's and LLMSniffer's signature-region lists
(from PROD_002F) actually have in common? Just inspection, no new metric.
"""
import json

overlap_ids = [
    "c0_test_42acb918f0f9",
    "c0_test_b4c24e630f64",
    "c0_test_b4eda3245609",
    "c0_test_47d1cf7a81ff",
    "c0_test_7f5026014142",
]

manifest = {json.loads(l)["sample_id"]: json.loads(l) for l in open("artifacts/pilot_manifest_prod001.jsonl", encoding="utf-8")}
transform_log = {(json.loads(l)["sample_id"], json.loads(l)["transformation_family"]): json.loads(l) for l in open("artifacts/prod001_transform_log.jsonl", encoding="utf-8")}

for sid in overlap_ids:
    row = manifest.get(sid)
    tr = transform_log.get((sid, "formatting"))
    if not row or not tr or tr["status"] != "SUCCESS":
        print(sid, "MISSING/NOT-SUCCESS")
        continue
    c0 = row["code"]
    ct = open(tr["output_path"], encoding="utf-8").read()
    print(f"\n===== {sid} ({row['language']}, {row['label']}, len={len(c0)}) =====")
    print(f"d_text={tr.get('d_text')} d_token={tr.get('d_token')} d_ast={tr.get('d_ast')}")
    # quick heuristic diffs
    print("quote_change:", c0.count("'") != ct.count("'") or c0.count('"') != ct.count('"'))
    print("blank_line_change:", c0.count("\n\n") != ct.count("\n\n"))
    print("indentation_sample (first indented line c0 vs t):")
    c0_lines = [l for l in c0.split("\n") if l.startswith((" ", "\t"))][:1]
    ct_lines = [l for l in ct.split("\n") if l.startswith((" ", "\t"))][:1]
    print("  c0:", repr(c0_lines[0][:20]) if c0_lines else None)
    print("  ct:", repr(ct_lines[0][:20]) if ct_lines else None)
