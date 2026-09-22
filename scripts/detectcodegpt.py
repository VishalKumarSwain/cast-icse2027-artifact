"""DetectCodeGPT-family zero-shot detector: DetectGPT-style perturbation
z-score using a base scoring LM (codellama/CodeLlama-7b-hf) and a mask-
filling model (Salesforce/codet5p-770m), per the contract in
docs/PROD_002_PROTOCOL.md and the nested-K design in
docs/DETECTCODEGPT_PROTOCOL.md.

s_K(c) = (LL(c) - mean_i LL(c~_i)) / std_i LL(c~_i)   for i in 1..K

Perturbations are generated ONCE at K=50 per sample with a fixed seed; all
K in {5,10,20,50} are computed from prefixes of that same set (nested
design), not independent redraws.

Performance note: both mask-filling and log-likelihood scoring are batched
across all K perturbations in a single forward/generate call each, rather
than looping one sequence at a time -- an early sequential-loop
implementation was orders of magnitude slower for no methodological reason
(same statistic, same inputs) and was replaced before any convergence/
calibration numbers were produced.
"""
import random
import re

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, T5ForConditionalGeneration

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

BASE_MODEL_NAME = "codellama/CodeLlama-7b-hf"
MASK_MODEL_NAME = "Salesforce/codet5p-770m"

PCT_WORDS_MASKED = 0.5
SPAN_LENGTH = 2
MAX_PERTURBATIONS = 50
MAX_NEW_TOKENS_PER_MASK = 12  # spans are SPAN_LENGTH=2 words; ample headroom without the old 256 blowup
MAX_MASKS_PER_VARIANT = 40  # caps mask count for long files -- without this, n_spans scales with
                             # code length unboundedly and max_new_tokens (mask_count * per-mask
                             # budget) exploded to thousands of tokens on Droid's longer samples,
                             # causing multi-hour stalls on individual files. See prod002 rerun note.
MAX_NEW_TOKENS_CEILING = 480  # hard ceiling regardless of mask count, for the same reason


def _split_words(code):
    return re.findall(r"\S+|\s+", code)


class DetectCodeGPTDetector:
    name = "DetectCodeGPT"
    calibrated = False  # raw z-score; threshold calibrated separately (see DETECTCODEGPT_PROTOCOL.md)

    def __init__(self, base_model_name=BASE_MODEL_NAME, mask_model_name=MASK_MODEL_NAME, seed=20260922):
        self.base_tokenizer = AutoTokenizer.from_pretrained(base_model_name)
        if self.base_tokenizer.pad_token is None:
            self.base_tokenizer.pad_token = self.base_tokenizer.eos_token
        self.base_model = AutoModelForCausalLM.from_pretrained(base_model_name, torch_dtype=torch.float16).to(DEVICE)
        self.base_model.eval()

        self.mask_tokenizer = AutoTokenizer.from_pretrained(mask_model_name)
        self.mask_model = T5ForConditionalGeneration.from_pretrained(mask_model_name, torch_dtype=torch.float16).to(DEVICE)
        self.mask_model.eval()
        self.seed = seed

    @torch.no_grad()
    def _batch_log_likelihood(self, codes, batch_size=8):
        results = []
        for i in range(0, len(codes), batch_size):
            batch = codes[i : i + batch_size]
            enc = self.base_tokenizer(
                batch, return_tensors="pt", truncation=True, max_length=1024, padding=True
            ).to(DEVICE)
            out = self.base_model(input_ids=enc["input_ids"], attention_mask=enc["attention_mask"])
            logits = out.logits[:, :-1, :]
            labels = enc["input_ids"][:, 1:]
            mask = enc["attention_mask"][:, 1:].float()
            logprobs = torch.log_softmax(logits.float(), dim=-1)
            token_ll = torch.gather(logprobs, 2, labels.unsqueeze(-1)).squeeze(-1)
            per_seq_ll = (token_ll * mask).sum(dim=1) / mask.sum(dim=1).clamp(min=1)
            for j in range(len(batch)):
                n_real_tokens = int(mask[j].sum().item())
                results.append(per_seq_ll[j].item() if n_real_tokens > 0 else None)
        return results

    def _build_masked_variants(self, code, n, rng):
        words = _split_words(code)
        non_space_idxs = [i for i, w in enumerate(words) if not w.isspace()]

        variants = []  # (masked_text, mask_count)
        for _ in range(n):
            n_spans = max(1, int(len(non_space_idxs) * PCT_WORDS_MASKED / SPAN_LENGTH))
            n_spans = min(n_spans, MAX_MASKS_PER_VARIANT)
            span_starts = sorted(set(rng.sample(non_space_idxs, k=min(n_spans, len(non_space_idxs)))))

            masked_words = list(words)
            mask_id = 0
            occupied = [False] * len(masked_words)
            for start in sorted(span_starts, reverse=True):
                end = min(start + SPAN_LENGTH, len(masked_words))
                if any(occupied[j] for j in range(start, end)):
                    continue
                masked_words[start:end] = [f"<extra_id_{mask_id}>"]
                for j in range(start, end):
                    if j < len(occupied):
                        occupied[j] = True
                mask_id += 1
            variants.append(("".join(masked_words), mask_id))
        return variants

    @torch.no_grad()
    def _batch_fill_masks(self, variants, batch_size=16):
        filled = []
        for i in range(0, len(variants), batch_size):
            batch = variants[i : i + batch_size]
            texts = [v[0] for v in batch]
            max_masks = max(v[1] for v in batch) if batch else 1
            enc = self.mask_tokenizer(
                texts, return_tensors="pt", truncation=True, max_length=512, padding=True
            ).to(DEVICE)
            gen = self.mask_model.generate(
                **enc,
                max_new_tokens=min(max(1, max_masks) * MAX_NEW_TOKENS_PER_MASK, MAX_NEW_TOKENS_CEILING),
                do_sample=True,
                top_p=0.96,
                temperature=1.0,
            )
            decoded = self.mask_tokenizer.batch_decode(gen, skip_special_tokens=False)
            for (masked_text, mask_id), filled_text in zip(batch, decoded):
                if mask_id == 0:
                    filled.append(masked_text)
                    continue
                result = masked_text
                pieces = re.split(r"<extra_id_\d+>", filled_text)
                for k in range(mask_id):
                    fill_piece = pieces[k + 1].strip() if k + 1 < len(pieces) else ""
                    result = result.replace(f"<extra_id_{k}>", fill_piece, 1)
                filled.append(result)
        return filled

    def generate_perturbations(self, code, n=MAX_PERTURBATIONS):
        rng = random.Random(hash((self.seed, code)) & 0xFFFFFFFF)
        variants = self._build_masked_variants(code, n, rng)
        try:
            return self._batch_fill_masks(variants)
        except Exception:
            return [code] * n  # degenerate perturbations counted, not silently dropped

    def score_at_k(self, code, perturbations_50, k):
        subset = perturbations_50[:k]
        lls = self._batch_log_likelihood([code] + subset)
        ll_orig, ll_perturbed = lls[0], [x for x in lls[1:] if x is not None]
        if ll_orig is None or len(ll_perturbed) < 2:
            return None
        mean_p = sum(ll_perturbed) / len(ll_perturbed)
        var_p = sum((x - mean_p) ** 2 for x in ll_perturbed) / len(ll_perturbed)
        std_p = var_p**0.5
        if std_p == 0:
            return None
        return (ll_orig - mean_p) / std_p
