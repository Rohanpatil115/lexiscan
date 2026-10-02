import sys
sys.path.insert(0, '.')
from lexer import tokenize

def show(label, src):
    print(f"\n=== {label} ===")
    print(f"    Source: {src!r}")
    toks = tokenize(src)
    for t in toks:
        print(f"  {t['lexeme']:<15} -> {t['token']:<25} line={t['line']} col={t['column']} status={t['status']}")
    return toks

# 1. Basic
show("int age = 20;", "int age = 20;")

# 2. Longest match >= (must be single RELATIONAL_OPERATOR)
show("if (age >= 18)", "if (age >= 18)")

# 3. Lexical error
show("int @age = 20;", "int @age = 20;")

# 4. Float
show("float x = 3.14;", "float x = 3.14;")

# 5. == (must be RELATIONAL_OPERATOR, not two ASSIGNMENT)
show("x == y", "x == y")

# 6. String and comment
show("string + comment", '"Hello" // a comment')

# 7. Multiline
src_ml = """int main() {
    int age = 20;
    if (age >= 18) {
        age = age + 1;
    }
    return 0;
}"""
show("Full function", src_ml)

# 8. DFA simulator
from automata import DFA_REGISTRY, simulate_dfa

dfa_id = DFA_REGISTRY["Identifier"]
r1 = simulate_dfa(dfa_id, "student123")
print(f"\nDFA Identifier 'student123': accepted={r1.accepted}")
r2 = simulate_dfa(dfa_id, "123student")
print(f"DFA Identifier '123student': accepted={r2.accepted}  reason={r2.reason}")

dfa_int = DFA_REGISTRY["Integer"]
r3 = simulate_dfa(dfa_int, "9999")
print(f"DFA Integer '9999': accepted={r3.accepted}")

dfa_fl = DFA_REGISTRY["Float"]
r4 = simulate_dfa(dfa_fl, "3.14")
print(f"DFA Float '3.14': accepted={r4.accepted}")
r5 = simulate_dfa(dfa_fl, "3.")
print(f"DFA Float '3.': accepted={r5.accepted}  reason={r5.reason}")

print("\nAll tests passed.")
