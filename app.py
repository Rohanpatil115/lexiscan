"""
app.py
======
LexiScan – Interactive Lexical Analyzer Using Finite Automata
Streamlit application entry point.

Run with:
    streamlit run app.py
"""

from __future__ import annotations

import streamlit as st
import pandas as pd
import graphviz

import lexer   as lx
import automata as au
import utils   as ut
import token_rules as rules

# ─── Page configuration ───────────────────────────────────────────────────────

st.set_page_config(
    page_title="LexiScan",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Global CSS (espresso theme) ──────────────────────────────────────────────

CSS = """
<style>
/* ── Base ───────────────────────────────────────────────── */
html, body, [data-testid="stAppViewContainer"] {
    background-color: #171310;
    color: #F3E8D5;
    font-family: 'Segoe UI', sans-serif;
}

[data-testid="stSidebar"] {
    background-color: #211A16;
    border-right: 1px solid #2B211B;
}



/* ── Headings ───────────────────────────────────────────── */
h1, h2, h3 { color: #F3E8D5; font-weight: 700; }
h4, h5, h6 { color: #B8A99A; }

/* ── Buttons ────────────────────────────────────────────── */
div.stButton > button {
    background-color: #7A4E2D;
    color: #F3E8D5;
    border: 1px solid #A66A3F;
    border-radius: 6px;
    padding: 0.45rem 1.2rem;
    font-weight: 600;
    letter-spacing: 0.04em;
    font-size: 0.88rem;
    transition: background 0.18s, border 0.18s;
}
div.stButton > button:hover {
    background-color: #A66A3F;
    border-color: #F3E8D5;
    color: #171310;
}
div.stButton > button:active {
    background-color: #5C3820;
}

/* ── Primary (scan) button ──────────────────────────────── */
div[data-testid="column"]:first-child div.stButton > button {
    background-color: #7A4E2D;
    font-size: 0.95rem;
}

/* ── Text input / code area ─────────────────────────────── */
textarea {
    background-color: #211A16 !important;
    color: #F3E8D5 !important;
    border: 1px solid #2B211B !important;
    border-radius: 6px !important;
    font-family: 'Cascadia Code', 'Fira Code', 'Courier New', monospace !important;
    font-size: 0.9rem !important;
}
textarea:focus {
    border-color: #7A4E2D !important;
    box-shadow: 0 0 0 2px rgba(122, 78, 45, 0.25) !important;
}

/* ── Selectbox ───────────────────────────────────────────── */
div[data-baseweb="select"] > div {
    background-color: #211A16 !important;
    border-color: #2B211B !important;
    color: #F3E8D5 !important;
    border-radius: 6px !important;
}
div[data-baseweb="select"] span {
    color: #F3E8D5 !important;
}

/* ── Radio buttons ───────────────────────────────────────── */
div.stRadio > label { color: #B8A99A; }
div.stRadio [data-testid="stMarkdownContainer"] p { color: #F3E8D5; }

/* ── DataFrames ──────────────────────────────────────────── */
.stDataFrame { border: 1px solid #2B211B; border-radius: 8px; }
.stDataFrame table { background: #211A16 !important; }
.stDataFrame th {
    background: #2B211B !important;
    color: #A66A3F !important;
    font-size: 0.78rem;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}
.stDataFrame td { color: #F3E8D5 !important; font-size: 0.85rem; }

/* ── Expander ────────────────────────────────────────────── */
details {
    background: #211A16;
    border: 1px solid #2B211B;
    border-radius: 8px;
    padding: 0.5rem 1rem;
}
summary { color: #A66A3F; font-weight: 600; cursor: pointer; }

/* ── Divider ─────────────────────────────────────────────── */
hr { border: none; border-top: 1px solid #2B211B; margin: 1.5rem 0; }

/* ── Metric labels ───────────────────────────────────────── */
[data-testid="stMetricLabel"] { color: #B8A99A !important; font-size: 0.72rem !important; }
[data-testid="stMetricValue"] { color: #F3E8D5 !important; }

/* ── Tabs ────────────────────────────────────────────────── */
button[data-baseweb="tab"] {
    color: #B8A99A !important;
    background: transparent !important;
    border-bottom: 2px solid transparent !important;
    font-size: 0.85rem;
    font-weight: 600;
    letter-spacing: 0.05em;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: #F3E8D5 !important;
    border-bottom: 2px solid #A66A3F !important;
}
[data-testid="stTabPanel"] { padding-top: 1.5rem; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# ─── Helper: card container ───────────────────────────────────────────────────

def card(content_html: str, padding: str = "1.2rem 1.5rem") -> None:
    st.markdown(
        f'<div style="background:#211A16;border:1px solid #2B211B;'
        f'border-radius:10px;padding:{padding};margin-bottom:0.8rem;">'
        f"{content_html}</div>",
        unsafe_allow_html=True,
    )


def section_title(text: str, icon: str = "") -> None:
    prefix = f"{icon} " if icon else ""
    st.markdown(
        f'<p style="color:#A66A3F;font-size:0.72rem;font-weight:700;'
        f'letter-spacing:0.12em;text-transform:uppercase;margin-bottom:0.3rem;">'
        f"{prefix}{text}</p>",
        unsafe_allow_html=True,
    )


def badge(text: str, colour: str = "#7A4E2D", fg: str = "#F3E8D5") -> str:
    return (
        f'<span style="background:{colour};color:{fg};'
        f'padding:2px 9px;border-radius:4px;font-size:0.72rem;'
        f'font-family:monospace;font-weight:700;letter-spacing:0.05em;">'
        f"{text}</span>"
    )


# ─── Session state defaults ───────────────────────────────────────────────────

if "tokens" not in st.session_state:
    st.session_state.tokens = []
if "source_code" not in st.session_state:
    st.session_state.source_code = ut.DEFAULT_EXAMPLE
if "scanned" not in st.session_state:
    st.session_state.scanned = False
if "presentation_mode" not in st.session_state:
    st.session_state.presentation_mode = False
if "sim_step" not in st.session_state:
    st.session_state.sim_step = 0
if "sim_result" not in st.session_state:
    st.session_state.sim_result = None
if "sim_input" not in st.session_state:
    st.session_state.sim_input = ""
if "sim_dfa_name" not in st.session_state:
    st.session_state.sim_dfa_name = "Identifier"


# ─── Sidebar navigation ───────────────────────────────────────────────────────

with st.sidebar:
    st.markdown(
        '<p style="color:#A66A3F;font-size:1.3rem;font-weight:800;'
        'letter-spacing:0.08em;margin-bottom:0;">◈ LEXISCAN</p>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p style="color:#B8A99A;font-size:0.72rem;margin-top:0;'
        'letter-spacing:0.08em;">TOC · FINITE AUTOMATA LAB</p>',
        unsafe_allow_html=True,
    )
    st.markdown("---")

    nav = st.radio(
        "Navigate",
        ["◈ Analyzer", "⚙ Finite Automata Lab", "▶ DFA Simulator", "ⓘ About"],
        label_visibility="collapsed",
    )

    st.markdown("---")
    pm_toggle = st.toggle(
        "🎓 Presentation Mode",
        value=st.session_state.presentation_mode,
    )
    st.session_state.presentation_mode = pm_toggle

    if pm_toggle:
        st.markdown(
            '<p style="color:#C49A5A;font-size:0.72rem;">'
            "Simplified view for classroom demo.</p>",
            unsafe_allow_html=True,
        )


pmode = st.session_state.presentation_mode

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: ANALYZER
# ═══════════════════════════════════════════════════════════════════════════════

if nav == "◈ Analyzer":

    # ── Header ─────────────────────────────────────────────────────────────

    if not pmode:
        st.markdown(
            '<p style="color:#B8A99A;font-size:0.7rem;font-weight:700;'
            'letter-spacing:0.15em;margin-bottom:0.2rem;">TOC • FINITE AUTOMATA LAB</p>',
            unsafe_allow_html=True,
        )

    st.markdown(
        '<h1 style="font-size:2.2rem;font-weight:800;letter-spacing:0.04em;'
        'margin-bottom:0;color:#F3E8D5;">◈ LEXISCAN</h1>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p style="color:#A66A3F;font-size:1rem;margin-top:0.1rem;">'
        "Interactive Lexical Analyzer &nbsp;·&nbsp; "
        '<em style="color:#B8A99A;">Decode the Language of Code.</em></p>',
        unsafe_allow_html=True,
    )
    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Source code input ───────────────────────────────────────────────────

    section_title("Source Code", "⌨")

    src = st.text_area(
        "source_input",
        value=st.session_state.source_code,
        height=260,
        label_visibility="collapsed",
        placeholder="Enter source code here…",
    )
    st.session_state.source_code = src

    # Action buttons
    col_scan, col_clear, col_ex, col_ex2, col_ex3, col_spacer = st.columns(
        [2, 1.4, 2.2, 2.2, 2.2, 3]
    )

    with col_scan:
        scan_clicked = st.button("⚡  SCAN CODE", key="btn_scan")

    with col_clear:
        if st.button("↻  Clear", key="btn_clear"):
            st.session_state.source_code = ""
            st.session_state.tokens      = []
            st.session_state.scanned     = False
            st.rerun()

    with col_ex:
        if st.button("▣  Example 1", key="btn_ex1"):
            st.session_state.source_code = ut.EXAMPLES["Example 1 – Simple Assignment"]
            st.session_state.scanned     = False
            st.rerun()

    with col_ex2:
        if st.button("▣  Example 2", key="btn_ex2"):
            st.session_state.source_code = ut.EXAMPLES["Example 2 – Function with Condition"]
            st.session_state.scanned     = False
            st.rerun()

    with col_ex3:
        if st.button("▣  Example 3 (Errors)", key="btn_ex3"):
            st.session_state.source_code = ut.EXAMPLES["Example 3 – Lexical Error Demo"]
            st.session_state.scanned     = False
            st.rerun()

    # ── Run lexer ────────────────────────────────────────────────────────────

    if scan_clicked:
        ok, msg = ut.validate_input(src)
        if not ok:
            st.error(msg)
        else:
            tokens = lx.tokenize(src)
            st.session_state.tokens  = tokens
            st.session_state.scanned = True

    tokens = st.session_state.tokens

    if st.session_state.scanned and tokens is not None:

        # ── Statistics row ────────────────────────────────────────────────

        stats = ut.compute_stats(tokens)

        st.markdown("<br>", unsafe_allow_html=True)
        section_title("Scan Results", "◎")

        mc = st.columns(4 if pmode else 8)
        stat_items = [
            ("TOTAL TOKENS", stats["Total Tokens"], "#F3E8D5"),
            ("KEYWORDS",     stats["Keywords"],     "#A66A3F"),
            ("IDENTIFIERS",  stats["Identifiers"],  "#7F9C72"),
            ("NUMBERS",      stats["Numbers"],      "#7FA0C4"),
        ]
        if not pmode:
            stat_items += [
                ("OPERATORS",  stats["Operators"],  "#C4917F"),
                ("SEPARATORS", stats["Separators"], "#9B8FC4"),
                ("STRINGS",    stats["Strings"],    "#C4B87F"),
                ("ERRORS",     stats["Errors"],     "#B85C5C"),
            ]

        for i, (label, val, colour) in enumerate(stat_items):
            with mc[i]:
                st.markdown(
                    f'<div style="background:#211A16;border:1px solid #2B211B;'
                    f'border-radius:8px;padding:0.75rem 1rem;text-align:center;">'
                    f'<p style="color:#B8A99A;font-size:0.62rem;font-weight:700;'
                    f'letter-spacing:0.12em;margin:0;">{label}</p>'
                    f'<p style="color:{colour};font-size:1.8rem;font-weight:800;'
                    f'margin:0.1rem 0 0;">{val}</p>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

        # ── Errors banner ─────────────────────────────────────────────────

        errors = [t for t in tokens if t["token"] == "UNKNOWN"]
        if errors:
            errs_html = ""
            for e in errors:
                errs_html += (
                    f'<div style="margin-bottom:0.5rem;">'
                    f'<span style="color:#B85C5C;font-weight:700;">⚠ LEXICAL ERROR</span>'
                    f'<span style="color:#B8A99A;font-size:0.82rem;margin-left:1rem;">'
                    f'Lexeme: </span><code style="color:#F3E8D5;">{e["lexeme"]}</code>'
                    f'<span style="color:#B8A99A;font-size:0.82rem;margin-left:1rem;">'
                    f'Line {e["line"]}, Col {e["column"]}</span>'
                    f'<span style="color:#B8A99A;font-size:0.82rem;margin-left:1rem;">'
                    f'— Unknown symbol not defined in the lexical specification.</span>'
                    f'</div>'
                )
            st.markdown(
                f'<div style="background:#2A1414;border:1px solid #B85C5C;'
                f'border-radius:8px;padding:1rem 1.2rem;margin-top:1rem;">'
                f'{errs_html}</div>',
                unsafe_allow_html=True,
            )

        # ── Token analysis table ──────────────────────────────────────────

        st.markdown("<br>", unsafe_allow_html=True)
        section_title("Token Analysis", "⬡")

        filter_options = [
            "All","Keywords","Identifiers","Numbers",
            "Operators","Separators","Strings","Comments","Errors",
        ]
        selected_filter = st.selectbox(
            "Filter by category",
            filter_options,
            label_visibility="collapsed",
        )

        filtered = ut.filter_tokens(tokens, selected_filter)
        df = ut.tokens_to_dataframe(filtered)

        # Style the Status column
        def style_status(val: str) -> str:
            if "Valid" in val:
                return "color:#7F9C72;font-weight:600;"
            return "color:#B85C5C;font-weight:600;"

        styled_df = df.style.map(style_status, subset=["Status"])

        st.dataframe(
            styled_df,
            use_container_width=True,
            hide_index=True,
            height=min(40 + 36 * len(df), 420),
        )

        st.markdown(
            f'<p style="color:#B8A99A;font-size:0.75rem;margin-top:0.3rem;">'
            f'Showing {len(filtered)} of {len(tokens)} tokens</p>',
            unsafe_allow_html=True,
        )

        # ── Token Inspector ───────────────────────────────────────────────

        if not pmode:
            st.markdown("<br>", unsafe_allow_html=True)
            section_title("Token Inspector", "◎")

            insp_options = [f"#{i+1}  {t['lexeme']}  →  {t['token']}"
                            for i, t in enumerate(tokens)]
            if insp_options:
                sel_idx = st.selectbox(
                    "Select a token to inspect",
                    range(len(insp_options)),
                    format_func=lambda i: insp_options[i],
                    label_visibility="collapsed",
                )
                tok = tokens[sel_idx]
                pattern = rules.PATTERN_DESCRIPTIONS.get(tok["token"], "—")
                explanation = rules.TOKEN_EXPLANATIONS.get(tok["token"], "")
                status_colour = "#7F9C72" if tok["status"] == "Valid" else "#B85C5C"
                status_text   = "✓ Accepted" if tok["status"] == "Valid" else "✕ Rejected"

                card(
                    f'<p style="color:#A66A3F;font-size:0.68rem;font-weight:700;'
                    f'letter-spacing:0.12em;margin-bottom:0.8rem;">TOKEN INSPECTOR</p>'
                    f'<table style="border-collapse:collapse;width:100%;font-size:0.85rem;">'
                    f'<tr><td style="color:#B8A99A;padding:3px 0;width:120px;">Lexeme</td>'
                    f'<td><code style="color:#F3E8D5;font-size:0.9rem;">{tok["lexeme"]}</code></td></tr>'
                    f'<tr><td style="color:#B8A99A;padding:3px 0;">Token</td>'
                    f'<td>{ut.token_badge_html(tok["token"])}</td></tr>'
                    f'<tr><td style="color:#B8A99A;padding:3px 0;">Category</td>'
                    f'<td style="color:#F3E8D5;">{tok["category"]}</td></tr>'
                    f'<tr><td style="color:#B8A99A;padding:3px 0;">Pattern</td>'
                    f'<td><code style="color:#C49A5A;font-size:0.82rem;">{pattern}</code></td></tr>'
                    f'<tr><td style="color:#B8A99A;padding:3px 0;">Line / Col</td>'
                    f'<td style="color:#F3E8D5;">{tok["line"]} / {tok["column"]}</td></tr>'
                    f'<tr><td style="color:#B8A99A;padding:3px 0;">Status</td>'
                    f'<td style="color:{status_colour};font-weight:700;">{status_text}</td></tr>'
                    f'</table>'
                    f'<hr style="border-color:#2B211B;margin:0.8rem 0;">'
                    f'<p style="color:#B8A99A;font-size:0.72rem;font-weight:700;'
                    f'letter-spacing:0.1em;margin-bottom:0.4rem;">WHY?</p>'
                    f'<p style="color:#F3E8D5;font-size:0.84rem;line-height:1.55;margin:0;">'
                    f'{explanation}</p>'
                )

        # ── Distribution chart ────────────────────────────────────────────

        if not pmode and len(tokens) > 0:
            import plotly.express as px

            dist = ut.category_distribution(tokens)
            if dist:
                st.markdown("<br>", unsafe_allow_html=True)
                section_title("Token Distribution", "◎")
                dist_df = pd.DataFrame(
                    {"Category": list(dist.keys()), "Count": list(dist.values())}
                )
                PALETTE = ["#7A4E2D","#A66A3F","#7F9C72","#7FA0C4",
                           "#C4917F","#9B8FC4","#C4B87F","#B85C5C"]
                fig = px.bar(
                    dist_df, x="Category", y="Count",
                    color="Category",
                    color_discrete_sequence=PALETTE,
                    template="plotly_dark",
                )
                fig.update_layout(
                    paper_bgcolor="#171310",
                    plot_bgcolor="#211A16",
                    font_color="#F3E8D5",
                    showlegend=False,
                    height=280,
                    margin=dict(l=10, r=10, t=10, b=10),
                    xaxis=dict(gridcolor="#2B211B"),
                    yaxis=dict(gridcolor="#2B211B"),
                )
                st.plotly_chart(fig, use_container_width=True)

        # ── TOC Connection (not in presentation mode) ──────────────────────

        if not pmode:
            st.markdown("<br>", unsafe_allow_html=True)
            with st.expander("⬡  WHY FINITE AUTOMATA? — TOC Connection", expanded=False):
                col_a, col_b = st.columns([1, 1])
                with col_a:
                    st.markdown(
                        """
<div style='font-family:monospace;font-size:0.85rem;color:#F3E8D5;line-height:2;'>
<span style='color:#A66A3F;'>TOKEN PATTERN</span><br>
&nbsp;&nbsp;&nbsp;&nbsp;↓<br>
<span style='color:#A66A3F;'>REGULAR EXPRESSION</span><br>
&nbsp;&nbsp;&nbsp;&nbsp;↓<br>
<span style='color:#A66A3F;'>REGULAR LANGUAGE</span><br>
&nbsp;&nbsp;&nbsp;&nbsp;↓<br>
<span style='color:#A66A3F;'>FINITE AUTOMATON</span><br>
&nbsp;&nbsp;&nbsp;&nbsp;↓<br>
<span style='color:#7F9C72;'>ACCEPT / REJECT</span>
</div>
                        """,
                        unsafe_allow_html=True,
                    )
                with col_b:
                    st.markdown(
                        """
<div style='font-size:0.85rem;color:#B8A99A;line-height:1.7;'>
<p>A lexical analyzer needs to recognize patterns such as
<strong style='color:#F3E8D5;'>identifiers</strong> and
<strong style='color:#F3E8D5;'>numbers</strong>.</p>
<p>These patterns can be expressed as
<strong style='color:#F3E8D5;'>regular expressions</strong>,
which describe <strong style='color:#F3E8D5;'>regular languages</strong>.</p>
<p>By the Kleene theorem, every regular language can be recognized
by a <strong style='color:#F3E8D5;'>finite automaton (DFA / NFA)</strong>.</p>
<p>Therefore, finite automata provide the theoretical
foundation for lexical recognition.</p>
</div>
                        """,
                        unsafe_allow_html=True,
                    )

            with st.expander("◎  HOW DOES LEXISCAN WORK?", expanded=False):
                st.markdown(
                    """
<div style='font-family:monospace;font-size:0.82rem;color:#F3E8D5;line-height:2.1;'>
1. Read source code<br>
&nbsp;&nbsp;&nbsp;&nbsp;↓<br>
2. Scan characters left-to-right<br>
&nbsp;&nbsp;&nbsp;&nbsp;↓<br>
3. Identify lexemes (longest match)<br>
&nbsp;&nbsp;&nbsp;&nbsp;↓<br>
4. Match token patterns (regex / DFA)<br>
&nbsp;&nbsp;&nbsp;&nbsp;↓<br>
5. Classify tokens<br>
&nbsp;&nbsp;&nbsp;&nbsp;↓<br>
6. Report lexical errors
</div>
                    """,
                    unsafe_allow_html=True,
                )

    elif not st.session_state.scanned:
        # Hero message when nothing has been scanned yet
        st.markdown(
            """
<div style='text-align:center;padding:3rem 0 2rem;'>
  <p style='color:#A66A3F;font-size:2rem;font-weight:800;letter-spacing:0.04em;
            margin-bottom:0.4rem;'>Decode the Language of Code.</p>
  <p style='color:#B8A99A;font-size:0.95rem;max-width:520px;margin:0 auto;'>
    Enter source code above, choose an example,
    and click <strong style='color:#F3E8D5;'>⚡ SCAN CODE</strong> to begin lexical analysis.
  </p>
</div>
            """,
            unsafe_allow_html=True,
        )


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: FINITE AUTOMATA
# ═══════════════════════════════════════════════════════════════════════════════

elif nav == "⚙ Finite Automata Lab":

    meta_keys = list(au.DFA_REGISTRY.keys())

    # ── Page header ──────────────────────────────────────────────────────────
    st.markdown(
        '<h2 style="font-size:1.6rem;font-weight:800;letter-spacing:0.04em;">'
        '⚙ FINITE AUTOMATA LAB</h2>',
        unsafe_allow_html=True,
    )
    if not pmode:
        st.markdown(
            '<p style="color:#B8A99A;font-size:0.88rem;">'
            "Explore how finite automata recognize the patterns used by a lexical analyzer.<br>"
            "Every diagram, transition table, and simulation on this page is mathematically accurate.</p>",
            unsafe_allow_html=True,
        )
    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Token pattern selector ────────────────────────────────────────────────
    section_title("Select Token Pattern", "◎")
    dfa_choice = st.selectbox(
        "Token type",
        meta_keys,
        label_visibility="collapsed",
        key="lab_dfa_choice",
    )
    dfa  = au.DFA_REGISTRY[dfa_choice]
    meta = au.DFA_META[dfa_choice]

    st.markdown("<br>", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 1 — Regular Expression
    # ══════════════════════════════════════════════════════════════════════════
    section_title("Regular Expression", "◎")
    card(
        f'<p style="color:#A66A3F;font-size:0.68rem;font-weight:700;'
        f'letter-spacing:0.12em;margin-bottom:0.5rem;">PATTERN</p>'
        f'<div style="background:#171310;border:1px solid #2B211B;border-radius:6px;'
        f'padding:0.7rem 1.2rem;margin-bottom:0.8rem;">'
        f'<code style="color:#C49A5A;font-size:1.2rem;font-weight:700;'
        f'letter-spacing:0.04em;">{meta["regex"]}</code>'
        f'</div>'
        f'<p style="color:#B8A99A;font-size:0.84rem;line-height:1.6;margin:0;">'
        f'{meta["regex_explain"]}</p>'
        f'<p style="color:#B8A99A;font-size:0.76rem;margin-top:0.6rem;">'
        f'<strong style="color:#A66A3F;">Alphabet Σ:</strong> '
        f'<code style="color:#F3E8D5;">{meta["alphabet"]}</code></p>'
    )

    # TOC flow arrow (compact)
    if not pmode:
        st.markdown(
            '<div style="font-family:monospace;font-size:0.78rem;color:#B8A99A;'
            'text-align:center;padding:0.4rem 0;letter-spacing:0.06em;">'
            '<span style="color:#A66A3F;">REGULAR EXPRESSION</span>'
            '&nbsp;&nbsp;→&nbsp;&nbsp;'
            '<span style="color:#A66A3F;">REGULAR LANGUAGE</span>'
            '&nbsp;&nbsp;→&nbsp;&nbsp;'
            '<span style="color:#A66A3F;">FINITE AUTOMATON</span>'
            '</div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 2 — DFA Diagram + Automaton Details (two columns)
    # ══════════════════════════════════════════════════════════════════════════
    col_diag, col_detail = st.columns([3, 2])

    with col_diag:
        section_title(f"{dfa_choice} — DFA Diagram", "◎")
        dot_src = au.dfa_to_dot(dfa)
        st.graphviz_chart(dot_src, use_container_width=True)

        # Legend
        st.markdown(
            '<p style="color:#B8A99A;font-size:0.72rem;margin-top:0.2rem;">'
            '<span style="color:#A66A3F;">→</span> Start state &nbsp;·&nbsp; '
            '<span style="color:#7F9C72;">⊙</span> Accepting state (double circle) &nbsp;·&nbsp; '
            'Dead/trap state omitted for clarity.</p>',
            unsafe_allow_html=True,
        )

    with col_detail:
        # ── Automaton details card ────────────────────────────────────────
        section_title("Automaton Details", "◎")
        visible_states = [s.name for s in dfa.states if s.name != dfa.dead_state]
        card(
            f'<table style="border-collapse:collapse;font-size:0.83rem;width:100%;">'
            f'<tr><td style="color:#B8A99A;padding:5px 0;width:130px;vertical-align:top;">Type</td>'
            f'<td style="color:#F3E8D5;font-weight:600;">DFA</td></tr>'
            f'<tr><td style="color:#B8A99A;padding:5px 0;vertical-align:top;">States</td>'
            f'<td><code style="color:#F3E8D5;">{", ".join(visible_states)}</code></td></tr>'
            f'<tr><td style="color:#B8A99A;padding:5px 0;vertical-align:top;">Alphabet Σ</td>'
            f'<td style="color:#F3E8D5;">{meta["alphabet"]}</td></tr>'
            f'<tr><td style="color:#B8A99A;padding:5px 0;vertical-align:top;">Start State q₀</td>'
            f'<td><code style="color:#C49A5A;font-weight:700;">{dfa.start}</code></td></tr>'
            f'<tr><td style="color:#B8A99A;padding:5px 0;vertical-align:top;">Accepting F</td>'
            f'<td><code style="color:#7F9C72;font-weight:700;">'
            + ", ".join(sorted(dfa.accepting))
            + f'</code></td></tr>'
            f'</table>',
            padding="1rem 1.2rem"
        )

        # ── Transition table (compact, formatted) ─────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        section_title("Transition Table  δ(state, input)", "◎")

        # Build a proper pivot-style table
        t_rows = []
        for from_st, trans_map in dfa.transitions.items():
            if from_st == dfa.dead_state:
                continue
            row: dict[str, str] = {}
            # State label with markers
            markers = ""
            if from_st == dfa.start:
                markers += "→ "
            if from_st in dfa.accepting:
                markers += "★ "
            row["State"] = markers + from_st
            for label, to_st in trans_map.items():
                row[label] = to_st
            t_rows.append(row)

        if t_rows:
            t_df = pd.DataFrame(t_rows).fillna("Dead")

            def _style_cell(v: str) -> str:
                if v in dfa.accepting:
                    return "color:#7F9C72;font-weight:600;"
                if "Dead" in v or "qd" in v:
                    return "color:#B85C5C;"
                if v.startswith(("→", "★")):
                    return "color:#C49A5A;font-weight:600;"
                return "color:#F3E8D5;"

            st.dataframe(
                t_df.style.map(_style_cell),
                hide_index=True,
                use_container_width=True,
            )
            st.markdown(
                '<p style="color:#B8A99A;font-size:0.72rem;margin-top:0.2rem;">'
                '→ Start &nbsp;·&nbsp; ★ Accepting &nbsp;·&nbsp; '
                '<span style="color:#B85C5C;">Dead</span> = trap state</p>',
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 3 — Language Recognized + Examples
    # ══════════════════════════════════════════════════════════════════════════
    col_lang, col_acc, col_rej = st.columns([2, 1, 1])

    with col_lang:
        section_title("Language Recognized", "◎")
        card(
            f'<p style="color:#A66A3F;font-size:0.68rem;font-weight:700;'
            f'letter-spacing:0.12em;margin-bottom:0.5rem;">FORMAL LANGUAGE</p>'
            f'<p style="color:#F3E8D5;font-size:0.85rem;line-height:1.65;margin-bottom:0.6rem;">'
            f'{meta["language_desc"]}</p>'
            f'<hr style="border-color:#2B211B;margin:0.6rem 0;">'
            f'<p style="color:#B8A99A;font-size:0.8rem;line-height:1.55;">'
            f'{meta["academic_note"]}</p>'
        )

    with col_acc:
        section_title("✓ Accepted Strings", "◎")
        items = "".join(
            f'<div style="background:#1A2B17;border:1px solid #2B3D27;border-radius:5px;'
            f'padding:4px 10px;margin-bottom:5px;font-family:monospace;'
            f'font-size:0.85rem;color:#7F9C72;">{s}</div>'
            for s in meta["accepted"]
        )
        st.markdown(
            f'<div style="margin-top:0.3rem;">{items}'
            f'<p style="color:#B8A99A;font-size:0.72rem;margin-top:0.5rem;">'
            f'{meta["accepted_reason"]}</p></div>',
            unsafe_allow_html=True,
        )

    with col_rej:
        section_title("✕ Rejected Strings", "◎")
        items = "".join(
            f'<div style="background:#2A1414;border:1px solid #3D2020;border-radius:5px;'
            f'padding:4px 10px;margin-bottom:5px;font-family:monospace;'
            f'font-size:0.85rem;color:#B85C5C;">{s}</div>'
            for s in meta["rejected"]
        )
        st.markdown(
            f'<div style="margin-top:0.3rem;">{items}'
            f'<p style="color:#B8A99A;font-size:0.72rem;margin-top:0.5rem;">'
            f'{meta["rejected_reason"]}</p></div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 4 — Collapsible: Formal 5-Tuple Definition
    # ══════════════════════════════════════════════════════════════════════════
    with st.expander("◎  FORMAL DEFINITION  —  M = (Q, Σ, δ, q₀, F)", expanded=False):
        fc_left, fc_right = st.columns([1, 1])
        with fc_left:
            st.markdown(
                f'<div style="font-family:monospace;font-size:0.85rem;line-height:2;color:#F3E8D5;">'
                f'<span style="color:#A66A3F;">M = (Q, Σ, δ, q₀, F)</span><br><br>'
                f'<span style="color:#B8A99A;">Q</span> = '
                f'{{ {", ".join(meta["Q"])} }}<br>'
                f'<span style="color:#B8A99A;">Σ</span> = '
                f'{{ {", ".join(meta["sigma"])} }}<br>'
                f'<span style="color:#B8A99A;">q₀</span> = '
                f'<span style="color:#C49A5A;">{meta["q0"]}</span><br>'
                f'<span style="color:#B8A99A;">F</span> = '
                f'{{ <span style="color:#7F9C72;">{", ".join(meta["F"])}</span> }}'
                f'</div>',
                unsafe_allow_html=True,
            )
        with fc_right:
            st.markdown(
                '<div style="font-size:0.82rem;color:#B8A99A;line-height:1.9;">'
                '<p><strong style="color:#F3E8D5;">Q</strong> — Set of all states in the automaton</p>'
                '<p><strong style="color:#F3E8D5;">Σ</strong> — Input alphabet (set of valid symbols)</p>'
                '<p><strong style="color:#F3E8D5;">δ</strong> — Transition function: Q × Σ → Q</p>'
                '<p><strong style="color:#F3E8D5;">q₀</strong> — Start state (initial configuration)</p>'
                '<p><strong style="color:#F3E8D5;">F</strong> — Set of accepting (final) states</p>'
                '</div>',
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            '<p style="color:#A66A3F;font-size:0.68rem;font-weight:700;'
            'letter-spacing:0.1em;margin-bottom:0.4rem;">TRANSITION FUNCTION δ</p>',
            unsafe_allow_html=True,
        )
        delta_lines = "".join(
            f'<div style="font-family:monospace;font-size:0.84rem;color:#F3E8D5;'
            f'line-height:1.9;">'
            f'<span style="color:#B8A99A;">δ(</span>'
            f'<span style="color:#C49A5A;">{frm}</span>'
            f'<span style="color:#B8A99A;">,&nbsp;</span>'
            f'<span style="color:#F3E8D5;">{inp}</span>'
            f'<span style="color:#B8A99A;">)</span>'
            f' = <span style="color:#7F9C72;">{to}</span>'
            f'</div>'
            for frm, inp, to in meta["delta_display"]
        )
        st.markdown(
            f'<div style="background:#171310;border:1px solid #2B211B;border-radius:6px;'
            f'padding:0.8rem 1.2rem;">{delta_lines}</div>',
            unsafe_allow_html=True,
        )

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 5 — DFA vs NFA (educational)
    # ══════════════════════════════════════════════════════════════════════════
    if not pmode:
        with st.expander("⬡  DFA vs NFA — Educational Comparison", expanded=False):
            st.markdown(
                '<p style="color:#B8A99A;font-size:0.84rem;margin-bottom:0.8rem;">'
                'LexiScan uses <strong style="color:#F3E8D5;">DFA-style recognition</strong>. '
                'Understanding the difference between DFA and NFA is important for TOC.</p>',
                unsafe_allow_html=True,
            )
            cmp_df = pd.DataFrame([
                ["One transition per input symbol", "Multiple transitions may exist"],
                ["No ε-transitions", "ε-transitions allowed"],
                ["Exactly one active state", "Multiple possible active states"],
                ["Deterministic execution", "Non-deterministic execution"],
                ["Easier to implement", "More compact to describe some languages"],
                ["Used in LexiScan ✓", "Not used in LexiScan"],
            ], columns=["DFA", "NFA"])

            def _style_dfa_col(v: str) -> str:
                if "✓" in v:
                    return "color:#7F9C72;font-weight:600;"
                return "color:#F3E8D5;"

            def _style_nfa_col(v: str) -> str:
                return "color:#B8A99A;"

            st.dataframe(
                cmp_df.style
                    .map(_style_dfa_col, subset=["DFA"])
                    .map(_style_nfa_col, subset=["NFA"]),
                hide_index=True,
                use_container_width=True,
            )
            st.markdown(
                '<p style="color:#B8A99A;font-size:0.82rem;line-height:1.6;margin-top:0.6rem;">'
                'By the <strong style="color:#F3E8D5;">Kleene theorem</strong>, every regular language '
                'can be recognized by both a DFA and an NFA. '
                'In practice, lexical analyzers use DFAs because they are deterministic — '
                'at each step, exactly one transition is possible, making them efficient to simulate.</p>',
                unsafe_allow_html=True,
            )

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 6 — From DFA to Token
    # ══════════════════════════════════════════════════════════════════════════
    if not pmode:
        st.markdown("<br>", unsafe_allow_html=True)
        section_title("From DFA to Token", "◎")
        ex_accepted = meta["accepted"][0]
        card(
            f'<p style="color:#A66A3F;font-size:0.68rem;font-weight:700;'
            f'letter-spacing:0.12em;margin-bottom:0.8rem;">COMPLETE RECOGNITION CHAIN</p>'
            f'<div style="font-family:monospace;font-size:0.85rem;color:#F3E8D5;'
            f'text-align:center;line-height:2.4;">'
            f'<span style="background:#2B211B;border:1px solid #7A4E2D;border-radius:5px;'
            f'padding:3px 14px;color:#C49A5A;">Input Lexeme: {ex_accepted}</span>'
            f'<br>↓<br>'
            f'<span style="background:#2B211B;border:1px solid #7A4E2D;border-radius:5px;'
            f'padding:3px 14px;color:#F3E8D5;">{dfa_choice} DFA</span>'
            f'<br>↓<br>'
            f'<span style="background:#2B211B;border:1px solid #7A4E2D;border-radius:5px;'
            f'padding:3px 14px;color:#F3E8D5;">Final State: '
            f'<span style="color:#7F9C72;">{", ".join(sorted(dfa.accepting))}</span> (accepting)</span>'
            f'<br>↓<br>'
            f'<span style="background:#1A2B17;border:1px solid #7F9C72;border-radius:5px;'
            f'padding:3px 14px;color:#7F9C72;font-weight:700;">✓ ACCEPTED</span>'
            f'<br>↓<br>'
            f'<span style="background:#2B211B;border:1px solid #7A4E2D;border-radius:5px;'
            f'padding:3px 14px;color:#F3E8D5;">Token: '
            f'<span style="color:#A66A3F;font-weight:700;">{dfa.token_type}</span></span>'
            f'</div>'
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 7 — Longest Match note
    # ══════════════════════════════════════════════════════════════════════════
    if not pmode:
        card(
            f'<p style="color:#A66A3F;font-size:0.68rem;font-weight:700;'
            f'letter-spacing:0.12em;margin-bottom:0.4rem;">LONGEST MATCH RULE</p>'
            f'<p style="color:#B8A99A;font-size:0.84rem;line-height:1.6;margin:0;">'
            f'{meta["longest_match_note"]}</p>'
        )


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: DFA SIMULATOR
# ═══════════════════════════════════════════════════════════════════════════════

elif nav == "▶ DFA Simulator":

    st.markdown(
        '<h2 style="font-size:1.6rem;font-weight:800;letter-spacing:0.04em;">'
        '▶ DFA SIMULATOR</h2>',
        unsafe_allow_html=True,
    )
    if not pmode:
        st.markdown(
            '<p style="color:#B8A99A;font-size:0.88rem;">'
            "Trace the execution of a DFA on any input string — one character at a time. "
            "Use <strong>Prev</strong> / <strong>Next</strong> to step through, "
            "or <strong>Simulate</strong> to run in full.</p>",
            unsafe_allow_html=True,
        )
    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Configuration row ────────────────────────────────────────────────────
    col_cfg, col_diag = st.columns([2, 3])

    with col_cfg:
        section_title("TOKEN TYPE", "◎")
        sim_dfa_name = st.selectbox(
            "DFA",
            list(au.DFA_REGISTRY.keys()),
            label_visibility="collapsed",
            key="sim_dfa_sel",
        )

        section_title("TEST STRING", "◎")
        test_input = st.text_input(
            "Input string",
            value=st.session_state.sim_input if st.session_state.sim_input else "student123",
            label_visibility="collapsed",
            max_chars=80,
            key="sim_text_input",
        )

        btn_col1, btn_col2 = st.columns([1, 1])
        with btn_col1:
            simulate_btn = st.button("▶  SIMULATE", key="btn_sim")
        with btn_col2:
            reset_btn = st.button("↺  RESET", key="btn_sim_reset")

        # Step nav buttons (only visible after simulation)
        if st.session_state.sim_result is not None:
            st.markdown("<br>", unsafe_allow_html=True)
            section_title("STEP NAVIGATION", "◎")
            nav_c1, nav_c2 = st.columns([1, 1])
            with nav_c1:
                prev_btn = st.button("◀  Prev", key="btn_prev")
            with nav_c2:
                next_btn = st.button("Next  ▶", key="btn_next")
            total_steps = len(st.session_state.sim_result.steps) - 1
            current_step = st.session_state.sim_step
            st.markdown(
                f'<p style="color:#B8A99A;font-size:0.78rem;margin-top:0.3rem;">'
                f'Step {current_step} of {total_steps}</p>',
                unsafe_allow_html=True,
            )

    # ── DFA diagram (static or highlighted) ─────────────────────────────────
    with col_diag:
        st.markdown("<br>", unsafe_allow_html=True)
        sim_dfa = au.DFA_REGISTRY[sim_dfa_name]
        # If a simulation is active for the same DFA, highlight current state
        if (st.session_state.sim_result is not None
                and st.session_state.sim_dfa_name == sim_dfa_name):
            steps_so_far = st.session_state.sim_result.steps
            cur_step_idx = min(st.session_state.sim_step, len(steps_so_far) - 1)
            hl_state = steps_so_far[cur_step_idx].next_state
            dot_src = au.dfa_to_dot(sim_dfa, highlight_state=hl_state)
        else:
            dot_src = au.dfa_to_dot(sim_dfa)
        st.graphviz_chart(dot_src, use_container_width=True)

    # ── Handle button actions ────────────────────────────────────────────────
    if reset_btn:
        st.session_state.sim_result = None
        st.session_state.sim_step   = 0
        st.session_state.sim_input  = ""
        st.rerun()

    if simulate_btn:
        if not test_input.strip():
            st.warning("Please enter a non-empty test string.")
        else:
            result = au.simulate_dfa(sim_dfa, test_input)
            st.session_state.sim_result   = result
            st.session_state.sim_step     = len(result.steps) - 1  # show full trace
            st.session_state.sim_input    = test_input
            st.session_state.sim_dfa_name = sim_dfa_name
            st.rerun()

    if st.session_state.sim_result is not None:
        if "prev_btn" in dir() and prev_btn:
            st.session_state.sim_step = max(0, st.session_state.sim_step - 1)
            st.rerun()
        if "next_btn" in dir() and next_btn:
            max_step = len(st.session_state.sim_result.steps) - 1
            st.session_state.sim_step = min(max_step, st.session_state.sim_step + 1)
            st.rerun()

    # ── Render simulation results ────────────────────────────────────────────
    result = st.session_state.sim_result
    if result is not None:
        cur_step = st.session_state.sim_step
        all_steps = result.steps

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Input string with highlighted character ───────────────────────
        section_title("DFA Execution", "◎")
        inp_str = st.session_state.sim_input

        if inp_str:
            # Highlight the character being read at current step
            ch_idx = cur_step - 1   # step 0 is the initial row (no char consumed)
            parts = []
            for i, ch in enumerate(inp_str):
                if i == ch_idx:
                    parts.append(
                        f'<span style="background:#C49A5A;color:#171310;'
                        f'font-weight:800;border-radius:3px;padding:0 4px;">{ch}</span>'
                    )
                else:
                    parts.append(
                        f'<span style="color:#B8A99A;">{ch}</span>'
                    )
            highlighted_input = "".join(parts)
            st.markdown(
                f'<div style="background:#171310;border:1px solid #2B211B;'
                f'border-radius:6px;padding:0.5rem 1rem;margin-bottom:0.6rem;'
                f'font-family:monospace;font-size:1.1rem;letter-spacing:0.08em;">'
                f'Input: {highlighted_input}</div>',
                unsafe_allow_html=True,
            )

        # ── Step table up to current step ─────────────────────────────────
        visible_steps = all_steps[:cur_step + 1]
        step_rows = []
        for s in visible_steps:
            step_rows.append({
                "Step":          s.step,
                "Character":     s.character,
                "Current State": s.current_state,
                "Next State":    s.next_state,
                "Note":          s.note,
            })
        step_df = pd.DataFrame(step_rows)

        def colour_state(val: str) -> str:
            if val in sim_dfa.accepting:
                return "color:#7F9C72;font-weight:700;"
            if val in ("DEAD", sim_dfa.dead_state or "qd"):
                return "color:#B85C5C;"
            return "color:#F3E8D5;"

        styled_steps = step_df.style.map(
            colour_state, subset=["Current State", "Next State"]
        )
        st.dataframe(
            styled_steps,
            hide_index=True,
            use_container_width=True,
            height=min(60 + 36 * len(step_df), 380),
        )

        # ── Current state indicator ───────────────────────────────────────
        if visible_steps:
            last = visible_steps[-1]
            cs  = last.next_state
            is_accepting = cs in sim_dfa.accepting
            is_dead      = cs in ("DEAD", sim_dfa.dead_state or "qd")
            state_colour = "#7F9C72" if is_accepting else ("#B85C5C" if is_dead else "#C49A5A")
            st.markdown(
                f'<div style="display:flex;align-items:center;gap:1rem;'
                f'background:#211A16;border:1px solid #2B211B;border-radius:8px;'
                f'padding:0.6rem 1.2rem;margin-top:0.4rem;">'
                f'<span style="color:#B8A99A;font-size:0.78rem;">Current State:</span>'
                f'<code style="color:{state_colour};font-size:1rem;font-weight:700;">{cs}</code>'
                f'</div>',
                unsafe_allow_html=True,
            )

        # ── Verdict (only shown when all steps consumed) ──────────────────
        all_consumed = cur_step >= len(all_steps) - 1
        if all_consumed:
            st.markdown("<br>", unsafe_allow_html=True)
            section_title("Verdict", "◎")
            if result.accepted:
                st.markdown(
                    f'<div style="background:#1A2B17;border:1px solid #7F9C72;'
                    f'border-radius:10px;padding:1.2rem 1.5rem;">'
                    f'<p style="color:#7F9C72;font-size:1.5rem;font-weight:800;margin:0;">✓ ACCEPTED</p>'
                    f'<p style="color:#B8A99A;font-size:0.85rem;margin:0.4rem 0 0;">'
                    f'The input <code style="color:#F3E8D5;">{inp_str}</code> '
                    f'is recognized as a valid '
                    f'<strong style="color:#F3E8D5;">{result.token_type}</strong>.</p>'
                    f'<p style="color:#B8A99A;font-size:0.8rem;margin-top:0.4rem;">'
                    f'Final state: <strong style="color:#7F9C72;">{result.final_state}</strong> '
                    f'— accepting state (double circle in diagram)</p>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f'<div style="background:#2A1414;border:1px solid #B85C5C;'
                    f'border-radius:10px;padding:1.2rem 1.5rem;">'
                    f'<p style="color:#B85C5C;font-size:1.5rem;font-weight:800;margin:0;">✕ REJECTED</p>'
                    f'<p style="color:#B8A99A;font-size:0.85rem;margin:0.4rem 0 0;">'
                    f'<strong>Reason:</strong> {result.reason}</p>'
                    f'<p style="color:#B8A99A;font-size:0.8rem;margin-top:0.4rem;">'
                    f'Final state: <strong style="color:#B85C5C;">{result.final_state}</strong> '
                    f'— not an accepting state</p>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

            # ── From DFA to Token chain ───────────────────────────────────
            if result.accepted:
                st.markdown("<br>", unsafe_allow_html=True)
                section_title("From DFA to Token", "◎")
                card(
                    f'<div style="font-family:monospace;font-size:0.85rem;color:#F3E8D5;'
                    f'text-align:center;line-height:2.4;">'
                    f'<span style="background:#2B211B;border:1px solid #7A4E2D;border-radius:5px;'
                    f'padding:3px 14px;color:#C49A5A;">Input Lexeme: {inp_str}</span>'
                    f'<br>↓<br>'
                    f'<span style="background:#2B211B;border:1px solid #7A4E2D;border-radius:5px;'
                    f'padding:3px 14px;color:#F3E8D5;">{sim_dfa_name} DFA</span>'
                    f'<br>↓<br>'
                    f'<span style="background:#2B211B;border:1px solid #7A4E2D;border-radius:5px;'
                    f'padding:3px 14px;color:#F3E8D5;">Final State: '
                    f'<span style="color:#7F9C72;">{result.final_state}</span> (accepting)</span>'
                    f'<br>↓<br>'
                    f'<span style="background:#1A2B17;border:1px solid #7F9C72;border-radius:5px;'
                    f'padding:3px 14px;color:#7F9C72;font-weight:700;">✓ ACCEPTED</span>'
                    f'<br>↓<br>'
                    f'<span style="background:#2B211B;border:1px solid #7A4E2D;border-radius:5px;'
                    f'padding:3px 14px;color:#F3E8D5;">Token: '
                    f'<span style="color:#A66A3F;font-weight:700;">{result.token_type}</span></span>'
                    f'</div>'
                )

            # ── Quick reference ───────────────────────────────────────────
            if not pmode:
                st.markdown("<br>", unsafe_allow_html=True)
                section_title("Quick Reference — Test Cases", "◎")
                dfa_meta = au.DFA_META.get(sim_dfa_name, {})
                acc_list = dfa_meta.get("accepted", [])
                rej_list = dfa_meta.get("rejected", [])
                ref_rows = (
                    [(s, "✓") for s in acc_list] +
                    [(s, "✕") for s in rej_list]
                )
                ref_df = pd.DataFrame(ref_rows, columns=["Input", "Expected"])

                def colour_expected(v: str) -> str:
                    return "color:#7F9C72;font-weight:700;" if "✓" in v else "color:#B85C5C;font-weight:700;"

                st.dataframe(
                    ref_df.style.map(colour_expected, subset=["Expected"]),
                    hide_index=True,
                    use_container_width=False,
                )



# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: ABOUT
# ═══════════════════════════════════════════════════════════════════════════════

elif nav == "ⓘ About":

    st.markdown(
        '<h2 style="font-size:1.6rem;font-weight:800;letter-spacing:0.04em;">'
        'ⓘ ABOUT LEXISCAN</h2>',
        unsafe_allow_html=True,
    )
    st.markdown("<hr>", unsafe_allow_html=True)

    col_l, col_r = st.columns([3, 2])

    with col_l:
        card(
            '<p style="color:#A66A3F;font-size:0.68rem;font-weight:700;'
            'letter-spacing:0.12em;margin-bottom:0.6rem;">OVERVIEW</p>'
            '<p style="color:#F3E8D5;font-size:0.88rem;line-height:1.65;">'
            '<strong>LexiScan</strong> is an interactive educational lexical analyzer '
            'built as a Theory of Computation course project. '
            'It demonstrates how source code is broken into lexemes, how those lexemes '
            'are classified into token categories, and how finite automata serve as the '
            'theoretical foundation for recognizing lexical patterns.</p>'
        )

        card(
            '<p style="color:#A66A3F;font-size:0.68rem;font-weight:700;'
            'letter-spacing:0.12em;margin-bottom:0.6rem;">PROBLEM STATEMENT</p>'
            '<p style="color:#B8A99A;font-size:0.85rem;line-height:1.65;">'
            'Understanding lexical analysis and its relationship with finite automata '
            'can be difficult when studied only theoretically. '
            'LexiScan provides an interactive way to observe how source code '
            'is divided into lexemes and classified into tokens, with step-by-step '
            'DFA simulation and accurate automaton visualizations.</p>'
        )

        card(
            '<p style="color:#A66A3F;font-size:0.68rem;font-weight:700;'
            'letter-spacing:0.12em;margin-bottom:0.8rem;">OBJECTIVES</p>'
            '<ol style="color:#B8A99A;font-size:0.85rem;line-height:1.9;margin:0;padding-left:1.2rem;">'
            '<li>Understand what lexical analysis is and why it is the first phase of compilation.</li>'
            '<li>Understand the concepts of lexemes, tokens, and token categories.</li>'
            '<li>See how regular expressions describe lexical patterns.</li>'
            '<li>Demonstrate finite automata (DFAs) for token recognition.</li>'
            '<li>Recognize and report lexical errors.</li>'
            '<li>Visualize DFA state transitions step-by-step.</li>'
            '</ol>'
        )

        card(
            '<p style="color:#A66A3F;font-size:0.68rem;font-weight:700;'
            'letter-spacing:0.12em;margin-bottom:0.8rem;">TOC CONNECTION</p>'
            '<p style="color:#B8A99A;font-size:0.85rem;line-height:1.65;">'
            'Every token pattern in LexiScan corresponds to a <strong style="color:#F3E8D5;">regular expression</strong>, '
            'which describes a <strong style="color:#F3E8D5;">regular language</strong>. '
            'By the Kleene theorem, every regular language is recognized by a '
            '<strong style="color:#F3E8D5;">deterministic finite automaton (DFA)</strong>. '
            'The DFA diagrams in LexiScan are the actual automata implementing those recognizers.</p>'
        )

        card(
            '<p style="color:#A66A3F;font-size:0.68rem;font-weight:700;'
            'letter-spacing:0.12em;margin-bottom:0.8rem;">LIMITATIONS</p>'
            '<ul style="color:#B8A99A;font-size:0.84rem;line-height:1.8;margin:0;padding-left:1.2rem;">'
            '<li>Educational analyzer — not a production-grade lexer.</li>'
            '<li>Supports C/C++-like syntax; does not handle all language constructs.</li>'
            '<li>Simplified string and comment handling (no escape sequences).</li>'
            '<li>No numeric formats beyond decimal integers and decimals.</li>'
            '<li>No parser, syntax tree, semantic analysis, or code generation.</li>'
            '</ul>'
        )

        card(
            '<p style="color:#A66A3F;font-size:0.68rem;font-weight:700;'
            'letter-spacing:0.12em;margin-bottom:0.8rem;">FUTURE SCOPE</p>'
            '<ul style="color:#B8A99A;font-size:0.84rem;line-height:1.8;margin:0;padding-left:1.2rem;">'
            '<li>Support for more programming languages.</li>'
            '<li>NFA visualization and NFA-to-DFA subset construction.</li>'
            '<li>Hexadecimal, octal, and scientific numeric literals.</li>'
            '<li>Full escape sequence handling in strings.</li>'
            '<li>Symbol table generation.</li>'
            '<li>Integration with a parser (syntax analysis phase).</li>'
            '</ul>'
        )

    with col_r:
        card(
            '<p style="color:#A66A3F;font-size:0.68rem;font-weight:700;'
            'letter-spacing:0.12em;margin-bottom:0.8rem;">TECHNOLOGY STACK</p>'
            '<table style="border-collapse:collapse;font-size:0.82rem;width:100%;">'
            '<tr><td style="color:#B8A99A;padding:4px 0;width:110px;">Language</td>'
            '<td style="color:#F3E8D5;">Python 3</td></tr>'
            '<tr><td style="color:#B8A99A;padding:4px 0;">UI</td>'
            '<td style="color:#F3E8D5;">Streamlit</td></tr>'
            '<tr><td style="color:#B8A99A;padding:4px 0;">Automata viz</td>'
            '<td style="color:#F3E8D5;">Graphviz</td></tr>'
            '<tr><td style="color:#B8A99A;padding:4px 0;">Tables</td>'
            '<td style="color:#F3E8D5;">Pandas</td></tr>'
            '<tr><td style="color:#B8A99A;padding:4px 0;">Charts</td>'
            '<td style="color:#F3E8D5;">Plotly</td></tr>'
            '<tr><td style="color:#B8A99A;padding:4px 0;">Patterns</td>'
            '<td style="color:#F3E8D5;">Python re module</td></tr>'
            '</table>'
        )

        card(
            '<p style="color:#A66A3F;font-size:0.68rem;font-weight:700;'
            'letter-spacing:0.12em;margin-bottom:0.8rem;">TOKEN TYPES</p>'
            '<ul style="color:#B8A99A;font-size:0.82rem;line-height:1.9;margin:0;padding-left:1.2rem;">'
            '<li><span style="color:#F3E8D5;">Keyword</span> — 22 reserved words</li>'
            '<li><span style="color:#F3E8D5;">Identifier</span> — [A-Za-z_][A-Za-z0-9_]*</li>'
            '<li><span style="color:#F3E8D5;">Integer</span> — [0-9]+</li>'
            '<li><span style="color:#F3E8D5;">Float</span> — [0-9]+\\.[0-9]+</li>'
            '<li><span style="color:#F3E8D5;">String</span> — double-quoted literals</li>'
            '<li><span style="color:#F3E8D5;">Comment</span> — // and /* … */</li>'
            '<li><span style="color:#F3E8D5;">Arithmetic Operator</span> — + - * /</li>'
            '<li><span style="color:#F3E8D5;">Relational Operator</span> — &lt; &gt; &lt;= &gt;= == !=</li>'
            '<li><span style="color:#F3E8D5;">Assignment</span> — =</li>'
            '<li><span style="color:#F3E8D5;">Logical Operator</span> — &amp;&amp; || !</li>'
            '<li><span style="color:#F3E8D5;">Separator</span> — ( ) { } [ ] ; , .</li>'
            '</ul>'
        )

        # ── Project Team ──────────────────────────────────────────────────

        card(
            '<p style="color:#A66A3F;font-size:0.68rem;font-weight:700;'
            'letter-spacing:0.12em;margin-bottom:0.8rem;">PROJECT TEAM</p>'
            '<table style="border-collapse:collapse;font-size:0.83rem;width:100%;">'

            '<tr>'
            '<td style="padding:6px 0;vertical-align:top;">'
            '<p style="color:#F3E8D5;font-weight:700;margin:0;">Member 1</p>'
            '<p style="color:#B8A99A;font-size:0.78rem;margin:0;">Lexical Analysis</p>'
            '</td>'
            '<td style="padding:6px 0 6px 1rem;vertical-align:top;">'
            '<span style="background:#2B211B;color:#A66A3F;padding:2px 8px;'
            'border-radius:4px;font-size:0.72rem;font-weight:700;">LEXER</span>'
            '</td>'
            '</tr>'

            '<tr>'
            '<td style="padding:6px 0;vertical-align:top;">'
            '<p style="color:#F3E8D5;font-weight:700;margin:0;">Member 2</p>'
            '<p style="color:#B8A99A;font-size:0.78rem;margin:0;">Finite Automata</p>'
            '</td>'
            '<td style="padding:6px 0 6px 1rem;vertical-align:top;">'
            '<span style="background:#2B3D27;color:#7F9C72;padding:2px 8px;'
            'border-radius:4px;font-size:0.72rem;font-weight:700;">AUTOMATA</span>'
            '</td>'
            '</tr>'

            '<tr>'
            '<td style="padding:6px 0;vertical-align:top;">'
            '<p style="color:#F3E8D5;font-weight:700;margin:0;">Member 3</p>'
            '<p style="color:#B8A99A;font-size:0.78rem;margin:0;">UI &amp; Testing</p>'
            '</td>'
            '<td style="padding:6px 0 6px 1rem;vertical-align:top;">'
            '<span style="background:#1E2B3D;color:#7FA0C4;padding:2px 8px;'
            'border-radius:4px;font-size:0.72rem;font-weight:700;">UI</span>'
            '</td>'
            '</tr>'

            '</table>'
            '<p style="color:#B8A99A;font-size:0.72rem;margin-top:0.8rem;">'
            'Theory of Computation Course — Academic Year 2025–26</p>'
        )

    # Footer
    st.markdown(
        '<hr><p style="color:#2B211B;font-size:0.72rem;text-align:center;">'
        '◈ LexiScan · Educational Lexical Analyzer · '
        'Theory of Computation Course Project</p>',
        unsafe_allow_html=True,
    )
