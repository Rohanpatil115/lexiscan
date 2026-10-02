"""
automata.py
===========
Finite automaton definitions and simulation logic for LexiScan.

Each DFA is represented as:
    - A set of states
    - An alphabet (implicit from the transition function)
    - A start state
    - A set of accepting states
    - A transition function: dict[state, dict[char_class, next_state]]

Character classes are used instead of individual characters so that the
DFAs remain compact and easy to visualize.

Graphviz DOT source is generated for each DFA so that Streamlit can render
a proper diagram.  The diagrams accurately reflect the transition logic used
in simulation — they are NOT decorative.
"""

from __future__ import annotations
from dataclasses import dataclass, field


# ─── DFA data structures ──────────────────────────────────────────────────────

@dataclass
class DFAState:
    name: str
    is_accepting: bool = False
    is_start:     bool = False


@dataclass
class DFA:
    name:          str                                # human-readable label
    states:        list[DFAState]
    start:         str                                # state name
    accepting:     set[str]
    transitions:   dict[str, dict[str, str]]          # {from_state: {label: to_state}}
    dead_state:    str | None = None                  # optional trap state name
    token_type:    str        = ""                    # e.g. "IDENTIFIER"

    def get_state(self, name: str) -> DFAState | None:
        for s in self.states:
            if s.name == name:
                return s
        return None


# ─── Simulation result ────────────────────────────────────────────────────────

@dataclass
class SimStep:
    step:          int
    character:     str   # "—" for initial row
    current_state: str
    next_state:    str
    note:          str = ""


@dataclass
class SimResult:
    accepted:    bool
    steps:       list[SimStep]
    final_state: str
    token_type:  str   # only meaningful when accepted
    reason:      str   # explanation for rejection


# ─── Character class helpers ──────────────────────────────────────────────────

def _char_class(ch: str, dfa_name: str) -> str:
    """
    Map a single character to the symbolic label used in the DFA transitions.
    This keeps the transition function small and diagram-friendly.
    """
    if dfa_name == "Identifier":
        if ch.isalpha() or ch == "_":
            return "letter/_"
        if ch.isdigit():
            return "digit"
        return "__dead__"

    if dfa_name == "Integer":
        if ch.isdigit():
            return "digit"
        return "__dead__"

    if dfa_name == "Float":
        if ch.isdigit():
            return "digit"
        if ch == ".":
            return "."
        return "__dead__"

    if dfa_name == "Relational":
        return ch   # exact character matching

    return "__dead__"


# ─── DFA definitions ──────────────────────────────────────────────────────────

def build_identifier_dfa() -> DFA:
    """
    Identifier DFA for [A-Za-z_][A-Za-z0-9_]*

    States:
        q0  – start (non-accepting)
        q1  – accepting: consumed ≥1 valid char starting with letter/_
        qd  – dead (trap) state: invalid character seen
    """
    return DFA(
        name="Identifier",
        token_type="IDENTIFIER",
        states=[
            DFAState("q0", is_start=True,     is_accepting=False),
            DFAState("q1",                     is_accepting=True),
            DFAState("qd",                     is_accepting=False),
        ],
        start="q0",
        accepting={"q1"},
        dead_state="qd",
        transitions={
            "q0": {
                "letter/_": "q1",
                "digit":    "qd",   # can't start with digit
            },
            "q1": {
                "letter/_": "q1",
                "digit":    "q1",
            },
            "qd": {},   # trap — no exits
        },
    )


def build_integer_dfa() -> DFA:
    """
    Integer DFA for [0-9]+

    States:
        q0  – start (non-accepting)
        q1  – accepting: consumed ≥1 digit
    """
    return DFA(
        name="Integer",
        token_type="INTEGER",
        states=[
            DFAState("q0", is_start=True, is_accepting=False),
            DFAState("q1",                is_accepting=True),
        ],
        start="q0",
        accepting={"q1"},
        transitions={
            "q0": {"digit": "q1"},
            "q1": {"digit": "q1"},
        },
    )


def build_float_dfa() -> DFA:
    """
    Float DFA for [0-9]+\\.[0-9]+

    States:
        q0  – start
        q1  – read ≥1 digit before the dot
        q2  – read the dot (non-accepting — need at least one digit after)
        q3  – accepting: read ≥1 digit after the dot
    """
    return DFA(
        name="Float",
        token_type="FLOAT",
        states=[
            DFAState("q0", is_start=True, is_accepting=False),
            DFAState("q1",                is_accepting=False),
            DFAState("q2",                is_accepting=False),
            DFAState("q3",                is_accepting=True),
        ],
        start="q0",
        accepting={"q3"},
        transitions={
            "q0": {"digit": "q1"},
            "q1": {"digit": "q1", ".": "q2"},
            "q2": {"digit": "q3"},
            "q3": {"digit": "q3"},
        },
    )


def build_relational_dfa() -> DFA:
    """
    Relational operator DFA.

    Recognises: <, >, <=, >=, ==, !=
    Demonstrates why the lexer must use lookahead (longest-match).

    States:
        q0   – start
        q_lt – saw <              (accepts <)
        q_gt – saw >              (accepts >)
        q_le – saw <=             (accepts <=)
        q_ge – saw >=             (accepts >=)
        q_e1 – saw =              (non-accepting mid-point for ==)
        q_eq – saw ==             (accepts ==)
        q_n  – saw !              (non-accepting mid-point for !=)
        q_ne – saw !=             (accepts !=)
    """
    return DFA(
        name="Relational",
        token_type="RELATIONAL_OPERATOR",
        states=[
            DFAState("q0",   is_start=True,  is_accepting=False),
            DFAState("q_lt",                  is_accepting=True),
            DFAState("q_gt",                  is_accepting=True),
            DFAState("q_le",                  is_accepting=True),
            DFAState("q_ge",                  is_accepting=True),
            DFAState("q_e1",                  is_accepting=False),
            DFAState("q_eq",                  is_accepting=True),
            DFAState("q_n",                   is_accepting=False),
            DFAState("q_ne",                  is_accepting=True),
        ],
        start="q0",
        accepting={"q_lt", "q_gt", "q_le", "q_ge", "q_eq", "q_ne"},
        transitions={
            "q0":   {"<": "q_lt", ">": "q_gt", "=": "q_e1", "!": "q_n"},
            "q_lt": {"=": "q_le"},
            "q_gt": {"=": "q_ge"},
            "q_le": {},
            "q_ge": {},
            "q_e1": {"=": "q_eq"},
            "q_eq": {},
            "q_n":  {"=": "q_ne"},
            "q_ne": {},
        },
    )


# Registry of all available DFAs
DFA_REGISTRY: dict[str, DFA] = {
    "Identifier":          build_identifier_dfa(),
    "Integer":             build_integer_dfa(),
    "Float":               build_float_dfa(),
    "Relational Operator": build_relational_dfa(),
}


# ─── Academic metadata per DFA ────────────────────────────────────────────────
# All information here must agree with the DFA definition above.

DFA_META: dict[str, dict] = {
    "Identifier": {
        "regex":        r"[A-Za-z_][A-Za-z0-9_]*",
        "regex_explain": (
            "Starts with a letter (A–Z, a–z) or underscore (_), "
            "followed by zero or more letters, digits (0–9), or underscores."
        ),
        "alphabet":     "{ letter, digit, _ }",
        "language_desc": (
            "L = { strings that begin with a letter or underscore, "
            "followed by zero or more letters, digits, or underscores }"
        ),
        # 5-tuple formal definition
        "Q":  ["q0", "q1"],
        "sigma": ["letter/_", "digit"],
        "q0": "q0",
        "F":  ["q1"],
        "delta_rows": [
            ("→ q0", "q1", "Dead", "q1"),
            ("★ q1", "q1", "q1",   "q1"),
        ],
        "delta_cols": ["State", "letter/_", "digit", "_"],
        "delta_display": [
            # (from, input, to)
            ("q0", "letter/_", "q1"),
            ("q0", "digit",    "Dead"),
            ("q1", "letter/_", "q1"),
            ("q1", "digit",    "q1"),
        ],
        "accepted": ["student", "student123", "_marks", "marks_1", "test_123"],
        "rejected": ["123student", "student@", "2fast"],
        "accepted_reason": "Begins with letter/_; all remaining chars are letter/digit/_.",
        "rejected_reason": "First character is a digit or string contains invalid symbol.",
        "academic_note": (
            "The identifier DFA has two meaningful states: q0 (start) and q1 (accepting). "
            "The first character must be a letter or underscore — this is the q0→q1 transition. "
            "Any subsequent character that is a letter, digit, or underscore keeps the DFA in q1 (self-loop). "
            "A digit as the very first character leads to the dead state — "
            "identifiers cannot start with a digit. "
            "This matches the rule used in most programming languages (C, Java, Python, etc.)."
        ),
        "longest_match_note": (
            "The lexer uses the longest-match rule: it continues reading characters "
            "as long as they keep the DFA in q1. The token is emitted when the next "
            "character would leave q1."
        ),
    },

    "Integer": {
        "regex":        r"[0-9]+",
        "regex_explain": "One or more decimal digits (0 through 9).",
        "alphabet":     "{ digit (0–9) }",
        "language_desc": "L = { non-empty strings of decimal digits }",
        "Q":  ["q0", "q1"],
        "sigma": ["digit"],
        "q0": "q0",
        "F":  ["q1"],
        "delta_display": [
            ("q0", "digit", "q1"),
            ("q1", "digit", "q1"),
        ],
        "delta_rows": [
            ("→ q0", "q1"),
            ("★ q1", "q1"),
        ],
        "delta_cols": ["State", "digit (0–9)"],
        "accepted": ["0", "10", "123", "9999"],
        "rejected": ["12a", "1.5", "abc"],
        "accepted_reason": "Consists entirely of one or more decimal digits.",
        "rejected_reason": "Contains a non-digit character.",
        "academic_note": (
            "The integer DFA is the simplest possible: q0 (start) transitions to q1 (accepting) "
            "on any digit, and q1 self-loops on further digits. "
            "At least one digit is required — the empty string is not accepted. "
            "Strings like '1.5' are accepted only up to '1'; the dot causes the DFA to stop, "
            "which is how the lexer separates integers from floats using longest-match."
        ),
        "longest_match_note": (
            "The lexer reads digits until a non-digit appears. "
            "If a dot follows the integer, it checks whether a float pattern applies."
        ),
    },

    "Float": {
        "regex":        r"[0-9]+\.[0-9]+",
        "regex_explain": (
            "One or more digits, followed by a decimal point (.), "
            "followed by one or more digits."
        ),
        "alphabet":     "{ digit (0–9), . }",
        "language_desc": (
            "L = { strings of one or more digits, a dot, and one or more digits }"
        ),
        "Q":  ["q0", "q1", "q2", "q3"],
        "sigma": ["digit", "."],
        "q0": "q0",
        "F":  ["q3"],
        "delta_display": [
            ("q0", "digit", "q1"),
            ("q1", "digit", "q1"),
            ("q1", ".",     "q2"),
            ("q2", "digit", "q3"),
            ("q3", "digit", "q3"),
        ],
        "delta_rows": [
            ("→ q0",  "q1",   "Dead"),
            ("  q1",  "q1",   "q2"),
            ("  q2",  "q3",   "Dead"),
            ("★ q3",  "q3",   "Dead"),
        ],
        "delta_cols": ["State", "digit (0–9)", ". (dot)"],
        "accepted": ["3.14", "10.5", "99.99", "0.0"],
        "rejected": ["3.", ".5", "3.14.15", "100"],
        "accepted_reason": "Digits before and after the decimal point — both required.",
        "rejected_reason": "Missing digits before or after the dot, or no dot at all.",
        "academic_note": (
            "The float DFA uses four states to enforce [0-9]+\\.[0-9]+. "
            "q0 is the start; q1 collects digits before the dot (non-accepting — dot not seen yet). "
            "Seeing a '.' moves to q2, which is non-accepting — at least one digit must follow. "
            "q3 (accepting) is entered after the first post-dot digit and loops on further digits. "
            "Notice that '3.' ends in q2 (rejected) and '.5' never even leaves q0 (rejected). "
            "Both '3.' and '.5' would be lexical errors if not preceded by valid tokens."
        ),
        "longest_match_note": (
            "The float pattern is tried before the integer pattern in the lexer. "
            "If the pattern [0-9]+\\.[0-9]+ matches, the token is FLOAT; "
            "otherwise the lexer falls back to [0-9]+ for INTEGER."
        ),
    },

    "Relational Operator": {
        "regex":        r"<= | >= | == | != | < | >",
        "regex_explain": (
            "One of the six relational operators: <, >, <=, >=, ==, !=. "
            "Two-character forms must be matched before single-character forms (longest match)."
        ),
        "alphabet":     "{ <, >, =, ! }",
        "language_desc": (
            "L = { <, >, <=, >=, ==, != }"
        ),
        "Q":  ["q0", "q_lt", "q_gt", "q_le", "q_ge", "q_e1", "q_eq", "q_n", "q_ne"],
        "sigma": ["<", ">", "=", "!"],
        "q0": "q0",
        "F":  ["q_lt", "q_gt", "q_le", "q_ge", "q_eq", "q_ne"],
        "delta_display": [
            ("q0",   "<",  "q_lt"),
            ("q0",   ">",  "q_gt"),
            ("q0",   "=",  "q_e1"),
            ("q0",   "!",  "q_n"),
            ("q_lt", "=",  "q_le"),
            ("q_gt", "=",  "q_ge"),
            ("q_e1", "=",  "q_eq"),
            ("q_n",  "=",  "q_ne"),
        ],
        "delta_rows": [],   # shown as a flow description instead
        "delta_cols": [],
        "accepted": ["<", ">", "<=", ">=", "==", "!="],
        "rejected": ["!", "=", "<>", "=>"],
        "accepted_reason": "Valid relational operator reaching an accepting state.",
        "rejected_reason": (
            "Either a single '!' or '=' which do not reach an accepting state alone, "
            "or a two-character sequence not in the language."
        ),
        "academic_note": (
            "The relational operator DFA illustrates the longest-match principle clearly. "
            "After seeing '>', the DFA is in q_gt (an accepting state). "
            "But if the very next character is '=', the DFA transitions to q_ge — "
            "accepting the longer '>=' as a single token. "
            "Without longest-match, '>' and '=' would be two separate tokens, "
            "which would be semantically wrong. "
            "Note that '=' alone is handled as ASSIGNMENT by the lexer, "
            "not as part of this DFA."
        ),
        "longest_match_note": (
            "The lexer checks two-character operators before single-character operators. "
            "This is exactly what the relational DFA formalises: "
            "accept the longest string that leads to an accepting state."
        ),
    },
}


# ─── DFA Simulator ───────────────────────────────────────────────────────────

def simulate_dfa(dfa: DFA, input_string: str) -> SimResult:
    """
    Simulate *dfa* on *input_string*, character by character.
    Returns a SimResult with step-by-step trace and accept/reject verdict.
    """
    current = dfa.start
    steps: list[SimStep] = []

    # Initial row
    steps.append(SimStep(
        step=0,
        character="—",
        current_state=current,
        next_state=current,
        note="Initial state",
    ))

    for i, ch in enumerate(input_string, start=1):
        label = _char_class(ch, dfa.name)

        trans = dfa.transitions.get(current, {})
        next_st = trans.get(label)

        if next_st is None:
            # No valid transition — move to dead state and stop
            dead = dfa.dead_state or "DEAD"
            steps.append(SimStep(
                step=i,
                character=ch,
                current_state=current,
                next_state=dead,
                note=f"No transition on '{ch}' — rejected",
            ))
            current = dead
            break

        steps.append(SimStep(
            step=i,
            character=ch,
            current_state=current,
            next_state=next_st,
        ))
        current = next_st

    accepted = current in dfa.accepting

    if accepted:
        reason = ""
    else:
        # Build a helpful rejection reason
        if not input_string:
            reason = "Empty input: the automaton needs at least one character."
        elif dfa.name == "Identifier" and input_string[0].isdigit():
            reason = (
                "An identifier must begin with a letter or underscore. "
                f"'{input_string[0]}' is a digit, so the DFA moves to the "
                "dead state immediately."
            )
        elif dfa.name == "Float" and "." not in input_string:
            reason = (
                "A float literal requires a decimal point followed by at "
                "least one digit."
            )
        elif dfa.name == "Float" and input_string.endswith("."):
            reason = (
                "The decimal point must be followed by at least one digit."
            )
        elif dfa.name == "Relational" and current not in dfa.accepting:
            reason = (
                f"The input '{input_string}' did not reach an accepting state. "
                "Valid relational operators are: < > <= >= == !="
            )
        else:
            reason = (
                f"The automaton ended in state '{current}', "
                "which is not an accepting state."
            )

    return SimResult(
        accepted=accepted,
        steps=steps,
        final_state=current,
        token_type=dfa.token_type if accepted else "",
        reason=reason,
    )


# ─── Graphviz DOT generation ──────────────────────────────────────────────────

def dfa_to_dot(dfa: DFA, highlight_state: str | None = None) -> str:
    """
    Generate Graphviz DOT source for *dfa*.

    highlight_state: if provided, that state node is coloured differently
                     (used during simulation to show the current state).
    """
    # Colour scheme matching the LexiScan theme
    C_BG           = "#211A16"
    C_EDGE         = "#A66A3F"
    C_STATE_FILL   = "#2B211B"
    C_STATE_BORDER = "#7A4E2D"
    C_ACCEPT_FILL  = "#2B3D27"
    C_ACCEPT_BORDER= "#7F9C72"
    C_START_ARROW  = "#A66A3F"
    C_FONT         = "#F3E8D5"
    C_HIGHLIGHT    = "#C49A5A"   # current state during simulation

    lines = [
        "digraph DFA {",
        f'  bgcolor="{C_BG}";',
        '  rankdir=LR;',
        '  node [fontname="Courier", fontsize=13];',
        f'  edge [color="{C_EDGE}", fontcolor="{C_FONT}", fontname="Courier", fontsize=11];',
        # Invisible start arrow
        f'  __start__ [shape=point, color="{C_START_ARROW}", width=0.2];',
        f'  __start__ -> {dfa.start} [color="{C_START_ARROW}"];',
    ]

    for state in dfa.states:
        sn = state.name
        if sn == dfa.dead_state:
            continue   # omit dead/trap state from diagram for clarity

        shape = "doublecircle" if state.is_accepting else "circle"

        if sn == highlight_state:
            fill   = C_HIGHLIGHT
            border = C_HIGHLIGHT
            font   = "#171310"
        elif state.is_accepting:
            fill   = C_ACCEPT_FILL
            border = C_ACCEPT_BORDER
            font   = C_FONT
        else:
            fill   = C_STATE_FILL
            border = C_STATE_BORDER
            font   = C_FONT

        lines.append(
            f'  {sn} [shape={shape}, style=filled, '
            f'fillcolor="{fill}", color="{border}", '
            f'fontcolor="{font}", label="{sn}"];'
        )

    # Edges — merge parallel edges (same from/to) into comma-separated labels
    edge_labels: dict[tuple[str, str], list[str]] = {}
    for from_state, trans in dfa.transitions.items():
        if from_state == dfa.dead_state:
            continue
        for label, to_state in trans.items():
            if to_state == dfa.dead_state:
                continue
            key = (from_state, to_state)
            edge_labels.setdefault(key, []).append(label)

    for (frm, to), labels in edge_labels.items():
        combined = ", ".join(labels)
        lines.append(f'  {frm} -> {to} [label="{combined}"];')

    lines.append("}")
    return "\n".join(lines)
