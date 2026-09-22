# PROD_003: Deeper Transformations -- Results

Protocol: `docs/PROD_003_PROTOCOL.md`. Same 199 C0 seeds, same three frozen
detectors, same validation/distance metrics. Two new families
(local_structural, deep_semantic) x two intensities (low, high).

## Applicability finding (the primary result of this phase)

**ApplicabilityRate = 0.05** (37/796 attempted), **TransformationSuccessRate
= 0.95** (35/37 applicable). This is dramatically lower than the earlier
three families (0.61-0.66 in PROD_001/PROD_002). Breakdown of the 35 SUCCESS
rows: Java local_structural 12+12 (low/high), Python local_structural 3+3,
Python deep_semantic 1+2, Java deep_semantic 1+1.

Semantic-equivalence check: only 4/35 reached true `DIFFERENTIAL_EXECUTION_PASSED`
verification; the other 31 degraded to `STRUCTURAL_ONLY_NO_ENTRY_POINT`, as
the protocol anticipated for Droid's fragment-heavy composition (most
samples are function/class fragments without an unambiguous, stdin-free
entry point).

**This is itself the primary finding of PROD_003**: the transformation
ladder's cosmetic/lexical end (formatting, lexical rename, control-flow)
applies broadly to this corpus; its structural/semantic end applies to a
small, specific minority of samples. Extending the ladder further into
deeper transformations would require either a different seed corpus (fewer
fragments, more complete programs) or narrower research claims scoped to
the subset of samples where these patterns exist -- noted as a limitation /
future-work item, not solved here.

## Diagnostic table (N shown explicitly; most cells N=1-12, illustrative not population-level)

| Detector | Lang | Family | Intensity | N | BaseOK | MeanΔ | MedianΔ | Flips |
|---|---|---|---|---|---|---|---|---|
| DetectCodeGPT | Java | deep_semantic | high | 1 | 0 | -0.2084 | -0.2084 | 0 |
| DetectCodeGPT | Java | deep_semantic | low | 1 | 0 | 0.3021 | 0.3021 | 0 |
| DetectCodeGPT | Java | local_structural | high | 12 | 5 | 0.1912 | 0.1209 | 2 |
| DetectCodeGPT | Java | local_structural | low | 12 | 5 | -0.1566 | -0.1346 | 3 |
| DetectCodeGPT | Python | deep_semantic | high | 2 | 2 | -0.1806 | -0.1806 | 0 |
| DetectCodeGPT | Python | deep_semantic | low | 1 | 1 | 0.5395 | 0.5395 | 0 |
| DetectCodeGPT | Python | local_structural | high | 3 | 2 | -0.2166 | 0.3753 | 1 |
| DetectCodeGPT | Python | local_structural | low | 3 | 2 | -0.4867 | -0.6520 | 1 |
| DroidDetect-Base | Java | deep_semantic | high | 1 | 1 | 0.0000 | 0.0000 | 0 |
| DroidDetect-Base | Java | deep_semantic | low | 1 | 1 | 0.0000 | 0.0000 | 0 |
| DroidDetect-Base | Java | local_structural | high | 12 | 11 | -0.0243 | 0.0000 | 0 |
| DroidDetect-Base | Java | local_structural | low | 12 | 11 | -0.0213 | 0.0000 | 0 |
| DroidDetect-Base | Python | deep_semantic | high | 2 | 2 | -0.0055 | -0.0055 | 0 |
| DroidDetect-Base | Python | deep_semantic | low | 1 | 1 | -0.0110 | -0.0110 | 0 |
| DroidDetect-Base | Python | local_structural | high | 3 | 3 | -0.0000 | -0.0000 | 0 |
| DroidDetect-Base | Python | local_structural | low | 3 | 3 | -0.0000 | -0.0000 | 0 |
| LLMSniffer | Java | deep_semantic | high | 1 | 0 | 0.0000 | 0.0000 | 0 |
| LLMSniffer | Java | deep_semantic | low | 1 | 0 | 0.0000 | 0.0000 | 0 |
| LLMSniffer | Java | local_structural | high | 12 | 5 | 0.0093 | 0.0041 | 1 |
| LLMSniffer | Java | local_structural | low | 12 | 5 | 0.0093 | 0.0041 | 1 |
| LLMSniffer | Python | deep_semantic | high | 2 | 2 | 0.0089 | 0.0089 | 0 |
| LLMSniffer | Python | deep_semantic | low | 1 | 1 | 0.0166 | 0.0166 | 0 |
| LLMSniffer | Python | local_structural | high | 3 | 2 | -0.0034 | -0.0014 | 0 |
| LLMSniffer | Python | local_structural | low | 3 | 2 | -0.0034 | -0.0014 | 0 |

## Qualitative observation (illustrative, not statistically established at this N)

The pattern from PROD_002F appears to hold directionally even at this small
scale: DroidDetect-Base and LLMSniffer both stay near-zero on
local_structural/deep_semantic (|MeanΔ| <= 0.024 for DroidDetect-Base,
<= 0.017 for LLMSniffer, across every cell) despite these transformations
producing larger structural edits than pure formatting. This is consistent
with -- but does not newly establish -- the earlier finding that
DroidDetect-Base's fragility is specific to cosmetic/whitespace-style
changes rather than a generic function of edit magnitude: here, bigger
structural edits do NOT reproduce its formatting-scale collapses.
DetectCodeGPT continues to show much larger raw movement (|MeanΔ| between
0.16 and 0.54 across cells), consistent with its diffuse Pattern B character
persisting at this deeper transformation level too.

**This paragraph is explicitly qualitative** -- no cell here has enough N to
support a statistical claim, and it is reported as a directionally
consistent observation for the discussion section, not as a new confirmed
result on par with PROD_001/PROD_002F.

## Status

Per the study's methodology plan, this is the last planned experiment.
Next steps: final statistical analysis across all phases, figures,
threats-to-validity writeup, manuscript. No further transformation
families, detectors, languages, or corpus expansion planned for this NIER
submission -- deferred to Future Work.
