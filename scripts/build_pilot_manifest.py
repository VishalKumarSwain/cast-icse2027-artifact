"""PILOT_001: sample a small, reproducible C_0 manifest from DroidCollection.

Stratified across language (Python, Java) x provenance label x generator
family, fixed seed. Writes manifest as JSONL with immutable sample_id and
full provenance, plus the raw code, to data/pilot_manifest.jsonl.

This does not mutate anything in Droid; C_0 rows are copied out and treated
as immutable seeds for all downstream transformation stages.
"""
import hashlib
import json
import random

from datasets import load_dataset, DownloadConfig

SEED = 20260919
LANGUAGES = ["Python", "Java"]
TARGET_PER_LANGUAGE = 15  # ~15 x 2 = 30 total for the pilot
LABELS_WANTED = ["HUMAN_GENERATED", "MACHINE_GENERATED", "MACHINE_REFINED"]


def sample_id_for(row, idx):
    h = hashlib.sha256(f"{row['Source']}|{row['Language']}|{row['Label']}|{idx}|{row['Code'][:200]}".encode()).hexdigest()[:12]
    return f"c0_{h}"


def main():
    rng = random.Random(SEED)
    dl_config = DownloadConfig(cache_dir="data/hf_cache")
    ds = load_dataset("project-droid/DroidCollection", split="train", download_config=dl_config)

    manifest = []
    for lang in LANGUAGES:
        lang_rows = ds.filter(lambda r: r["Language"] == lang and r["Label"] in LABELS_WANTED, num_proc=4)
        by_label = {lbl: [] for lbl in LABELS_WANTED}
        for i, row in enumerate(lang_rows):
            by_label[row["Label"]].append(i)

        per_label_target = max(1, TARGET_PER_LANGUAGE // len(LABELS_WANTED))
        chosen_indices = []
        for lbl, idxs in by_label.items():
            rng.shuffle(idxs)
            chosen_indices.extend(idxs[:per_label_target])

        for idx in chosen_indices:
            row = lang_rows[idx]
            sid = sample_id_for(row, idx)
            manifest.append(
                {
                    "sample_id": sid,
                    "language": row["Language"],
                    "label": row["Label"],
                    "generator": row["Generator"],
                    "model_family": row["Model_Family"],
                    "source": row["Source"],
                    "generation_mode": row["Generation_Mode"],
                    "code": row["Code"],
                    "droid_split": "train",
                    "droid_row_index": idx,
                    "seed": SEED,
                }
            )

    with open("artifacts/pilot_manifest.jsonl", "w", encoding="utf-8") as f:
        for row in manifest:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"wrote {len(manifest)} C_0 seeds to artifacts/pilot_manifest.jsonl")
    by_lang_label = {}
    for row in manifest:
        key = (row["language"], row["label"])
        by_lang_label[key] = by_lang_label.get(key, 0) + 1
    for k, v in sorted(by_lang_label.items()):
        print(k, v)


if __name__ == "__main__":
    main()
