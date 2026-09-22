"""PROD_002F: cross-detector forensics on PROD_002's frozen data. No new
transformations, detector contracts, thresholds, or distance definitions --
pure analysis of artifacts/prod002_detector_scores.jsonl plus the frozen
baseline files, per docs/PROD_002_PROTOCOL.md and the DetectCodeGPT
calibration/K-convergence docs.

Produces, per detector (never mixing raw-score scales across detectors):
  - within-detector delta-score distribution shape (median/p90/max/"spikiness")
    to distinguish Pattern A (localized: near-zero majority + rare huge
    swings) from Pattern B (diffuse: broadly moderate movement)
  - a detector-relative signature-region count (small d_text/d_token/d_ast,
    |delta| large RELATIVE TO THAT DETECTOR's own distribution, not a fixed
    absolute cutoff shared across detectors of different scales)
  - for the two detectors with a well-defined scalar decision threshold
    (LLMSniffer @ 0.5, DetectCodeGPT @ 2.931), a threshold-margin analysis
    for every flip: is s0 already close to the threshold (Pattern C,
    threshold/calibration noise) or far from it (genuine large movement)?
"""
import json
import statistics
from collections import defaultdict

THRESHOLDS = {"LLMSniffer": 0.5, "DetectCodeGPT": 2.931085010288198}
# DroidDetect-Base tracks a single true-class probability, not a full
# multiclass margin -- no scalar decision threshold is stored in the joined
# score rows, so it is excluded from the threshold-margin analysis (noted
# explicitly, not silently skipped).

rows = [json.loads(l) for l in open("artifacts/prod002_detector_scores.jsonl", encoding="utf-8")]
rows = [r for r in rows if r.get("delta_score") is not None]

by_detector = defaultdict(list)
for r in rows:
    by_detector[r["detector"]].append(r)

print("=" * 100)
print("1. WITHIN-DETECTOR delta-score distribution shape (never compared across detectors directly)")
print("=" * 100)
detector_abs_delta_p75 = {}
for det, rs in sorted(by_detector.items()):
    abs_deltas = sorted(abs(r["delta_score"]) for r in rs)
    n = len(abs_deltas)
    median = abs_deltas[n // 2]
    p75 = abs_deltas[int(n * 0.75)]
    p90 = abs_deltas[int(n * 0.90)]
    mx = abs_deltas[-1]
    spikiness = (mx / median) if median > 0 else float("inf")
    detector_abs_delta_p75[det] = p75
    pattern = "A (localized: rare huge swings)" if spikiness > 20 else "B (diffuse: no extreme outliers)"
    print(f"{det:16} n={n:4} median|d|={median:.4f} p75={p75:.4f} p90={p90:.4f} max={mx:.4f} spikiness(max/median)={spikiness:.1f} -> Pattern {pattern}")

print("\nBy detector x language x family (median|delta|, p90|delta|, n):")
groups = defaultdict(list)
for r in rows:
    groups[(r["detector"], r["language"], r["transformation_family"])].append(r)
for (det, lang, fam), rs in sorted(groups.items()):
    abs_deltas = sorted(abs(r["delta_score"]) for r in rs)
    n = len(abs_deltas)
    median = abs_deltas[n // 2]
    p90 = abs_deltas[int(n * 0.90)]
    print(f"{det:16} {lang:8} {fam:16} n={n:3} median|d|={median:.4f} p90={p90:.4f}")

print("\n" + "=" * 100)
print("2. DETECTOR-RELATIVE signature region (d_text>0, d_token<=5, d_ast==0, |delta| >= 2x that detector's own p75|delta|)")
print("=" * 100)
for det, rs in sorted(by_detector.items()):
    cutoff = 2 * detector_abs_delta_p75[det]
    sig_rows = [
        r for r in rs
        if r.get("d_text") is not None and r["d_text"] > 0
        and r.get("d_token") is not None and r["d_token"] <= 5
        and r.get("d_ast") == 0
        and abs(r["delta_score"]) >= cutoff
    ]
    print(f"{det:16} cutoff(2xP75)={cutoff:.4f}  signature-region rows: {len(sig_rows)} / {len(rs)}")
    for r in sig_rows[:10]:
        print(f"    {r['sample_id']} {r['language']} {r['transformation_family']} delta={r['delta_score']:.4f} d_text={r['d_text']} d_token={r['d_token']}")

print("\n" + "=" * 100)
print("3. THRESHOLD-MARGIN analysis for flips (LLMSniffer @0.5, DetectCodeGPT @2.931 only; DroidDetect-Base has no stored scalar margin)")
print("=" * 100)
for det, tau in THRESHOLDS.items():
    rs = [r for r in by_detector[det] if r.get("flip")]
    if not rs:
        continue
    margins = [abs(r["s0"] - tau) for r in rs]
    median_margin_all = statistics.median(abs(r["s0"] - tau) for r in by_detector[det])
    near_boundary = sum(1 for m in margins if m < median_margin_all)
    far_boundary = len(margins) - near_boundary
    print(f"\n{det} (threshold={tau}): {len(rs)} flips total")
    print(f"  median margin (all samples, for reference) = {median_margin_all:.4f}")
    print(f"  flips with s0 CLOSER to threshold than the typical sample (near-boundary, Pattern C candidate): {near_boundary}")
    print(f"  flips with s0 FARTHER from threshold than typical (genuine large movement): {far_boundary}")
    print(f"  {'sample_id':16} {'lang':8} {'family':16} {'s0':>8} {'sT':>8} {'m0':>8} {'|delta|':>8}")
    for r in sorted(rs, key=lambda x: abs(x["s0"] - tau)):
        m0 = abs(r["s0"] - tau)
        print(f"  {r['sample_id']:16} {r['language']:8} {r['transformation_family']:16} {r['s0']:8.4f} {r['sT']:8.4f} {m0:8.4f} {abs(r['delta_score']):8.4f}")
