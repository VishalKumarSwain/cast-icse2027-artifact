"""Forensic drill-down on the DroidDetect-Base x Python x formatting cell
from PILOT_004: sample-level table, truncation check, baseline-correct-only
flip count, and before/after source dump for the largest negative deltas.
"""
import json

scores = [json.loads(l) for l in open("artifacts/pilot004_detector_scores.jsonl", encoding="utf-8")]
transform_log = [json.loads(l) for l in open("artifacts/pilot_transform_log_v3.jsonl", encoding="utf-8")]
manifest = {json.loads(l)["sample_id"]: json.loads(l) for l in open("artifacts/pilot_manifest_v2.jsonl", encoding="utf-8")}

t_index = {(r["sample_id"], r["transformation_family"]): r for r in transform_log}

cell = [
    r for r in scores
    if r["detector"] == "DroidDetect-Base" and r["language"] == "Python" and r["transformation_family"] == "formatting"
]
cell.sort(key=lambda r: r["delta_score"])

print(f"n={len(cell)}")
print(f"{'sample_id':16}{'label':18}{'s0':>8}{'sT':>8}{'delta':>9}{'flip':>6}{'base_ok':>8}{'tok_c0':>7}{'tok_t':>7}{'trunc_c0':>9}{'trunc_t':>9}{'tokdist':>8}{'astdelta':>9}")
for r in cell:
    tr = t_index[(r["sample_id"], "formatting")]
    print(
        f"{r['sample_id']:16}{r['label']:18}{r['s0']:8.4f}{r['sT']:8.4f}{r['delta_score']:9.4f}"
        f"{str(r['flip']):>6}{str(r['baseline_correct']):>8}{r['c0_input_tokens']:7}{r['t_input_tokens']:7}"
        f"{str(r['c0_truncated']):>9}{str(r['t_truncated']):>9}{tr['token_distance']:8}{str(tr['ast_node_count_delta']):>9}"
    )

# baseline-correct-only flip analysis
baseline_correct_rows = [r for r in cell if r["baseline_correct"]]
flips_among_correct = [r for r in baseline_correct_rows if r["flip"]]
print(f"\nOf {len(baseline_correct_rows)} baseline-correct samples, {len(flips_among_correct)} flipped after formatting.")
print("Those sample_ids:", [r["sample_id"] for r in flips_among_correct])

# dump before/after source for the 5 most negative deltas
print("\n" + "=" * 80)
print("BEFORE/AFTER SOURCE for 5 most negative-delta samples")
print("=" * 80)
for r in cell[:5]:
    sid = r["sample_id"]
    tr = t_index[(sid, "formatting")]
    c0 = manifest[sid]["code"]
    ct = open(tr["output_path"], encoding="utf-8").read()
    print(f"\n----- {sid}  delta={r['delta_score']:.4f}  flip={r['flip']}  baseline_correct={r['baseline_correct']} -----")
    print(f"label={r['label']}  tokens_c0={r['c0_input_tokens']} tokens_t={r['t_input_tokens']} "
          f"truncated_c0={r['c0_truncated']} truncated_t={r['t_truncated']} token_distance={tr['token_distance']}")
    print("--- C0 (first 500 chars) ---")
    print(c0[:500])
    print("--- T(C0) (first 500 chars) ---")
    print(ct[:500])
