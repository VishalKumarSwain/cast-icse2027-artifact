"""PILOT_002: fragment-aware Java validation + CST-based Python control-flow
rewrite + three-outcome status model (SUCCESS / NOT_APPLICABLE /
VALIDATION_FAILED / TRANSFORM_ERROR).

Does not touch PILOT_001's outputs (artifacts/pilot_transform_log.jsonl,
artifacts/transformed/) -- writes to separate v2 paths so PILOT_001 remains
as evidence of why the validation protocol changed.

Java validation policy (source-kind aware, tiered):
  c0_parse_valid            : tree-sitter parses with no ERROR node (structural)
  c0_native_compile_valid   : javac compiles the snippet as-is
  wrapper_used              : True if a synthetic harness class was needed
  c0_wrapped_compile_valid  : javac compiles the snippet inside a synthetic wrapper
  validation_status         : STANDALONE_VALID > WRAPPER_VALID > STRUCTURAL_ONLY > PARSE_INVALID
The wrapper is a validation instrument ONLY -- detector input is always the
original, unwrapped snippet text.

Python control-flow rewrite is now CST-based (libcst), replacing the pilot's
regex/string-splice implementation to remove the indentation defect found in
PILOT_001.
"""
import difflib
import json
import os
import re
import subprocess
import tempfile

import black
import libcst as cst
from libcst import FlattenSentinel, RemovalSentinel

GJF_JAR = "/data/aihuman/tools/gjf/gjf.jar"
JDK_BIN = "/data/aihuman/tools/jdk17/bin"

OUT_DIR = "artifacts/transformed_v2"
WRAPPER_DIR = "artifacts/java_wrappers_v2"  # validation instrument only, never detector input
LOG_PATH = "artifacts/pilot_transform_log_v2.jsonl"

STANDALONE_SOURCES = {"TACO", "LEETCODE", "CODEFORCES", "ATCODER"}


# ---------- distance metrics ----------

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


# ---------- Python validation (unchanged: compile() is a sufficient gate) ----------

def validate_python(code):
    try:
        compile(code, "<pilot>", "exec")
        return True, None
    except SyntaxError as e:
        return False, str(e)


# ---------- Java tiered, fragment-aware validation ----------

def _java_tree_sitter_parse_ok(code):
    import tree_sitter_java as tsjava
    from tree_sitter import Language, Parser

    lang = Language(tsjava.language())
    parser = Parser(lang)
    tree = parser.parse(code.encode())

    def has_error(node):
        if node.type == "ERROR" or node.is_missing:
            return True
        return any(has_error(c) for c in node.children)

    return not has_error(tree.root_node)


def _javac_compile(code, workdir):
    m = re.search(r"\bclass\s+(\w+)", code)
    fname = m.group(1) if m else "Pilot"
    path = os.path.join(workdir, f"{fname}.java")
    with open(path, "w", encoding="utf-8") as f:
        f.write(code)
    result = subprocess.run(
        [f"{JDK_BIN}/javac", "-d", workdir, path],
        capture_output=True,
        text=True,
        timeout=30,
    )
    return result.returncode == 0, (result.stderr[:2000] if result.returncode != 0 else None)


JAVA_WRAPPER_TEMPLATE_VERSION = "v1"


def _wrap_java_fragment(code, sample_id):
    """Best-effort synthetic harness: wraps a bare function/statement fragment
    in a minimal class so javac can attempt compilation. Returns None if the
    fragment already looks like a full compilation unit (has its own class)."""
    if re.search(r"\bclass\s+\w+", code):
        return None
    wrapped = (
        "import java.util.*;\n"
        "import java.io.*;\n\n"
        f"class PilotWrapper_{sample_id} {{\n"
        f"{code}\n"
        "}\n"
    )
    return wrapped


def validate_java(code, sample_id, source):
    is_standalone_source = source in STANDALONE_SOURCES

    parse_valid = _java_tree_sitter_parse_ok(code)

    native_compile_valid = None
    with tempfile.TemporaryDirectory() as td:
        native_compile_valid, native_err = _javac_compile(code, td)

    wrapper_used = False
    wrapped_compile_valid = None
    wrapper_code = None
    if not native_compile_valid:
        wrapper_code = _wrap_java_fragment(code, sample_id)
        if wrapper_code is not None:
            wrapper_used = True
            with tempfile.TemporaryDirectory() as td:
                wrapped_compile_valid, wrapped_err = _javac_compile(wrapper_code, td)

    if native_compile_valid:
        status = "STANDALONE_VALID"
    elif wrapped_compile_valid:
        status = "WRAPPER_VALID"
    elif parse_valid:
        status = "STRUCTURAL_ONLY"
    else:
        status = "PARSE_INVALID"

    return {
        "source_kind": "standalone_source" if is_standalone_source else "fragment_source",
        "c0_parse_valid": parse_valid,
        "c0_native_compile_valid": bool(native_compile_valid),
        "wrapper_used": wrapper_used,
        "wrapper_template_version": JAVA_WRAPPER_TEMPLATE_VERSION if wrapper_used else None,
        "c0_wrapped_compile_valid": bool(wrapped_compile_valid) if wrapper_used else None,
        "validation_status": status,
        "wrapper_code": wrapper_code,  # validation instrument only; never written as detector input
    }


# ---------- transformations: lexical rename (unchanged logic, reclassified outcomes) ----------

class PyRenameOneIdentifier(cst.CSTTransformer):
    def __init__(self, target):
        self.target = target

    def leave_Name(self, original_node, updated_node):
        if updated_node.value == self.target:
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
        return None, "NOT_APPLICABLE"
    try:
        tree = cst.parse_module(code)
    except Exception as e:
        return None, f"TRANSFORM_ERROR: {e}"
    new_tree = tree.visit(PyRenameOneIdentifier(name))
    return new_tree.code, None


def transform_lexical_rename_java(code):
    m = re.search(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*=\s*[^=]", code)
    if not m or len(m.group(1)) < 2 or m.group(1) in {"if", "for", "while", "return"}:
        return None, "NOT_APPLICABLE"
    name = m.group(1)
    new_code = re.sub(rf"\b{re.escape(name)}\b", f"{name}_renamed", code)
    return new_code, None


# ---------- transformations: formatting (unchanged) ----------

def transform_formatting_python(code):
    try:
        return black.format_str(code, mode=black.Mode()), None
    except Exception as e:
        return None, f"NOT_APPLICABLE: {e}"  # unparseable-by-black input, not a pipeline bug


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
            return None, "NOT_APPLICABLE"
        return result.stdout, None


# ---------- transformations: control-flow, Python now CST-based ----------

class PyForRangeToWhile(cst.CSTTransformer):
    """Rewrites the first top-level-in-its-block `for x in range(...): body`
    into `x = start; while x < stop: body; x += step`, using CST node
    replacement so indentation is handled by libcst, not string-splicing."""

    def __init__(self):
        self.done = False

    def leave_For(self, original_node, updated_node):
        if self.done:
            return updated_node
        it = updated_node.iter
        if not (isinstance(it, cst.Call) and isinstance(it.func, cst.Name) and it.func.value == "range"):
            return updated_node
        if not isinstance(updated_node.target, cst.Name):
            return updated_node

        args = [a.value for a in it.args]
        if len(args) == 1:
            start_expr, stop_expr, step_expr = cst.Integer("0"), args[0], cst.Integer("1")
        elif len(args) == 2:
            start_expr, stop_expr, step_expr = args[0], args[1], cst.Integer("1")
        elif len(args) == 3:
            start_expr, stop_expr, step_expr = args[0], args[1], args[2]
        else:
            return updated_node

        var = updated_node.target
        assign = cst.SimpleStatementLine(
            body=[cst.Assign(targets=[cst.AssignTarget(target=var)], value=start_expr)]
        )
        increment = cst.SimpleStatementLine(
            body=[cst.AugAssign(target=var, operator=cst.AddAssign(), value=step_expr)]
        )
        new_body_stmts = list(updated_node.body.body) + [increment]
        while_stmt = cst.While(
            test=cst.Comparison(
                left=var,
                comparisons=[cst.ComparisonTarget(operator=cst.LessThan(), comparator=stop_expr)],
            ),
            body=updated_node.body.with_changes(body=new_body_stmts),
        )
        self.done = True
        return FlattenSentinel([assign, while_stmt])


def transform_control_flow_python(code):
    try:
        tree = cst.parse_module(code)
    except Exception as e:
        return None, f"NOT_APPLICABLE: C0 does not parse ({e})"
    transformer = PyForRangeToWhile()
    new_tree = tree.visit(transformer)
    if not transformer.done:
        return None, "NOT_APPLICABLE"
    return new_tree.code, None


FOR_JAVA_RE = re.compile(
    r"for\s*\(\s*(?:int\s+)?(\w+)\s*=\s*([^;]+);\s*\1\s*<\s*([^;]+);\s*\1\s*(\+\+|\+=\s*(\d+))\s*\)\s*\{"
)


def transform_control_flow_java(code):
    m = FOR_JAVA_RE.search(code)
    if not m:
        return None, "NOT_APPLICABLE"
    var, start, bound = m.group(1), m.group(2), m.group(3)
    step = "1" if "++" in (m.group(4) or "") else (m.group(5) or "1")
    open_idx = code.index("{", m.end() - 1)
    depth, i = 0, open_idx
    while i < len(code):
        if code[i] == "{":
            depth += 1
        elif code[i] == "}":
            depth -= 1
            if depth == 0:
                break
        i += 1
    if depth != 0:
        return None, "TRANSFORM_ERROR: unbalanced braces"
    body = code[open_idx + 1 : i]
    replacement = f"int {var} = {start};\nwhile ({var} < {bound}) {{{body}{var} += {step};\n}}"
    return code[: m.start()] + replacement + code[i + 1 :], None


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

AST_COUNTERS = {"Python": approx_ast_node_count_python, "Java": approx_ast_node_count_java}


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(WRAPPER_DIR, exist_ok=True)
    rows = [json.loads(l) for l in open("artifacts/pilot_manifest.jsonl", encoding="utf-8")]

    logs = []
    for row in rows:
        lang = row["language"]
        sid = row["sample_id"]
        code0 = row["code"]
        source = row["source"]

        if lang == "Python":
            c0_valid, c0_err = validate_python(code0)
            c0_meta = {"c0_valid": c0_valid, "c0_valid_error": c0_err}
        else:
            jv = validate_java(code0, sid, source)
            c0_meta = jv
            wrapper_path = None
            if jv["wrapper_used"] and jv["wrapper_code"]:
                wrapper_path = f"{WRAPPER_DIR}/{sid}__c0_wrapper.java"
                with open(wrapper_path, "w", encoding="utf-8") as f:
                    f.write(jv["wrapper_code"])
            c0_meta = {k: v for k, v in jv.items() if k != "wrapper_code"}
            c0_meta["wrapper_path"] = wrapper_path

        base_ast = AST_COUNTERS[lang](code0)

        for family, fn in TRANSFORMS[lang].items():
            log = {
                "sample_id": sid,
                "language": lang,
                "label": row["label"],
                "model_family": row["model_family"],
                "source": source,
                "transformation_family": family,
                "intensity": "low",
                **c0_meta,
            }
            try:
                new_code, err = fn(code0)
            except Exception as e:
                new_code, err = None, f"TRANSFORM_ERROR: {e}"

            if new_code is None:
                status = "NOT_APPLICABLE" if (err or "").startswith("NOT_APPLICABLE") else "TRANSFORM_ERROR"
                log.update({"status": status, "error": err})
                logs.append(log)
                continue

            if lang == "Python":
                t_valid, t_err = validate_python(new_code)
                status = "SUCCESS" if t_valid else "VALIDATION_FAILED"
                log["transform_valid"] = t_valid
                log["transform_valid_error"] = t_err
            else:
                tjv = validate_java(new_code, sid + "_t", source)
                # transformed code must reach at least the same validation tier as C0
                tier_order = {"PARSE_INVALID": 0, "STRUCTURAL_ONLY": 1, "WRAPPER_VALID": 2, "STANDALONE_VALID": 3}
                c0_tier = tier_order.get(c0_meta.get("validation_status"), 0)
                t_tier = tier_order.get(tjv["validation_status"], 0)
                status = "SUCCESS" if t_tier >= c0_tier and t_tier >= 1 else "VALIDATION_FAILED"
                t_wrapper_path = None
                if tjv["wrapper_used"] and tjv["wrapper_code"]:
                    t_wrapper_path = f"{WRAPPER_DIR}/{sid}__{family}_wrapper.java"
                    with open(t_wrapper_path, "w", encoding="utf-8") as f:
                        f.write(tjv["wrapper_code"])
                log["transform_parse_valid"] = tjv["c0_parse_valid"]
                log["transform_native_compile_valid"] = tjv["c0_native_compile_valid"]
                log["transform_wrapper_used"] = tjv["wrapper_used"]
                log["transform_wrapped_compile_valid"] = tjv["c0_wrapped_compile_valid"]
                log["transform_wrapper_path"] = t_wrapper_path
                log["transform_validation_status"] = tjv["validation_status"]

            out_ext = "py" if lang == "Python" else "java"
            out_path = f"{OUT_DIR}/{sid}__{family}.{out_ext}"
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(new_code)  # always the raw snippet; wrapper never used as detector input

            new_ast = AST_COUNTERS[lang](new_code) if status == "SUCCESS" else None
            log.update(
                {
                    "status": status,
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

    from collections import Counter

    attempted = len(logs)
    applicable = sum(1 for l in logs if l["status"] != "NOT_APPLICABLE")
    success = sum(1 for l in logs if l["status"] == "SUCCESS")
    print(f"attempted={attempted} applicable={applicable} success={success}")
    print(f"ApplicabilityRate={applicable/attempted:.2f} TransformationSuccessRate={(success/applicable if applicable else 0):.2f}")
    print(Counter((l["language"], l["transformation_family"], l["status"]) for l in logs))
    print("Java C0 validation_status distribution:", Counter(l["validation_status"] for l in logs if l["language"] == "Java"))


if __name__ == "__main__":
    main()
