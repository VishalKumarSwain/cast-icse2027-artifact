"""Detector contracts for PILOT_003.

Both detectors are loaded from their released checkpoints with architectures
reconstructed from public source (LLMSniffer notebook code) or from the
checkpoint's own state-dict key structure (DroidDetect-Base, which ships no
modeling code). Every detector wrapper returns a dict with the fields needed
to distinguish truncation effects from transformation effects:

  raw_score, predicted_label, input_tokens, truncated, tokens_removed,
  effective_input_hash

No detector's forward pass is modified to accommodate our corpus; if a
detector cannot process a sample reproducibly, that is recorded as an
incompatibility (see PILOT_003 report), not patched.
"""
import hashlib
import re

import torch
import torch.nn as nn
from transformers import AutoModel, AutoTokenizer

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


def _effective_hash(token_ids):
    return hashlib.sha256(str(token_ids).encode()).hexdigest()[:16]


def remove_java_comments(code):
    code = re.sub(r"//.*", "", code)
    code = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL)
    return code


# ---------------------------------------------------------------------------
# Detector A: LLMSniffer (GraphCodeBERT + custom binary head)
#
# Contract:
#   repo: github.com/mahirlabibdihan/llmsniffer @ b0e8a4f72c5296ab2766448e5ca38f8d5260376a
#   checkpoint: huggingface.co/mahirlabibdihan/LLMSniffer/gptsniffer.pth
#   encoder: microsoft/graphcodebert-base
#   training domain: Java ONLY (GPTSniffer dataset is Java-only; filename-label
#     convention 0_=human/1_=AI). Applying to Python is OUT-OF-DOMAIN -- we
#     still run it (for cross-language comparison) but every result on Python
#     inputs must be flagged non-calibrated / out-of-domain in analysis.
#   preprocessing: comment stripping (remove_java_comments, exact regex from
#     source) applied ONLY for Java, matching training; Python inputs are
#     tokenized as-is (no equivalent preprocessing exists in source).
#   tokenizer max_length: 512, padding='max_length', truncation=True (from
#     source's CodeDataset.__getitem__).
#   output: single logit -> sigmoid -> P(class=1). Label convention from
#     GPTSniffer: 0=human, 1=AI/ChatGPT. NOT a calibrated probability in the
#     statistical sense -- it's a trained sigmoid score; treat as raw_score
#     for decay analysis, only use predicted_label (threshold 0.5) for flips.
# ---------------------------------------------------------------------------

class CodeBERTBinaryClassifier(nn.Module):
    def __init__(self, encoder_model):
        super().__init__()
        self.encoder = encoder_model
        self.classifier = nn.Sequential(
            nn.Dropout(0.3),
            nn.Linear(self.encoder.config.hidden_size, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, 1),
        )

    def forward(self, input_ids, attention_mask):
        outputs = self.encoder(input_ids=input_ids, attention_mask=attention_mask)
        cls_output = outputs.last_hidden_state[:, 0, :]
        logits = self.classifier(cls_output).squeeze(-1)
        return logits


class LLMSnifferDetector:
    name = "LLMSniffer"
    max_length = 512
    calibrated = False  # trained sigmoid score, not a statistically calibrated probability
    training_domain_language = "Java"

    def __init__(self, checkpoint_path):
        self.tokenizer = AutoTokenizer.from_pretrained("microsoft/graphcodebert-base")
        base = AutoModel.from_pretrained("microsoft/graphcodebert-base")
        self.model = CodeBERTBinaryClassifier(base)
        state_dict = torch.load(checkpoint_path, map_location="cpu")
        missing, unexpected = self.model.load_state_dict(state_dict, strict=False)
        assert not missing and not unexpected, f"key mismatch: missing={missing} unexpected={unexpected}"
        self.model.to(DEVICE)
        self.model.eval()

    def score(self, code, language):
        text = remove_java_comments(code) if language == "Java" else code
        enc = self.tokenizer(text, add_special_tokens=True, truncation=False)
        full_len = len(enc["input_ids"])
        truncated = full_len > self.max_length
        enc_t = self.tokenizer(
            text, padding="max_length", max_length=self.max_length, truncation=True, return_tensors="pt"
        ).to(DEVICE)
        with torch.no_grad():
            logit = self.model(enc_t["input_ids"], enc_t["attention_mask"])
            prob = torch.sigmoid(logit).item()
        used_ids = enc_t["input_ids"][0].tolist()
        return {
            "detector": self.name,
            "raw_score": prob,
            "predicted_label": "AI" if prob > 0.5 else "HUMAN",
            "input_tokens": full_len,
            "truncated": truncated,
            "tokens_removed": max(0, full_len - self.max_length),
            "effective_input_hash": _effective_hash(used_ids),
            "out_of_domain": language != self.training_domain_language,
        }


# ---------------------------------------------------------------------------
# Detector B: DroidDetect-Base (ModernBERT + text projection + 4-class head)
#
# Contract:
#   checkpoint: huggingface.co/project-droid/DroidDetect-Base (Apache-2.0)
#   NO modeling code is published for this checkpoint. Architecture is
#   reconstructed from the state-dict's own key names, which match ModernBERT
#   internals exactly (text_encoder.layers.N.attn.Wqkv / .attn.Wo /
#   .mlp.Wi / .mlp.Wo / .attn_norm / .mlp_norm / .final_norm), plus
#   text_projection (Linear 768->256; NOTE config.json claims
#   projection_dim=128, which is WRONG/stale relative to the actual weights --
#   we trust the weight shapes) and classifier (Linear 256->4).
#   Pooling strategy (CLS-token vs mean-pooling) is UNDOCUMENTED. Both are
#   implemented here; PILOT_003's sanity check against Droid's own dev split
#   (disjoint from our pilot manifest) picks whichever reaches non-trivial
#   accuracy, and that choice + its accuracy is recorded as part of the
#   detector contract, not assumed.
#   labels (from Droid schema audit): 0..3 correspond to
#   [HUMAN_GENERATED, MACHINE_GENERATED, MACHINE_REFINED,
#    MACHINE_GENERATED_ADVERSARIAL] -- ORDER UNVERIFIED (no id2label shipped);
#   sanity check also disambiguates this mapping empirically.
#   tokenizer max_length: ModernBERT supports long context; we cap at 512 to
#   match LLMSniffer's budget for comparability, logging truncation the same
#   way.
# ---------------------------------------------------------------------------

class DroidDetectModel(nn.Module):
    def __init__(self, base_model_name="answerdotai/ModernBERT-base", proj_dim=256, num_classes=4):
        super().__init__()
        self.text_encoder = AutoModel.from_pretrained(base_model_name)
        hidden = self.text_encoder.config.hidden_size
        self.text_projection = nn.Linear(hidden, proj_dim)
        self.classifier = nn.Linear(proj_dim, num_classes)

    def forward(self, input_ids, attention_mask, pooling="cls"):
        out = self.text_encoder(input_ids=input_ids, attention_mask=attention_mask).last_hidden_state
        if pooling == "cls":
            pooled = out[:, 0, :]
        else:  # mean pooling over non-padded tokens
            mask = attention_mask.unsqueeze(-1).float()
            pooled = (out * mask).sum(1) / mask.sum(1).clamp(min=1)
        proj = self.text_projection(pooled)
        logits = self.classifier(proj)
        return logits


class DroidDetectDetector:
    name = "DroidDetect-Base"
    max_length = 512
    calibrated = False  # softmax output, calibration not verified
    label_names = ["HUMAN_GENERATED", "MACHINE_GENERATED", "MACHINE_REFINED", "MACHINE_GENERATED_ADVERSARIAL"]

    def __init__(self, checkpoint_path, pooling="cls"):
        self.tokenizer = AutoTokenizer.from_pretrained("answerdotai/ModernBERT-base")
        self.model = DroidDetectModel()
        state_dict = torch.load(checkpoint_path, map_location="cpu")
        remapped = {k.replace("text_encoder.", "text_encoder.", 1): v for k, v in state_dict.items()}
        missing, unexpected = self.model.load_state_dict(remapped, strict=False)
        self._load_report = {"missing": missing, "unexpected": unexpected}
        self.model.to(DEVICE)
        self.model.eval()
        self.pooling = pooling

    def score(self, code, language):
        enc = self.tokenizer(code, add_special_tokens=True, truncation=False)
        full_len = len(enc["input_ids"])
        truncated = full_len > self.max_length
        enc_t = self.tokenizer(
            code, padding="max_length", max_length=self.max_length, truncation=True, return_tensors="pt"
        ).to(DEVICE)
        with torch.no_grad():
            logits = self.model(enc_t["input_ids"], enc_t["attention_mask"], pooling=self.pooling)
            probs = torch.softmax(logits, dim=-1)[0]
        pred_idx = int(torch.argmax(probs).item())
        used_ids = enc_t["input_ids"][0].tolist()
        return {
            "detector": self.name,
            "raw_score": probs.tolist(),
            "predicted_label": self.label_names[pred_idx],
            "input_tokens": full_len,
            "truncated": truncated,
            "tokens_removed": max(0, full_len - self.max_length),
            "effective_input_hash": _effective_hash(used_ids),
            "pooling": self.pooling,
        }
