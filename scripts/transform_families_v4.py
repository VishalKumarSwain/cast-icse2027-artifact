"""PROD_003: local_structural and deep_semantic transformation families, per
docs/PROD_003_PROTOCOL.md. LOW/HIGH intensity. Reuses (imports, does not
modify) PILOT_002's validation functions.

Safety design note (why these specific rewrites are safe-by-construction
rather than needing full data-flow analysis): both families restrict
applicability to patterns where correctness follows from the rewrite's
structure itself, and rely on the existing tiered parse/compile validation
gate to reject any instance where that assumption doesn't hold (e.g. a
Java lambda capturing a non-effectively-final variable simply fails to
compile, and is caught the same way any other VALIDATION_FAILED is).
"""
import re

import libcst as cst
from libcst import FlattenSentinel


# ---------------------------------------------------------------------------
# Python: local structural (extract-method via nested-function-closure)
# ---------------------------------------------------------------------------

def _is_bare_expr_stmt(stmt):
    return (
        isinstance(stmt, cst.SimpleStatementLine)
        and len(stmt.body) == 1
        and isinstance(stmt.body[0], cst.Expr)
    )


def _find_eligible_runs(body_stmts, min_len=3):
    runs = []
    i = 0
    n = len(body_stmts)
    while i < n:
        if _is_bare_expr_stmt(body_stmts[i]):
            j = i
            while j < n and _is_bare_expr_stmt(body_stmts[j]):
                j += 1
            if j - i >= min_len:
                runs.append((i, j))
            i = j
        else:
            i += 1
    return runs


class PyExtractMethod(cst.CSTTransformer):
    def __init__(self, max_extractions):
        self.max_extractions = max_extractions
        self.count = 0

    def leave_FunctionDef(self, original_node, updated_node):
        if self.count >= self.max_extractions:
            return updated_node
        body = updated_node.body
        if not isinstance(body, cst.IndentedBlock):
            return updated_node
        stmts = list(body.body)
        runs = _find_eligible_runs(stmts)
        if not runs:
            return updated_node

        start, end = runs[0]
        helper_name = f"_extracted_{self.count}"
        helper_def = cst.FunctionDef(
            name=cst.Name(helper_name),
            params=cst.Parameters(),
            body=cst.IndentedBlock(body=stmts[start:end]),
        )
        call_stmt = cst.SimpleStatementLine(
            body=[cst.Expr(value=cst.Call(func=cst.Name(helper_name)))]
        )
        new_stmts = stmts[:start] + [helper_def, call_stmt] + stmts[end:]
        self.count += 1
        return updated_node.with_changes(body=body.with_changes(body=new_stmts))


def transform_local_structural_python(code, intensity):
    try:
        tree = cst.parse_module(code)
    except Exception as e:
        return None, f"NOT_APPLICABLE: C0 does not parse ({e})"
    max_extractions = 1 if intensity == "low" else 3
    transformer = PyExtractMethod(max_extractions)
    new_tree = tree.visit(transformer)
    if transformer.count == 0:
        return None, "NOT_APPLICABLE"
    return new_tree.code, None


# ---------------------------------------------------------------------------
# Python: deep semantic-preserving (accumulator->comprehension + De Morgan)
# ---------------------------------------------------------------------------

class PyAccumulatorToComprehension(cst.CSTTransformer):
    """Rewrites:
        X = []
        for V in ITER:
            X.append(EXPR)
    into:
        X = [EXPR for V in ITER]
    Safe because it only fires when the loop body is EXACTLY one append call
    onto the immediately-preceding freshly-initialized empty list -- no other
    statement can depend on incremental state of X during the loop.
    """

    def __init__(self):
        self.done = False

    def leave_IndentedBlock(self, original_node, updated_node):
        stmts = list(updated_node.body)
        for i in range(len(stmts) - 1):
            init, loop = stmts[i], stmts[i + 1]
            if self.done:
                break
            if not (
                isinstance(init, cst.SimpleStatementLine)
                and len(init.body) == 1
                and isinstance(init.body[0], cst.Assign)
                and len(init.body[0].targets) == 1
                and isinstance(init.body[0].targets[0].target, cst.Name)
                and isinstance(init.body[0].value, cst.List)
                and len(init.body[0].value.elements) == 0
            ):
                continue
            list_name = init.body[0].targets[0].target.value
            if not isinstance(loop, cst.For):
                continue
            loop_body_stmts = loop.body.body if isinstance(loop.body, cst.IndentedBlock) else None
            if not loop_body_stmts or len(loop_body_stmts) != 1:
                continue
            single = loop_body_stmts[0]
            if not (
                isinstance(single, cst.SimpleStatementLine)
                and len(single.body) == 1
                and isinstance(single.body[0], cst.Expr)
                and isinstance(single.body[0].value, cst.Call)
                and isinstance(single.body[0].value.func, cst.Attribute)
                and single.body[0].value.func.attr.value == "append"
                and isinstance(single.body[0].value.func.value, cst.Name)
                and single.body[0].value.func.value.value == list_name
                and len(single.body[0].value.args) == 1
            ):
                continue

            expr = single.body[0].value.args[0].value
            comp = cst.ListComp(
                elt=expr,
                for_in=cst.CompFor(target=loop.target, iter=loop.iter),
            )
            new_assign = cst.SimpleStatementLine(
                body=[cst.Assign(targets=[cst.AssignTarget(target=cst.Name(list_name))], value=comp)]
            )
            new_stmts = stmts[:i] + [new_assign] + stmts[i + 2 :]
            self.done = True
            return updated_node.with_changes(body=new_stmts)
        return updated_node


DE_MORGAN_AND_RE = re.compile(r"not\s*\(\s*([^()]+?)\s+and\s+([^()]+?)\s*\)")
DE_MORGAN_OR_RE = re.compile(r"not\s*\(\s*([^()]+?)\s+or\s+([^()]+?)\s*\)")


def _apply_de_morgan(code):
    m = DE_MORGAN_AND_RE.search(code)
    if m:
        a, b = m.group(1).strip(), m.group(2).strip()
        return code[: m.start()] + f"(not {a}) or (not {b})" + code[m.end() :], True
    m = DE_MORGAN_OR_RE.search(code)
    if m:
        a, b = m.group(1).strip(), m.group(2).strip()
        return code[: m.start()] + f"(not {a}) and (not {b})" + code[m.end() :], True
    return code, False


def transform_deep_semantic_python(code, intensity):
    try:
        tree = cst.parse_module(code)
    except Exception as e:
        return None, f"NOT_APPLICABLE: C0 does not parse ({e})"

    transformer = PyAccumulatorToComprehension()
    new_tree = tree.visit(transformer)
    applied_low = transformer.done
    result_code = new_tree.code if applied_low else code

    if intensity == "low":
        if not applied_low:
            return None, "NOT_APPLICABLE"
        return result_code, None

    # HIGH: also attempt De Morgan restructuring; degrade to LOW's result if
    # boolean pattern isn't present (per protocol, not NOT_APPLICABLE)
    result_code2, applied_high = _apply_de_morgan(result_code)
    if not applied_low and not applied_high:
        return None, "NOT_APPLICABLE"
    return result_code2, None


# ---------------------------------------------------------------------------
# Java: local structural (extract-method via Runnable lambda closure)
# ---------------------------------------------------------------------------

JAVA_CALL_STMT_RE = re.compile(r"^[ \t]*[\w.]+\([^;{}]*\)\s*;\s*$")


def _find_eligible_java_runs(lines, min_len=3):
    runs = []
    i = 0
    n = len(lines)
    while i < n:
        if JAVA_CALL_STMT_RE.match(lines[i]):
            j = i
            while j < n and JAVA_CALL_STMT_RE.match(lines[j]):
                j += 1
            if j - i >= min_len:
                runs.append((i, j))
            i = j
        else:
            i += 1
    return runs


def transform_local_structural_java(code, intensity):
    lines = code.split("\n")
    runs = _find_eligible_java_runs(lines)
    if not runs:
        return None, "NOT_APPLICABLE"
    max_extractions = 1 if intensity == "low" else min(3, len(runs))
    new_lines = list(lines)
    offset = 0
    for k, (start, end) in enumerate(runs[:max_extractions]):
        s, e = start + offset, end + offset
        indent_match = re.match(r"^([ \t]*)", new_lines[s])
        indent = indent_match.group(1) if indent_match else ""
        block = new_lines[s:e]
        replacement = (
            [f"{indent}Runnable _extracted_{k} = () -> {{"]
            + block
            + [f"{indent}}};", f"{indent}_extracted_{k}.run();"]
        )
        new_lines = new_lines[:s] + replacement + new_lines[e:]
        offset += len(replacement) - (e - s)
    return "\n".join(new_lines), None


# ---------------------------------------------------------------------------
# Java: deep semantic-preserving (indexed-for -> enhanced-for + De Morgan)
# ---------------------------------------------------------------------------

JAVA_INDEXED_FOR_RE = re.compile(
    r"for\s*\(\s*int\s+(\w+)\s*=\s*0\s*;\s*\1\s*<\s*([\w.]+)\.length\s*;\s*\1\s*\+\+\s*\)\s*\{"
)


def _apply_enhanced_for(code):
    m = JAVA_INDEXED_FOR_RE.search(code)
    if not m:
        return code, False
    var, arr = m.group(1), m.group(2)
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
        return code, False
    body = code[open_idx + 1 : i]
    indexed_access = re.escape(f"{arr}[{var}]")
    if re.search(rf"\b{var}\b", re.sub(indexed_access, "", body)):
        return code, False  # var used for more than indexing -- not a safe rewrite here
    new_body = re.sub(indexed_access, "item", body)
    replacement = f"for (var item : {arr}) {{{new_body}}}"
    return code[: m.start()] + replacement + code[i + 1 :], True


def transform_deep_semantic_java(code, intensity):
    result_low, applied_low = _apply_enhanced_for(code)
    if intensity == "low":
        if not applied_low:
            return None, "NOT_APPLICABLE"
        return result_low, None

    result_high, applied_high = _apply_de_morgan(result_low if applied_low else code)
    if not applied_low and not applied_high:
        return None, "NOT_APPLICABLE"
    return result_high, None
