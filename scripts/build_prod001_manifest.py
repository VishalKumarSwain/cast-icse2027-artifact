"""PROD_001: build the 200-seed (100 Python + 100 Java) production manifest
from Droid's held-out test split, stratified across provenance label and,
for machine labels, across generator family. Disjoint from PILOT_004's
30-seed manifest (different seed, and explicitly checked for sample_id
collisions before writing).
"""
import hashlib
import json
import random

from datasets import load_dataset, DownloadConfig

SEED = 20260921  # distinct from PILOT_002 (20260919) and PILOT_004 (20260920)
LANGUAGES = ["Python", "Java"]
TARGET_PER_LANGUAGE = 100
LABELS_WANTED = ["HUMAN_GENERATED", "MACHINE_GENERATED", "MACHINE_REFINED"]
DATASET_NAME = "project-droid/DroidCollection"
SPLIT = "test"


def sample_id_for(row, idx, split):
    h = hashlib.sha256(f"{split}|{row['Source']}|{row['Language']}|{row['Label']}|{idx}|{row['Code'][:200]}".encode()).hexdigest()[:12]
    return f"c0_{split}_{h}"


def stratified_pick(rng, by_label, per_label_target):
    chosen = []
    for lbl, idxs in by_label.items():
        if lbl == "HUMAN_GENERATED":
            pool = list(idxs)
            rng.shuffle(pool)
            chosen.extend(pool[:per_label_target])
        else:
            pool = idxs  # dict: model_family -> list of indices
            families = list(pool.keys())
            rng.shuffle(families)
            per_family_target = max(1, per_label_target // max(1, len(families)))
            picked_for_label = []
            for fam in families:
                fam_idxs = list(pool[fam])
                rng.shuffle(fam_idxs)
                picked_for_label.extend(fam_idxs[:per_family_target])
            # top up if rounding left us short
            leftover_pool = [i for fam in families for i in pool[fam] if i not in picked_for_label]
            rng.shuffle(leftover_pool)
            while len(picked_for_label) < per_label_target and leftover_pool:
                picked_for_label.append(leftover_pool.pop())
            chosen.extend(picked_for_label[:per_label_target])
    return chosen


def main():
    rng = random.Random(SEED)
    dl_config = DownloadConfig(cache_dir="data/hf_cache")
    ds = load_dataset(DATASET_NAME, split=SPLIT, download_config=dl_config)

    pilot004_ids = {json.loads(l)["sample_id"] for l in open("artifacts/pilot_manifest_v2.jsonl", encoding="utf-8")}

    manifest = []
    per_label_target = TARGET_PER_LANGUAGE // len(LABELS_WANTED)
    for lang in LANGUAGES:
        lang_rows = ds.filter(lambda r: r["Language"] == lang and r["Label"] in LABELS_WANTED, num_proc=4)

        by_label = {"HUMAN_GENERATED": []}
        by_label["MACHINE_GENERATED"] = {}
        by_label["MACHINE_REFINED"] = {}
        for i, row in enumerate(lang_rows):
            lbl = row["Label"]
            if lbl == "HUMAN_GENERATED":
                by_label[lbl].append(i)
            else:
                by_label[lbl].setdefault(row["Model_Family"], []).append(i)

        chosen_indices = stratified_pick(rng, by_label, per_label_target)
        # top up to exactly TARGET_PER_LANGUAGE if stratification left a gap
        if len(chosen_indices) < TARGET_PER_LANGUAGE:
            all_idxs = set(range(len(lang_rows)))
            remaining = list(all_idxs - set(chosen_indices))
            rng.shuffle(remaining)
            chosen_indices.extend(remaining[: TARGET_PER_LANGUAGE - len(chosen_indices)])

        for idx in chosen_indices[:TARGET_PER_LANGUAGE]:
            row = lang_rows[idx]
            sid = sample_id_for(row, idx, SPLIT)
            if sid in pilot004_ids:
                continue  # guard against accidental overlap with PILOT_004
            manifest.append(
                {
                    "sample_id": sid,
                    "dataset": DATASET_NAME,
                    "dataset_split": SPLIT,
                    "language": row["Language"],
                    "label": row["Label"],
                    "generator": row["Generator"],
                    "model_family": row["Model_Family"],
                    "source": row["Source"],
                    "generation_mode": row["Generation_Mode"],
                    "code": row["Code"],
                    "droid_row_index": idx,
                    "seed": SEED,
                }
            )

    overlap = pilot004_ids & {r["sample_id"] for r in manifest}
    assert not overlap, f"unexpected overlap with PILOT_004 manifest: {overlap}"

    with open("artifacts/pilot_manifest_prod001.jsonl", "w", encoding="utf-8") as f:
        for row in manifest:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    with open("docs/pilot_manifest_prod001_provenance.md", "w") as f:
        f.write("# PROD_001 C0 manifest provenance\n\n")
        f.write(f"- dataset: {DATASET_NAME}\n- split: {SPLIT}\n- seed: {SEED}\n")
        f.write(f"- n samples: {len(manifest)}\n")
        f.write("- disjoint from PILOT_004's 30-seed manifest (checked, 0 overlap)\n")

    print(f"wrote {len(manifest)} C0 seeds to artifacts/pilot_manifest_prod001.jsonl")
    counts = {}
    for row in manifest:
        key = (row["language"], row["label"])
        counts[key] = counts.get(key, 0) + 1
    for k, v in sorted(counts.items()):
        print(k, v)

    fam_counts = {}
    for row in manifest:
        if row["label"] != "HUMAN_GENERATED":
            key = (row["language"], row["label"], row["model_family"])
            fam_counts[key] = fam_counts.get(key, 0) + 1
    print("\nGenerator-family stratification:")
    for k, v in sorted(fam_counts.items()):
        print(k, v)


if __name__ == "__main__":
    main()
