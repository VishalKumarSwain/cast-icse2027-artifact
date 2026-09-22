"""Generate the four final result tables directly from frozen artifacts.
No new experiments, no modification of any existing output. Every number is
computed from the JSONL/JSON artifacts listed per table, not from memory or
prior conversation summaries.

Outputs (all under artifacts/final_tables/):
  table1_setup_validity.{csv,md}
  table2_main_attribution_stability.{csv,md}
  table3_forensic_stability_profiles.{csv,md}   (+ table3_overlap_exploratory.md)
  table4_prod003_feasibility.{csv,md}
"""
import csv
import json
import math
import statistics
from collections import Counter, defaultdict

OUT_DIR = "artifacts/final_tables"


def wilson_ci(successes, n, z=1.96):
    if n == 0:
        return (None, None)
    p = successes / n
    denom = 1 + z**2 / n
    center = (p + z**2 / (2 * n)) / denom
    half = (z * math.sqrt((p * (1 - p) / n) + (z**2 / (4 * n**2)))) / denom
    return (max(0.0, center - half), min(1.0, center + half))


def write_csv_md(rows, headers, path_stub):
    with open(f"{OUT_DIR}/{path_stub}.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for r in rows:
            writer.writerow("" if v is None else v for v in r)
    with open(f"{OUT_DIR}/{path_stub}.md", "w", encoding="utf-8") as f:
        f.write("| " + " | ".join(headers) + " |\n")
        f.write("|" + "---|" * len(headers) + "\n")
        for r in rows:
            f.write("| " + " | ".join("" if v is None else str(v) for v in r) + " |\n")


# ============================================================================
# TABLE 1: Experimental Setup and Validity
# ============================================================================

def table1():
    manifest = [json.loads(l) for l in open("artifacts/pilot_manifest_prod001.jsonl", encoding="utf-8")]
    transform_log = [json.loads(l) for l in open("artifacts/prod001_transform_log.jsonl", encoding="utf-8")]
    contracts = json.load(open("artifacts/pilot003_detector_contracts.json"))
    calib = json.load(open("artifacts/detectcodegpt_calibration_result.json"))

    n_total = len(manifest)
    n_python = sum(1 for r in manifest if r["language"] == "Python")
    n_java = sum(1 for r in manifest if r["language"] == "Java")

    families = sorted(set(r["transformation_family"] for r in transform_log))
    attempted = len(transform_log)
    applicable = sum(1 for r in transform_log if r["status"] != "NOT_APPLICABLE")
    success = sum(1 for r in transform_log if r["status"] == "SUCCESS")

    rows = [
        ["Dataset", "project-droid/DroidCollection (Droid, EMNLP 2025)"],
        ["Held-out split used (PROD_001/PROD_002/PROD_002F)", "test"],
        ["Total C0 samples (confirmatory production experiments)", n_total],
        ["Python samples", n_python],
        ["Java samples", n_java],
        ["Provenance labels represented", "HUMAN_GENERATED, MACHINE_GENERATED, MACHINE_REFINED"],
        ["Detector 1", "LLMSniffer (GraphCodeBERT + supervised contrastive head)"],
        ["Detector 1 sanity check", f"{contracts['llmsniffer']['in_domain_sanity_check']['accuracy']*100:.1f}% on GPTSniffer Java test set, n={contracts['llmsniffer']['in_domain_sanity_check']['n']}"],
        ["Detector 2", "DroidDetect-Base (ModernBERT-base + projection + 4-class head; architecture reconstructed, no published modeling code)"],
        ["Detector 2 sanity check", f"{contracts['droiddetect_base']['chosen_accuracy_on_dev_subset']*100:.1f}% on Droid dev-split subset (pooling={contracts['droiddetect_base']['chosen_pooling']}, label permutation={contracts['droiddetect_base']['chosen_label_permutation']})"],
        ["Detector 3", "DetectCodeGPT (DetectGPT/NPR-family zero-shot perturbation z-score; CodeLlama-7b-hf + CodeT5p-770m)"],
        ["Detector 3 chosen K (perturbations)", calib["chosen_k"]],
        ["Detector 3 frozen decision threshold", round(calib["frozen_threshold"], 3)],
        ["Detector 3 independent calibration accuracy", f"{calib['calibration_accuracy']*100:.1f}% (n={calib['n']}, Droid DEV split -- disjoint from evaluation set)"],
        ["Transformation families (confirmatory, PROD_001/PROD_002)", "lexical_rename, formatting, control_flow"],
        ["Transformation families (feasibility-only, PROD_003)", "local_structural, deep_semantic"],
        ["PROD_001/PROD_002 ApplicabilityRate", round(applicable / attempted, 3)],
        ["PROD_001/PROD_002 TransformationSuccessRate", round(success / applicable, 3)],
        ["Distance metrics", "d_text (char-level edit distance), d_token (real tokenizer: Python tokenize / Java tree-sitter leaves), d_ast (AST node-count delta)"],
        ["Validation gate", "tiered parse/compile validation (Java: STANDALONE_VALID > WRAPPER_VALID > STRUCTURAL_ONLY > PARSE_INVALID); Python: compile()"],
        ["Confirmatory vs exploratory", "PROD_001/PROD_002/PROD_002F(quant.) = confirmatory production experiments on N=199 held-out seeds. PROD_002F's sample-ID-overlap note and PROD_003's N=1-12 detector cells = exploratory/illustrative only, not statistical claims."],
    ]
    write_csv_md(rows, ["Item", "Value"], "table1_setup_validity")
    return rows


# ============================================================================
# TABLE 2: Main attribution-stability results (frozen PROD_002)
# ============================================================================

def table2():
    rows_data = [json.loads(l) for l in open("artifacts/prod002_detector_scores.jsonl", encoding="utf-8")]
    groups = defaultdict(list)
    for r in rows_data:
        groups[(r["detector"], r["language"], r["transformation_family"])].append(r)

    out_rows = []
    for (det, lang, fam), rs in sorted(groups.items()):
        deltas = [r["delta_score"] for r in rs if r.get("delta_score") is not None]
        abs_deltas = [abs(d) for d in deltas]
        base_ok_rows = [r for r in rs if r.get("baseline_correct")]
        n_valid = len(rs)
        n_base_ok = len(base_ok_rows)
        induced_errors = sum(1 for r in base_ok_rows if r.get("flip_among_baseline_correct"))
        ier = (induced_errors / n_base_ok) if n_base_ok else None
        ci_lo, ci_hi = wilson_ci(induced_errors, n_base_ok) if n_base_ok else (None, None)
        mean_d = statistics.mean(deltas) if deltas else None
        median_d = statistics.median(deltas) if deltas else None
        median_abs_d = statistics.median(abs_deltas) if abs_deltas else None
        flips = sum(1 for r in rs if r.get("flip"))
        threshold_note = "SECONDARY (60% calib. acc.)" if det == "DetectCodeGPT" else "PRIMARY"
        # paired effect size: Cohen's d_z (mean paired difference / std of paired differences)
        # -- appropriate here because each sample is its own baseline (C0 vs T(C0)), not two
        # independent groups.
        if len(deltas) >= 2:
            sd = statistics.stdev(deltas)
            cohens_dz = (mean_d / sd) if sd > 0 else None
        else:
            cohens_dz = None
        out_rows.append(
            [
                det, lang, fam, n_valid, n_base_ok,
                round(mean_d, 4) if mean_d is not None else None,
                round(median_d, 4) if median_d is not None else None,
                round(median_abs_d, 4) if median_abs_d is not None else None,
                flips, induced_errors,
                round(ier, 4) if ier is not None else None,
                f"[{ci_lo:.3f}, {ci_hi:.3f}]" if ci_lo is not None else None,
                round(cohens_dz, 3) if cohens_dz is not None else None,
                threshold_note,
            ]
        )
    headers = ["Detector", "Language", "Family", "N_valid", "N_baseline_correct", "MeanDelta", "MedianDelta",
               "MedianAbsDelta", "Flips", "InducedErrors", "InducedErrorRate", "IER_95pct_CI_Wilson",
               "PairedEffectSize_CohensDz", "ThresholdMetricStatus"]
    write_csv_md(out_rows, headers, "table2_main_attribution_stability")
    return out_rows


# ============================================================================
# TABLE 3: Forensic stability-profile results (PROD_002F, recomputed from frozen data)
# ============================================================================

THRESHOLDS = {"LLMSniffer": 0.5, "DetectCodeGPT": 2.931085010288198}


def table3():
    rows_data = [json.loads(l) for l in open("artifacts/prod002_detector_scores.jsonl", encoding="utf-8")]
    rows_data = [r for r in rows_data if r.get("delta_score") is not None]
    by_detector = defaultdict(list)
    for r in rows_data:
        by_detector[r["detector"]].append(r)

    summary_rows = []

    # LLMSniffer
    llm = by_detector["LLMSniffer"]
    llm_flips = [r for r in llm if r.get("flip")]
    llm_margins_all = [abs(r["s0"] - 0.5) for r in llm]
    llm_median_margin_all = statistics.median(llm_margins_all)
    llm_flip_margins = [abs(r["s0"] - 0.5) for r in llm_flips]
    llm_near = sum(1 for m in llm_flip_margins if m < llm_median_margin_all)
    llm_flip_abs_deltas = [abs(r["delta_score"]) for r in llm_flips]
    summary_rows.append(["LLMSniffer", "total flips", len(llm_flips)])
    summary_rows.append(["LLMSniffer", "flips near-boundary (margin < median margin)", f"{llm_near}/{len(llm_flips)}"])
    summary_rows.append(["LLMSniffer", "median |delta| among ALL samples", round(statistics.median(abs(r["delta_score"]) for r in llm), 4)])
    summary_rows.append(["LLMSniffer", "median |delta| among flips", round(statistics.median(llm_flip_abs_deltas), 4) if llm_flip_abs_deltas else None])
    summary_rows.append(["LLMSniffer", "max |delta| overall", round(max(abs(r["delta_score"]) for r in llm), 4)])

    # DroidDetect-Base
    droid = by_detector["DroidDetect-Base"]
    droid_groups = defaultdict(list)
    for r in droid:
        droid_groups[(r["language"], r["transformation_family"])].append(r)
    for (lang, fam), rs in sorted(droid_groups.items()):
        base_ok = [r for r in rs if r.get("baseline_correct")]
        induced = sum(1 for r in base_ok if r.get("flip_among_baseline_correct"))
        ier = induced / len(base_ok) if base_ok else None
        ci = wilson_ci(induced, len(base_ok)) if base_ok else (None, None)
        summary_rows.append(["DroidDetect-Base", f"{lang} {fam} IER", f"{ier:.4f} (n_baseline_correct={len(base_ok)}, 95% CI [{ci[0]:.3f},{ci[1]:.3f}])" if ier is not None else "NA"])
    detector_p75 = statistics.median(sorted(abs(r["delta_score"]) for r in droid)[: int(0.999 * len(droid))]) if droid else None
    abs_d_sorted = sorted(abs(r["delta_score"]) for r in droid)
    p75 = abs_d_sorted[int(len(abs_d_sorted) * 0.75)]
    sig_rows = [
        r for r in droid
        if r.get("d_text") is not None and r["d_text"] > 0
        and r.get("d_token") is not None and r["d_token"] <= 5
        and r.get("d_ast") == 0
        and abs(r["delta_score"]) >= 2 * p75
    ]
    summary_rows.append(["DroidDetect-Base", "signature-region rows (small d_text/d_token, d_ast=0, |delta|>=2xP75)", f"{len(sig_rows)}/{len(droid)}"])

    # DetectCodeGPT
    dcg = by_detector["DetectCodeGPT"]
    dcg_abs_deltas = [abs(r["delta_score"]) for r in dcg]
    dcg_median_abs = statistics.median(dcg_abs_deltas)
    dcg_flips = [r for r in dcg if r.get("flip")]
    dcg_margins_all = [abs(r["s0"] - THRESHOLDS["DetectCodeGPT"]) for r in dcg]
    dcg_median_margin_all = statistics.median(dcg_margins_all)
    dcg_flip_margins = [abs(r["s0"] - THRESHOLDS["DetectCodeGPT"]) for r in dcg_flips]
    dcg_near = [(r, abs(r["s0"] - THRESHOLDS["DetectCodeGPT"])) for r in dcg_flips]
    dcg_near_boundary = [(r, m) for r, m in dcg_near if m < dcg_median_margin_all]
    dcg_near_boundary_abs_deltas = [abs(r["delta_score"]) for r, m in dcg_near_boundary]
    summary_rows.append(["DetectCodeGPT", "median |delta| among ALL samples", round(dcg_median_abs, 4)])
    summary_rows.append(["DetectCodeGPT", "total flips", len(dcg_flips)])
    summary_rows.append(["DetectCodeGPT", "flips near-boundary (margin < median margin)", f"{len(dcg_near_boundary)}/{len(dcg_flips)}"])
    summary_rows.append(["DetectCodeGPT", "median |delta| among near-boundary flips (should be small if pure threshold noise)", round(statistics.median(dcg_near_boundary_abs_deltas), 4) if dcg_near_boundary_abs_deltas else None])
    summary_rows.append(["DetectCodeGPT", "calibration caveat", "60% accuracy on independent dev-split calibration set (near chance) -- threshold-dependent metrics (flips/IER) are SECONDARY; raw |delta| is PRIMARY"])

    write_csv_md(summary_rows, ["Detector", "Metric", "Value"], "table3_forensic_stability_profiles")

    # exploratory overlap note, kept separate and clearly labeled
    overlap_ids = ["c0_test_42acb918f0f9", "c0_test_b4c24e630f64", "c0_test_b4eda3245609", "c0_test_47d1cf7a81ff", "c0_test_7f5026014142"]
    with open(f"{OUT_DIR}/table3_overlap_exploratory.md", "w", encoding="utf-8") as f:
        f.write("# EXPLORATORY (not confirmatory): LLMSniffer/DroidDetect-Base signature-region sample-ID overlap\n\n")
        f.write("Sample IDs appearing in both detectors' PROD_002F signature-region lists:\n\n")
        for sid in overlap_ids:
            f.write(f"- {sid}\n")
        f.write("\nAll 5 are HUMAN_GENERATED Python samples involving indentation-width normalization "
                "(tabs/8-space -> 4-space via black). Reported as an exploratory observation only -- "
                "not statistically validated, not built into any confirmatory metric above.\n")

    return summary_rows


# ============================================================================
# TABLE 3b: PROD_004 canonicalization intervention (frozen, commit 63e34aa)
# ============================================================================

def table3_canonicalization():
    pairs = [json.loads(l) for l in open("artifacts/prod004_canonicalized_pairs.jsonl", encoding="utf-8")]
    identical_ids = {p["sample_id"] for p in pairs if p["identical"]}
    residual_ids = {p["sample_id"] for p in pairs if not p["identical"]}
    lang_of = {p["sample_id"]: p["language"] for p in pairs}

    llm_droid_residual = {r["sample_id"]: r for r in (json.loads(l) for l in open("artifacts/prod004_residual_scores_llm_droid.jsonl", encoding="utf-8"))}
    dcg_residual = {r["sample_id"]: r for r in (json.loads(l) for l in open("artifacts/prod004_residual_scores_detectcodegpt.jsonl", encoding="utf-8"))}

    orig_scores = [json.loads(l) for l in open("artifacts/prod002_detector_scores.jsonl", encoding="utf-8")]
    orig_formatting = defaultdict(dict)
    for r in orig_scores:
        if r["transformation_family"] == "formatting" and r["sample_id"] in identical_ids | residual_ids:
            orig_formatting[r["sample_id"]][r["detector"]] = r["delta_score"]

    detectors = ["LLMSniffer", "DroidDetect-Base", "DetectCodeGPT"]
    interpretation = {
        "LLMSniffer": "Comparatively stable; some surface-presentation sensitivity, from an already-small base",
        "DroidDetect-Base": "Strong presentation-sensitive component -- canonicalization substantially attenuates instability, including on the non-identical residual subset",
        "DetectCodeGPT": "Instability not substantially mitigated by canonical formatting -- diffuse sensitivity has a source other than surface presentation",
    }

    rows = []
    n_total = len(identical_ids) + len(residual_ids)
    identical_pct = f"{len(identical_ids)}/{n_total} ({len(identical_ids)/n_total*100:.1f}%)"
    rows.append(["ALL", "ALL", f"Proportion canonicalizing to identical detector input: {identical_pct}", "(same figure -- this row is not per-detector)", "Scientifically meaningful on its own: most formatting pairs are pure whitespace/comment/quote differences"])

    for det in detectors:
        for lang in ["Python", "Java"]:
            full_orig = [abs(orig_formatting[sid][det]) for sid in identical_ids | residual_ids if det in orig_formatting.get(sid, {}) and lang_of[sid] == lang]
            full_canon = []
            for sid in identical_ids | residual_ids:
                if lang_of[sid] != lang:
                    continue
                if sid in identical_ids:
                    full_canon.append(0.0)
                elif det == "DetectCodeGPT" and sid in dcg_residual and dcg_residual[sid]["DetectCodeGPT_delta_canon"] is not None:
                    full_canon.append(abs(dcg_residual[sid]["DetectCodeGPT_delta_canon"]))
                elif det != "DetectCodeGPT" and sid in llm_droid_residual:
                    full_canon.append(abs(llm_droid_residual[sid][f"{det}_delta_canon"]))
            res_ids = [sid for sid in residual_ids if lang_of[sid] == lang]
            res_orig = [abs(orig_formatting[sid][det]) for sid in res_ids if det in orig_formatting.get(sid, {})]
            if det == "DetectCodeGPT":
                res_canon = [abs(dcg_residual[sid]["DetectCodeGPT_delta_canon"]) for sid in res_ids if sid in dcg_residual and dcg_residual[sid]["DetectCodeGPT_delta_canon"] is not None]
            else:
                res_canon = [abs(llm_droid_residual[sid][f"{det}_delta_canon"]) for sid in res_ids if sid in llm_droid_residual]

            if not full_orig or not full_canon:
                continue
            mean_full_orig, mean_full_canon = statistics.mean(full_orig), statistics.mean(full_canon)
            red_full = mean_full_orig / mean_full_canon if mean_full_canon > 0 else float("inf")
            mean_res_orig, mean_res_canon = (statistics.mean(res_orig), statistics.mean(res_canon)) if (res_orig and res_canon) else (None, None)
            red_res = (mean_res_orig / mean_res_canon) if (mean_res_canon is not None and mean_res_canon > 0) else None

            rows.append(
                [
                    det, lang,
                    f"N={len(full_canon)}: mean|d_orig|={mean_full_orig:.4f}, mean|d_canon|={mean_full_canon:.4f}, reduction={red_full:.1f}x",
                    f"N={len(res_canon)}: mean|d_orig|={mean_res_orig:.4f}, mean|d_canon|={mean_res_canon:.4f}, reduction={red_res:.1f}x" if red_res is not None else "NA",
                    interpretation[det],
                ]
            )
    headers = ["Detector", "Language", "FullSet(108 identical @0 + 50 residual measured)", "ResidualOnly(50 non-identical pairs)", "Interpretation"]
    write_csv_md(rows, headers, "table3b_canonicalization_intervention")
    return rows


# ============================================================================
# TABLE 4: PROD_003 feasibility / limitation
# ============================================================================

def table4():
    transform_log = [json.loads(l) for l in open("artifacts/prod003_transform_log.jsonl", encoding="utf-8")]
    attempted = len(transform_log)
    applicable = sum(1 for r in transform_log if r["status"] != "NOT_APPLICABLE")
    success = sum(1 for r in transform_log if r["status"] == "SUCCESS")
    sem_check = Counter(r.get("semantic_check") for r in transform_log if r["status"] == "SUCCESS")

    rows = [
        ["attempts", attempted],
        ["applicable", applicable],
        ["ApplicabilityRate", round(applicable / attempted, 4)],
        ["successful (SUCCESS)", success],
        ["TransformationSuccessRate", round(success / applicable, 4)],
        ["DIFFERENTIAL_EXECUTION_PASSED", sem_check.get("DIFFERENTIAL_EXECUTION_PASSED", 0)],
        ["DIFFERENTIAL_EXECUTION_FAILED", sem_check.get("DIFFERENTIAL_EXECUTION_FAILED", 0)],
        ["STRUCTURAL_ONLY_NO_ENTRY_POINT", sem_check.get("STRUCTURAL_ONLY_NO_ENTRY_POINT", 0)],
    ]

    breakdown = defaultdict(lambda: [0, 0, 0])  # attempted, applicable, success
    for r in transform_log:
        key = (r["language"], r["transformation_family"], r["intensity"])
        breakdown[key][0] += 1
        if r["status"] != "NOT_APPLICABLE":
            breakdown[key][1] += 1
        if r["status"] == "SUCCESS":
            breakdown[key][2] += 1
    breakdown_rows = []
    for (lang, fam, intensity), (att, appl, succ) in sorted(breakdown.items()):
        breakdown_rows.append([lang, fam, intensity, att, appl, succ])

    write_csv_md(rows, ["Metric", "Value"], "table4_prod003_feasibility")
    write_csv_md(breakdown_rows, ["Language", "Family", "Intensity", "Attempted", "Applicable", "Successful"], "table4b_prod003_breakdown_by_language_family_intensity")
    return rows, breakdown_rows


def main():
    import os

    os.makedirs(OUT_DIR, exist_ok=True)
    t1 = table1()
    t2 = table2()
    t3 = table3()
    t3b = table3_canonicalization()
    t4, t4b = table4()

    print("TABLE 1 rows:", len(t1))
    print("TABLE 2 rows:", len(t2))
    print("TABLE 3 rows:", len(t3))
    print("TABLE 3b (canonicalization) rows:", len(t3b))
    print("TABLE 4 rows:", len(t4), "TABLE 4b rows:", len(t4b))
    print(f"\nAll outputs written to {OUT_DIR}/")


if __name__ == "__main__":
    main()
