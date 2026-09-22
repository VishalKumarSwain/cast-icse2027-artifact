| Detector | Language | Family | N_valid | N_baseline_correct | MeanDelta | MedianDelta | MedianAbsDelta | Flips | InducedErrors | InducedErrorRate | IER_95pct_CI_Wilson | PairedEffectSize_CohensDz | ThresholdMetricStatus |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| DetectCodeGPT | Java | control_flow | 17 | 11 | 0.0002 | 0.1307 | 0.5837 | 3 | 2 | 0.1818 | [0.051, 0.477] | 0.0 | SECONDARY (60% calib. acc.) |
| DetectCodeGPT | Java | formatting | 64 | 36 | 0.2182 | 0.1979 | 0.477 | 11 | 6 | 0.1667 | [0.079, 0.319] | 0.264 | SECONDARY (60% calib. acc.) |
| DetectCodeGPT | Java | lexical_rename | 83 | 48 | 0.1538 | 0.1671 | 0.5249 | 16 | 8 | 0.1667 | [0.087, 0.296] | 0.165 | SECONDARY (60% calib. acc.) |
| DetectCodeGPT | Python | control_flow | 26 | 14 | 0.0528 | 0.0679 | 0.3563 | 8 | 7 | 0.5 | [0.268, 0.732] | 0.077 | SECONDARY (60% calib. acc.) |
| DetectCodeGPT | Python | formatting | 94 | 48 | 0.0788 | -0.0083 | 0.5276 | 24 | 12 | 0.25 | [0.149, 0.388] | 0.089 | SECONDARY (60% calib. acc.) |
| DetectCodeGPT | Python | lexical_rename | 81 | 43 | -0.0118 | 0.1152 | 0.4114 | 19 | 13 | 0.3023 | [0.186, 0.451] | -0.015 | SECONDARY (60% calib. acc.) |
| DroidDetect-Base | Java | control_flow | 17 | 14 | 0.0039 | 0.0 | 0.0044 | 2 | 1 | 0.0714 | [0.013, 0.315] | 0.015 | PRIMARY |
| DroidDetect-Base | Java | formatting | 64 | 54 | -0.1197 | -0.0047 | 0.0328 | 13 | 13 | 0.2407 | [0.146, 0.369] | -0.408 | PRIMARY |
| DroidDetect-Base | Java | lexical_rename | 83 | 71 | 0.0054 | 0.0 | 0.0013 | 4 | 2 | 0.0282 | [0.008, 0.097] | 0.032 | PRIMARY |
| DroidDetect-Base | Python | control_flow | 26 | 26 | -0.0015 | 0.0 | 0.0 | 1 | 1 | 0.0385 | [0.007, 0.189] | -0.028 | PRIMARY |
| DroidDetect-Base | Python | formatting | 94 | 83 | -0.276 | -0.0088 | 0.0566 | 32 | 29 | 0.3494 | [0.256, 0.457] | -0.64 | PRIMARY |
| DroidDetect-Base | Python | lexical_rename | 81 | 73 | -0.0028 | 0.0 | 0.0001 | 6 | 3 | 0.0411 | [0.014, 0.114] | -0.024 | PRIMARY |
| LLMSniffer | Java | control_flow | 17 | 4 | 0.0233 | 0.0247 | 0.0247 | 5 | 0 | 0.0 | [0.000, 0.490] | 1.389 | PRIMARY |
| LLMSniffer | Java | formatting | 64 | 24 | 0.0092 | 0.0119 | 0.0191 | 13 | 2 | 0.0833 | [0.023, 0.258] | 0.243 | PRIMARY |
| LLMSniffer | Java | lexical_rename | 83 | 35 | 0.0094 | 0.0085 | 0.0085 | 5 | 0 | 0.0 | [0.000, 0.099] | 1.487 | PRIMARY |
| LLMSniffer | Python | control_flow | 26 | 15 | 0.0065 | 0.006 | 0.0099 | 2 | 0 | 0.0 | [0.000, 0.204] | 0.331 | PRIMARY |
| LLMSniffer | Python | formatting | 94 | 62 | 0.0036 | 0.0004 | 0.0169 | 8 | 4 | 0.0645 | [0.025, 0.154] | 0.086 | PRIMARY |
| LLMSniffer | Python | lexical_rename | 81 | 52 | 0.0072 | 0.0056 | 0.006 | 1 | 1 | 0.0192 | [0.003, 0.101] | 0.659 | PRIMARY |
