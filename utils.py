"""
utils.py
========
Formatting helpers, statistics, UI utilities, and validation helpers
for LexiScan.
"""

from __future__ import annotations
from collections import Counter
from typing import Any

import pandas as pd

import token_rules as rules


# ─── Statistics ───────────────────────────────────────────────────────────────

def compute_stats(tokens: list[dict]) -> dict[str, int]:
    """Return a summary statistics dict from a list of token dicts."""
    total     = len(tokens)
    keywords  = sum(1 for t in tokens if t["token"] == "KEYWORD")
    idents    = sum(1 for t in tokens if t["token"] == "IDENTIFIER")
    numbers   = sum(1 for t in tokens if t["token"] in ("INTEGER", "FLOAT"))
    operators = sum(1 for t in tokens if t["category"] == "Operator")
    separators= sum(1 for t in tokens if t["token"] == "SEPARATOR")
    strings   = sum(1 for t in tokens if t["token"] == "STRING")
    comments  = sum(1 for t in tokens if t["token"] == "COMMENT")
    errors    = sum(1 for t in tokens if t["token"] == "UNKNOWN")

    return {
        "Total Tokens": total,
        "Keywords":     keywords,
        "Identifiers":  idents,
        "Numbers":      numbers,
        "Operators":    operators,
        "Separators":   separators,
        "Strings":      strings,
        "Comments":     comments,
        "Errors":       errors,
    }


def category_distribution(tokens: list[dict]) -> dict[str, int]:
    """Return a category → count mapping suitable for a Plotly chart."""
    counter: Counter[str] = Counter()
    for t in tokens:
        counter[t["category"]] += 1
    return dict(counter.most_common())


# ─── Pandas DataFrame helpers ─────────────────────────────────────────────────

def tokens_to_dataframe(tokens: list[dict]) -> pd.DataFrame:
    """Convert token list to a numbered DataFrame for display."""
    rows = []
    for i, t in enumerate(tokens, start=1):
        rows.append({
            "#":        i,
            "Line":     t["line"],
            "Lexeme":   t["lexeme"],
            "Token":    t["token"],
            "Category": t["category"],
            "Status":   "✓ Valid" if t["status"] == "Valid" else "✕ Error",
        })
    return pd.DataFrame(rows)


def filter_tokens(tokens: list[dict], category_filter: str) -> list[dict]:
    """Filter token list by the selected category label."""
    mapping = {
        "All":        None,
        "Keywords":   "Keyword",
        "Identifiers":"Identifier",
        "Numbers":    "Number",
        "Operators":  "Operator",
        "Separators": "Separator",
        "Strings":    "String",
        "Comments":   "Comment",
        "Errors":     "Error",
    }
    target = mapping.get(category_filter)
    if target is None:
        return tokens
    return [t for t in tokens if t["category"] == target]


# ─── Validation helpers ───────────────────────────────────────────────────────

def validate_input(source: str) -> tuple[bool, str]:
    """
    Basic sanity check on source code input.
    Returns (is_valid, message).
    """
    if not source or not source.strip():
        return False, "Input is empty. Please enter some source code."
    if len(source) > 10_000:
        return False, "Input is too large (max 10,000 characters)."
    return True, ""


# ─── Formatting helpers ───────────────────────────────────────────────────────

def status_icon(status: str) -> str:
    return "✓" if status == "Valid" else "✕"


def token_badge_html(token_name: str) -> str:
    """Return a small HTML badge coloured by token category."""
    colours = {
        "KEYWORD":             ("#7A4E2D", "#F3E8D5"),
        "IDENTIFIER":          ("#2B3D27", "#7F9C72"),
        "INTEGER":             ("#1E2B3D", "#7FA0C4"),
        "FLOAT":               ("#1E2B3D", "#7FA0C4"),
        "STRING":              ("#2D2B1A", "#C4B87F"),
        "COMMENT":             ("#2B2B2B", "#888888"),
        "ARITHMETIC_OPERATOR": ("#3D2B1A", "#C4917F"),
        "RELATIONAL_OPERATOR": ("#3D2B1A", "#C4917F"),
        "ASSIGNMENT":          ("#3D2B1A", "#C4917F"),
        "LOGICAL_OPERATOR":    ("#3D2B1A", "#C4917F"),
        "SEPARATOR":           ("#2B2535", "#9B8FC4"),
        "UNKNOWN":             ("#3D1A1A", "#B85C5C"),
    }
    bg, fg = colours.get(token_name, ("#2B211B", "#B8A99A"))
    return (
        f'<span style="background:{bg};color:{fg};'
        f'padding:2px 8px;border-radius:4px;font-size:0.75rem;'
        f'font-family:monospace;font-weight:600;">{token_name}</span>'
    )


# ─── Sample programs ──────────────────────────────────────────────────────────

EXAMPLES: dict[str, str] = {
    "Example 1 – Simple Assignment": """\
int age = 20;
""",

    "Example 2 – Function with Condition": """\
int main() {
    int age = 20;

    if (age >= 18) {
        age = age + 1;
    }

    return 0;
}
""",

    "Example 3 – Lexical Error Demo": """\
int @age = 20;
float #price = 9.99;
char $grade = 'A';
""",
}

DEFAULT_EXAMPLE = EXAMPLES["Example 2 – Function with Condition"]
