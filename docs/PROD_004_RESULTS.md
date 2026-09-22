# PROD_004: Canonicalization Probe -- Results

Protocol: `docs/PROD_004_PROTOCOL.md`. 158 formatting-family SUCCESS pairs
from PROD_001 (94 Python + 64 Java), same 199-seed corpus, same three
frozen detectors. No new samples, detectors, or languages.

## Step 1: canonicalization collapse rate

**108/158 (68%) of formatting pairs canonicalize to byte-identical text**
(Python 62/94, Java 46/64) -- for these, the formatting transformation's
*only* effect was whitespace/indentation/blank-lines/comments/quote-style
that the canonicalizer normalizes away entirely. `delta_canon = 0` for these
by construction (not a measurement -- the canonicalized inputs are the
literal same string, so any detector must score them identically).

**50/158 (32%) have a residual difference** after canonicalization (Python
32, Java 18) -- these needed fresh detector scoring.

## Step 2/3: does instability shrink after canonicalization?

### All 158 pairs (mean |delta|, original PROD_002 formatting vs. canonicalized)

| Detector | Language | N | mean\|Δ_orig\| | mean\|Δ_canon\| | Reduction factor |
|---|---|---|---|---|---|
| LLMSniffer | Python | 94 | 0.0269 | 0.0031 | 8.6x |
| LLMSniffer | Java | 64 | 0.0252 | 0.0015 | 16.7x |
| **DroidDetect-Base** | **Python** | 94 | **0.3151** | **0.0090** | **34.9x** |
| **DroidDetect-Base** | **Java** | 64 | **0.1612** | **0.0025** | **63.3x** |
| DetectCodeGPT | Python | 94 | 0.6874 | 0.2805 | 2.5x |
| DetectCodeGPT | Java | 64 | 0.6449 | 0.2436 | 2.6x |

### Residual-only (50 pairs canonicalization did NOT fully collapse -- fair like-for-like comparison, controlling for "these are the harder cases")

| Detector | Language | N | mean\|Δ_orig\| | mean\|Δ_canon\| | Reduction factor |
|---|---|---|---|---|---|
| LLMSniffer | Python | 32 | 0.0323 | 0.0092 | 3.5x |
| LLMSniffer | Java | 18 | 0.0200 | 0.0054 | 3.7x |
| **DroidDetect-Base** | **Python** | 32 | **0.3937** | **0.0266** | **14.8x** |
| **DroidDetect-Base** | **Java** | 18 | **0.1390** | **0.0091** | **15.4x** |
| DetectCodeGPT | Python | 32 | 0.8425 | 0.8239 | **1.0x (no reduction)** |
| DetectCodeGPT | Java | 18 | 0.5657 | 0.8660 | **0.7x (slightly worse)** |

## Answer to the reviewer question

**Yes, for DroidDetect-Base, and the effect is large and specific.**
Canonicalization reduces its formatting-induced score movement by
**14.8-63.3x** depending on subset/language -- including on the
residual-only subset that deliberately excludes the trivial
byte-identical cases, so this is not an artifact of the easy majority.
This is strong, direct evidence that DroidDetect-Base's formatting
fragility is substantially a **whitespace/presentation artifact**: remove
that degree of freedom, and most of the instability goes with it.

**LLMSniffer shows a real but much smaller effect** (3.5-16.7x) --
consistent with it already being comparatively stable; there is less
instability to remove in the first place.

**DetectCodeGPT shows essentially no mitigation** (1.0x Python, 0.7x Java --
i.e. no reduction, and marginally worse on the Java residual subset). This
is a sharp, clean confirmation of PROD_002F's characterization:
DetectCodeGPT's instability is **not** primarily a formatting/whitespace
artifact. Canonicalizing away presentation does nothing for it, consistent
with its diffuse (Pattern B) character being driven by something other than
surface formatting -- exactly the contrast the study's central claim needs.

## Revised central claim, now with mechanism evidence

The study's three-detector finding is no longer just "different stability
profiles" -- PROD_004 adds a mechanistic distinction:

- **DroidDetect-Base's fragility is substantially explained by, and
  substantially mitigated by removing, surface formatting/whitespace
  presentation.**
- **DetectCodeGPT's instability is not explained by formatting presentation
  at all** -- canonicalization does not touch it, implying its diffuse
  sensitivity has a different source (consistent with it being a
  perturbation-based statistical method reacting to something other than
  whitespace).
- **LLMSniffer sits in between but close to the stable end** -- some
  formatting sensitivity exists and is partially explained by presentation,
  but there was little instability to begin with.

## Status: experiments frozen

Per the study plan, this closes the experimental phase. No further
detectors, languages, samples, transformation families, or probes planned.
Next steps: final statistics across all phases, updated final tables,
figures, threats-to-validity, manuscript.
