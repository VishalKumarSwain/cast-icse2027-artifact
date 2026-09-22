"""PROD_004 step 3: compare |delta_canon| (canonicalized formatting pairs)
against the already-frozen PROD_002 |delta_score| (raw formatting pairs) for
the same sample_ids, per detector. The 108 byte-identical pairs contribute
delta_canon=0 by construction; the 50 residual pairs get their measured
delta_canon from the fresh scoring.
"""
import json
import statistics
from collections import defaultdict

pairs = [json.loads(l) for l in open("artifacts/prod004_canonicalized_pairs.jsonl", encoding="utf-8")]
identical_ids = {p["sample_id"] for p in pairs if p["identical"]}
residual_ids = {p["sample_id"] for p in pairs if not p["identical"]}
lang_of = {p["sample_id"]: p["language"] for p in pairs}

llm_droid_residual = {r["sample_id"]: r for r in (json.loads(l) for l in open("artifacts/prod004_residual_scores_llm_droid.jsonl", encoding="utf-8"))}
dcg_residual = {r["sample_id"]: r for r in (json.loads(l) for l in open("artifacts/prod004_residual_scores_detectcodegpt.jsonl", encoding="utf-8"))}

# original PROD_002 formatting deltas for the same 158 sample_ids
orig_scores = [json.loads(l) for l in open("artifacts/prod002_detector_scores.jsonl", encoding="utf-8")]
orig_formatting = defaultdict(dict)  # sample_id -> detector -> delta_score
for r in orig_scores:
    if r["transformation_family"] == "formatting" and r["sample_id"] in identical_ids | residual_ids:
        orig_formatting[r["sample_id"]][r["detector"]] = r["delta_score"]

DETECTORS = ["LLMSniffer", "DroidDetect-Base", "DetectCodeGPT"]

delta_canon_by_detector_lang = defaultdict(list)
delta_orig_by_detector_lang = defaultdict(list)

for sid in identical_ids | residual_ids:
    lang = lang_of[sid]
    for det in DETECTORS:
        if sid in identical_ids:
            delta_canon = 0.0
        else:
            if det == "DetectCodeGPT":
                delta_canon = dcg_residual.get(sid, {}).get("DetectCodeGPT_delta_canon")
            else:
                delta_canon = llm_droid_residual.get(sid, {}).get(f"{det}_delta_canon")
        delta_orig = orig_formatting.get(sid, {}).get(det)
        if delta_canon is not None:
            delta_canon_by_detector_lang[(det, lang)].append(abs(delta_canon))
        if delta_orig is not None:
            delta_orig_by_detector_lang[(det, lang)].append(abs(delta_orig))

print("=== ALL 158 pairs (108 trivially identical -> delta_canon=0, 50 residual -> measured) ===")
print(f"{'Detector':16} {'Lang':8} {'N':>4} {'mean|delta_ORIG|':>18} {'mean|delta_CANON|':>18} {'ReductionFactor':>16}")
summary_rows = []
for det in DETECTORS:
    for lang in ["Python", "Java"]:
        key = (det, lang)
        orig_vals = delta_orig_by_detector_lang[key]
        canon_vals = delta_canon_by_detector_lang[key]
        if not orig_vals or not canon_vals:
            continue
        mean_orig = statistics.mean(orig_vals)
        mean_canon = statistics.mean(canon_vals)
        reduction = (mean_orig / mean_canon) if mean_canon > 0 else float("inf")
        n = len(canon_vals)
        print(f"{det:16} {lang:8} {n:>4} {mean_orig:>18.4f} {mean_canon:>18.4f} {reduction:>16.1f}")
        summary_rows.append(["ALL_158", det, lang, n, mean_orig, mean_canon, reduction])

print("\n=== RESIDUAL-ONLY (50 pairs where canonicalization did NOT fully collapse them): same-subset comparison ===")
print(f"{'Detector':16} {'Lang':8} {'N':>4} {'mean|delta_ORIG|':>18} {'mean|delta_CANON|':>18} {'ReductionFactor':>16}")
for det in DETECTORS:
    for lang in ["Python", "Java"]:
        residual_lang_ids = [sid for sid in residual_ids if lang_of[sid] == lang]
        orig_vals = [abs(orig_formatting[sid][det]) for sid in residual_lang_ids if det in orig_formatting.get(sid, {})]
        if det == "DetectCodeGPT":
            canon_vals = [abs(dcg_residual[sid]["DetectCodeGPT_delta_canon"]) for sid in residual_lang_ids if sid in dcg_residual and dcg_residual[sid]["DetectCodeGPT_delta_canon"] is not None]
        else:
            canon_vals = [abs(llm_droid_residual[sid][f"{det}_delta_canon"]) for sid in residual_lang_ids if sid in llm_droid_residual]
        if not orig_vals or not canon_vals:
            continue
        mean_orig = statistics.mean(orig_vals)
        mean_canon = statistics.mean(canon_vals)
        reduction = (mean_orig / mean_canon) if mean_canon > 0 else float("inf")
        n = len(canon_vals)
        print(f"{det:16} {lang:8} {n:>4} {mean_orig:>18.4f} {mean_canon:>18.4f} {reduction:>16.1f}")
        summary_rows.append(["RESIDUAL_50", det, lang, n, mean_orig, mean_canon, reduction])

with open("artifacts/prod004_summary.csv", "w") as f:
    f.write("subset,detector,language,n,mean_abs_delta_original,mean_abs_delta_canonicalized,reduction_factor\n")
    for row in summary_rows:
        f.write(",".join(str(x) for x in row) + "\n")

print(f"\nByte-identical-after-canonicalization pairs: {len(identical_ids)}/158 (delta_canon=0 by construction)")
print(f"Residual (non-identical) pairs freshly scored: {len(residual_ids)}/158")
