"""Analyses requested by the ICSE 2027 NIER round-2 review, computed entirely
from already-frozen artifacts (no new inference/sampling):
  W2: per-detector, per-language confusion matrices on the 199-program baseline.
  W4: flip-direction-by-true-class (human->AI "false accusation" vs AI->human
      "evasion") among baseline-correct, flipped, formatting-family pairs.
  W5: absolute score levels of canonicalized inputs (saturation check).
  W7: rank correlation between d_text/d_token/d_ast and |delta_score|, per
      detector, over all confirmatory-family pairs.
"""
import json
import statistics
from collections import defaultdict, Counter


def spearman(xs, ys):
    n = len(xs)
    if n < 3:
        return None
    def rank(vals):
        order = sorted(range(len(vals)), key=lambda i: vals[i])
        ranks = [0.0] * len(vals)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and vals[order[j + 1]] == vals[order[i]]:
                j += 1
            avg_rank = (i + j) / 2.0 + 1
            for k in range(i, j + 1):
                ranks[order[k]] = avg_rank
            i = j + 1
        return ranks
    rx, ry = rank(xs), rank(ys)
    mx, my = sum(rx) / n, sum(ry) / n
    cov = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    sx = (sum((a - mx) ** 2 for a in rx)) ** 0.5
    sy = (sum((b - my) ** 2 for b in ry)) ** 0.5
    if sx == 0 or sy == 0:
        return None
    return cov / (sx * sy)


def provenance_binary(label):
    return "HUMAN" if label == "HUMAN_GENERATED" else "AI"


# ============================================================================
# W2: confusion matrices on the 199-program baseline
# ============================================================================
print("=" * 70)
print("W2: BASELINE CONFUSION MATRICES (199 programs)")
print("=" * 70)

baseline = [json.loads(l) for l in open("artifacts/prod001_c0_baseline.jsonl", encoding="utf-8")]
dcg_baseline = {r["sample_id"]: r for r in (json.loads(l) for l in open("artifacts/prod002_detectcodegpt_c0_baseline.jsonl", encoding="utf-8"))}

confusion_rows = []
for lang in ["Python", "Java"]:
    rows_lang = [r for r in baseline if r["language"] == lang]
    # LLMSniffer: binary HUMAN/AI
    llm_conf = Counter()
    for r in rows_lang:
        true2 = provenance_binary(r["label"])
        pred2 = r["scores"]["LLMSniffer"]["predicted_label"]
        llm_conf[(true2, pred2)] += 1
    n = len(rows_lang)
    acc = sum(v for k, v in llm_conf.items() if k[0] == k[1]) / n if n else 0
    majority = max(Counter(provenance_binary(r["label"]) for r in rows_lang).values()) / n if n else 0
    print(f"\nLLMSniffer {lang} (n={n}): accuracy={acc:.3f}, majority-class baseline={majority:.3f}")
    for k in sorted(llm_conf):
        print(f"  true={k[0]:6s} pred={k[1]:6s}: {llm_conf[k]}")
    confusion_rows.append(["LLMSniffer", lang, n, acc, majority, dict(llm_conf)])

    # DroidDetect-Base: 2-class collapse (using existing predicted_label_mapped)
    droid_conf = Counter()
    for r in rows_lang:
        true2 = provenance_binary(r["label"])
        pred4 = r["scores"]["DroidDetect-Base"]["predicted_label_mapped"]
        pred2 = provenance_binary(pred4)
        droid_conf[(true2, pred2)] += 1
    acc_d = sum(v for k, v in droid_conf.items() if k[0] == k[1]) / n if n else 0
    print(f"\nDroidDetect-Base {lang} (n={n}, 2-class): accuracy={acc_d:.3f}, majority-class baseline={majority:.3f}")
    for k in sorted(droid_conf):
        print(f"  true={k[0]:6s} pred={k[1]:6s}: {droid_conf[k]}")
    confusion_rows.append(["DroidDetect-Base", lang, n, acc_d, majority, dict(droid_conf)])

    # DetectCodeGPT
    dcg_conf = Counter()
    dcg_rows_lang = [dcg_baseline[r["sample_id"]] for r in rows_lang if r["sample_id"] in dcg_baseline]
    for r in dcg_rows_lang:
        true2 = provenance_binary(r["label"])
        pred2 = r["pred0"]
        dcg_conf[(true2, pred2)] += 1
    n_dcg = len(dcg_rows_lang)
    acc_dcg = sum(v for k, v in dcg_conf.items() if k[0] == k[1]) / n_dcg if n_dcg else 0
    print(f"\nDetectCodeGPT {lang} (n={n_dcg}): accuracy={acc_dcg:.3f}")
    for k in sorted(dcg_conf):
        print(f"  true={k[0]:6s} pred={k[1]:6s}: {dcg_conf[k]}")
    confusion_rows.append(["DetectCodeGPT", lang, n_dcg, acc_dcg, None, dict(dcg_conf)])

with open("artifacts/final_tables/table7_baseline_confusion.csv", "w") as f:
    f.write("detector,language,n,accuracy,majority_class_baseline,confusion\n")
    for row in confusion_rows:
        f.write(f"{row[0]},{row[1]},{row[2]},{row[3]:.4f},{row[4] if row[4] is not None else ''},\"{row[5]}\"\n")

# ============================================================================
# W4: flip-direction-by-true-class, formatting family, baseline-correct
# ============================================================================
print("\n" + "=" * 70)
print("W4: FLIP DIRECTION BY TRUE CLASS (formatting family, baseline-correct)")
print("=" * 70)

all_scores = [json.loads(l) for l in open("artifacts/prod002_detector_scores.jsonl", encoding="utf-8")]
droid_2class = [json.loads(l) for l in open("artifacts/prod001_droiddetect_2class_reclassified.jsonl", encoding="utf-8")]

flip_dir_rows = []

# LLMSniffer + DetectCodeGPT: derive decision0/decisionT from s0/sT and known thresholds
THRESH = {"LLMSniffer": 0.5, "DetectCodeGPT": 2.931085010288198}
for det in ["LLMSniffer", "DetectCodeGPT"]:
    rows = [r for r in all_scores if r["detector"] == det and r["transformation_family"] == "formatting" and r.get("baseline_correct") and r.get("flip")]
    dir_counts = Counter()
    for r in rows:
        true2 = provenance_binary(r["label"])
        d0 = "AI" if r["s0"] > THRESH[det] else "HUMAN"
        dT = "AI" if r["sT"] > THRESH[det] else "HUMAN"
        direction = f"{d0}->{dT}"
        dir_counts[(true2, direction)] += 1
    print(f"\n{det} formatting flips among baseline-correct (n_flips={len(rows)}):")
    for k in sorted(dir_counts):
        print(f"  true_class={k[0]:6s} flip_direction={k[1]:12s}: {dir_counts[k]}")
    false_accusation = sum(v for k, v in dir_counts.items() if k[1] == "HUMAN->AI")
    evasion = sum(v for k, v in dir_counts.items() if k[1] == "AI->HUMAN")
    flip_dir_rows.append([det, len(rows), false_accusation, evasion, dict(dir_counts)])

# DroidDetect-Base: already have 2-class flip direction potential from reclassified file
droid_fmt = [r for r in droid_2class if r["transformation_family"] == "formatting" and r["baseline_correct_2class"] and r["flip_2class"]]
dir_counts_droid = Counter()
for r in droid_fmt:
    true2 = provenance_binary(r["label"])
    pred0_2 = provenance_binary(r["baseline_pred_4class"])
    predT_2 = provenance_binary(r["transformed_pred_4class"])
    direction = f"{pred0_2}->{predT_2}"
    dir_counts_droid[(true2, direction)] += 1
print(f"\nDroidDetect-Base formatting flips among baseline-correct (2-class, n_flips={len(droid_fmt)}):")
for k in sorted(dir_counts_droid):
    print(f"  true_class={k[0]:6s} flip_direction={k[1]:12s}: {dir_counts_droid[k]}")
false_accusation_d = sum(v for k, v in dir_counts_droid.items() if k[1] == "HUMAN->AI")
evasion_d = sum(v for k, v in dir_counts_droid.items() if k[1] == "AI->HUMAN")
flip_dir_rows.append(["DroidDetect-Base", len(droid_fmt), false_accusation_d, evasion_d, dict(dir_counts_droid)])

with open("artifacts/final_tables/table8_flip_direction.csv", "w") as f:
    f.write("detector,n_flips_formatting_baseline_correct,human_to_ai_false_accusation,ai_to_human_evasion,detail\n")
    for row in flip_dir_rows:
        f.write(f"{row[0]},{row[1]},{row[2]},{row[3]},\"{row[4]}\"\n")

# ============================================================================
# W5: canonicalized absolute score levels (saturation check)
# ============================================================================
print("\n" + "=" * 70)
print("W5: CANONICALIZED SCORE SATURATION CHECK (residual pairs, F(C0)/F(T(C0)))")
print("=" * 70)

llm_droid_residual = [json.loads(l) for l in open("artifacts/prod004_residual_scores_llm_droid.jsonl", encoding="utf-8")]
dcg_residual = [json.loads(l) for l in open("artifacts/prod004_residual_scores_detectcodegpt.jsonl", encoding="utf-8")]

sat_rows = []
for det in ["LLMSniffer", "DroidDetect-Base"]:
    s0s = [r[f"{det}_s0"] for r in llm_droid_residual]
    sTs = [r[f"{det}_sT"] for r in llm_droid_residual]
    all_canon = s0s + sTs
    mean_c = statistics.mean(all_canon)
    near0 = sum(1 for v in all_canon if v < 0.05) / len(all_canon)
    near1 = sum(1 for v in all_canon if v > 0.95) / len(all_canon)
    print(f"{det}: mean canonicalized score={mean_c:.3f}, frac<0.05={near0:.3f}, frac>0.95={near1:.3f}, n={len(all_canon)}")
    sat_rows.append([det, mean_c, near0, near1, len(all_canon)])

dcg_s0s = [r["DetectCodeGPT_s0"] for r in dcg_residual]
dcg_sTs = [r["DetectCodeGPT_sT"] for r in dcg_residual]
dcg_all = dcg_s0s + dcg_sTs
mean_dcg = statistics.mean(dcg_all)
frac_above_thresh = sum(1 for v in dcg_all if v > THRESH["DetectCodeGPT"]) / len(dcg_all)
print(f"DetectCodeGPT: mean canonicalized score={mean_dcg:.3f}, frac>threshold({THRESH['DetectCodeGPT']:.2f})={frac_above_thresh:.3f}, n={len(dcg_all)}")
sat_rows.append(["DetectCodeGPT", mean_dcg, frac_above_thresh, None, len(dcg_all)])

with open("artifacts/final_tables/table9_canonicalized_saturation.csv", "w") as f:
    f.write("detector,mean_canonicalized_score,frac_near_0_or_below_thresh,frac_near_1,n\n")
    for row in sat_rows:
        f.write(",".join(str(x) if x is not None else "" for x in row) + "\n")

# ============================================================================
# W7: distance vs |delta| correlation
# ============================================================================
print("\n" + "=" * 70)
print("W7: SPEARMAN CORRELATION, DISTANCE vs |delta_score| (confirmatory families)")
print("=" * 70)

corr_rows = []
for det in ["LLMSniffer", "DroidDetect-Base", "DetectCodeGPT"]:
    rows = [r for r in all_scores if r["detector"] == det and r.get("delta_score") is not None
            and r.get("d_text") is not None and r.get("d_token") is not None and r.get("d_ast") is not None]
    abs_delta = [abs(r["delta_score"]) for r in rows]
    d_text = [r["d_text"] for r in rows]
    d_token = [r["d_token"] for r in rows]
    d_ast = [r["d_ast"] for r in rows]
    rho_text = spearman(d_text, abs_delta)
    rho_token = spearman(d_token, abs_delta)
    rho_ast = spearman(d_ast, abs_delta)
    print(f"{det} (n={len(rows)}): rho(d_text)={rho_text:.3f}, rho(d_token)={rho_token:.3f}, rho(d_ast)={rho_ast:.3f}")
    corr_rows.append([det, len(rows), rho_text, rho_token, rho_ast])

with open("artifacts/final_tables/table10_distance_correlation.csv", "w") as f:
    f.write("detector,n,spearman_d_text,spearman_d_token,spearman_d_ast\n")
    for row in corr_rows:
        f.write(",".join(str(x) for x in row) + "\n")

print("\nAll tables written to artifacts/final_tables/table7-10_*.csv")
