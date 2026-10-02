"""
token_rules.py
==============
Defines keywords, token names, regular expression patterns,
operators, and separators for the LexiScan lexical analyzer.

These patterns represent the regular languages that the lexer uses
to classify lexemes into token categories.
"""

# ─── Keywords ────────────────────────────────────────────────────────────────

KEYWORDS: set[str] = {
    "int", "float", "double", "char", "void",
    "if", "else", "for", "while", "return",
    "class", "public", "private", "static", "const",
    "new", "delete", "break", "continue",
    "switch", "case", "default",
}

# ─── Token category names ─────────────────────────────────────────────────────

TOKEN_NAMES = {
    # Identifiers & Keywords
    "KEYWORD":               "Keyword",
    "IDENTIFIER":            "Identifier",

    # Numeric literals
    "FLOAT":                 "Number",
    "INTEGER":               "Number",

    # String and comment
    "STRING":                "String",
    "COMMENT":               "Comment",

    # Operators
    "ARITHMETIC_OPERATOR":   "Operator",
    "RELATIONAL_OPERATOR":   "Operator",
    "ASSIGNMENT":            "Operator",
    "LOGICAL_OPERATOR":      "Operator",

    # Separators
    "SEPARATOR":             "Separator",

    # Errors
    "UNKNOWN":               "Error",
}

# ─── Operator tables (order matters — longer first) ──────────────────────────

# Multi-character operators must appear before single-character versions.
RELATIONAL_OPERATORS: list[tuple[str, str]] = [
    ("<=", "RELATIONAL_OPERATOR"),
    (">=", "RELATIONAL_OPERATOR"),
    ("==", "RELATIONAL_OPERATOR"),
    ("!=", "RELATIONAL_OPERATOR"),
    ("<",  "RELATIONAL_OPERATOR"),
    (">",  "RELATIONAL_OPERATOR"),
]

LOGICAL_OPERATORS: list[tuple[str, str]] = [
    ("&&", "LOGICAL_OPERATOR"),
    ("||", "LOGICAL_OPERATOR"),
    ("!",  "LOGICAL_OPERATOR"),
]

ARITHMETIC_OPERATORS: list[tuple[str, str]] = [
    ("+", "ARITHMETIC_OPERATOR"),
    ("-", "ARITHMETIC_OPERATOR"),
    ("*", "ARITHMETIC_OPERATOR"),
    ("/", "ARITHMETIC_OPERATOR"),
]

ASSIGNMENT_OPERATORS: list[tuple[str, str]] = [
    ("=", "ASSIGNMENT"),
]

# Ordered operator list used by the lexer for longest-match scanning.
# Multi-character patterns are checked before single-character ones.
ALL_OPERATORS: list[tuple[str, str]] = (
    RELATIONAL_OPERATORS
    + LOGICAL_OPERATORS
    + ARITHMETIC_OPERATORS
    + ASSIGNMENT_OPERATORS
)

# ─── Separators ──────────────────────────────────────────────────────────────

SEPARATORS: set[str] = {"(", ")", "{", "}", "[", "]", ";", ",", "."}

# ─── Regular expression patterns ─────────────────────────────────────────────
# These are the patterns used by the lexer.  They directly correspond to the
# regular languages that each token category recognises.

import re

PATTERN_FLOAT      = re.compile(r"[0-9]+\.[0-9]+")
PATTERN_INTEGER    = re.compile(r"[0-9]+")
PATTERN_IDENTIFIER = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")

# String: double-quoted, no newline inside (simplified)
PATTERN_STRING     = re.compile(r'"[^"\n]*"')

# Comments
PATTERN_COMMENT_SINGLE = re.compile(r"//[^\n]*")
PATTERN_COMMENT_MULTI  = re.compile(r"/\*.*?\*/", re.DOTALL)

# ─── Human-readable pattern descriptions (for the inspector) ──────────────────

PATTERN_DESCRIPTIONS: dict[str, str] = {
    "KEYWORD":             "Reserved word (exact match)",
    "IDENTIFIER":          r"[A-Za-z_][A-Za-z0-9_]*",
    "INTEGER":             r"[0-9]+",
    "FLOAT":               r"[0-9]+\.[0-9]+",
    "STRING":              r'"[^"\n]*"',
    "COMMENT":             r"//[^\n]*  or  /* ... */",
    "ARITHMETIC_OPERATOR": r"+ | - | * | /",
    "RELATIONAL_OPERATOR": r"< | > | <= | >= | == | !=",
    "ASSIGNMENT":          r"=",
    "LOGICAL_OPERATOR":    r"&& | || | !",
    "SEPARATOR":           r"( ) { } [ ] ; , .",
    "UNKNOWN":             "No matching pattern",
}

# ─── Token explanations (for the inspector "WHY?" section) ───────────────────

TOKEN_EXPLANATIONS: dict[str, str] = {
    "KEYWORD": (
        "This lexeme exactly matches one of the reserved words in the "
        "language specification (e.g. int, if, while). "
        "Keywords are recognised before identifiers."
    ),
    "IDENTIFIER": (
        "The first character is a letter or underscore, and all remaining "
        "characters are letters, digits, or underscores. "
        "This satisfies the regular expression [A-Za-z_][A-Za-z0-9_]*."
    ),
    "INTEGER": (
        "The lexeme consists entirely of one or more decimal digits (0–9), "
        "matching the pattern [0-9]+."
    ),
    "FLOAT": (
        "The lexeme matches [0-9]+\\.[0-9]+: digits before the decimal "
        "point, a literal dot, and digits after the decimal point."
    ),
    "STRING": (
        "The lexeme is enclosed in double quotes with no embedded newline, "
        "matching the simplified pattern \"[^\"\\n]*\"."
    ),
    "COMMENT": (
        "The lexeme is a single-line comment starting with // or a "
        "block comment enclosed in /* and */."
    ),
    "ARITHMETIC_OPERATOR": (
        "The lexeme is one of the four basic arithmetic operators: +, -, *, /."
    ),
    "RELATIONAL_OPERATOR": (
        "The lexeme is a comparison operator. The lexer uses longest-match "
        "so >= is recognised as a single token, not > followed by =."
    ),
    "ASSIGNMENT": (
        "A single = that did not form a longer operator (== is a relational "
        "operator, recognised first by the longest-match rule)."
    ),
    "LOGICAL_OPERATOR": (
        "The lexeme is a logical operator: && (AND), || (OR), or ! (NOT). "
        "Multi-character forms are matched before the single ! character."
    ),
    "SEPARATOR": (
        "The character is a punctuation separator: "
        "parentheses, braces, brackets, semicolon, comma, or dot."
    ),
    "UNKNOWN": (
        "No lexical rule recognises this character or sequence. "
        "This is a lexical error."
    ),
}
