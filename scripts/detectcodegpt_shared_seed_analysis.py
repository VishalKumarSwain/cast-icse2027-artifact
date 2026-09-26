"""Analysis of the shared-seed DetectCodeGPT runs (scripts/detectcodegpt_shared_seed.py).

Reads artifacts/prod007_dcg_shared_seed_<seed>.jsonl for two seeds (default 111 and 222).
Reports:
  1. Test-set noise floor: C0 re-scored under a different seed (same input), on the
     199-program test corpus (the earlier control used 40 dev-split programs).
  2. Shared-seed transformation effect: for each formatting pair, delta = s(T(C0)) - s(C0)
     with both scored under the SAME seed; decision-flip rate among baseline-correct pairs.
  3. Reproducibility: correlation of the per-pair delta between the two seeds. A real
     transformation effect should reproduce across seeds; pure perturbation noise should not.
Writes artifacts/final_tables/table14_dcg_shared_seed.csv.
"""
import csv
import json
import math
import statistics
import sys

from scipy import stats

THRESH = 2.931085010288198


def load(seed):
    c0, tr = {}, {}
    for l in open(f"artifacts/prod007_dcg_shared_seed_{seed}.jsonl", encoding="utf-8"):
        d = json.loads(l)
        if d["s"] is None:
            continue
        if d["kind"] == "c0":
            c0[d["sample_id"]] = d
        else:
            tr[(d["sample_id"], d["transformation_family"])] = d
    return c0, tr


def pred(s):
    return "AI" if s > THRESH else "HUMAN"


def main(seeds=(111, 222)):
    a, b = seeds
    c0a, tra = load(a)
    c0b, trb = load(b)
    out = [("metric", "value")]

    # 1. test-set noise floor (same input, different seed)
    common = sorted(set(c0a) & set(c0b))
    d = [abs(c0a[k]["s"] - c0b[k]["s"]) for k in common]
    flips = [pred(c0a[k]["s"]) != pred(c0b[k]["s"]) for k in common]
    print(f"Noise floor on the test corpus (C0 under seed {a} vs {b}): n={len(common)}, "
          f"decision flips {sum(flips)}/{len(common)} = {sum(flips)/len(common):.3f}, "
          f"mean |delta| = {statistics.mean(d):.3f}, median = {statistics.median(d):.3f}")
    out += [("noise_n", len(common)), ("noise_flip_rate", sum(flips) / len(common)),
            ("noise_mean_abs_delta", statistics.mean(d)), ("noise_median_abs_delta", statistics.median(d))]

    # 2. shared-seed transformation effect, per seed
    def effects(c0, tr):
        rows = []
        for (sid, fam), t in tr.items():
            if sid not in c0:
                continue
            s0, sT = c0[sid]["s"], t["s"]
            prov = c0[sid]["provenance"]
            rows.append(dict(sid=sid, lang=t["language"], delta=sT - s0, s0=s0, sT=sT,
                             base_correct=(pred(s0) == prov), flip=(pred(s0) != pred(sT))))
        return rows

    ea, eb = effects(c0a, tra), effects(c0b, trb)
    for seed, e in ((a, ea), (b, eb)):
        bc = [r for r in e if r["base_correct"]]
        fl = sum(r["flip"] for r in bc)
        print(f"Shared seed {seed}: formatting pairs n={len(e)}, mean |delta| = "
              f"{statistics.mean(abs(r['delta']) for r in e):.3f}; IER among baseline-correct = {fl}/{len(bc)} = {fl/max(1,len(bc)):.3f}")
        out += [(f"shared_seed_{seed}_mean_abs_delta", statistics.mean(abs(r['delta']) for r in e)),
                (f"shared_seed_{seed}_IER", f"{fl}/{len(bc)}")]
        for lang in ("Python", "Java"):
            bcl = [r for r in bc if r["lang"] == lang]
            fll = sum(r["flip"] for r in bcl)
            if bcl:
                print(f"   {lang}: {fll}/{len(bcl)} = {fll/len(bcl):.3f}")
                out.append((f"shared_seed_{seed}_IER_{lang}", f"{fll}/{len(bcl)}"))

    # 3. reproducibility of the per-pair delta across seeds
    ia = {r["sid"]: r["delta"] for r in ea}
    ib = {r["sid"]: r["delta"] for r in eb}
    cs = sorted(set(ia) & set(ib))
    if len(cs) > 3:
        x = [ia[k] for k in cs]
        y = [ib[k] for k in cs]
        rho, p = stats.spearmanr(x, y)
        r_, pr = stats.pearsonr(x, y)
        agree = sum(1 for u, v in zip(x, y) if (u > 0) == (v > 0)) / len(cs)
        print(f"Reproducibility of per-pair delta across seeds (n={len(cs)}): Spearman rho = {rho:.2f} (p = {p:.2g}), "
              f"Pearson r = {r_:.2f}, sign agreement = {agree:.2f}")
        out += [("repro_n", len(cs)), ("repro_spearman", rho), ("repro_spearman_p", p), ("repro_pearson", r_), ("repro_sign_agreement", agree)]
        # same comparison for a noise-only reference: C0-vs-C0 differences are noise by construction
        print(f"Reference: mean |delta| across seeds on identical C0 input = {statistics.mean(d):.3f} "
              f"vs mean |delta| under shared seeds for formatting = "
              f"{statistics.mean([abs(v) for v in x]):.3f} (seed {a}), {statistics.mean([abs(v) for v in y]):.3f} (seed {b})")

    with open("artifacts/final_tables/table14_dcg_shared_seed.csv", "w", newline="") as f:
        csv.writer(f).writerows(out)
    print("Wrote artifacts/final_tables/table14_dcg_shared_seed.csv")


if __name__ == "__main__":
    main(tuple(int(x) for x in sys.argv[1:3]) if len(sys.argv) >= 3 else (111, 222))
