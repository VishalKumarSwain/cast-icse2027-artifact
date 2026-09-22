| Item | Value |
|---|---|
| Dataset | project-droid/DroidCollection (Droid, EMNLP 2025) |
| Held-out split used (PROD_001/PROD_002/PROD_002F) | test |
| Total C0 samples (confirmatory production experiments) | 199 |
| Python samples | 100 |
| Java samples | 99 |
| Provenance labels represented | HUMAN_GENERATED, MACHINE_GENERATED, MACHINE_REFINED |
| Detector 1 | LLMSniffer (GraphCodeBERT + supervised contrastive head) |
| Detector 1 sanity check | 90.0% on GPTSniffer Java test set, n=20 |
| Detector 2 | DroidDetect-Base (ModernBERT-base + projection + 4-class head; architecture reconstructed, no published modeling code) |
| Detector 2 sanity check | 87.5% on Droid dev-split subset (pooling=cls, label permutation=[0, 1, 2, 3]) |
| Detector 3 | DetectCodeGPT (DetectGPT/NPR-family zero-shot perturbation z-score; CodeLlama-7b-hf + CodeT5p-770m) |
| Detector 3 chosen K (perturbations) | 50 |
| Detector 3 frozen decision threshold | 2.931 |
| Detector 3 independent calibration accuracy | 60.0% (n=40, Droid DEV split -- disjoint from evaluation set) |
| Transformation families (confirmatory, PROD_001/PROD_002) | lexical_rename, formatting, control_flow |
| Transformation families (feasibility-only, PROD_003) | local_structural, deep_semantic |
| PROD_001/PROD_002 ApplicabilityRate | 0.616 |
| PROD_001/PROD_002 TransformationSuccessRate | 0.992 |
| Distance metrics | d_text (char-level edit distance), d_token (real tokenizer: Python tokenize / Java tree-sitter leaves), d_ast (AST node-count delta) |
| Validation gate | tiered parse/compile validation (Java: STANDALONE_VALID > WRAPPER_VALID > STRUCTURAL_ONLY > PARSE_INVALID); Python: compile() |
| Confirmatory vs exploratory | PROD_001/PROD_002/PROD_002F(quant.) = confirmatory production experiments on N=199 held-out seeds. PROD_002F's sample-ID-overlap note and PROD_003's N=1-12 detector cells = exploratory/illustrative only, not statistical claims. |
