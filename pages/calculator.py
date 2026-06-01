"""
═══════════════════════════════════════════════════════════════════════════
OMNIX VISION — Calculator (Phase 3)
═══════════════════════════════════════════════════════════════════════════
Phase-3 changes:
    ✓ Full translation (EN/AR + RTL)
    ✓ History persisted to data/calc_history.json (per user)
    ✓ Activity logging for major calculations
    ✓ All 8 tabs preserved: Basic, Scientific, Solver, Graph,
      Units, Number Systems, Formulas, History
    ✓ Memory persisted across sessions
═══════════════════════════════════════════════════════════════════════════
"""

import json
import math
import csv
from io import StringIO
from datetime import datetime
from pathlib import Path

import streamlit as st

from utils.language import t, init_language, apply_rtl_css, is_rtl
from utils.activity import log_action


# ═══════════════════════════════════════════════════════════════════════════
# Paths & Persistence
# ═══════════════════════════════════════════════════════════════════════════
BASE_DIR    = Path(__file__).resolve().parent.parent
DATA_DIR    = BASE_DIR / "data"
CALC_FILE   = DATA_DIR / "calc_history.json"
DATA_DIR.mkdir(parents=True, exist_ok=True)

MAX_HISTORY_PER_USER = 200


def _load_calc_data(user_id: str) -> dict:
    """Load calc history + memory for current user."""
    if not CALC_FILE.exists():
        return {"history": [], "memory": 0.0}
    try:
        with open(CALC_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        user_data = data.get(str(user_id), {})
        return {
            "history": user_data.get("history", []),
            "memory":  float(user_data.get("memory", 0.0)),
        }
    except (json.JSONDecodeError, OSError, ValueError):
        return {"history": [], "memory": 0.0}


def _save_calc_data(user_id: str, history: list, memory: float):
    """Persist calc history + memory."""
    all_data = {}
    if CALC_FILE.exists():
        try:
            with open(CALC_FILE, "r", encoding="utf-8") as f:
                all_data = json.load(f)
        except (json.JSONDecodeError, OSError):
            all_data = {}

    all_data[str(user_id)] = {
        "history": history[-MAX_HISTORY_PER_USER:],
        "memory":  memory,
    }

    try:
        with open(CALC_FILE, "w", encoding="utf-8") as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)
    except OSError:
        pass


# ═══════════════════════════════════════════════════════════════════════════
# Main Render
# ═══════════════════════════════════════════════════════════════════════════

def render_calculator():
    init_language()
    apply_rtl_css()

    if not st.session_state.get("logged_in", False):
        st.session_state.page = "login"
        st.rerun()

    user_id = st.session_state.get("user", "anonymous")
    is_ar   = is_rtl()

    # ── Load history & memory from disk (once per session) ────────────────
    if "calc_loaded" not in st.session_state:
        data = _load_calc_data(user_id)
        st.session_state.history       = data["history"]
        st.session_state.memory        = data["memory"]
        st.session_state.calc_loaded   = True

    # ── CSS ───────────────────────────────────────────────────────────────
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@400;600;700&display=swap');

    [data-testid="stSidebar"], [data-testid="collapsedControl"] {{ display: none; }}

    [data-testid="stAppDeployButton"],
    [data-testid="stToolbar"],
    header[data-testid="stHeader"] {{
        background: transparent !important;
        box-shadow: none !important;
    }}

    .block-container {{
        max-width: 1150px;
        padding-top: 1.4rem;
        padding-left: 1rem;
        padding-right: 1rem;
        {"direction: rtl;" if is_ar else ""}
    }}

    .stApp {{
        background:
            radial-gradient(ellipse at 10% 10%, rgba(56,189,248,0.13) 0%, transparent 40%),
            radial-gradient(ellipse at 90% 8%,  rgba(168,85,247,0.13) 0%, transparent 40%),
            radial-gradient(ellipse at 50% 98%, rgba(34,197,94,0.07)  0%, transparent 36%),
            linear-gradient(160deg, #020617 0%, #060d1f 50%, #0a0520 100%);
        color: #f8fafc;
        font-family: 'Rajdhani', sans-serif;
    }}

    .hero {{
        position: relative; overflow: hidden;
        background: linear-gradient(135deg, rgba(2,6,23,0.97), rgba(15,23,42,0.78));
        border: 1px solid rgba(56,189,248,0.28);
        border-radius: 30px;
        padding: 36px 32px;
        text-align: center;
        box-shadow: 0 0 55px rgba(56,189,248,0.12);
        margin-bottom: 22px;
    }}
    .hero h1 {{
        font-family: 'Orbitron', monospace;
        font-size: 42px;
        font-weight: 900;
        margin: 0;
        letter-spacing: 3px;
        background: linear-gradient(90deg, #38bdf8 0%, #a855f7 40%, #22c55e 75%, #38bdf8 100%);
        background-size: 300% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: shimmer 5s linear infinite;
    }}
    @keyframes shimmer {{ to {{ background-position: 300% center; }} }}
    .hero p {{
        color: #475569;
        font-size: 13px;
        margin-top: 10px;
        letter-spacing: 1.5px;
    }}

    .feature-card {{
        background: linear-gradient(145deg, rgba(2,6,23,0.97), rgba(15,23,42,0.78));
        border: 1px solid rgba(56,189,248,0.16);
        border-radius: 22px;
        padding: 22px 16px 18px;
        text-align: center;
        min-height: 148px;
        transition: all 0.38s cubic-bezier(0.34,1.56,0.64,1);
        margin-bottom: 16px;
    }}
    .feature-card:hover {{
        transform: translateY(-8px) scale(1.015);
        border-color: rgba(56,189,248,0.65);
        box-shadow: 0 16px 44px rgba(56,189,248,0.18);
    }}
    .animated-icon {{
        font-size: 44px;
        display: block;
        margin-bottom: 10px;
        filter: drop-shadow(0 0 14px rgba(56,189,248,0.45));
        animation: floatIcon 2.8s ease-in-out infinite;
    }}
    @keyframes floatIcon {{
        0%,100% {{ transform: translateY(0) scale(1); }}
        50% {{ transform: translateY(-8px) scale(1.06); }}
    }}
    .feature-title {{
        font-family: 'Orbitron', monospace;
        color: #38bdf8;
        font-size: 14px;
        font-weight: 700;
        margin-bottom: 6px;
        letter-spacing: 1px;
    }}
    .feature-text {{ color: #64748b; font-size: 12px; }}

    .glass-card {{
        background: linear-gradient(145deg, rgba(2,6,23,0.97), rgba(15,23,42,0.80));
        border: 1px solid rgba(56,189,248,0.18);
        border-radius: 26px;
        padding: 28px 26px;
        box-shadow: 0 0 40px rgba(56,189,248,0.08);
        margin-top: 14px;
        position: relative;
        overflow: hidden;
    }}

    .section-title {{
        font-family: 'Orbitron', monospace;
        color: #38bdf8;
        font-size: 18px;
        font-weight: 700;
        margin-bottom: 6px;
        letter-spacing: 1px;
        {"text-align: right;" if is_ar else ""}
    }}
    .section-note {{
        color: #475569;
        font-size: 13px;
        margin-bottom: 20px;
        letter-spacing: 0.5px;
        {"text-align: right;" if is_ar else ""}
    }}
    .sub-title {{
        font-family: 'Orbitron', monospace;
        color: #7dd3fc;
        font-size: 14px;
        font-weight: 700;
        letter-spacing: 1px;
        margin: 18px 0 10px;
        padding-left: 10px;
        border-left: 2px solid rgba(56,189,248,0.40);
    }}

    .result-screen {{
        background: linear-gradient(135deg, rgba(2,6,23,0.98), rgba(8,47,73,0.55));
        border: 1px solid rgba(34,197,94,0.65);
        color: #22c55e;
        border-radius: 20px;
        padding: 20px 24px;
        text-align: center;
        font-family: 'Orbitron', monospace;
        font-size: 22px;
        font-weight: 900;
        margin-top: 18px;
        word-break: break-word;
        box-shadow: 0 0 28px rgba(34,197,94,0.14);
        animation: resultPop 0.35s cubic-bezier(0.34,1.56,0.64,1);
    }}
    @keyframes resultPop {{
        from {{ transform: scale(0.94); opacity: 0; }}
        to {{ transform: scale(1); opacity: 1; }}
    }}

    .memory-val {{
        background: rgba(56,189,248,0.06);
        border: 1px solid rgba(56,189,248,0.18);
        border-radius: 14px;
        padding: 10px 16px;
        font-family: 'Orbitron', monospace;
        font-size: 13px;
        color: #7dd3fc;
        margin-top: 8px;
        letter-spacing: 1px;
    }}

    div[data-testid="stTextInput"] input,
    div[data-testid="stNumberInput"] input {{
        background: rgba(56,189,248,0.05) !important;
        color: #e0f2fe !important;
        border: 1px solid rgba(56,189,248,0.28) !important;
        border-radius: 14px !important;
        padding: 11px 14px !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-size: 15px !important;
    }}

    div[data-baseweb="tab-list"] {{
        gap: 6px;
        justify-content: center;
        flex-wrap: wrap;
        background: transparent !important;
    }}
    button[data-baseweb="tab"] {{
        background: rgba(2,6,23,0.80) !important;
        border-radius: 14px !important;
        color: #475569 !important;
        font-weight: 700 !important;
        font-family: 'Rajdhani', sans-serif !important;
        border: 1px solid rgba(56,189,248,0.12) !important;
        padding: 10px 16px !important;
        font-size: 14px !important;
    }}
    button[data-baseweb="tab"][aria-selected="true"] {{
        background: linear-gradient(135deg, rgba(14,165,233,0.22), rgba(124,58,237,0.20)) !important;
        color: #f1f5f9 !important;
        border: 1px solid rgba(56,189,248,0.55) !important;
    }}

    .stButton > button {{
        background: linear-gradient(135deg, #0ea5e9 0%, #7c3aed 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 14px !important;
        padding: 12px 20px !important;
        font-weight: 700 !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-size: 15px !important;
        letter-spacing: 0.5px !important;
        transition: 0.28s ease !important;
        box-shadow: 0 4px 18px rgba(14,165,233,0.18) !important;
    }}
    .stButton > button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 28px rgba(124,58,237,0.36) !important;
    }}
    </style>
    """, unsafe_allow_html=True)

    # ── Helpers ───────────────────────────────────────────────────────────
    def add_history(operation, result):
        st.session_state.history.append({
            "Time":      datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Operation": operation,
            "Result":    str(result),
        })
        _save_calc_data(user_id, st.session_state.history, st.session_state.memory)

    def show_result(value):
        st.markdown(f'<div class="result-screen">{value}</div>', unsafe_allow_html=True)

    def is_binary(v):       return v != "" and all(c in "01" for c in v)
    def is_octal(v):        return v != "" and all(c in "01234567" for c in v)
    def is_decimal(v):      return v != "" and v.isdigit()
    def is_hexadecimal(v):
        try:    int(v, 16); return v != ""
        except ValueError: return False

    def convert_to_decimal(value, system_type):
        value = value.strip().upper()
        checks = {
            "Binary":      (is_binary,      2,  "Invalid binary number"),
            "Octal":       (is_octal,        8,  "Invalid octal number"),
            "Decimal":     (is_decimal,      10, "Invalid decimal number"),
            "Hexadecimal": (is_hexadecimal,  16, "Invalid hexadecimal number"),
        }
        if system_type not in checks:
            raise ValueError("Unknown number system")
        fn, base, msg = checks[system_type]
        if not fn(value):
            raise ValueError(msg)
        return int(value, base)

    def decimal_to_systems(d):
        return {
            "Binary":      bin(d)[2:],
            "Octal":       oct(d)[2:],
            "Decimal":     str(d),
            "Hexadecimal": hex(d)[2:].upper(),
        }

    def safe_calculate_expression(expr):
        funcs = {
            "abs": abs, "round": round, "pow": pow,
            "sqrt": math.sqrt,
            "sin":  lambda x: math.sin(math.radians(x)),
            "cos":  lambda x: math.cos(math.radians(x)),
            "tan":  lambda x: math.tan(math.radians(x)),
            "asin": lambda x: math.degrees(math.asin(x)),
            "acos": lambda x: math.degrees(math.acos(x)),
            "atan": lambda x: math.degrees(math.atan(x)),
            "log": math.log10, "ln": math.log,
            "factorial": math.factorial,
            "pi": math.pi, "e": math.e,
        }
        return eval(expr.replace("^", "**"), {"__builtins__": {}}, funcs)

    def create_csv_from_history():
        out = StringIO()
        w = csv.DictWriter(out, fieldnames=["Time", "Operation", "Result"])
        w.writeheader()
        for row in st.session_state.history:
            w.writerow(row)
        return out.getvalue().encode("utf-8")

    # ── Back Button ───────────────────────────────────────────────────────
    back_col, *_ = st.columns([1.4, 8])
    with back_col:
        if st.button(t("back"), use_container_width=True, key="calc_back_btn"):
            st.session_state.page = "home"
            st.rerun()

    # ── Hero ──────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="hero">
        <h1>🧮 {t('calculator').upper()}</h1>
        <p>ADVANCED CALCULATOR · SMART SOLVER · UNIT CONVERTER · NUMBER SYSTEMS · GRAPH</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Feature Cards ─────────────────────────────────────────────────────
    f1, f2, f3, f4 = st.columns(4)
    feature_data = [
        (f1, "🧮", t("basic_calculator"),  "Fast arithmetic operations"),
        (f2, "🔬", t("scientific_mode"),   "Trig · Logs · Roots"),
        (f3, "🔁", t("smart_converter"),   "Units & measurements"),
        (f4, "💻", t("number_systems"),    "BIN · OCT · DEC · HEX"),
    ]
    for col, icon, title, desc in feature_data:
        with col:
            st.markdown(f"""
            <div class="feature-card">
                <span class="animated-icon">{icon}</span>
                <div class="feature-title">{title}</div>
                <div class="feature-text">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    # ── Tabs ──────────────────────────────────────────────────────────────
    tabs = st.tabs([
        f"🧮 {t('basic_calculator')}",
        f"🔬 {t('scientific_mode')}",
        "🧠 Solver",
        "📈 Graph",
        f"🔁 {t('smart_converter')}",
        f"💻 {t('number_systems')}",
        "📘 Formulas",
        f"📜 {t('history')}",
    ])

    # ═══════════════════ TAB 0: BASIC ════════════════════════════════════
    with tabs[0]:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="section-title">🧮 {t("basic_calculator")}</div>',
                    unsafe_allow_html=True)
        st.markdown('<div class="section-note">Fast arithmetic with memory support.</div>',
                    unsafe_allow_html=True)

        c1, c2, c3 = st.columns([2, 1, 2])
        with c1: a  = st.number_input("First Number",  value=0.0, key="basic_a")
        with c2: op = st.selectbox("Operation", ["+", "-", "×", "÷", "^", "%"], key="basic_op")
        with c3: b  = st.number_input("Second Number", value=0.0, key="basic_b")

        if st.button(f"⚡ {t('calculate')}", use_container_width=True, key="basic_calculate"):
            result = None
            if   op == "+": result = a + b
            elif op == "-": result = a - b
            elif op == "×": result = a * b
            elif op == "÷":
                if b == 0: st.error("❌ Division by zero is not allowed.")
                else: result = a / b
            elif op == "^": result = math.pow(a, b)
            elif op == "%":
                if b == 0: st.error("❌ Modulo by zero is not allowed.")
                else: result = a % b
            if result is not None:
                show_result(f"{a} {op} {b} = {result}")
                add_history(f"{a} {op} {b}", result)
                log_action("calc_basic", user_id=user_id, category="data",
                           details=f"{a} {op} {b} = {result}")

        st.markdown('<div class="sub-title">Memory Control</div>', unsafe_allow_html=True)
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            if st.button("M+", use_container_width=True, key="memory_plus"):
                st.session_state.memory += a
                _save_calc_data(user_id, st.session_state.history, st.session_state.memory)
                st.success("Added to memory.")
        with m2:
            if st.button("M−", use_container_width=True, key="memory_minus"):
                st.session_state.memory -= a
                _save_calc_data(user_id, st.session_state.history, st.session_state.memory)
                st.success("Subtracted from memory.")
        with m3:
            if st.button("MR", use_container_width=True, key="memory_read"):
                show_result(f"Memory: {st.session_state.memory}")
        with m4:
            if st.button("MC", use_container_width=True, key="memory_clear"):
                st.session_state.memory = 0.0
                _save_calc_data(user_id, st.session_state.history, st.session_state.memory)
                st.success("Memory cleared.")

        st.markdown(f'<div class="memory-val">💾 Memory: {st.session_state.memory}</div>',
                    unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ═══════════════════ TAB 1: SCIENTIFIC ═══════════════════════════════
    with tabs[1]:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="section-title">🔬 {t("scientific_mode")}</div>',
                    unsafe_allow_html=True)
        st.markdown('<div class="section-note">Degree-based trigonometry, logarithms, roots, and more.</div>',
                    unsafe_allow_html=True)

        operation = st.selectbox("Scientific Operation", [
            "Square Root", "Sin", "Cos", "Tan",
            "Log10", "Natural Log", "Factorial",
            "Radians", "Degrees", "Absolute Value",
        ], key="scientific_operation")
        value = st.number_input("Enter Value", value=0.0, key="scientific_value")

        if st.button(f"⚗️ {t('calculate')}", use_container_width=True, key="scientific_calculate"):
            result = None
            try:
                if   operation == "Square Root":
                    if value < 0: st.error("❌ Square root does not accept negative numbers.")
                    else: result = math.sqrt(value)
                elif operation == "Sin":            result = math.sin(math.radians(value))
                elif operation == "Cos":            result = math.cos(math.radians(value))
                elif operation == "Tan":            result = math.tan(math.radians(value))
                elif operation == "Log10":
                    if value <= 0: st.error("❌ Log10 requires a positive number.")
                    else: result = math.log10(value)
                elif operation == "Natural Log":
                    if value <= 0: st.error("❌ Natural log requires a positive number.")
                    else: result = math.log(value)
                elif operation == "Factorial":
                    if value < 0 or value != int(value):
                        st.error("❌ Factorial requires a non-negative whole number.")
                    else: result = math.factorial(int(value))
                elif operation == "Radians":        result = math.radians(value)
                elif operation == "Degrees":        result = math.degrees(value)
                elif operation == "Absolute Value": result = abs(value)
            except Exception as e:
                st.error(f"❌ {e}")
            if result is not None:
                show_result(f"{operation}({value}) = {result}")
                add_history(f"{operation}({value})", result)
                log_action("calc_scientific", user_id=user_id, category="data",
                           details=f"{operation}({value})")

        st.markdown('</div>', unsafe_allow_html=True)

    # ═══════════════════ TAB 2: SOLVER ═══════════════════════════════════
    with tabs[2]:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🧠 Smart Expression Solver</div>',
                    unsafe_allow_html=True)
        st.markdown('<div class="section-note">Examples: sin(30) + log(100) · sqrt(64) · 5^2 + 10 · pi * 2</div>',
                    unsafe_allow_html=True)

        expr = st.text_input("Enter Mathematical Expression",
                             value="sin(30) + log(100)",
                             key="expression_input")
        if st.button(f"🔍 Solve Expression", use_container_width=True, key="expression_solve"):
            try:
                result = safe_calculate_expression(expr)
                show_result(f"= {result}")
                add_history(expr, result)
                log_action("calc_expression", user_id=user_id, category="data",
                           details=expr[:50])
            except Exception:
                st.error("❌ Invalid expression. Try: sqrt(64), sin(30), log(100), 5^2 + 10")

        st.markdown('</div>', unsafe_allow_html=True)

    # ═══════════════════ TAB 3: GRAPH ════════════════════════════════════
    with tabs[3]:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📈 Graph Calculator</div>',
                    unsafe_allow_html=True)
        st.markdown('<div class="section-note">Draw functions: sin(x) · cos(x) · x**2 · x**3 + 2*x</div>',
                    unsafe_allow_html=True)

        function_text = st.text_input("Enter Function f(x)", value="sin(x)", key="graph_function")
        gc1, gc2 = st.columns(2)
        with gc1: start = st.number_input("Start X", value=-10.0, key="graph_start")
        with gc2: end   = st.number_input("End X",   value=10.0,  key="graph_end")

        if st.button("📊 Draw Graph", use_container_width=True, key="draw_graph"):
            try:
                import numpy as np
                import matplotlib.pyplot as plt
                if start >= end:
                    st.error("❌ Start X must be less than End X.")
                else:
                    x = np.linspace(start, end, 400)
                    ns = {
                        "x": x, "sin": np.sin, "cos": np.cos, "tan": np.tan,
                        "sqrt": np.sqrt, "log": np.log10, "ln": np.log,
                        "abs": np.abs, "pi": np.pi, "e": np.e,
                    }
                    y = eval(function_text.replace("^", "**"), {"__builtins__": {}}, ns)
                    fig, ax = plt.subplots(facecolor="#020617")
                    ax.set_facecolor("#060d1f")
                    ax.plot(x, y, color="#38bdf8", linewidth=2)
                    ax.set_title(f"f(x) = {function_text}", color="#7dd3fc", fontsize=13)
                    ax.set_xlabel("x", color="#475569")
                    ax.set_ylabel("f(x)", color="#475569")
                    ax.tick_params(colors="#475569")
                    ax.grid(True, color="#1e293b", linestyle="--", alpha=0.5)
                    for spine in ax.spines.values():
                        spine.set_edgecolor("#1e293b")
                    st.pyplot(fig)
                    add_history(f"Graph: {function_text}", "Generated")
                    log_action("calc_graph", user_id=user_id, category="data",
                               details=function_text[:50])
            except ModuleNotFoundError:
                st.error("❌ Install required: pip install numpy matplotlib")
            except Exception:
                st.error("❌ Invalid function. Try: sin(x), cos(x), x**2")

        st.markdown('</div>', unsafe_allow_html=True)

    # ═══════════════════ TAB 4: UNITS ════════════════════════════════════
    with tabs[4]:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="section-title">🔁 {t("smart_converter")}</div>',
                    unsafe_allow_html=True)
        st.markdown('<div class="section-note">Convert common units across 8 categories.</div>',
                    unsafe_allow_html=True)

        category = st.selectbox("Category", [
            "Length", "Mass", "Temperature", "Time",
            "Data Storage", "Speed", "Area", "Volume",
        ], key="unit_category")
        value = st.number_input("Input Value", value=0.0, key="unit_value")

        conversions = {
            "Length": {
                "Meter → Kilometer": value / 1000,    "Kilometer → Meter": value * 1000,
                "Meter → Centimeter": value * 100,    "Centimeter → Meter": value / 100,
                "Meter → Millimeter": value * 1000,   "Millimeter → Meter": value / 1000,
            },
            "Mass": {
                "Kilogram → Gram": value * 1000,      "Gram → Kilogram": value / 1000,
                "Kilogram → Pound": value * 2.20462,  "Pound → Kilogram": value / 2.20462,
            },
            "Temperature": {
                "Celsius → Fahrenheit": (value * 9 / 5) + 32,
                "Fahrenheit → Celsius": (value - 32) * 5 / 9,
                "Celsius → Kelvin": value + 273.15,
                "Kelvin → Celsius": value - 273.15,
            },
            "Time": {
                "Second → Minute": value / 60,  "Minute → Second": value * 60,
                "Hour → Minute": value * 60,    "Minute → Hour": value / 60,
                "Day → Hour": value * 24,        "Hour → Day": value / 24,
            },
            "Data Storage": {
                "Byte → KB": value / 1024, "KB → MB": value / 1024,
                "MB → GB": value / 1024,    "GB → MB": value * 1024,
                "GB → TB": value / 1024,    "TB → GB": value * 1024,
            },
            "Speed": {
                "m/s → km/h": value * 3.6,  "km/h → m/s": value / 3.6,
            },
            "Area": {
                "m² → km²": value / 1_000_000,  "km² → m²": value * 1_000_000,
                "m² → cm²": value * 10000,
            },
            "Volume": {
                "Liter → Milliliter": value * 1000,     "Milliliter → Liter": value / 1000,
                "Cubic Meter → Liter": value * 1000,    "Liter → Cubic Meter": value / 1000,
            },
        }

        selected = st.selectbox("Conversion", list(conversions[category].keys()),
                                key="unit_selected")

        if st.button("🔄 Convert", use_container_width=True, key="unit_convert"):
            result = conversions[category][selected]
            show_result(f"{selected}<br>{value} → {round(result, 6)}")
            add_history(f"{selected}: {value}", result)
            log_action("calc_unit", user_id=user_id, category="data",
                       details=f"{category}: {selected}")

        st.markdown('</div>', unsafe_allow_html=True)

    # ═══════════════════ TAB 5: NUMBER SYSTEMS ═══════════════════════════
    with tabs[5]:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="section-title">💻 {t("number_systems")}</div>',
                    unsafe_allow_html=True)
        st.markdown('<div class="section-note">Convert between Binary, Octal, Decimal, and Hexadecimal.</div>',
                    unsafe_allow_html=True)

        st.markdown('<div class="sub-title">Specific Conversion</div>', unsafe_allow_html=True)
        conversion_mode = st.selectbox("Choose Conversion", [
            "Binary to Decimal", "Binary to Octal", "Binary to Hexadecimal",
            "Decimal to Binary", "Decimal to Octal", "Decimal to Hexadecimal",
            "Octal to Binary",   "Octal to Decimal", "Octal to Hexadecimal",
            "Hexadecimal to Binary", "Hexadecimal to Decimal", "Hexadecimal to Octal",
        ], key="number_conversion_mode")

        number_input_val = st.text_input("Enter Number", value="1010", key="number_input")

        if st.button("🔢 Convert Number", use_container_width=True, key="number_convert"):
            try:
                clean = number_input_val.strip().upper()
                source, target = conversion_mode.split(" to ")
                dec = convert_to_decimal(clean, source)
                result = decimal_to_systems(dec)[target]
                show_result(f"{conversion_mode}<br>{clean} → {result}")
                add_history(f"{conversion_mode} ({clean})", result)
                log_action("calc_numsys", user_id=user_id, category="data",
                           details=conversion_mode)
            except Exception:
                st.error("❌ Invalid input for selected number system.")

        st.markdown('<div class="sub-title">Convert to All Systems</div>', unsafe_allow_html=True)
        input_type      = st.selectbox("Input Type",
                                       ["Binary", "Octal", "Decimal", "Hexadecimal"],
                                       key="number_input_type")
        universal_input = st.text_input("Enter Value", value="10", key="universal_number_input")

        if st.button("🌐 Convert To All Systems", use_container_width=True, key="number_convert_all"):
            try:
                clean = universal_input.strip().upper()
                dec   = convert_to_decimal(clean, input_type)
                sys_  = decimal_to_systems(dec)
                r1, r2, r3, r4 = st.columns(4)
                for col, label, key_name in [
                    (r1, "BIN", "Binary"), (r2, "OCT", "Octal"),
                    (r3, "DEC", "Decimal"), (r4, "HEX", "Hexadecimal"),
                ]:
                    with col:
                        show_result(f"{label}<br>{sys_[key_name]}")
                add_history(
                    f"Full from {input_type}: {clean}",
                    f"BIN={sys_['Binary']}, OCT={sys_['Octal']}, "
                    f"DEC={sys_['Decimal']}, HEX={sys_['Hexadecimal']}"
                )
            except Exception:
                st.error("❌ Invalid input for selected number system.")

        st.markdown('</div>', unsafe_allow_html=True)

    # ═══════════════════ TAB 6: FORMULAS ═════════════════════════════════
    with tabs[6]:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📘 Formula Helper</div>',
                    unsafe_allow_html=True)
        st.markdown('<div class="section-note">Quick formulas for common real-world calculations.</div>',
                    unsafe_allow_html=True)

        formula = st.selectbox("Choose Formula", [
            "Speed = Distance / Time", "Area of Circle",
            "Ohm Law", "BMI", "Percentage",
        ], key="formula_select")

        if formula == "Speed = Distance / Time":
            fc1, fc2 = st.columns(2)
            with fc1: distance = st.number_input("Distance", value=0.0, key="formula_distance")
            with fc2: time_val = st.number_input("Time",     value=1.0, key="formula_time")
            if st.button("⚡ Calculate Speed", use_container_width=True, key="formula_speed"):
                if time_val == 0: st.error("❌ Time cannot be zero.")
                else:
                    r = distance / time_val
                    show_result(f"Speed = {r}")
                    add_history("Speed = Distance / Time", r)

        elif formula == "Area of Circle":
            radius = st.number_input("Radius", value=0.0, key="formula_radius")
            if st.button("⚡ Calculate Area", use_container_width=True, key="formula_area"):
                r = math.pi * radius ** 2
                show_result(f"Area = {round(r, 6)}")
                add_history("Area of Circle", r)

        elif formula == "Ohm Law":
            fc1, fc2 = st.columns(2)
            with fc1: voltage    = st.number_input("Voltage (V)",    value=0.0, key="formula_voltage")
            with fc2: resistance = st.number_input("Resistance (Ω)", value=1.0, key="formula_resistance")
            if st.button("⚡ Calculate Current", use_container_width=True, key="formula_ohm"):
                if resistance == 0: st.error("❌ Resistance cannot be zero.")
                else:
                    r = voltage / resistance
                    show_result(f"I = {r} A")
                    add_history("Ohm Law I = V / R", r)

        elif formula == "BMI":
            fc1, fc2 = st.columns(2)
            with fc1: weight = st.number_input("Weight (kg)", value=70.0, key="formula_weight")
            with fc2: height = st.number_input("Height (m)",  value=1.70, key="formula_height")
            if st.button("⚡ Calculate BMI", use_container_width=True, key="formula_bmi"):
                if height == 0: st.error("❌ Height cannot be zero.")
                else:
                    r = weight / (height ** 2)
                    bmi_label = (
                        "Underweight" if r < 18.5 else
                        "Normal"      if r < 25   else
                        "Overweight"  if r < 30   else "Obese"
                    )
                    show_result(f"BMI = {round(r, 2)} — {bmi_label}")
                    add_history("BMI", round(r, 2))

        elif formula == "Percentage":
            fc1, fc2 = st.columns(2)
            with fc1: part  = st.number_input("Part",  value=0.0, key="formula_part")
            with fc2: whole = st.number_input("Whole", value=1.0, key="formula_whole")
            if st.button("⚡ Calculate Percentage", use_container_width=True, key="formula_percentage"):
                if whole == 0: st.error("❌ Whole cannot be zero.")
                else:
                    r = (part / whole) * 100
                    show_result(f"{part} / {whole} = {round(r, 4)}%")
                    add_history("Percentage", r)

        st.markdown('</div>', unsafe_allow_html=True)

    # ═══════════════════ TAB 7: HISTORY ══════════════════════════════════
    with tabs[7]:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="section-title">📜 {t("history")}</div>',
                    unsafe_allow_html=True)
        st.markdown('<div class="section-note">Review all operations and export as CSV.</div>',
                    unsafe_allow_html=True)

        if not st.session_state.history:
            st.markdown("""
            <div style="text-align:center;padding:40px;color:#334155;
                        font-family:'Orbitron',monospace;font-size:14px;letter-spacing:2px;">
                NO CALCULATIONS YET
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(
                f'<div class="memory-val">📊 Total operations: {len(st.session_state.history)}</div>',
                unsafe_allow_html=True
            )
            st.write("")
            st.dataframe(st.session_state.history, use_container_width=True)

            hc1, hc2 = st.columns(2)
            with hc1:
                st.download_button(
                    label="📥 Download CSV",
                    data=create_csv_from_history(),
                    file_name="omnix_calculator_history.csv",
                    mime="text/csv",
                    use_container_width=True,
                    key="download_history",
                )
            with hc2:
                if st.button("🗑 Clear History", use_container_width=True, key="clear_history"):
                    st.session_state.history = []
                    _save_calc_data(user_id, st.session_state.history, st.session_state.memory)
                    log_action("calc_history_cleared", user_id=user_id, category="data")
                    st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)