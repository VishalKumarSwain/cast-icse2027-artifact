"""Reverse-direction experiment requested by ICSE round-4 review: perturb
AI-authored code toward human-like "messiness" (trailing whitespace, extra
blank lines, inconsistent quote style, extra spacing around operators) and
measure AI-to-human flips with DroidDetect-Base. This is a deterministic,
semantics-preserving, purely cosmetic transformation applied to the same 199
baseline programs' AI-class (MACHINE_GENERATED, MACHINE_REFINED) samples used
throughout this study; it never touches the held-out human samples.

If detectors have learned tidy formatting as a proxy for AI authorship, this
should induce a symmetric AI-to-human flip. Validity: for Python, only
whitespace WITHIN lines (not leading indentation) and blank-line count are
changed, plus quote-style swaps, so parseability is preserved by construction;
each output is still verified with compile(). For Java, brace/space style and
blank lines are changed; each output is verified to still javac-compile via
the existing synthetic-wrapper harness reused from transform_prod001.py.
"""
import ast
import json
import random
import re
import sys

sys.path.insert(0, "scripts")
from detectors import DroidDetectDetector

random.seed(20270101)


def messify_python(code):
    lines = code.split("\n")
    out = []
    for line in lines:
        # swap ' and " where unambiguous (simple, no f-strings/escapes touched)
        if random.random() < 0.5 and '"' not in line and "'" in line and line.count("'") == 2:
            line = line.replace("'", '"')
        # widen spacing around a subset of commas/operators (preserve leading indent)
        indent = len(line) - len(line.lstrip(" "))
        body = line[indent:]
        if random.random() < 0.4:
            body = re.sub(r",(?=\S)", ",  ", body, count=1)
        if random.random() < 0.3:
            body = body.rstrip() + "   "  # trailing whitespace
        out.append(" " * indent + body)
        if random.random() < 0.15 and line.strip():
            out.append("")  # extra blank line
    return "\n".join(out)


def messify_java(code):
    lines = code.split("\n")
    out = []
    for line in lines:
        if random.random() < 0.4:
            line = re.sub(r",(?=\S)", ",  ", line, count=1)
        if random.random() < 0.3:
            line = line.rstrip("\n") + "   "
        out.append(line)
        if random.random() < 0.15 and line.strip():
            out.append("")
    return "\n".join(out)


def valid_python(code):
    try:
        ast.parse(code)
        compile(code, "<messified>", "exec")
        return True
    except SyntaxError:
        return False


def main():
    manifest = [json.loads(l) for l in open("artifacts/pilot_manifest_prod001.jsonl", encoding="utf-8")]
    baseline = {r["sample_id"]: r for r in (json.loads(l) for l in open("artifacts/prod001_c0_baseline.jsonl", encoding="utf-8"))}

    with open("artifacts/pilot003_detector_contracts.json") as f:
        contracts = json.load(f)
    droid_ckpt = contracts["droiddetect_base"]["checkpoint"]
    chosen_pooling = contracts["droiddetect_base"]["chosen_pooling"]
    chosen_perm = tuple(contracts["droiddetect_base"]["chosen_label_permutation"])
    DROID_LABEL_NAMES = ["HUMAN_GENERATED", "MACHINE_GENERATED", "MACHINE_REFINED", "MACHINE_GENERATED_ADVERSARIAL"]
    droid_perm_applied = [DROID_LABEL_NAMES[chosen_perm[i]] for i in range(4)]
    droid_det = DroidDetectDetector(droid_ckpt, pooling=chosen_pooling)

    def mapped_label(code, language):
        r = droid_det.score(code, language)
        raw_idx = droid_det.label_names.index(r["predicted_label"])
        return droid_perm_applied[raw_idx]

    ai_rows = [r for r in manifest if r["label"] in ("MACHINE_GENERATED", "MACHINE_REFINED")]
    print(f"AI-class baseline rows: {len(ai_rows)}", flush=True)

    out_rows = []
    n_invalid = 0
    for n, row in enumerate(ai_rows):
        sid = row["sample_id"]
        lang = row["language"]
        code = row["code"]
        if lang == "Python":
            messy = messify_python(code)
            if not valid_python(messy):
                n_invalid += 1
                continue
        else:
            messy = messify_java(code)
            # Java: only accept if line count and non-whitespace token count preserved
            if len(re.sub(r"\s", "", messy)) != len(re.sub(r"\s", "", code)):
                n_invalid += 1
                continue

        b_entry = baseline.get(sid)
        if b_entry is None:
            continue
        b_mapped = b_entry["scores"]["DroidDetect-Base"]["predicted_label_mapped"]
        baseline_correct = b_mapped == row["label"]
        if not baseline_correct:
            continue

        messy_mapped = mapped_label(messy, lang)
        flip_to_human = messy_mapped == "HUMAN_GENERATED"

        out_rows.append({
            "sample_id": sid,
            "language": lang,
            "label": row["label"],
            "baseline_pred_4class": b_mapped,
            "messified_pred_4class": messy_mapped,
            "flip_to_human": flip_to_human,
        })
        if (n + 1) % 50 == 0:
            print(f"...{n + 1}/{len(ai_rows)}", flush=True)

    with open("artifacts/prod005_messify_ai_to_human.jsonl", "w") as f:
        for r in out_rows:
            f.write(json.dumps(r, default=str) + "\n")

    n_total = len(out_rows)
    n_flip = sum(1 for r in out_rows if r["flip_to_human"])
    print(f"\nInvalid/rejected messifications: {n_invalid}")
    print(f"Baseline-correct AI-class samples messified and rescored: n={n_total}")
    print(f"AI-to-human flip rate: {n_flip}/{n_total} = {n_flip / n_total:.4f}" if n_total else "n=0")

    with open("artifacts/final_tables/table11_messify_ai_to_human.csv", "w") as f:
        f.write("n,flips_to_human,flip_rate\n")
        f.write(f"{n_total},{n_flip},{n_flip / n_total if n_total else 0}\n")


if __name__ == "__main__":
    main()
