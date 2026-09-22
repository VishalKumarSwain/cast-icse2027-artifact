"""Identity-transformation control for DetectCodeGPT, per the reviewer's
concern that its perturbations (space/newline insertions) make re-scoring the
SAME code with a different random seed give a different score, so its
"diffuse, family-independent instability" (Section IV-A) needs a measured
noise floor before it can be told apart from re-scoring noise.

DetectCodeGPT's perturbation positions are seeded by hash((self.seed, code)),
so re-instantiating the detector with a different seed and re-scoring the
IDENTICAL code (no transformation at all) isolates exactly this noise source.

Reuses the frozen 40-sample dev-split calibration set (docs/
DETECTCODEGPT_CALIBRATION_RESULTS.md) rather than the held-out test split,
so the confirmatory PROD_002 test-split results stay untouched by this
diagnostic. build_calibration_sample() is deterministic (same dev-split
iteration order), so re-running it reproduces the same 40 rows in the same
order as artifacts/detectcodegpt_calibration_scores.jsonl.
"""
import json
import sys

sys.path.insert(0, "scripts")
from detectcodegpt_calibration import build_calibration_sample, CHOSEN_K
from detectcodegpt import DetectCodeGPTDetector

FROZEN_THRESHOLD = 2.931085010288198
IDENTITY_SEED = 13371337  # any value different from the frozen seed=20260922


def main():
    rows = build_calibration_sample()
    original = [json.loads(l) for l in open("artifacts/detectcodegpt_calibration_scores.jsonl", encoding="utf-8")]
    assert len(rows) == len(original), f"calibration set size drifted: {len(rows)} vs {len(original)}"

    det = DetectCodeGPTDetector(seed=IDENTITY_SEED)

    out_rows = []
    for n, (row, orig) in enumerate(zip(rows, original)):
        code = row["Code"]
        lang = row["Language"]
        perturbations = det.generate_perturbations(code, n=CHOSEN_K)
        s_fresh = det.score_at_k(code, perturbations, CHOSEN_K)
        s0 = orig["score"]
        decision0 = s0 > FROZEN_THRESHOLD
        decision_fresh = s_fresh > FROZEN_THRESHOLD
        out_rows.append({
            "label": orig["label"],
            "binary_label": orig["binary_label"],
            "language": orig["language"],
            "s0_original_seed": s0,
            "s_fresh_seed": s_fresh,
            "delta": s_fresh - s0,
            "decision0": decision0,
            "decision_fresh": decision_fresh,
            "flip_noop": decision0 != decision_fresh,
        })
        print(f"...{n + 1}/{len(rows)} delta={s_fresh - s0:.3f} flip={decision0 != decision_fresh}", flush=True)

    with open("artifacts/detectcodegpt_identity_control.jsonl", "w") as f:
        for r in out_rows:
            f.write(json.dumps(r, default=str) + "\n")

    n_total = len(out_rows)
    n_flips = sum(1 for r in out_rows if r["flip_noop"])
    deltas = [abs(r["delta"]) for r in out_rows]
    mean_abs_delta = sum(deltas) / len(deltas)
    median_abs_delta = sorted(deltas)[len(deltas) // 2]

    print(f"\nIdentity-control (no-op, fresh seed) results over n={n_total} dev-split calibration samples:")
    print(f"  Decision-flip rate on identical input: {n_flips}/{n_total} = {n_flips / n_total:.3f}")
    print(f"  Mean |delta| (re-scoring noise): {mean_abs_delta:.3f}")
    print(f"  Median |delta|: {median_abs_delta:.3f}")

    with open("artifacts/final_tables/table6_detectcodegpt_identity_control.csv", "w") as f:
        f.write("n,decision_flip_rate,mean_abs_delta,median_abs_delta\n")
        f.write(f"{n_total},{n_flips / n_total},{mean_abs_delta},{median_abs_delta}\n")

    print("Wrote artifacts/detectcodegpt_identity_control.jsonl and artifacts/final_tables/table6_detectcodegpt_identity_control.csv")


if __name__ == "__main__":
    main()
