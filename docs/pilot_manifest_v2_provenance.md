# PILOT_004 C0 manifest provenance

- dataset: project-droid/DroidCollection
- split used: **test**
- test split used directly, no fallback needed
- seed: 20260920
- n samples: 30
- rationale: held out from Droid's train split specifically to avoid the train/test contamination found in PILOT_003 for DroidDetect-Base, which was trained on DroidCollection (train split almost certainly included).
