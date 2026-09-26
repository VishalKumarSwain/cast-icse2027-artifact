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
    fig, ax = plt.subplots(figsize=(16.8, 8.3))
    ax.set_xlim(0, 16.8)
    ax.set_ylim(0, 8.3)
    ax.axis("off")

    def box(x, y, w, h, label, face="#EAEAF2", fontsize=9, edge="black", lw=1.0):
        ax.add_patch(plt.Rectangle((x, y), w, h, fill=True, facecolor=face, edgecolor=edge, linewidth=lw, zorder=2))
        ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", fontsize=fontsize, zorder=3)

    def diamond(cx, cy, w, h, label, face="#FFF3CD", fontsize=9):
        pts = [(cx, cy + h / 2), (cx + w / 2, cy), (cx, cy - h / 2), (cx - w / 2, cy)]
        ax.add_patch(plt.Polygon(pts, closed=True, facecolor=face, edgecolor="black", linewidth=1.0, zorder=2))
        ax.text(cx, cy, label, ha="center", va="center", fontsize=fontsize, zorder=3)

    def arrow(p0, p1, color="black", lw=1.2, style="->"):
        ax.annotate("", xy=p1, xytext=p0, arrowprops=dict(arrowstyle=style, lw=lw, color=color), zorder=4)

    def step(x, y, n):
        ax.add_patch(plt.Circle((x, y), 0.17, facecolor="#4C72B0", edgecolor="black", linewidth=0.8, zorder=5))
        ax.text(x, y, str(n), ha="center", va="center", fontsize=8, color="white", fontweight="bold", zorder=6)

    def band(y0, h, face, edge, title):
        ax.add_patch(plt.Rectangle((0.05, y0), 16.7, h, fill=True, facecolor=face, edgecolor=edge,
                                    linestyle="--", linewidth=1.3, zorder=0))
        ax.text(0.25, y0 + h - 0.3, title, fontsize=12, fontweight="bold", ha="left", va="top", zorder=1)

    # ================= band backgrounds (sized to clear their own content) =================
    band(4.75, 3.35, "#EAF3FB", "#4C72B0", "Row 1 -- Main pipeline")
    band(2.70, 1.90, "#EAF6EC", "#55A868", "Row 2 -- Canonicalization intervention (mirrored right-to-left)")
    band(0.05, 2.50, "#FBEAEA", "#C44E52",
         "Row 3 -- Identity-transformation noise-floor control (Section 2.3) -- independent of the main pipeline")

    # ================= Row 1: main pipeline =================
    # C0 is the input, not a numbered step. Step (1) is applying T to get
    # T(C0); (2) validation; (3) distance measurement; (4) scoring; (5) IER.
    box(0.3, 5.60, 1.7, 1.3, "$C_0$\nprogram of known\nprovenance")
    box(2.6, 5.60, 2.0, 1.3, "$T(C_0)$\nfixed, deterministic\ntransformation")
    box(5.2, 6.15, 2.3, 1.0, "Validation gate\n(parse/compile tier;\ninvalid outcomes kept)")
    box(5.2, 5.50, 2.3, 0.55, "measure $d_\\mathrm{text}, d_\\mathrm{token}, d_\\mathrm{AST}$ (not scored)", fontsize=8)
    box(8.1, 5.60, 2.5, 1.3, "Score $D(C_0)$ and $D(T(C_0))$\nwith 3 frozen detectors:\nLLMSniffer, DroidDetect-Base,\nDetectCodeGPT")
    box(11.3, 5.60, 2.1, 1.3, "$\\Delta_D$, decision-flip,\nInduced Error Rate\n(Eq. 1)")
    diamond(14.5, 6.25, 1.75, 1.6, "large\nmovement?")

    step(3.6, 7.22, 1)
    step(6.35, 7.22, 2)
    step(9.35, 7.22, 4)
    step(12.35, 7.22, 5)

    arrow((2.0, 6.25), (2.6, 6.25))
    arrow((4.6, 6.50), (5.2, 6.65))
    arrow((4.6, 6.00), (5.08, 5.79))
    arrow((10.6, 6.25), (11.3, 6.25))
    arrow((13.4, 6.25), (13.63, 6.25))

    # Both C0 and T(C0) feed the scoring step -- two color-coded arrows so
    # the diagram doesn't imply only T(C0) is scored.
    arrow((1.15, 5.60), (1.15, 5.30), color="#4C72B0", style="-")
    arrow((1.15, 5.30), (9.0, 5.30), color="#4C72B0", style="-")
    arrow((9.0, 5.30), (9.0, 5.60), color="#4C72B0")
    ax.text(1.3, 5.35, "$C_0$", fontsize=8, color="#4C72B0", style="italic", ha="left")

    arrow((3.6, 5.60), (3.6, 5.05), color="#C44E52", style="-")
    arrow((3.6, 5.05), (9.6, 5.05), color="#C44E52", style="-")
    arrow((9.6, 5.05), (9.6, 5.60), color="#C44E52")
    ax.text(1.3, 5.10, "$T(C_0)$", fontsize=8, color="#C44E52", style="italic", ha="left")

    # "no" exit
    arrow((15.375, 6.25), (15.9, 6.25), color="#555555", lw=1.0)
    ax.text(15.55, 6.47, "no", fontsize=8, style="italic", color="#555555", ha="left")
    ax.text(15.55, 5.90, "report IER\nonly", fontsize=7, color="#555555", ha="left", style="italic")

    # "yes" exit -- drops from the diamond straight down into the
    # Canonicalizer box's top edge in Row 2, crossing the gap between bands.
    arrow((14.5, 5.45), (14.5, 3.95))
    ax.text(14.7, 5.15, "yes", fontsize=8, style="italic", color="#555555", ha="left")

    # ================= Row 2: canonicalization intervention (mirrored) =================
    box(11.3, 2.85, 2.1, 1.1, "Canonicalizer $F$: strip\nwhitespace, blank lines,\ncomments, quote style")
    box(8.1, 2.85, 2.5, 1.1, "Score $F(C_0)$, $F(T(C_0))$\nwith same 3 detectors")
    box(5.2, 2.85, 2.3, 1.1, "split: residual vs.\ntrivially-identical\n($F(C_0){=}F(T(C_0))$, $\\Delta{=}0$)")
    box(2.6, 2.85, 2.0, 1.1, "reduction\nfactor,\nresidual-only", face="#EAEAF2")

    arrow((11.3, 3.40), (10.6, 3.40))
    arrow((8.1, 3.40), (7.5, 3.40))
    arrow((5.2, 3.40), (4.6, 3.40))

    # ================= Row 3: identity-transformation noise-floor control =================
    box(0.3, 0.7, 2.0, 1.1, "$C_0$, fresh\nrandom seed,\nno transformation")
    box(2.6, 0.7, 2.0, 1.1, "re-score with\nsame 3 detectors")
    box(4.95, 0.7, 2.55, 1.1, "noise floor: decision-flip\nrate and mean $|\\Delta|$ on\nunchanged input")
    arrow((2.3, 1.25), (2.6, 1.25))
    arrow((4.6, 1.25), (4.95, 1.25))

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

    fig, axes = plt.subplots(1, 3, figsize=(7.0, 2.4))
    for ax, det, b, a in zip(axes, detectors, before, after):
        bars = ax.bar([0, 1], [b, a], width=0.5,
                      color=["#C44E52", "#8C8C8C"], edgecolor="black", linewidth=0.5)
        reduction = b / a if a > 0 else float("inf")
        ax.text(0.5, max(b, a) * 1.08, f"{reduction:.1f}x", ha="center", fontsize=9, fontweight="bold")
        ax.set_xticks([0, 1])
        ax.set_xticklabels(["before", "after"], fontsize=9)
        ax.tick_params(axis="y", labelsize=8)
        ax.set_title(det, fontsize=9)
        ax.set_ylim(0, max(b, a) * 1.25)
    axes[0].set_ylabel("Mean |score delta|\n(own scale per detector)")
    fig.tight_layout()
    fig.savefig(f"{OUT_DIR}/figure3_canonicalization_intervention.png", dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    figure1()
    figure2()
    figure3()
    print(f"Figures written to {OUT_DIR}/")
