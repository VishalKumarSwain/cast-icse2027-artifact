"""Confound analyses for the DroidDetect-Base formatting result (paper Section 4.1).

Addresses two questions raised about the headline human-to-AI flip rate:
  (a) Is it explained by program length? (flipped human samples are shorter)
  (b) Is the family comparison (formatting vs rename vs control-flow) explained
      by edit size alone?

Reads only frozen artifacts (no GPU / model access):
  artifacts/pilot_manifest_prod001.jsonl              (program text -> length)
  artifacts/prod001_transform_log.jsonl               (d_text, d_token, d_ast)
  artifacts/prod001_droiddetect_2class_reclassified.jsonl  (flip decisions)
Writes artifacts/final_tables/table13_confound_analysis.csv and prints a summary.
"""
import csv
import json
import math

import numpy as np
from scipy import stats
from scipy.optimize import minimize


def load(path):
    return [json.loads(l) for l in open(path, encoding="utf-8")]


def logistic_fit(X, y):
    """Plain maximum-likelihood logistic regression; returns coef, se, p (Wald)."""
    X = np.column_stack([np.ones(len(X)), X])

    def nll(b):
        z = X @ b
        return np.sum(np.logaddexp(0, z) - y * z) + 1e-6 * np.sum(b ** 2)

    res = minimize(nll, np.zeros(X.shape[1]), method="BFGS")
    b = res.x
    p = 1 / (1 + np.exp(-(X @ b)))
    W = p * (1 - p)
    cov = np.linalg.inv(X.T @ (X * W[:, None]) + 1e-6 * np.eye(X.shape[1]))
    se = np.sqrt(np.diag(cov))
    z = b / se
    pv = 2 * (1 - stats.norm.cdf(np.abs(z)))
    return b, se, pv


def main():
    man = {m["sample_id"]: m for m in load("artifacts/pilot_manifest_prod001.jsonl")}
    tl = {(r["sample_id"], r["transformation_family"]): r for r in load("artifacts/prod001_transform_log.jsonl")}
    rows = []
    for r in load("artifacts/prod001_droiddetect_2class_reclassified.jsonl"):
        if not r["baseline_correct_2class"]:
            continue
        t = tl.get((r["sample_id"], r["transformation_family"]))
        if t is None or t.get("d_text") is None:
            continue
        n = len(man[r["sample_id"]]["code"])
        rows.append(dict(
            fam=r["transformation_family"], label=r["label"], lang=r["language"],
            flip=int(r["flip_among_baseline_correct_2class"]),
            n=n, d_text=t["d_text"], norm=t["d_text"] / n, d_ast=t["d_ast"]))
    out = []

    # (a) length confound, human-written formatting pairs
    hf = [r for r in rows if r["fam"] == "formatting" and r["label"] == "HUMAN_GENERATED"]
    y = np.array([r["flip"] for r in hf], float)
    logn = np.array([math.log(r["n"]) for r in hf])
    norm = np.array([r["norm"] for r in hf])
    java = np.array([1.0 if r["lang"] == "Java" else 0.0 for r in hf])
    print(f"Human formatting pairs: n={len(hf)}, flipped={int(y.sum())}")
    for name, cols in [
        ("log_length_only", [logn]),
        ("norm_edit_only", [norm]),
        ("log_length+norm_edit+java", [logn, norm, java]),
    ]:
        Z = np.column_stack(cols)
        mu, sd = Z.mean(0), Z.std(0)
        b, se, pv = logistic_fit((Z - mu) / sd, y)
        for i, c in enumerate(cols):
            lab = ["log_length", "norm_edit", "java"][i] if name.count("+") else name.replace("_only", "")
            print(f"  [{name}] {lab}: OR per 1 SD = {math.exp(b[i+1]):.2f}, p = {pv[i+1]:.3f}")
            out.append(("logit_" + name, lab, f"{math.exp(b[i+1]):.3f}", f"{pv[i+1]:.4f}"))
    rho, p = stats.spearmanr(logn, y)
    print(f"  Spearman(log length, flip) = {rho:.2f}, p = {p:.3f}")
    out.append(("spearman", "log_length_vs_flip", f"{rho:.3f}", f"{p:.4f}"))
    order = np.argsort([r["n"] for r in hf])
    half = len(hf) // 2
    for nm, idx in (("shorter_half", order[:half]), ("longer_half", order[half:])):
        k = int(sum(hf[i]["flip"] for i in idx))
        print(f"  {nm}: {k}/{len(idx)} flipped ({k/len(idx):.1%})")
        out.append(("length_half", nm, f"{k}/{len(idx)}", f"{k/len(idx):.4f}"))

    # (a2) does the human-vs-AI asymmetry survive length control?
    allf = [r for r in rows if r["fam"] == "formatting"]
    yy = np.array([r["flip"] for r in allf], float)
    Z = np.column_stack([
        [1.0 if r["label"] == "HUMAN_GENERATED" else 0.0 for r in allf],
        [math.log(r["n"]) for r in allf],
        [r["norm"] for r in allf],
        [1.0 if r["lang"] == "Java" else 0.0 for r in allf]])
    mu, sd = Z.mean(0), Z.std(0)
    sd[0] = 1.0
    mu[0] = 0.0
    b, se, pv = logistic_fit((Z - mu) / sd, yy)
    print(f"\nAll formatting pairs (human+AI), n={len(allf)}: logit(flip) ~ human + log_length + norm_edit + java")
    print(f"  human-written (vs AI-class): OR = {math.exp(b[1]):.1f}, p = {pv[1]:.4f}")
    print(f"  log_length (per 1 SD): OR = {math.exp(b[2]):.2f}, p = {pv[2]:.4f}")
    out.append(("logit_pooled_class", "human_vs_AI", f"{math.exp(b[1]):.2f}", f"{pv[1]:.5f}"))
    out.append(("logit_pooled_class", "log_length", f"{math.exp(b[2]):.3f}", f"{pv[2]:.5f}"))
    for cap in (1000, 1500, 2500):
        h = [r for r in allf if r["label"] == "HUMAN_GENERATED" and r["n"] <= cap]
        a = [r for r in allf if r["label"] != "HUMAN_GENERATED" and r["n"] <= cap]
        hk = sum(r["flip"] for r in h)
        ak = sum(r["flip"] for r in a)
        if h and a:
            _, fp = stats.fisher_exact([[hk, len(h) - hk], [ak, len(a) - ak]])
            print(f"  length <= {cap} chars: human {hk}/{len(h)} flipped vs AI-class {ak}/{len(a)} (Fisher p = {fp:.2g})")
            out.append(("length_matched_class", f"<= {cap}", f"human {hk}/{len(h)} vs AI {ak}/{len(a)}", f"{fp:.3g}"))

    # (b) IER by family within matched normalized-edit-size range (human-written code)
    print("\nDroidDetect-Base IER on human-written code, by family and normalized edit size (d_text/len)")
    for fam in ["lexical_rename", "control_flow", "formatting"]:
        fr = [r for r in rows if r["fam"] == fam and r["label"] == "HUMAN_GENERATED"]
        if fr:
            print(f"  {fam}: n={len(fr)}, median norm-edit={np.median([r['norm'] for r in fr]):.4f}, "
                  f"IER={sum(r['flip'] for r in fr)}/{len(fr)}")
            out.append(("family_human", fam, f"{sum(r['flip'] for r in fr)}/{len(fr)}",
                        f"{np.median([r['norm'] for r in fr]):.5f}"))
    fmt = [r for r in rows if r["fam"] == "formatting" and r["label"] == "HUMAN_GENERATED"]
    small = sorted(r["norm"] for r in fmt)
    for lo, hi in [(0.0, 0.05), (0.05, 0.10), (0.10, 0.20), (0.20, 9)]:
        sel = [r for r in fmt if lo <= r["norm"] < hi]
        if sel:
            print(f"  formatting, norm-edit [{lo:.2f},{hi:.2f}): {sum(r['flip'] for r in sel)}/{len(sel)}")
            out.append(("formatting_bin", f"[{lo},{hi})", f"{sum(r['flip'] for r in sel)}/{len(sel)}", ""))
    rn = [r for r in rows if r["fam"] != "formatting" and r["label"] == "HUMAN_GENERATED"]
    print(f"  non-formatting families combined: max norm-edit = {max(r['norm'] for r in rn):.4f}, "
          f"flips {sum(r['flip'] for r in rn)}/{len(rn)}")
    cap = max(r["norm"] for r in rn)
    sel = [r for r in fmt if r["norm"] <= cap]
    if sel:
        print(f"  formatting restricted to norm-edit <= {cap:.4f}: {sum(r['flip'] for r in sel)}/{len(sel)}")
        out.append(("formatting_matched_to_rename_max", f"<= {cap:.4f}",
                    f"{sum(r['flip'] for r in sel)}/{len(sel)}", ""))

    # (c) like-for-like accuracy of the DroidDetect-Base reconstruction on the 199-program
    # held-out test corpus: exact 4-class match (the metric used in the n=24 dev check)
    # vs binary human-vs-AI collapse (the metric used for the formatting/IER results)
    def wilson(k, n, z=1.959964):
        p = k / n
        c = (p + z * z / (2 * n)) / (1 + z * z / n)
        h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
        return c - h, c + h

    base = load("artifacts/prod001_c0_baseline.jsonl")
    ai = ("MACHINE_GENERATED", "MACHINE_REFINED")
    k4 = sum(b["scores"]["DroidDetect-Base"]["predicted_label"] == b["label"] for b in base)
    def is_ai(lbl):
        return lbl != "HUMAN_GENERATED"
    k2 = sum(is_ai(b["scores"]["DroidDetect-Base"]["predicted_label"]) == is_ai(b["label"]) for b in base)
    k4ai = sum(b["scores"]["DroidDetect-Base"]["predicted_label"] == b["label"] for b in base if b["label"] in ai)
    n_ai = sum(b["label"] in ai for b in base)
    print(f"\nDroidDetect-Base on the {len(base)}-program test corpus:")
    for nm, k, n in (("4-class exact match", k4, len(base)), ("binary human-vs-AI", k2, len(base)),
                     ("4-class exact match, AI-class rows only", k4ai, n_ai)):
        lo, hi = wilson(k, n)
        print(f"  {nm}: {k}/{n} = {k/n:.1%}  Wilson 95% CI [{lo*100:.1f}, {hi*100:.1f}]")
        out.append(("accuracy", nm, f"{k}/{n}", f"[{lo*100:.1f},{hi*100:.1f}]"))
    lo, hi = wilson(21, 24)
    print(f"  (dev-split sanity check, 4-class exact match: 21/24 = 87.5%  Wilson 95% CI [{lo*100:.1f}, {hi*100:.1f}])")

    # (d) provenance of the 365 transformed pairs
    tlog = load("artifacts/prod001_transform_log.jsonl")
    import collections
    st = collections.Counter(r["status"] for r in tlog)
    print(f"\nTransformation attempts: {len(tlog)} (199 programs x 3 families); status counts: {dict(st)}")
    out.append(("transform_attempts", "total", str(len(tlog)), json.dumps(dict(st))))

    with open("artifacts/final_tables/table13_confound_analysis.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["analysis", "term", "value", "p_or_extra"])
        w.writerows(out)
    print("Wrote artifacts/final_tables/table13_confound_analysis.csv")


if __name__ == "__main__":
    main()
