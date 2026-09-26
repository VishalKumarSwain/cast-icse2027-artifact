"""DetectCodeGPT with SHARED perturbation seeds across C0 and T(C0) (review response).

The original scoring (detectcodegpt.py) draws perturbation positions from
random.Random(hash((seed, code))) and samples mask fills from torch's unseeded global
RNG, so C0 and T(C0) receive independent perturbation randomness, and Python's
per-process string hashing makes even a repeated run irreproducible. Here both sources
of randomness are keyed on (seed, sample_id) with a stable hash, so C0 and T(C0) of the
same program are scored under the same perturbation randomness, and a run is
reproducible.

Usage: python scripts/detectcodegpt_shared_seed.py --seed 111 --out artifacts/prod007_dcg_shared_seed_111.jsonl
Scores every C0 program and every successful PROD_001 transformation (frozen K=50,
frozen threshold). Run with two different --seed values: the seed-to-seed change in
C0 scores is a test-set noise floor, and a transformation effect that is real should
reproduce across seeds.
"""
import argparse
import functools
import hashlib
import json
import random
import sys
import time

import torch

sys.path.insert(0, "scripts")
from detectcodegpt import DetectCodeGPTDetector

print = functools.partial(print, flush=True)

CHOSEN_K = 50
FROZEN_THRESHOLD = 2.931085010288198


def stable_int(*parts):
    h = hashlib.sha256("|".join(str(p) for p in parts).encode()).hexdigest()
    return int(h[:8], 16)


class SharedSeedDetector(DetectCodeGPTDetector):
    def perturb_keyed(self, code, key, n=CHOSEN_K):
        s = stable_int(self.seed, key)
        rng = random.Random(s)
        variants = self._build_masked_variants(code, n, rng)
        torch.manual_seed(s)
        torch.cuda.manual_seed_all(s)
        try:
            return self._batch_fill_masks(variants)
        except Exception:
            return [code] * n


def pred(score):
    if score is None:
        return None
    return "AI" if score > FROZEN_THRESHOLD else "HUMAN"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--limit", type=int, default=0, help="score only the first N programs (smoke test)")
    ap.add_argument("--families", default="formatting,lexical_rename,control_flow",
                    help="comma-separated transformation families to score alongside C0")
    a = ap.parse_args()

    det = SharedSeedDetector(seed=a.seed)
    manifest = [json.loads(l) for l in open("artifacts/pilot_manifest_prod001.jsonl", encoding="utf-8")]
    tlog = [json.loads(l) for l in open("artifacts/prod001_transform_log.jsonl", encoding="utf-8")]
    succ = {}
    for r in tlog:
        if r["status"] == "SUCCESS":
            succ.setdefault(r["sample_id"], []).append(r)
    if a.limit:
        manifest = manifest[: a.limit]

    fams = set(a.families.split(","))
    import os
    done = set()
    if os.path.exists(a.out):
        for l in open(a.out):
            try:
                done.add(json.loads(l)["sample_id"])
            except Exception:
                pass
    t_start = time.time()
    with open(a.out, "a") as f:
        for n, row in enumerate(manifest):
            sid = row["sample_id"]
            if sid in done:
                continue
            prov = "HUMAN" if row["label"] == "HUMAN_GENERATED" else "AI"
            lines = []
            s0 = det.score_at_k(row["code"], det.perturb_keyed(row["code"], sid), CHOSEN_K)
            lines.append({"kind": "c0", "seed": a.seed, "sample_id": sid, "language": row["language"],
                          "label": row["label"], "provenance": prov, "s": s0})
            for t in succ.get(sid, []):
                if t["transformation_family"] not in fams:
                    continue
                code_t = open(t["output_path"], encoding="utf-8").read()
                sT = det.score_at_k(code_t, det.perturb_keyed(code_t, sid), CHOSEN_K)
                lines.append({"kind": "transformed", "seed": a.seed, "sample_id": sid,
                              "language": row["language"], "label": row["label"], "provenance": prov,
                              "transformation_family": t["transformation_family"], "s": sT,
                              "d_text": t.get("d_text"), "d_token": t.get("d_token"), "d_ast": t.get("d_ast")})
            for ln in lines:
                f.write(json.dumps(ln) + "\n")
            f.flush()
            torch.cuda.empty_cache()
            print(f"seed={a.seed} {n + 1}/{len(manifest)} sid={sid} elapsed={time.time() - t_start:.0f}s")
    print("done")


if __name__ == "__main__":
    main()
