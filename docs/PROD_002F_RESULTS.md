# PROD_002F: Cross-Detector Forensics -- Results

Pure analysis of PROD_002's frozen data (`artifacts/prod002_detector_scores.jsonl`).
No transformations, detector contracts, thresholds, or distance definitions
were touched. Script: `scripts/prod002f_forensics.py`.

## 1. Within-detector distribution shape: three genuinely different patterns

| Detector | median\|Δ\| | p75 | p90 | max | spikiness (max/median) | Pattern |
|---|---|---|---|---|---|---|
| DroidDetect-Base | 0.0055 | 0.107 | 0.704 | 1.000 | **182.7** | **A -- localized: near-zero majority, rare huge swings** |
| LLMSniffer | 0.0106 | 0.022 | 0.042 | 0.215 | 20.3 | A-shaped but **tiny in absolute terms** -- see caveat below |
| DetectCodeGPT | 0.4779 | 0.886 | 1.394 | 3.974 | 8.3 | **B -- diffuse: moderate-to-large movement is the norm, not the exception** |

**Important nuance on LLMSniffer**: its spikiness ratio (20.3) crosses the
same numeric threshold as DroidDetect-Base's, but the absolute scale is
utterly different -- LLMSniffer's "huge swing" (max=0.215) is smaller than
DroidDetect-Base's *median* swing in its most affected cell. LLMSniffer is
not exhibiting DroidDetect-Base's phenomenon at a smaller scale; it is
essentially stable, full stop, with a handful of slightly-larger-than-usual
(but still small) movements. This is exactly the normalization the
pre-registration insisted on: absolute cross-detector delta comparison would
have been misleading here.

**DetectCodeGPT's median|Δ| of 0.48 is itself the finding**: this detector
does not have a "quiet majority" the way the other two do. Score movement
under transformation is the typical case, not a rare event, for this
detector -- textbook Pattern B (diffuse sensitivity), not Pattern A.

## 2. Detector-relative signature region (small d_text/d_token/d_ast, |Δ| >= 2x that detector's own p75)

| Detector | Signature rows | Dominant family | Notable |
|---|---|---|---|
| DroidDetect-Base | 36/365 | Python formatting | Matches PILOT_004/PROD_001 exactly |
| LLMSniffer | 13/365 | Python/Java formatting | **Substantial sample-ID overlap with DroidDetect-Base's list** (see below) |
| DetectCodeGPT | 5/365 | Java lexical_rename/formatting | **No sample-ID overlap** with the other two; requires much larger d_text (up to 388) to register |

**The LLMSniffer/DroidDetect-Base overlap is a new finding, not previously
visible in the IER table.** Several of the exact same sample_ids
(`c0_test_42acb918f0f9`, `c0_test_b4c24e630f64`, `c0_test_b4eda3245609`,
`c0_test_47d1cf7a81ff`, `c0_test_7f5026014142`, ...) appear in *both*
detectors' signature-region lists. That is: the same specific tiny cosmetic
edits are each detector's *most-affected* cases, proportionally -- but
DroidDetect-Base's reaction is a near-total collapse (Δ up to -1.00) while
LLMSniffer's reaction to the identical edit is a small nudge (Δ around
0.05-0.16). This suggests these specific transformations carry some
model-agnostic signal that both architectures register, just at wildly
different sensitivity -- not that LLMSniffer is immune to what
DroidDetect-Base reacts to.

DetectCodeGPT's signature cases are a disjoint set of samples requiring much
larger textual change to register as unusual for it -- consistent with its
diffuse (Pattern B) character: it doesn't have a hair-trigger response to
near-zero edits the way DroidDetect-Base does.

## 3. Threshold-margin analysis for flips (LLMSniffer @0.5, DetectCodeGPT @2.931)

DroidDetect-Base excluded -- no scalar margin is stored for its multiclass
argmax decision in the joined score rows (noted as a limitation, not
silently skipped).

| Detector | Total flips | Near-boundary (Pattern C candidates) | Far-from-boundary | Near-boundary flips' typical \|Δ\| |
|---|---|---|---|---|
| LLMSniffer | 34 | 31 (91%) | 3 (9%) | **tiny** (median ~0.02-0.03, nearly all <0.05) |
| DetectCodeGPT | 81 | 68 (84%) | 13 (16%) | **large** (median ~0.5-0.6, many >1.0, up to 2.7) |

**This is the sharpest distinction in the whole analysis.** Both detectors
have most of their flips classified as "near-boundary" by the margin
criterion -- but that label means something completely different for each:

- **LLMSniffer's near-boundary flips are genuine threshold/calibration noise
  (Pattern C)**: s0 sits within ~0.01-0.05 of 0.5, and the score barely moves
  (|Δ| typically 0.01-0.08) to cross it. This is exactly "C0=0.499, T=0.511"
  -- a coin landing on the other side, not a substantive reaction to the
  transformation.
- **DetectCodeGPT's near-boundary flips are NOT threshold noise despite the
  label**: even when s0 happens to sit closer to 2.931 than typical, the
  actual score movement causing the flip is large in absolute terms (0.3-1.5+,
  comparable to or larger than its typical movement overall). DetectCodeGPT's
  threshold sits in the middle of a score distribution that moves a lot
  regardless of where the threshold is -- so many of its flips are "large
  real movement that happened to cross an arbitrarily-placed boundary,"
  not "tiny real movement that happened to be near the boundary."

## Synthesis

Three detectors, three different failure/stability modes -- not one
phenomenon at different scales:

1. **LLMSniffer**: genuinely stable. Its rare flips are calibration noise on
   already-uncertain samples (Pattern C), and even its "signature region"
   outliers are objectively small movements.
2. **DroidDetect-Base**: localized, substantive fragility (Pattern A) --
   most samples nearly untouched, a specific minority (concentrated in
   Python/Java formatting) collapse almost completely. This replicates
   PILOT_004/PROD_001 and is not a calibration artifact.
3. **DetectCodeGPT**: diffuse, substantive instability (Pattern B) -- score
   movement under transformation is typical, not exceptional, for this
   detector, and its flips reflect real large-magnitude score movement, not
   threshold jitter, despite weak (60%) calibration accuracy. Its weakness
   is a genuinely different phenomenon from DroidDetect-Base's, concentrated
   more in control_flow/lexical_rename than formatting specifically.

**Revised RQ4 conclusion**: "different detector architectures possess
distinct transformation-specific fragility profiles" (the stronger
alternative framing from the PROD_002 write-up) is the better-supported
reading, now with forensic detail: one detector is stable, one fails
sharply and locally on a specific transformation, and one fails broadly and
diffusely across transformations -- three qualitatively different reliability
profiles from three architectures on the identical corpus and identical
transformations.

## Exploratory note: what do the overlapping samples have in common?

Labeled explicitly as exploratory -- inspection only, not a new metric or
method (`scripts/exploratory_overlap_check.py`). All 5 sample_ids shared
between DroidDetect-Base's and LLMSniffer's signature-region lists are:

- **All `HUMAN_GENERATED`, all Python** (5/5)
- **All involve indentation-width normalization**: the original code used
  non-standard indentation (tabs, or 8-space) that black normalized to the
  conventional 4-space. No quote-style changes in any of the 5; blank-line
  changes present in 2/5.

A plausible (not established) reading: idiosyncratic human whitespace
convention is itself part of what both models associate with human
authorship, and normalizing it away is the single largest textual surprise
a "cosmetic" formatter can inflict on already-nonstandard code -- both
architectures register losing that signal, at very different sensitivity.
This is stated as a plausible mechanism, not a validated one. No further
method is built around this observation; if it doesn't hold up under
PROD_003's scale, it is dropped without affecting the main analysis.

## What this does NOT establish

- LLMSniffer/DroidDetect-Base's signature-region sample-ID overlap (13
  shared-ish cases) is suggestive but N is small; it is not established that
  this generalizes, only that it is visible in this data.
- DetectCodeGPT's Pattern B characterization is still read through a 60%-
  calibrated instrument; "diffuse instability" here should be understood as
  "diffuse raw-score movement," not as a validated claim about its practical
  detection reliability in absolute terms.
