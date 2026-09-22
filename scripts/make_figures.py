"""Generate the three analysis-stage figures from frozen artifacts only.
Figure 2 uses Induced Error Rate (a bounded 0-1 proportion) for cross-
detector comparison, NOT raw |delta| -- raw score scales differ across
detectors and are not directly comparable (see docs/PROD_002F_RESULTS.md).
Figure 3 is a within-detector before/after comparison (canonicalization),
which is legitimate since it never compares absolute scale across detectors.
"""
import json
from collections import defaultdict

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT_DIR = "artifacts/final_tables/figures"
import os

os.makedirs(OUT_DIR, exist_ok=True)

DETECTOR_COLORS = {"LLMSniffer": "#4C72B0", "DroidDetect-Base": "#DD8452", "DetectCodeGPT": "#55A868"}


# ============================================================================
# Figure 1: CAST methodology schematic
# ============================================================================

def figure1():
    fig, ax = plt.subplots(figsize=(10, 4.2))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4)
    ax.axis("off")

    boxes = [
        (0.3, 1.5, 1.6, 1, "C0\n(held-out seed)"),
        (2.3, 1.5, 1.9, 1, "T(C0)\ntransformation"),
        (4.6, 2.6, 1.9, 1, "Validation gate\n(parse/compile tier)"),
        (4.6, 0.4, 1.9, 1, "d_text / d_token / d_AST\n(measured, not scored)"),
        (6.9, 1.5, 1.9, 1, "3 frozen\ndetectors"),
        (9.0, 2.6, 0.9, 1, "score\nmovement\n/ IER"),
        (9.0, 0.4, 0.9, 1, "canonicalize\n(intervention)"),
    ]
    for x, y, w, h, label in boxes:
        ax.add_patch(plt.Rectangle((x, y), w, h, fill=True, facecolor="#EAEAF2", edgecolor="black"))
        ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", fontsize=8.5)

    arrows = [
        ((1.9, 2.0), (2.3, 2.0)),
        # T(C0) is validated and distance-measured against C0 (side branches, not fed to detectors)
        ((4.2, 2.2), (4.6, 3.1)),
        ((4.2, 1.8), (4.6, 0.9)),
        # C0 and T(C0) are what the detectors actually score
        ((4.2, 2.0), (6.9, 2.0)),
        ((8.8, 2.0), (9.0, 3.1)),
        ((8.8, 2.0), (9.0, 0.9)),
    ]
    for (x0, y0), (x1, y1) in arrows:
        ax.annotate("", xy=(x1, y1), xytext=(x0, y0), arrowprops=dict(arrowstyle="->", lw=1.2))
    ax.annotate("$D(C_0)$ and $D(T(C_0))$ both scored", xy=(5.55, 1.7), ha="center", fontsize=7, style="italic", color="#555555")

    ax.set_title("Figure 1: CAST -- Controlled, distance-instrumented Attribution-Stability Testing", fontsize=11)
    fig.tight_layout()
    fig.savefig(f"{OUT_DIR}/figure1_cast_methodology.png", dpi=200)
    plt.close(fig)


# ============================================================================
# Figure 2: detector-specific stability profiles (IER, bounded 0-1, cross-detector comparable)
# ============================================================================

def figure2():
    rows = [json.loads(l) for l in open("artifacts/prod002_detector_scores.jsonl", encoding="utf-8")]
    groups = defaultdict(list)
    for r in rows:
        groups[(r["detector"], r["language"], r["transformation_family"])].append(r)

    families = ["control_flow", "lexical_rename", "formatting"]
    detectors = ["LLMSniffer", "DroidDetect-Base", "DetectCodeGPT"]
    languages = ["Python", "Java"]

    def ier(det, lang, fam):
        rs = groups.get((det, lang, fam), [])
        base_ok = [r for r in rs if r.get("baseline_correct")]
        induced = sum(1 for r in base_ok if r.get("flip_among_baseline_correct"))
        return (induced / len(base_ok) * 100) if base_ok else 0.0

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8), sharey=True)
    for ax, lang in zip(axes, languages):
        x = range(len(families))
        width = 0.25
        for i, det in enumerate(detectors):
            vals = [ier(det, lang, fam) for fam in families]
            ax.bar([xi + i * width for xi in x], vals, width, label=det, color=DETECTOR_COLORS[det],
                   hatch="//" if det == "DetectCodeGPT" else None, edgecolor="black", linewidth=0.5)
        ax.set_xticks([xi + width for xi in x])
        ax.set_xticklabels(families, fontsize=9)
        ax.set_title(lang, fontsize=10)
    axes[0].set_ylabel("Induced Error Rate (%)\namong baseline-correct samples")
    axes[1].legend(fontsize=8, loc="upper left")
    fig.suptitle("Figure 2: Detector-specific attribution-stability profiles by language\n(DetectCodeGPT hatched: threshold-dependent, 60% calibration accuracy -- secondary metric)", fontsize=10)
    fig.tight_layout(rect=[0, 0, 1, 0.88])
    fig.savefig(f"{OUT_DIR}/figure2_detector_stability_profiles.png", dpi=200)
    plt.close(fig)


# ============================================================================
# Figure 3: canonicalization intervention (within-detector before/after -- legitimate paired comparison)
# ============================================================================

def figure3():
    pairs = [json.loads(l) for l in open("artifacts/prod004_canonicalized_pairs.jsonl", encoding="utf-8")]
    identical_ids = {p["sample_id"] for p in pairs if p["identical"]}
    residual_ids = {p["sample_id"] for p in pairs if not p["identical"]}

    llm_droid_residual = {r["sample_id"]: r for r in (json.loads(l) for l in open("artifacts/prod004_residual_scores_llm_droid.jsonl", encoding="utf-8"))}
    dcg_residual = {r["sample_id"]: r for r in (json.loads(l) for l in open("artifacts/prod004_residual_scores_detectcodegpt.jsonl", encoding="utf-8"))}
    orig_scores = [json.loads(l) for l in open("artifacts/prod002_detector_scores.jsonl", encoding="utf-8")]
    orig_formatting = defaultdict(dict)
    for r in orig_scores:
        if r["transformation_family"] == "formatting" and r["sample_id"] in identical_ids | residual_ids:
            orig_formatting[r["sample_id"]][r["detector"]] = r["delta_score"]

    # Residual-only (excludes pairs that trivially collapse to identical under
    # canonicalization), per reviewer feedback that full-set factors are inflated
    # by the ~68% of formatting pairs that are Delta=0 by construction.
    detectors = ["LLMSniffer", "DroidDetect-Base", "DetectCodeGPT"]
    before, after = [], []
    for det in detectors:
        orig_vals = [abs(orig_formatting[sid][det]) for sid in residual_ids if det in orig_formatting.get(sid, {})]
        canon_vals = []
        for sid in residual_ids:
            if det == "DetectCodeGPT" and sid in dcg_residual and dcg_residual[sid]["DetectCodeGPT_delta_canon"] is not None:
                canon_vals.append(abs(dcg_residual[sid]["DetectCodeGPT_delta_canon"]))
            elif det != "DetectCodeGPT" and sid in llm_droid_residual:
                canon_vals.append(abs(llm_droid_residual[sid][f"{det}_delta_canon"]))
        before.append(sum(orig_vals) / len(orig_vals))
        after.append(sum(canon_vals) / len(canon_vals))

    fig, axes = plt.subplots(1, 3, figsize=(9.6, 3.6))
    for ax, det, b, a in zip(axes, detectors, before, after):
        bars = ax.bar([0, 1], [b, a], width=0.5,
                      color=["#C44E52", "#8C8C8C"], edgecolor="black", linewidth=0.5)
        reduction = b / a if a > 0 else float("inf")
        ax.text(0.5, max(b, a) * 1.08, f"{reduction:.1f}x", ha="center", fontsize=9, fontweight="bold")
        ax.set_xticks([0, 1])
        ax.set_xticklabels(["before", "after"], fontsize=8)
        ax.set_title(det, fontsize=9)
        ax.set_ylim(0, max(b, a) * 1.25)
    axes[0].set_ylabel("Mean |score delta|\n(own scale per detector)")
    fig.suptitle("Canonicalization intervention -- residual pairs only, within-detector before/after\n(each panel its own y-axis; scales are NOT comparable across detectors)", fontsize=10)
    fig.tight_layout(rect=[0, 0, 1, 0.85])
    fig.savefig(f"{OUT_DIR}/figure3_canonicalization_intervention.png", dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    figure1()
    figure2()
    figure3()
    print(f"Figures written to {OUT_DIR}/")
