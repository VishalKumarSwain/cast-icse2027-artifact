"""PROD_004 canonicalizer: whitespace/comment/quote-invariant token-joined
form, per docs/PROD_004_PROTOCOL.md. Reuses this study's existing tokenizers.
"""
import io
import re
import tokenize


def canonicalize_python(code):
    try:
        tokens = []
        for tok in tokenize.generate_tokens(io.StringIO(code).readline):
            if tok.type in (
                tokenize.ENCODING, tokenize.ENDMARKER, tokenize.COMMENT,
                tokenize.NL, tokenize.NEWLINE, tokenize.INDENT, tokenize.DEDENT,
            ):
                continue
            s = tok.string
            if tok.type == tokenize.STRING:
                if s[:1] in ("'", '"') or s[:2].lower() in ("r'", 'r"', "f'", 'f"', "b'", 'b"'):
                    prefix_match = re.match(r"^[a-zA-Z]*", s)
                    prefix = prefix_match.group(0) if prefix_match else ""
                    body = s[len(prefix):]
                    if body.startswith("'''") or body.startswith('"""'):
                        inner = body[3:-3]
                        s = f'{prefix}"""{inner}"""'
                    elif body.startswith("'") or body.startswith('"'):
                        inner = body[1:-1]
                        inner = inner.replace('"', '\\"').replace("\\'", "'")
                        s = f'{prefix}"{inner}"'
            tokens.append(s)
        return " ".join(tokens)
    except (tokenize.TokenizeError, IndentationError, SyntaxError):
        return None


def canonicalize_java(code):
    import tree_sitter_java as tsjava
    from tree_sitter import Language, Parser

    lang = Language(tsjava.language())
    parser = Parser(lang)
    tree = parser.parse(code.encode())
    tokens = []
    comment_types = {"comment", "line_comment", "block_comment"}

    def walk(node):
        if len(node.children) == 0:
            if node.type not in comment_types:
                tokens.append(node.text.decode(errors="replace"))
            return
        for c in node.children:
            walk(c)

    walk(tree.root_node)
    return " ".join(tokens)


def canonicalize(code, language):
    if language == "Python":
        return canonicalize_python(code)
    elif language == "Java":
        return canonicalize_java(code)
    raise ValueError(language)
