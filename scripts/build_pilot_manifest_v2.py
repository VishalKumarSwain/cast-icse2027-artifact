"""PILOT_004: rebuild C0 manifest from a held-out Droid split (test preferred,
dev as documented fallback), to avoid the train-split contamination found in
PILOT_003 for DroidDetect-Base. Same stratification logic as PILOT_002's
manifest builder, just parameterized on split and re-seeded so sample_ids
cannot collide with the PILOT_002 (train-split) manifest.

Adds explicit provenance fields required going forward: dataset,
dataset_version, dataset_split, sample_id.
"""
import hashlib
import json
import random

from datasets import load_dataset, DownloadConfig

SEED = 20260920  # distinct from PILOT_002's seed (20260919) -- different draw, same method
LANGUAGES = ["Python", "Java"]
TARGET_PER_LANGUAGE = 15
LABELS_WANTED = ["HUMAN_GENERATED", "MACHINE_GENERATED", "MACHINE_REFINED"]
DATASET_NAME = "project-droid/DroidCollection"
DATASET_VERSION = "commit unknown at audit time (2026-09-19); see docs/droid_audit.json for schema snapshot"


def sample_id_for(row, idx, split):
    h = hashlib.sha256(f"{split}|{row['Source']}|{row['Language']}|{row['Label']}|{idx}|{row['Code'][:200]}".encode()).hexdigest()[:12]
    return f"c0_{split}_{h}"


def try_build(split):
    rng = random.Random(SEED)
    dl_config = DownloadConfig(cache_dir="data/hf_cache")
    ds = load_dataset(DATASET_NAME, split=split, download_config=dl_config)

    if not len(ds):
        return None, f"split '{split}' is empty"
    if "Label" not in ds.column_names or "Language" not in ds.column_names:
        return None, f"split '{split}' missing required columns"

    manifest = []
    for lang in LANGUAGES:
        lang_rows = ds.filter(lambda r: r["Language"] == lang and r["Label"] in LABELS_WANTED, num_proc=4)
        by_label = {lbl: [] for lbl in LABELS_WANTED}
        for i, row in enumerate(lang_rows):
            by_label[row["Label"]].append(i)

        if any(len(v) == 0 for v in by_label.values()):
            return None, f"split '{split}' language '{lang}' missing at least one wanted label entirely"

        per_label_target = max(1, TARGET_PER_LANGUAGE // len(LABELS_WANTED))
        chosen_indices = []
        for lbl, idxs in by_label.items():
            rng.shuffle(idxs)
            chosen_indices.extend(idxs[:per_label_target])

        for idx in chosen_indices:
            row = lang_rows[idx]
            sid = sample_id_for(row, idx, split)
            manifest.append(
                {
                    "sample_id": sid,
                    "dataset": DATASET_NAME,
                    "dataset_version": DATASET_VERSION,
                    "dataset_split": split,
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
    return manifest, None


def main():
    manifest, err = try_build("test")
    used_split = "test"
    fallback_reason = None
    if manifest is None:
        fallback_reason = f"test split unusable ({err}); falling back to dev split"
        print(fallback_reason)
        manifest, err2 = try_build("dev")
        used_split = "dev"
        if manifest is None:
            raise RuntimeError(f"dev split also unusable: {err2}")

    with open("artifacts/pilot_manifest_v2.jsonl", "w", encoding="utf-8") as f:
        for row in manifest:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    with open("docs/pilot_manifest_v2_provenance.md", "w") as f:
        f.write(f"# PILOT_004 C0 manifest provenance\n\n")
        f.write(f"- dataset: {DATASET_NAME}\n")
        f.write(f"- split used: **{used_split}**\n")
        if fallback_reason:
            f.write(f"- fallback reason: {fallback_reason}\n")
        else:
            f.write(f"- test split used directly, no fallback needed\n")
        f.write(f"- seed: {SEED}\n")
        f.write(f"- n samples: {len(manifest)}\n")
        f.write(f"- rationale: held out from Droid's train split specifically to avoid the "
                f"train/test contamination found in PILOT_003 for DroidDetect-Base, which was "
                f"trained on DroidCollection (train split almost certainly included).\n")

    print(f"wrote {len(manifest)} C0 seeds from split='{used_split}' to artifacts/pilot_manifest_v2.jsonl")
    by_lang_label = {}
    for row in manifest:
        key = (row["language"], row["label"])
        by_lang_label[key] = by_lang_label.get(key, 0) + 1
    for k, v in sorted(by_lang_label.items()):
        print(k, v)


if __name__ == "__main__":
    main()
