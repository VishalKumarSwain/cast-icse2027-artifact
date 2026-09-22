"""PILOT_001 step 4-7: apply the three pilot transformations to each C_0 seed,
validate (parse/compile), compute distance metrics, and write one row per
(sample_id, transformation) to artifacts/pilot_transform_log.jsonl.

Transformations (pilot-only subset of the full ladder):
  - lexical_rename   : rename one identifier (low intensity)
  - formatting       : run the language's canonical formatter
  - control_flow     : rewrite one canonical for-loop into an equivalent while-loop

C_0 itself is never mutated in place: every transform reads the manifest's
`code` field fresh and writes its own output file plus a log row. Failed
transforms (parse/compile/validation failure) are logged as
TRANSFORM_FAILED / VALIDATION_FAILED, never silently dropped.
"""
import difflib
import json
import os
import re
import subprocess
import tempfile

import black
import libcst as cst

GJF_JAR = "/data/aihuman/tools/gjf/gjf.jar"
JDK_BIN = "/data/aihuman/tools/jdk17/bin"

OUT_DIR = "artifacts/transformed"
LOG_PATH = "artifacts/pilot_transform_log.jsonl"


# ---------- distance metrics (pilot approximations; refine at protocol freeze) ----------

def token_distance(a, b):
    ta, tb = a.split(), b.split()
    sm = difflib.SequenceMatcher(a=ta, b=tb, autojunk=False)
    matches = sum(block.size for block in sm.get_matching_blocks())
    return max(len(ta), len(tb)) - matches


def char_edit_distance(a, b):
    sm = difflib.SequenceMatcher(a=a, b=b, autojunk=False)
    matches = sum(block.size for block in sm.get_matching_blocks())
    return max(len(a), len(b)) - matches


def approx_ast_node_count_python(code):
    try:
        import ast

        return sum(1 for _ in ast.walk(ast.parse(code)))
    except Exception:
        return None


def approx_ast_node_count_java(code):
    import tree_sitter_java as tsjava
    from tree_sitter import Language, Parser

    lang = Language(tsjava.language())
    parser = Parser(lang)
    tree = parser.parse(code.encode())
    count = 0

    def walk(node):
        nonlocal count
        count += 1
        for c in node.children:
            walk(c)

    walk(tree.root_node)
    return count


# ---------- validation ----------

def validate_python(code):
    try:
        compile(code, "<pilot>", "exec")
        return True, None
    except SyntaxError as e:
        return False, str(e)


def validate_java(code, class_name_hint="Pilot"):
    with tempfile.TemporaryDirectory() as td:
        # Java requires the public class name to match the filename; try to
        # detect it, else wrap wouldn't compile standalone snippets are common
        # in Droid (functions/snippets, not full classes) so treat "parses
        # with javac -Xstdout as syntax check" via a permissive wrapper.
        m = re.search(r"\bclass\s+(\w+)", code)
        fname = m.group(1) if m else class_name_hint
        path = os.path.join(td, f"{fname}.java")
        with open(path, "w", encoding="utf-8") as f:
            f.write(code)
        result = subprocess.run(
            [f"{JDK_BIN}/javac", "-d", td, path],
            capture_output=True,
            text=True,
            timeout=30,
        )
        return result.returncode == 0, (result.stderr[:2000] if result.returncode != 0 else None)


# ---------- transformations ----------

class PyRenameOneIdentifier(cst.CSTTransformer):
    """Rename the first user-defined Name assigned via a simple assignment."""

    def __init__(self):
        self.target = None
        self.done = False

    def leave_Name(self, original_node, updated_node):
        if self.target and updated_node.value == self.target:
            return updated_node.with_changes(value=f"{self.target}_renamed")
        return updated_node


def find_first_assigned_name(code):
    try:
        tree = cst.parse_module(code)
    except Exception:
        return None
    found = {}

    class Finder(cst.CSTVisitor):
        def visit_Assign(self, node):
            if not found and len(node.targets) == 1:
                t = node.targets[0].target
                if isinstance(t, cst.Name) and not t.value.startswith("_"):
                    found["name"] = t.value

    tree.visit(Finder())
    return found.get("name")


def transform_lexical_rename_python(code):
    name = find_first_assigned_name(code)
    if not name:
        return None, "NO_IDENTIFIER_FOUND"
    try:
        tree = cst.parse_module(code)
    except Exception as e:
        return None, f"PARSE_FAILED: {e}"
    transformer = PyRenameOneIdentifier()
    transformer.target = name
    new_tree = tree.visit(transformer)
    return new_tree.code, None


def transform_lexical_rename_java(code):
    # Rename the first local variable declared via a simple `Type name =` pattern.
    m = re.search(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*=\s*[^=]", code)
    if not m:
        return None, "NO_IDENTIFIER_FOUND"
    name = m.group(1)
    if len(name) < 2 or name in {"if", "for", "while", "return"}:
        return None, "NO_IDENTIFIER_FOUND"
    new_name = f"{name}_renamed"
    new_code = re.sub(rf"\b{re.escape(name)}\b", new_name, code)
    return new_code, None


def transform_formatting_python(code):
    try:
        return black.format_str(code, mode=black.Mode()), None
    except Exception as e:
        return None, f"FORMAT_FAILED: {e}"


def transform_formatting_java(code):
    with tempfile.TemporaryDirectory() as td:
        path = os.path.join(td, "In.java")
        with open(path, "w", encoding="utf-8") as f:
            f.write(code)
        result = subprocess.run(
            [f"{JDK_BIN}/java", "-jar", GJF_JAR, path],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            return None, f"FORMAT_FAILED: {result.stderr[:1000]}"
        return result.stdout, None


FOR_WHILE_PY_RE = re.compile(
    r"for (\w+) in range\((.+?)\):\n((?:[ \t]+.*\n?)+)"
)


def transform_control_flow_python(code):
    m = FOR_WHILE_PY_RE.search(code)
    if not m:
        return None, "NO_MATCHING_FOR_LOOP"
    var, rng, body = m.group(1), m.group(2), m.group(3)
    indent_match = re.match(r"([ \t]+)", body)
    indent = indent_match.group(1) if indent_match else "    "
    parts = [p.strip() for p in rng.split(",")]
    start = parts[0] if len(parts) > 1 else "0"
    stop = parts[1] if len(parts) > 1 else parts[0]
    step = parts[2] if len(parts) > 2 else "1"
    replacement = (
        f"{var} = {start}\n"
        f"while {var} < ({stop}):\n"
        f"{body}"
        f"{indent}{var} += {step}\n"
    )
    new_code = code[: m.start()] + replacement + code[m.end():]
    return new_code, None


FOR_JAVA_RE = re.compile(
    r"for\s*\(\s*(?:int\s+)?(\w+)\s*=\s*([^;]+);\s*\1\s*<\s*([^;]+);\s*\1\s*(\+\+|\+=\s*(\d+))\s*\)\s*\{"
)


def transform_control_flow_java(code):
    m = FOR_JAVA_RE.search(code)
    if not m:
        return None, "NO_MATCHING_FOR_LOOP"
    var, start, bound = m.group(1), m.group(2), m.group(3)
    step = "1" if m.group(3) is None or "++" in (m.group(3) or "") else (m.group(4) or "1")
    # find matching closing brace for this for-block (naive depth counter)
    open_idx = code.index("{", m.end() - 1)
    depth = 0
    i = open_idx
    while i < len(code):
        if code[i] == "{":
            depth += 1
        elif code[i] == "}":
            depth -= 1
            if depth == 0:
                break
        i += 1
    if depth != 0:
        return None, "UNBALANCED_BRACES"
    body = code[open_idx + 1 : i]
    replacement = (
        f"int {var} = {start};\n"
        f"while ({var} < {bound}) {{"
        f"{body}"
        f"{var} += {step};\n"
        f"}}"
    )
    new_code = code[: m.start()] + replacement + code[i + 1 :]
    return new_code, None


TRANSFORMS = {
    "Python": {
        "lexical_rename": transform_lexical_rename_python,
        "formatting": transform_formatting_python,
        "control_flow": transform_control_flow_python,
    },
    "Java": {
        "lexical_rename": transform_lexical_rename_java,
        "formatting": transform_formatting_java,
        "control_flow": transform_control_flow_java,
    },
}

VALIDATORS = {"Python": validate_python, "Java": validate_java}
AST_COUNTERS = {"Python": approx_ast_node_count_python, "Java": approx_ast_node_count_java}


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    rows = [json.loads(l) for l in open("artifacts/pilot_manifest.jsonl", encoding="utf-8")]

    logs = []
    for row in rows:
        lang = row["language"]
        sid = row["sample_id"]
        code0 = row["code"]

        base_ok, base_err = VALIDATORS[lang](code0)
        base_ast = AST_COUNTERS[lang](code0)

        for family, fn in TRANSFORMS[lang].items():
            log = {
                "sample_id": sid,
                "language": lang,
                "label": row["label"],
                "model_family": row["model_family"],
                "transformation_family": family,
                "intensity": "low",
                "c0_valid": base_ok,
                "c0_valid_error": base_err,
            }
            try:
                new_code, err = fn(code0)
            except Exception as e:
                new_code, err = None, f"EXCEPTION: {e}"

            if new_code is None:
                log.update({"status": "TRANSFORM_FAILED", "error": err})
                logs.append(log)
                continue

            valid, verr = VALIDATORS[lang](new_code)
            status = "OK" if valid else "VALIDATION_FAILED"

            out_ext = "py" if lang == "Python" else "java"
            out_path = f"{OUT_DIR}/{sid}__{family}.{out_ext}"
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(new_code)

            new_ast = AST_COUNTERS[lang](new_code) if valid else None

            log.update(
                {
                    "status": status,
                    "error": verr,
                    "output_path": out_path,
                    "token_distance": token_distance(code0, new_code),
                    "char_edit_distance": char_edit_distance(code0, new_code),
                    "ast_node_count_c0": base_ast,
                    "ast_node_count_transformed": new_ast,
                    "ast_node_count_delta": (new_ast - base_ast) if (base_ast is not None and new_ast is not None) else None,
                }
            )
            logs.append(log)

    with open(LOG_PATH, "w", encoding="utf-8") as f:
        for log in logs:
            f.write(json.dumps(log, ensure_ascii=False) + "\n")

    ok = sum(1 for l in logs if l["status"] == "OK")
    print(f"{ok}/{len(logs)} transform rows OK")
    from collections import Counter

    print(Counter((l["language"], l["transformation_family"], l["status"]) for l in logs))


if __name__ == "__main__":
    main()
