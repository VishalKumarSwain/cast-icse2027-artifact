"""Formal significance test for the central asymmetry claim in Section 4.1 of
the paper: DroidDetect-Base's human-to-AI formatting flip rate (58.0%, 29/50)
versus its AI-to-human messify flip rate (5.2%, 5/96).

These are two independent samples (different, non-overlapping sets of
programs: baseline-correct HUMAN_GENERATED formatting pairs vs. baseline-
correct AI-class messify pairs), not a paired before/after design on the same
subjects, so McNemar's test does not apply. We use Fisher's exact test on the
resulting 2x2 contingency table, which is exact (not an approximation) and
appropriate regardless of the small cell counts involved.

Reads only frozen artifacts already produced by earlier scripts:
  - artifacts/prod001_droiddetect_2class_reclassified.jsonl (human-to-AI side)
  - artifacts/prod005_messify_ai_to_human.jsonl (AI-to-human side)
No GPU or model access required.
"""
import json

from scipy.stats import fisher_exact


def main():
    # Human-to-AI side: formatting family, HUMAN_GENERATED, baseline-correct (2-class)
    reclass_rows = [json.loads(l) for l in open("artifacts/prod001_droiddetect_2class_reclassified.jsonl", encoding="utf-8")]
    human_fmt = [
        r for r in reclass_rows
        if r["transformation_family"] == "formatting"
        and r["label"] == "HUMAN_GENERATED"
        and r["baseline_correct_2class"]
    ]
    human_n = len(human_fmt)
    human_flipped = sum(1 for r in human_fmt if r["flip_among_baseline_correct_2class"])
    human_not_flipped = human_n - human_flipped

    # AI-to-human side: messify experiment, baseline-correct AI-class pairs
    messify_rows = [json.loads(l) for l in open("artifacts/prod005_messify_ai_to_human.jsonl", encoding="utf-8")]
    ai_n = len(messify_rows)
    ai_flipped = sum(1 for r in messify_rows if r["flip_to_human"])
    ai_not_flipped = ai_n - ai_flipped

    table = [[human_flipped, human_not_flipped], [ai_flipped, ai_not_flipped]]
    odds_ratio, p_value = fisher_exact(table)

    print(f"Human-to-AI (formatting, HUMAN_GENERATED, baseline-correct): {human_flipped}/{human_n} = {human_flipped / human_n:.4f}")
    print(f"AI-to-human (messify, baseline-correct AI-class):            {ai_flipped}/{ai_n} = {ai_flipped / ai_n:.4f}")
    print(f"2x2 table: {table}")
    print(f"Fisher's exact test: odds ratio = {odds_ratio:.4f}, p = {p_value:.6e}")

    with open("artifacts/final_tables/table12_significance_test.csv", "w") as f:
        f.write("comparison,n,flipped,rate,odds_ratio,p_value\n")
        f.write(f"human_to_AI_formatting,{human_n},{human_flipped},{human_flipped / human_n},{odds_ratio},{p_value}\n")
        f.write(f"AI_to_human_messify,{ai_n},{ai_flipped},{ai_flipped / ai_n},{odds_ratio},{p_value}\n")

    print("Wrote artifacts/final_tables/table12_significance_test.csv")


if __name__ == "__main__":
    main()
