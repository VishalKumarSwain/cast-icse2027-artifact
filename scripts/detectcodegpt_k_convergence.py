"""DetectCodeGPT K-convergence study, per docs/DETECTCODEGPT_PROTOCOL.md.
25 held-out samples, disjoint from PILOT_004 (30) and PROD_001 (199),
K in {5,10,20,50}, nested perturbation design, predeclared acceptance rule.
"""
import hashlib
import json
import random
import time

from datasets import load_dataset, DownloadConfig
from scipy.stats import spearmanr

import sys
sys.path.insert(0, "scripts")
from detectcodegpt import DetectCodeGPTDetector

SEED = 20260922
N = 25
K_VALUES = [5, 10, 20, 50]


def build_convergence_sample():
    used_ids = set()
    for path in ["artifacts/pilot_manifest_v2.jsonl", "artifacts/pilot_manifest_prod001.jsonl"]:
        used_ids |= {json.loads(l)["sample_id"] for l in open(path, encoding="utf-8")}

    rng = random.Random(SEED)
    dl_config = DownloadConfig(cache_dir="data/hf_cache")
    ds = load_dataset("project-droid/DroidCollection", split="test", download_config=dl_config)
    ds = ds.filter(lambda r: r["Language"] in ("Python", "Java"), num_proc=4)

    idxs = list(range(len(ds)))
    rng.shuffle(idxs)

    picked = []
    for i in idxs:
        row = ds[i]
        h = hashlib.sha256(f"test|{row['Source']}|{row['Language']}|{row['Label']}|{i}|{row['Code'][:200]}".encode()).hexdigest()[:12]
        sid = f"c0_test_{h}"
        if sid in used_ids:
            continue
        picked.append({"sample_id": sid, "language": row["Language"], "label": row["Label"], "code": row["Code"]})
        if len(picked) >= N:
            break
    return picked


def main():
    samples = build_convergence_sample()
    with open("artifacts/detectcodegpt_kconv_manifest.jsonl", "w") as f:
        for s in samples:
            f.write(json.dumps(s, default=str) + "\n")
    print(f"built {len(samples)} disjoint convergence samples")

    det = DetectCodeGPTDetector()

    rows = []
    for s in samples:
        t0 = time.time()
        perturbations = det.generate_perturbations(s["code"], n=max(K_VALUES))
        gen_time = time.time() - t0

        scores = {}
        timings = {}
        for k in K_VALUES:
            t0 = time.time()
            scores[k] = det.score_at_k(s["code"], perturbations, k)
            timings[k] = time.time() - t0

        rows.append({"sample_id": s["sample_id"], "language": s["language"], "gen_time": gen_time, "scores": scores, "timings": timings})
        print(s["sample_id"], scores, {k: round(v, 2) for k, v in timings.items()})

    with open("artifacts/detectcodegpt_kconv_results.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r, default=str) + "\n")

    s50 = [r["scores"][50] for r in rows if r["scores"][50] is not None]
    report = {}
    for k in [5, 10, 20]:
        pairs = [(r["scores"][k], r["scores"][50]) for r in rows if r["scores"][k] is not None and r["scores"][50] is not None]
        if len(pairs) < 3:
            report[k] = {"n": len(pairs), "note": "insufficient valid pairs"}
            continue
        sk_vals = [p[0] for p in pairs]
        s50_vals = [p[1] for p in pairs]
        rho, _ = spearmanr(sk_vals, s50_vals)
        abs_diffs = sorted(abs(a - b) for a, b in pairs)
        median_abs_diff = abs_diffs[len(abs_diffs) // 2]
        std_s50 = (sum((x - sum(s50) / len(s50)) ** 2 for x in s50) / len(s50)) ** 0.5 if s50 else None
        rel_dev = median_abs_diff / std_s50 if std_s50 else None
        mean_runtime = sum(r["timings"][k] for r in rows) / len(rows)
        report[k] = {
            "n": len(pairs),
            "rho_vs_k50": rho,
            "median_abs_diff": median_abs_diff,
            "std_s50": std_s50,
            "relative_deviation": rel_dev,
            "mean_runtime_sec": mean_runtime,
            "passes_rule": bool(rho is not None and rho >= 0.95 and rel_dev is not None and rel_dev <= 0.10),
        }

    mean_runtime_50 = sum(r["timings"][50] for r in rows) / len(rows)
    report[50] = {"n": len(s50), "rho_vs_k50": 1.0, "median_abs_diff": 0.0, "relative_deviation": 0.0, "mean_runtime_sec": mean_runtime_50, "passes_rule": True}

    with open("artifacts/detectcodegpt_kconv_report.json", "w") as f:
        json.dump(report, f, indent=2, default=str)

    chosen_k = 50
    for k in [5, 10, 20]:
        if report[k].get("passes_rule"):
            chosen_k = k
            break
    report["chosen_k"] = chosen_k
    print(json.dumps(report, indent=2, default=str))
    print(f"\nCHOSEN K = {chosen_k} (per predeclared rule in docs/DETECTCODEGPT_PROTOCOL.md)")


if __name__ == "__main__":
    main()
