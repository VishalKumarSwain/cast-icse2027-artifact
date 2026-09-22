"""Three explicitly separated distance measures, replacing the collapsed
whitespace-split `token_distance` used in PILOT_002-PILOT_004 (see
docs/PILOT_004_FORENSIC_FORMATTING.md for why that metric was blind to
indentation/blank-line changes).

  d_text  : raw character-level distance (presentation-level: indentation
            width, blank lines, quote style -- anything textual).
  d_token : lexical/token-stream distance using a real tokenizer (Python's
            `tokenize` module, which emits INDENT/DEDENT/NEWLINE/NL as real
            tokens; tree-sitter leaf tokens for Java).
  d_ast   : structural distance (kept as the existing AST-node-count delta
            approximation; not changed by this fix).

Hierarchy: Textual -> Lexical -> Structural -> Behavioral. A pure formatting
transformation can and should show d_text > 0 with d_ast = 0 -- that is the
correct representation of the PILOT_004 formatting finding, not something to
collapse into a single number.
"""
import difflib
import io
import tokenize


def d_text(a, b):
    sm = difflib.SequenceMatcher(a=a, b=b, autojunk=False)
    matches = sum(block.size for block in sm.get_matching_blocks())
    return max(len(a), len(b)) - matches


def _python_token_stream(code):
    tokens = []
    try:
        for tok in tokenize.generate_tokens(io.StringIO(code).readline):
            if tok.type in (tokenize.ENCODING, tokenize.ENDMARKER):
                continue
            # keep INDENT/DEDENT/NEWLINE/NL as real tokens (this is the whole
            # point -- the old whitespace-split metric discarded exactly these)
            tokens.append((tokenize.tok_name[tok.type], tok.string))
    except (tokenize.TokenizeError, IndentationError, SyntaxError):
        return None
    return tokens


def d_token_python(a, b):
    ta, tb = _python_token_stream(a), _python_token_stream(b)
    if ta is None or tb is None:
        return None
    sm = difflib.SequenceMatcher(a=ta, b=tb, autojunk=False)
    matches = sum(block.size for block in sm.get_matching_blocks())
    return max(len(ta), len(tb)) - matches


def _java_token_stream(code):
    import tree_sitter_java as tsjava
    from tree_sitter import Language, Parser

    lang = Language(tsjava.language())
    parser = Parser(lang)
    tree = parser.parse(code.encode())
    tokens = []

    def walk(node):
        if len(node.children) == 0:  # leaf token
            tokens.append((node.type, node.text.decode(errors="replace")))
        for c in node.children:
            walk(c)

    walk(tree.root_node)
    return tokens


def d_token_java(a, b):
    ta, tb = _java_token_stream(a), _java_token_stream(b)
    sm = difflib.SequenceMatcher(a=ta, b=tb, autojunk=False)
    matches = sum(block.size for block in sm.get_matching_blocks())
    return max(len(ta), len(tb)) - matches


def d_token(a, b, language):
    if language == "Python":
        return d_token_python(a, b)
    elif language == "Java":
        return d_token_java(a, b)
    raise ValueError(f"unsupported language: {language}")
