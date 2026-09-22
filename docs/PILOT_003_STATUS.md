# PILOT_003

**Status: REVISE**

**Detector integration: PASS**
- LLMSniffer loaded correctly (checkpoint key match verified, strict load,
  90% accuracy on its own in-domain GPTSniffer Java test sanity set, n=20).
- DroidDetect-Base architecture reconstructed from checkpoint key names (no
  modeling code was published for this checkpoint); pooling strategy and
  label order empirically disambiguated against a Droid dev-split subset
  (n=24): both CLS and mean pooling reach 87.5% accuracy under the identity
  label permutation, confirming the reconstruction is very likely correct.

**Experimental sampling protocol: REVISE**
- Reason: the PILOT_002 C0 manifest was sampled from Droid's **train** split.
  DroidDetect-Base was (almost certainly) trained on that split, so its 100%
  `baseline_correct` rate across every (language x family) cell in
  `artifacts/pilot003_detector_scores.jsonl` reflects memorization, not
  generalization, and this may also distort `Delta_score` / eventual
  Minimum-Flip-Perturbation measurements (a memorized point can have an
  atypically large margin).
- Action: do not use these samples in the main decay analysis. Superseded by
  PILOT_004, which resamples C0 from a held-out split.

**Preserved as diagnostic evidence, not overwritten:**
- `artifacts/pilot003_detector_scores.jsonl`
- `artifacts/pilot003_detector_contracts.json`
- `artifacts/pilot003_c0_baseline.jsonl`
- `artifacts/pilot003_diagnostic_table.csv`

**Contract validation vs. experimental baseline performance (kept distinct
going forward, per methodology decision):**
- Contract validation answers "did we install/run the detector correctly?"
  -- LLMSniffer 90% / DroidDetect-Base 87.5%, both on curated sanity sets.
- Experimental baseline performance answers "how does this detector behave
  on our actual experimental distribution?" -- this is what PILOT_004's C0
  baseline measures, and it is expected to differ from the sanity numbers
  above (e.g. LLMSniffer's Java baseline_correct on Droid's Java samples was
  well below its 90% in-domain sanity accuracy -- a real distributional
  finding, not a bug).
