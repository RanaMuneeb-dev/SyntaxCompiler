import re
from dataclasses import dataclass
from typing import List

# Token types
TT_KEYWORD     = "KEYWORD"
TT_IDENT       = "IDENT"
TT_NUMBER      = "NUMBER"
TT_STRING      = "STRING"
TT_OP          = "OP"
TT_COMPARE     = "COMPARE"
TT_LOGIC_AND   = "LOGIC_AND"
TT_LOGIC_OR    = "LOGIC_OR"
TT_LOGIC_NOT   = "LOGIC_NOT"
TT_ASSIGN      = "ASSIGN"
TT_SEMI        = "SEMI"
TT_LPAREN      = "LPAREN"
TT_RPAREN      = "RPAREN"
TT_LBRACE      = "LBRACE"
TT_RBRACE      = "RBRACE"
TT_COMMA       = "COMMA"
TT_EOF         = "EOF"

# Canonical keyword dictionary (English & Roman Urdu)
KEYWORD_MAP = {
    # English
    "let": "let",
    "print": "print",
    "if": "if",
    "else": "else",
    "while": "while",

    # Roman Urdu
    "rakho": "let",
    "banao": "let",
    "dikhao": "print",
    "bolo": "print",
    "likho": "print",
    "agar": "if",
    "warna": "else",
    "jabtak": "while",
}

# Roman Urdu logical keywords mapping to logical tokens
LOGIC_WORD_MAP = {
    "aur": ("LOGIC_AND", "&&"),
    "ya":  ("LOGIC_OR",  "||"),
    "nahi":("LOGIC_NOT", "!"),
}

TOKEN_SPEC = [
    ("COMMENT_MULTI",  r"/\*[\s\S]*?\*/"),
    ("COMMENT_SINGLE", r"//[^\n]*"),
    ("STRING",         r'"([^"\\]|\\.)*"'),
    ("NUMBER",         r"\d+(\.\d+)?"),
    ("COMPARE",        r"==|!=|<=|>=|<|>"),       # must come BEFORE ASSIGN and LOGIC_NOT
    ("LOGIC_AND",      r"&&"),
    ("LOGIC_OR",       r"\|\|"),
    ("LOGIC_NOT",      r"!"),
    ("ASSIGN",         r"="),
    ("OP",             r"[+\-*/%]"),
    ("SEMI",           r";"),
    ("LPAREN",         r"\("),
    ("RPAREN",         r"\)"),
    ("LBRACE",         r"\{"),
    ("RBRACE",         r"\}"),
    ("COMMA",          r","),
    ("IDENT",          r"[a-zA-Z_][a-zA-Z0-9_]*"),
    ("SKIP",           r"[ \t\n\r]+"),
    ("MISMATCH",       r"."),
]

MASTER = re.compile("|".join(f"(?P<{name}>{pattern})" for name, pattern in TOKEN_SPEC))


@dataclass
class Token:
    type: str
    value: str
    line: int
    col: int
    canonical: str = ""

    def __post_init__(self):
        if not self.canonical:
            self.canonical = self.value

    def __repr__(self):
        return f"Token({self.type}, {self.value!r}, canonical={self.canonical!r}, line={self.line}, col={self.col})"


class LexerError(Exception):
    def __init__(self, message, line, col):
        super().__init__(message)
        self.line = line
        self.col = col


def tokenize(source: str) -> List[Token]:
    tokens = []
    line = 1
    line_start = 0

    for mo in MASTER.finditer(source):
        kind = mo.lastgroup
        value = mo.group()
        col = mo.start() - line_start + 1

        if kind == "SKIP":
            newlines = value.count("\n")
            if newlines:
                line += newlines
                line_start = mo.end() - (len(value) - value.rfind("\n") - 1)
            continue

        if kind in ("COMMENT_SINGLE", "COMMENT_MULTI"):
            newlines = value.count("\n")
            if newlines:
                line += newlines
                line_start = mo.end() - (len(value) - value.rfind("\n") - 1)
            continue

        if kind == "MISMATCH":
            raise LexerError(f"Unexpected character: {value!r}", line, col)

        if kind == "STRING":
            inner = value[1:-1]
            inner = inner.replace('\\"', '"')
            inner = inner.replace('\\n', '\n')
            inner = inner.replace('\\t', '\t')
            inner = inner.replace('\\\\', '\\')
            tokens.append(Token(kind, inner, line, col, canonical=inner))
            continue

        if kind == "IDENT":
            lower_val = value.lower()
            if lower_val in LOGIC_WORD_MAP:
                logic_type, canon = LOGIC_WORD_MAP[lower_val]
                tokens.append(Token(logic_type, value, line, col, canonical=canon))
                continue
            if lower_val in KEYWORD_MAP:
                canon = KEYWORD_MAP[lower_val]
                tokens.append(Token(TT_KEYWORD, value, line, col, canonical=canon))
                continue

        tokens.append(Token(kind, value, line, col, canonical=value))

    tokens.append(Token(TT_EOF, "", line, 0, canonical=""))
    return tokens
