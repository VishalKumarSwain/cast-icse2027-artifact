"""Phase 0 audit of DroidCollection: schema, language/provenance counts,
license fields, and test/problem-id availability. Read-only, no torch needed.
"""
import json
from collections import Counter

from datasets import load_dataset, DownloadConfig


def main():
    dl_config = DownloadConfig(cache_dir="data/hf_cache")
    ds = load_dataset("project-droid/DroidCollection", download_config=dl_config)

    report = {"splits": {k: len(v) for k, v in ds.items()}}

    train = ds["train"] if "train" in ds else next(iter(ds.values()))
    report["columns"] = train.column_names
    report["features"] = {k: str(v) for k, v in train.features.items()}

    sample_n = min(50000, len(train))
    sample = train.select(range(sample_n))

    if "Language" in sample.column_names:
        report["language_counts_sample"] = dict(Counter(sample["Language"]))
    if "Label" in sample.column_names:
        report["label_counts_sample"] = dict(Counter(sample["Label"]))
    if "Source" in sample.column_names:
        report["source_counts_sample"] = dict(Counter(sample["Source"]))
    if "Model_Family" in sample.column_names:
        report["model_family_counts_sample"] = dict(Counter(sample["Model_Family"]))

    # Look at one example row per label to inspect whether problem/test fields exist
    report["example_rows"] = {}
    if "Label" in train.column_names:
        seen_labels = set()
        for row in train:
            lbl = row.get("Label")
            if lbl not in seen_labels:
                seen_labels.add(lbl)
                trimmed = {k: (v[:300] if isinstance(v, str) else v) for k, v in row.items()}
                report["example_rows"][str(lbl)] = trimmed
            if len(seen_labels) >= 4:
                break

    with open("docs/droid_audit.json", "w") as f:
        json.dump(report, f, indent=2, default=str)

    print(json.dumps({k: v for k, v in report.items() if k != "example_rows"}, indent=2, default=str))
    print("\nFull report (incl. example rows) written to docs/droid_audit.json")


if __name__ == "__main__":
    main()
