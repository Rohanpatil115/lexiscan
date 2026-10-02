"""
lexer.py
========
Core lexical analysis engine for LexiScan.

Implements a hand-written scanner that reads source code from left to right,
applies the longest-match (maximal-munch) principle, and classifies each
lexeme into a token category using the rules defined in token_rules.py.

Each token is a dict with the fields:
    lexeme   – the actual matched text
    token    – token type name (e.g. KEYWORD, IDENTIFIER)
    category – human-readable category (e.g. Keyword, Identifier)
    line     – 1-based source line number
    column   – 1-based column where the lexeme starts
    status   – "Valid" | "Error"
"""

from __future__ import annotations
from typing import TypedDict

import token_rules as rules


# ─── Token data structure ─────────────────────────────────────────────────────

class Token(TypedDict):
    lexeme:   str
    token:    str
    category: str
    line:     int
    column:   int
    status:   str


def _make_token(
    lexeme:  str,
    token:   str,
    line:    int,
    column:  int,
) -> Token:
    """Construct a Token dict."""
    status   = "Error" if token == "UNKNOWN" else "Valid"
    category = rules.TOKEN_NAMES.get(token, "Unknown")
    return Token(
        lexeme=lexeme,
        token=token,
        category=category,
        line=line,
        column=column,
        status=status,
    )


# ─── Main lexer function ──────────────────────────────────────────────────────

def tokenize(source: str) -> list[Token]:
    """
    Scan *source* and return a list of Token dicts.

    Algorithm (simplified):
        1. Maintain a cursor (pos) and a (line, col) tracker.
        2. At each position try patterns in a fixed priority order.
        3. Always try the longest possible match first (maximal munch).
        4. Advance the cursor by the length of the matched lexeme.
        5. Unknown characters are emitted as UNKNOWN tokens (lexical errors).
    """
    tokens: list[Token] = []
    pos    = 0
    line   = 1
    col    = 1
    src    = source

    def advance(length: int, matched_text: str) -> None:
        """Update pos, line, col after consuming *length* characters."""
        nonlocal pos, line, col
        for ch in matched_text:
            if ch == "\n":
                line += 1
                col   = 1
            else:
                col  += 1
        pos += length

    while pos < len(src):
        # ── Skip whitespace ────────────────────────────────────────────────
        if src[pos] in " \t\r\n":
            ch = src[pos]
            # Track newlines before advancing
            if ch == "\n":
                line += 1
                col   = 1
            else:
                col  += 1
            pos += 1
            continue

        start_line = line
        start_col  = col

        rest = src[pos:]

        # ── Multi-line comment /* … */ ─────────────────────────────────────
        m = rules.PATTERN_COMMENT_MULTI.match(rest)
        if m:
            lexeme = m.group(0)
            tokens.append(_make_token(lexeme, "COMMENT", start_line, start_col))
            advance(len(lexeme), lexeme)
            continue

        # ── Single-line comment // … ───────────────────────────────────────
        m = rules.PATTERN_COMMENT_SINGLE.match(rest)
        if m:
            lexeme = m.group(0)
            tokens.append(_make_token(lexeme, "COMMENT", start_line, start_col))
            advance(len(lexeme), lexeme)
            continue

        # ── String literal "…" ─────────────────────────────────────────────
        m = rules.PATTERN_STRING.match(rest)
        if m:
            lexeme = m.group(0)
            tokens.append(_make_token(lexeme, "STRING", start_line, start_col))
            advance(len(lexeme), lexeme)
            continue

        # ── Operators (longest-match via ordered list) ─────────────────────
        matched_op = False
        for op_text, op_token in rules.ALL_OPERATORS:
            if rest.startswith(op_text):
                tokens.append(_make_token(op_text, op_token, start_line, start_col))
                advance(len(op_text), op_text)
                matched_op = True
                break
        if matched_op:
            continue

        # ── Separator ──────────────────────────────────────────────────────
        if src[pos] in rules.SEPARATORS:
            ch = src[pos]
            tokens.append(_make_token(ch, "SEPARATOR", start_line, start_col))
            advance(1, ch)
            continue

        # ── Float (must be tried before integer) ──────────────────────────
        m = rules.PATTERN_FLOAT.match(rest)
        if m:
            lexeme = m.group(0)
            tokens.append(_make_token(lexeme, "FLOAT", start_line, start_col))
            advance(len(lexeme), lexeme)
            continue

        # ── Integer ───────────────────────────────────────────────────────
        m = rules.PATTERN_INTEGER.match(rest)
        if m:
            lexeme = m.group(0)
            tokens.append(_make_token(lexeme, "INTEGER", start_line, start_col))
            advance(len(lexeme), lexeme)
            continue

        # ── Identifier / Keyword ──────────────────────────────────────────
        m = rules.PATTERN_IDENTIFIER.match(rest)
        if m:
            lexeme = m.group(0)
            tok = "KEYWORD" if lexeme in rules.KEYWORDS else "IDENTIFIER"
            tokens.append(_make_token(lexeme, tok, start_line, start_col))
            advance(len(lexeme), lexeme)
            continue

        # ── Unknown character (lexical error) ─────────────────────────────
        ch = src[pos]
        tokens.append(_make_token(ch, "UNKNOWN", start_line, start_col))
        advance(1, ch)

    return tokens
