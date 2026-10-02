# ◈ LexiScan

**Interactive Lexical Analyzer Using Finite Automata**

> *Decode the Language of Code.*

---

## Overview

LexiScan is an interactive educational lexical analyzer built as a **Theory of Computation** course project.
It demonstrates how source code is broken into *lexemes*, how those lexemes are classified into *token categories*, and how **finite automata** serve as the theoretical foundation for recognizing lexical patterns.

This is an **Educational Lexical Analyzer** — not a complete compiler.

---

## Problem Statement

Understanding lexical analysis and its relationship with finite automata can be difficult when studied only theoretically.
LexiScan provides an interactive way to observe how source code is divided into lexemes and classified into tokens, with:

- Step-by-step DFA simulation
- Accurate automaton visualizations
- Token-by-token inspection

---

## Objectives

1. Understand lexical analysis as the first phase of compilation.
2. Understand the concepts of *lexemes*, *tokens*, and *token categories*.
3. See how regular expressions describe lexical patterns.
4. Demonstrate finite automata (DFAs) for token recognition.
5. Recognize and report lexical errors.
6. Visualize DFA state transitions step-by-step.

---

## Theory of Computation Connection

```
SOURCE CODE
     ↓
TOKEN PATTERN (Regular Expression)
     ↓
REGULAR LANGUAGE
     ↓
FINITE AUTOMATON (DFA)
     ↓
ACCEPT / REJECT
     ↓
TOKEN CLASSIFICATION
     ↓
LEXICAL ANALYZER OUTPUT
```

A lexical analyzer reads source code and breaks it into *lexemes*.
Each lexeme is classified into a token category.
Many token patterns can be represented using **regular expressions**.
Regular languages can be recognized by **finite automata**.
Therefore, finite automata provide the theoretical foundation for lexical recognition.

---

## Features

| Feature | Description |
|---|---|
| **Lexical Analysis** | Scans C/C++-like source code into tokens |
| **Longest Match** | Maximal-munch rule: `>=` is one token, not `>` + `=` |
| **Lexical Errors** | Reports unknown symbols with line/column info |
| **Token Inspector** | Shows pattern, explanation, and status for each token |
| **Token Filter** | Filter table by category |
| **DFA Diagrams** | Accurate Graphviz automaton for each token type |
| **DFA Simulator** | Step-by-step state trace for any input string |
| **Statistics** | Count of each token category |
| **Distribution Chart** | Visual breakdown of token types |
| **Presentation Mode** | Simplified view for classroom demonstration |

---

## Technology Stack

| Tool | Purpose |
|---|---|
| Python 3 | Core language |
| Streamlit | Web UI |
| Python `re` module | Regex pattern matching |
| Graphviz | DFA visualization |
| Pandas | Token table display |
| Plotly | Distribution chart |

---

## Token Types

| Token | Pattern | Example |
|---|---|---|
| KEYWORD | Reserved word | `int`, `if`, `while` |
| IDENTIFIER | `[A-Za-z_][A-Za-z0-9_]*` | `age`, `student123` |
| INTEGER | `[0-9]+` | `0`, `20`, `9999` |
| FLOAT | `[0-9]+\.[0-9]+` | `3.14`, `99.99` |
| STRING | `"[^"\n]*"` | `"Hello"` |
| COMMENT | `//…` or `/*…*/` | `// note` |
| ARITHMETIC_OPERATOR | `+ - * /` | `+`, `*` |
| RELATIONAL_OPERATOR | `< > <= >= == !=` | `>=`, `==` |
| ASSIGNMENT | `=` | `=` |
| LOGICAL_OPERATOR | `&& \|\| !` | `&&` |
| SEPARATOR | `( ) { } [ ] ; , .` | `;`, `{` |
| UNKNOWN | No match | `@`, `#` |

---

## Finite Automata

| DFA | Recognizes | Accepting State |
|---|---|---|
| Identifier DFA | `[A-Za-z_][A-Za-z0-9_]*` | q1 |
| Integer DFA | `[0-9]+` | q1 |
| Float DFA | `[0-9]+\.[0-9]+` | q3 |
| Relational Operator DFA | `< > <= >= == !=` | q_lt, q_gt, q_le, q_ge, q_eq, q_ne |

---

## Project Structure

```
LexiScan/
│
├── app.py           ← Streamlit application (UI, navigation, pages)
├── lexer.py         ← Lexical analysis engine (scanner, tokenizer)
├── automata.py      ← DFA definitions, simulator, Graphviz DOT generator
├── token_rules.py   ← Keywords, patterns, operators, separators
├── utils.py         ← Statistics, DataFrames, sample programs
├── requirements.txt
├── README.md
│
└── assets/
    └── examples/
```

---

## Installation

```bash
# 1. Clone or download the project
cd LexiScan

# 2. (Recommended) Create a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt
```

> **Note:** You also need the Graphviz binary installed on your system.
> Download from https://graphviz.org/download/ and add it to your PATH.

---

## Running the Application

```bash
streamlit run app.py
```

The application opens at `http://localhost:8501` in your browser.

---

## Example

**Input:**
```cpp
int age = 20;

if (age >= 18) {
    age = age + 1;
}
```

**Output (partial):**

| # | Line | Lexeme | Token | Category | Status |
|---|---|---|---|---|---|
| 1 | 1 | int | KEYWORD | Keyword | ✓ Valid |
| 2 | 1 | age | IDENTIFIER | Identifier | ✓ Valid |
| 3 | 1 | = | ASSIGNMENT | Operator | ✓ Valid |
| 4 | 1 | 20 | INTEGER | Number | ✓ Valid |
| 5 | 1 | ; | SEPARATOR | Separator | ✓ Valid |
| 6 | 3 | if | KEYWORD | Keyword | ✓ Valid |
| … | … | … | … | … | … |

---

## Demo Flow (3–5 minutes)

1. Open LexiScan at `http://localhost:8501`.
2. Click **▣ Example 2** to load the sample function.
3. Click **⚡ SCAN CODE**.
4. Observe token statistics and the token table.
5. Navigate to **⬡ Finite Automata** → select **Identifier**.
6. View the DFA diagram and transition table.
7. Navigate to **▶ DFA Simulator** → select **Identifier**.
8. Enter `student123` → click **▶ SIMULATE** → observe q0→q1 transitions → **ACCEPTED**.
9. Enter `123student` → **SIMULATE** → observe rejection at q0 (digit) → **REJECTED**.
10. Return to **◈ Analyzer** → load **▣ Example 3 (Errors)** → scan → observe error markers.

---

## Team Contributions

| Member | Role | Modules |
|---|---|---|
| Member 1 | Lexical Analysis | `lexer.py`, `token_rules.py` |
| Member 2 | Finite Automata | `automata.py` |
| Member 3 | UI & Testing | `app.py`, `utils.py` |

---

## Limitations

- Educational lexical analyzer — not a production-grade lexer.
- Supports C/C++-like syntax; does not handle all language constructs.
- Simplified string handling: no escape sequences, no multiline strings.
- No hexadecimal, octal, or scientific numeric formats.
- No parser, syntax tree, semantic analysis, or code generation.
- DFAs are hand-coded for readability; NFA construction is not implemented.

---

## Future Scope

- Support for additional programming languages (Python, Java).
- NFA visualization and NFA-to-DFA subset construction demonstration.
- Hexadecimal, octal, and scientific numeric literals.
- Full escape sequence handling in string literals.
- Symbol table generation.
- Integration with a recursive-descent parser (syntax analysis phase).
- Complete compiler front-end pipeline.

---

*◈ LexiScan · Theory of Computation Course Project · Academic Year 2025–26*
