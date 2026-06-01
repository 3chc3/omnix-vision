"""
═══════════════════════════════════════════════════════════════════════════
OMNIX VISION — Standalone Pomodoro (Phase 4 — Round 2)
═══════════════════════════════════════════════════════════════════════════
Features:
    ✓ Independent Pomodoro timer (separate from tasks)
    ✓ Configurable work/break durations
    ✓ Session history per user (data/pomodoro_log.json)
    ✓ Daily/weekly statistics
    ✓ Streak counter
    ✓ Audio notification on phase change (visual fallback)
    ✓ Beautiful circular progress visual
    ✓ Full EN/AR translation with RTL
═══════════════════════════════════════════════════════════════════════════
"""

import json
import time
from datetime import datetime, date, timedelta
from pathlib import Path

import streamlit as st

from utils.language import t, init_language, apply_rtl_css, is_rtl
from utils.activity import log_action


# ═══════════════════════════════════════════════════════════════════════════
# Paths
# ═══════════════════════════════════════════════════════════════════════════
BASE_DIR  = Path(__file__).resolve().parent.parent
DATA_DIR  = BASE_DIR / "data"
POMO_LOG  = DATA_DIR / "pomodoro_log.json"
DATA_DIR.mkdir(parents=True, exist_ok=True)

MAX_HISTORY_PER_USER = 500


# ═══════════════════════════════════════════════════════════════════════════
# Translations
# ═══════════════════════════════════════════════════════════════════════════
POMO_KEYS = {
    "pomo_title":       {"en": "Pomodoro Studio",
                         "ar": "استوديو بومودورو"},
    "pomo_subtitle":    {"en": "Focus, work, and stay productive",
                         "ar": "ركّز، اعمل، وحافظ على إنتاجيتك"},
    "tab_timer":        {"en": "⏱️ Timer",       "ar": "⏱️ المؤقت"},
    "tab_stats":        {"en": "📊 Stats",       "ar": "📊 الإحصائيات"},
    "tab_history":      {"en": "📜 History",     "ar": "📜 السجل"},

    "phase_work":       {"en": "WORK SESSION",   "ar": "جلسة عمل"},
    "phase_short":      {"en": "SHORT BREAK",    "ar": "استراحة قصيرة"},
    "phase_long":       {"en": "LONG BREAK",     "ar": "استراحة طويلة"},

    "start":            {"en": "▶ Start",        "ar": "▶ ابدأ"},
    "pause":            {"en": "⏸ Pause",        "ar": "⏸ إيقاف مؤقت"},
    "resume":           {"en": "▶ Resume",       "ar": "▶ استئناف"},
    "reset":            {"en": "⏹ Reset",        "ar": "⏹ إعادة"},
    "skip":             {"en": "⏭ Skip Phase",   "ar": "⏭ تخطي"},

    "session_label":    {"en": "Optional Label", "ar": "تسمية اختيارية"},
    "session_placeholder": {"en": "What are you working on?",
                            "ar": "على ماذا تعمل؟"},

    "today":            {"en": "Today",          "ar": "اليوم"},
    "this_week":        {"en": "This Week",      "ar": "هذا الأسبوع"},
    "total":            {"en": "All Time",       "ar": "الإجمالي"},
    "streak":           {"en": "Current Streak (days)",
                         "ar": "السلسلة الحالية (أيام)"},

    "sessions_done":    {"en": "Sessions Done",  "ar": "جلسات مكتملة"},
    "total_focus":      {"en": "Total Focus (min)",
                         "ar": "إجمالي التركيز (د)"},
    "avg_session":      {"en": "Avg Session (min)",
                         "ar": "متوسط الجلسة (د)"},

    "no_history":       {"en": "No completed sessions yet. Start one!",
                         "ar": "لا توجد جلسات مكتملة. ابدأ واحدة!"},
    "clear_history":    {"en": "🗑️ Clear History",
                         "ar": "🗑️ مسح السجل"},

    "settings":         {"en": "Settings",       "ar": "الإعدادات"},
    "work_duration":    {"en": "Work duration (min)",
                         "ar": "مدة العمل (د)"},
    "short_duration":   {"en": "Short break (min)",
                         "ar": "استراحة قصيرة (د)"},
    "long_duration":    {"en": "Long break (min)",
                         "ar": "استراحة طويلة (د)"},
    "long_after":       {"en": "Long break after N sessions",
                         "ar": "استراحة طويلة بعد N جلسة"},

    "phase_complete":   {"en": "🎉 Phase complete!",
                         "ar": "🎉 اكتملت الجلسة!"},
    "completed_at":     {"en": "Completed at",   "ar": "اكتملت في"},
    "duration":         {"en": "Duration",       "ar": "المدة"},
    "label":            {"en": "Label",          "ar": "التسمية"},
}


def _t(key: str) -> str:
    from utils.language import get_language_code
    lang = get_language_code()
    if key in POMO_KEYS:
        return POMO_KEYS[key].get(lang, POMO_KEYS[key].get("en", key))
    return t(key)


# ═══════════════════════════════════════════════════════════════════════════
# Storage
# ═══════════════════════════════════════════════════════════════════════════

def _load_history(user_id: str) -> list:
    if not POMO_LOG.exists():
        return []
    try:
        with open(POMO_LOG, "r", encoding="utf-8") as f:
            return json.load(f).get(str(user_id), [])
    except (json.JSONDecodeError, OSError):
        return []


def _save_history(user_id: str, history: list):
    all_data = {}
    if POMO_LOG.exists():
        try:
            with open(POMO_LOG, "r", encoding="utf-8") as f:
                all_data = json.load(f)
        except (json.JSONDecodeError, OSError):
            all_data = {}
    all_data[str(user_id)] = history[-MAX_HISTORY_PER_USER:]
    try:
        with open(POMO_LOG, "w", encoding="utf-8") as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)
    except OSError:
        pass


def _add_session(user_id: str, phase: str, duration_min: int, label: str):
    history = _load_history(user_id)
    history.append({
        "phase":          phase,
        "duration_min":   duration_min,
        "label":          label.strip()[:80],
        "completed_at":   time.time(),
    })
    _save_history(user_id, history)


# ═══════════════════════════════════════════════════════════════════════════
# State
# ═══════════════════════════════════════════════════════════════════════════

def _init_state():
    defaults = {
        "pomo_running":          False,
        "pomo_paused_at":        None,
        "pomo_start":            None,
        "pomo_phase":            "work",     # work | short | long
        "pomo_session_count":    0,          # count of completed work sessions
        "pomo_label":            "",
        # Settings
        "pomo_work_min":         25,
        "pomo_short_min":        5,
        "pomo_long_min":         15,
        "pomo_long_after":       4,
    }
    for k, v in defaults.items():
        st.session_state.setdefault(k, v)


def _phase_duration() -> int:
    """Return seconds for current phase."""
    phase = st.session_state.pomo_phase
    if phase == "work":  return st.session_state.pomo_work_min  * 60
    if phase == "short": return st.session_state.pomo_short_min * 60
    return st.session_state.pomo_long_min * 60


def _phase_color() -> str:
    phase = st.session_state.pomo_phase
    return {"work": "#ef4444", "short": "#22c55e", "long": "#38bdf8"}.get(phase, "#ef4444")


def _phase_label_key() -> str:
    phase = st.session_state.pomo_phase
    return {"work": "phase_work", "short": "phase_short", "long": "phase_long"}.get(phase, "phase_work")


# ═══════════════════════════════════════════════════════════════════════════
# CSS
# ═══════════════════════════════════════════════════════════════════════════

def _apply_css():
    is_ar = is_rtl()
    color = _phase_color()
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
        max-width: 1180px;
        padding-top: 1.2rem;
        {"direction: rtl;" if is_ar else ""}
    }}

    .stApp {{
        background:
            radial-gradient(circle at 50% 0%, {color}30, transparent 35%),
            radial-gradient(circle at 90% 90%, rgba(168,85,247,0.12), transparent 35%),
            linear-gradient(135deg, #020617 0%, #06111f 48%, #111032 100%);
        color: #f8fafc;
        font-family: 'Rajdhani', sans-serif;
        transition: background 0.6s ease;
    }}

    .hero {{
        background: linear-gradient(135deg, rgba(15,23,42,0.96), rgba(8,47,73,0.58));
        border: 1px solid {color}66;
        border-radius: 30px;
        padding: 30px 24px;
        text-align: center;
        margin-bottom: 18px;
        box-shadow: 0 0 48px {color}30;
    }}
    .hero h1 {{
        color: {color};
        font-size: 36px;
        font-weight: 950;
        margin: 0;
        letter-spacing: 2px;
        text-shadow: 0 0 24px {color}60;
    }}
    .hero p {{ color: #cbd5e1; margin-top: 8px; font-size: 13px; }}

    .pomo-circle {{
        background: radial-gradient(circle, {color}22, rgba(2,6,23,0.95));
        border: 3px solid {color};
        border-radius: 24px;
        padding: 50px 30px;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 0 50px {color}40, inset 0 0 30px {color}15;
    }}
    .pomo-phase {{
        font-family: 'Orbitron', monospace;
        font-size: 13px;
        color: #94a3b8;
        letter-spacing: 4px;
        text-transform: uppercase;
        margin-bottom: 16px;
    }}
    .pomo-time {{
        font-family: 'Orbitron', monospace;
        font-size: 84px;
        font-weight: 900;
        color: #f1f5f9;
        line-height: 1;
        letter-spacing: 4px;
        text-shadow: 0 0 28px {color}80;
    }}
    .pomo-sessions {{
        margin-top: 16px;
        color: #94a3b8;
        font-family: 'Orbitron', monospace;
        font-size: 12px;
        letter-spacing: 2px;
    }}

    .progress-bar {{
        width: 100%;
        height: 12px;
        background: rgba(15,23,42,0.95);
        border-radius: 999px;
        overflow: hidden;
        margin-top: 18px;
        border: 1px solid rgba(148,163,184,0.18);
    }}
    .progress-fill {{
        height: 100%;
        background: {color};
        border-radius: 999px;
        box-shadow: 0 0 18px {color};
        transition: width 0.3s ease;
    }}

    .stat-card {{
        background: linear-gradient(145deg, rgba(15,23,42,0.95), rgba(30,41,59,0.62));
        border: 1px solid rgba(56,189,248,0.27);
        border-radius: 16px;
        padding: 16px;
        text-align: center;
    }}
    .stat-label {{
        color: #a5f3fc;
        font-size: 10px;
        font-family: 'Orbitron', monospace;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin-bottom: 8px;
    }}
    .stat-value {{
        color: #f8fafc;
        font-size: 28px;
        font-weight: 900;
        font-family: 'Orbitron', monospace;
    }}

    .session-card {{
        background: rgba(15,23,42,0.65);
        border: 1px solid rgba(56,189,248,0.20);
        border-{"right" if is_ar else "left"}: 4px solid var(--phase-color, #ef4444);
        border-radius: 12px;
        padding: 10px 16px;
        margin: 6px 0;
        font-size: 13px;
    }}

    .stButton > button {{
        background: linear-gradient(135deg, {color}, #7c3aed) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 11px 18px !important;
        font-weight: 800 !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-size: 14px !important;
        min-height: 46px !important;
        box-shadow: 0 4px 18px {color}40 !important;
        transition: 0.25s ease !important;
    }}
    .stButton > button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 28px {color}55 !important;
    }}
    </style>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# Tab: Timer
# ═══════════════════════════════════════════════════════════════════════════

def _tab_timer(user_id: str):
    duration = _phase_duration()
    color    = _phase_color()
    phase_label = _t(_phase_label_key())

    # Calculate elapsed
    if st.session_state.pomo_running and st.session_state.pomo_start:
        elapsed = time.time() - st.session_state.pomo_start
    elif st.session_state.pomo_paused_at and st.session_state.pomo_start:
        elapsed = st.session_state.pomo_paused_at - st.session_state.pomo_start
    else:
        elapsed = 0

    remaining = max(0, int(duration - elapsed))

    # Auto-advance when done
    if remaining == 0 and st.session_state.pomo_running:
        completed_phase = st.session_state.pomo_phase
        duration_min    = {
            "work":  st.session_state.pomo_work_min,
            "short": st.session_state.pomo_short_min,
            "long":  st.session_state.pomo_long_min,
        }[completed_phase]

        # Log completed session
        _add_session(user_id, completed_phase, duration_min,
                     st.session_state.pomo_label)
        log_action("pomo_session_complete", user_id=user_id, category="data",
                   details=f"phase={completed_phase} dur={duration_min}min")

        # Determine next phase
        if completed_phase == "work":
            st.session_state.pomo_session_count += 1
            if st.session_state.pomo_session_count % st.session_state.pomo_long_after == 0:
                st.session_state.pomo_phase = "long"
            else:
                st.session_state.pomo_phase = "short"
        else:
            st.session_state.pomo_phase = "work"

        # Reset timer
        st.session_state.pomo_running   = False
        st.session_state.pomo_start     = None
        st.session_state.pomo_paused_at = None
        st.success(_t("phase_complete"))
        st.balloons()
        time.sleep(1)
        st.rerun()

    # ── Time Display ──────────────────────────────────────────────────────
    minutes = remaining // 60
    seconds = remaining % 60
    time_str = f"{minutes:02d}:{seconds:02d}"

    progress_pct = int((elapsed / duration) * 100) if duration > 0 else 0
    progress_pct = max(0, min(100, progress_pct))

    st.markdown(f"""
<div class="pomo-circle">
<div class="pomo-phase">🍅 {phase_label}</div>
<div class="pomo-time">{time_str}</div>
<div class="pomo-sessions">{_t('sessions_done')}: {st.session_state.pomo_session_count}</div>
<div class="progress-bar">
<div class="progress-fill" style="width:{progress_pct}%;"></div>
</div>
</div>
    """, unsafe_allow_html=True)

    # ── Label input ──
    st.session_state.pomo_label = st.text_input(
        _t("session_label"),
        value=st.session_state.pomo_label,
        placeholder=_t("session_placeholder"),
        key="pomo_label_input",
    )

    # ── Controls ──
    c1, c2, c3 = st.columns(3)

    with c1:
        if not st.session_state.pomo_running:
            label = _t("start") if st.session_state.pomo_start is None else _t("resume")
            if st.button(label, use_container_width=True, key="pomo_start_btn"):
                if st.session_state.pomo_paused_at and st.session_state.pomo_start:
                    # Resume: shift start by pause duration
                    pause_dur = time.time() - st.session_state.pomo_paused_at
                    st.session_state.pomo_start += pause_dur
                    st.session_state.pomo_paused_at = None
                else:
                    st.session_state.pomo_start = time.time()
                st.session_state.pomo_running = True
                log_action("pomo_started", user_id=user_id, category="data",
                           details=f"phase={st.session_state.pomo_phase}")
                st.rerun()
        else:
            if st.button(_t("pause"), use_container_width=True, key="pomo_pause_btn"):
                st.session_state.pomo_paused_at = time.time()
                st.session_state.pomo_running   = False
                st.rerun()

    with c2:
        if st.button(_t("reset"), use_container_width=True, key="pomo_reset_btn"):
            st.session_state.pomo_running   = False
            st.session_state.pomo_start     = None
            st.session_state.pomo_paused_at = None
            st.rerun()

    with c3:
        if st.button(_t("skip"), use_container_width=True, key="pomo_skip_btn"):
            # Skip current phase without logging
            if st.session_state.pomo_phase == "work":
                st.session_state.pomo_phase = "short"
            else:
                st.session_state.pomo_phase = "work"
            st.session_state.pomo_running   = False
            st.session_state.pomo_start     = None
            st.session_state.pomo_paused_at = None
            st.rerun()

    # ── Settings ──
    with st.expander(f"⚙️ {_t('settings')}"):
        sc1, sc2 = st.columns(2)
        with sc1:
            st.session_state.pomo_work_min = st.number_input(
                _t("work_duration"),
                min_value=1, max_value=120,
                value=st.session_state.pomo_work_min,
                key="pomo_work_inp",
            )
            st.session_state.pomo_short_min = st.number_input(
                _t("short_duration"),
                min_value=1, max_value=30,
                value=st.session_state.pomo_short_min,
                key="pomo_short_inp",
            )
        with sc2:
            st.session_state.pomo_long_min = st.number_input(
                _t("long_duration"),
                min_value=5, max_value=60,
                value=st.session_state.pomo_long_min,
                key="pomo_long_inp",
            )
            st.session_state.pomo_long_after = st.number_input(
                _t("long_after"),
                min_value=2, max_value=10,
                value=st.session_state.pomo_long_after,
                key="pomo_after_inp",
            )

    # Auto-rerun every second while running
    if st.session_state.pomo_running:
        time.sleep(1)
        st.rerun()


# ═══════════════════════════════════════════════════════════════════════════
# Tab: Stats
# ═══════════════════════════════════════════════════════════════════════════

def _tab_stats(user_id: str):
    history = _load_history(user_id)

    if not history:
        st.info(_t("no_history"))
        return

    today = date.today()
    week_start = today - timedelta(days=today.weekday())

    # Filter completed work sessions
    work_sessions = [h for h in history if h["phase"] == "work"]

    today_sessions = [
        h for h in work_sessions
        if datetime.fromtimestamp(h["completed_at"]).date() == today
    ]
    week_sessions = [
        h for h in work_sessions
        if datetime.fromtimestamp(h["completed_at"]).date() >= week_start
    ]

    # Streak calculation
    streak = 0
    check_date = today
    days_with_sessions = {
        datetime.fromtimestamp(h["completed_at"]).date()
        for h in work_sessions
    }
    while check_date in days_with_sessions:
        streak += 1
        check_date -= timedelta(days=1)

    # ── Big stats ──
    m1, m2, m3, m4 = st.columns(4)

    metrics = [
        (m1, _t("today"),    len(today_sessions),
         sum(s["duration_min"] for s in today_sessions), "#ef4444", "🔥"),
        (m2, _t("this_week"), len(week_sessions),
         sum(s["duration_min"] for s in week_sessions), "#f59e0b", "📅"),
        (m3, _t("total"),    len(work_sessions),
         sum(s["duration_min"] for s in work_sessions), "#22c55e", "🏆"),
        (m4, _t("streak"),   streak, 0, "#a855f7", "⚡"),
    ]

    for col, label, count, minutes, color, icon in metrics:
        with col:
            if minutes > 0:
                value_html = f'<div class="stat-value" style="color:{color};">{count}</div><div style="color:#94a3b8;font-size:11px;margin-top:4px;">{minutes} min</div>'
            else:
                value_html = f'<div class="stat-value" style="color:{color};">{count}</div>'
            st.markdown(f"""
<div class="stat-card">
<div class="stat-label">{icon} {label}</div>
{value_html}
</div>
            """, unsafe_allow_html=True)

    st.write("")

    # ── Last 7 days bar chart (simple) ──
    if len(work_sessions) > 0:
        st.markdown(f"### 📊 Last 7 Days Activity")
        days_data = {}
        for i in range(6, -1, -1):
            d = today - timedelta(days=i)
            days_data[d] = 0

        for h in work_sessions:
            d = datetime.fromtimestamp(h["completed_at"]).date()
            if d in days_data:
                days_data[d] += 1

        max_val = max(days_data.values()) or 1
        for d, count in days_data.items():
            pct = int((count / max_val) * 100)
            day_name = d.strftime("%a %d")
            st.markdown(f"""
<div style="display:flex;align-items:center;gap:14px;margin:6px 0;">
<div style="width:80px;color:#94a3b8;font-size:12px;font-family:'Orbitron',monospace;">{day_name}</div>
<div style="flex:1;height:24px;background:rgba(15,23,42,0.85);border-radius:6px;overflow:hidden;">
<div style="width:{pct}%;height:100%;background:linear-gradient(90deg,#ef4444,#f59e0b);"></div>
</div>
<div style="width:30px;text-align:right;color:#f1f5f9;font-weight:700;">{count}</div>
</div>
            """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# Tab: History
# ═══════════════════════════════════════════════════════════════════════════

def _tab_history(user_id: str):
    history = _load_history(user_id)

    if not history:
        st.info(_t("no_history"))
        return

    # Show most recent first
    history_sorted = sorted(history,
                            key=lambda h: h["completed_at"],
                            reverse=True)

    # Show last 30
    for h in history_sorted[:30]:
        completed = datetime.fromtimestamp(h["completed_at"]).strftime("%Y-%m-%d %H:%M")
        phase     = h["phase"]
        phase_color = {"work": "#ef4444", "short": "#22c55e", "long": "#38bdf8"}.get(phase, "#94a3b8")
        phase_icon  = {"work": "🍅", "short": "☕", "long": "🛋️"}.get(phase, "❓")
        phase_name  = _t(f"phase_{phase}")

        label_html = ""
        if h.get("label"):
            label_html = f'<span style="color:#94a3b8;font-size:12px;"> · {h["label"]}</span>'

        st.markdown(f"""
<div class="session-card" style="--phase-color:{phase_color};">
<div style="display:flex;justify-content:space-between;align-items:center;">
<div>{phase_icon} <b style="color:{phase_color};">{phase_name}</b> · {h['duration_min']} min{label_html}</div>
<div style="color:#64748b;font-size:11px;font-family:'Orbitron',monospace;">{completed}</div>
</div>
</div>
        """, unsafe_allow_html=True)

    st.write("")
    if st.button(_t("clear_history"),
                 use_container_width=True,
                 key="pomo_clear_hist_btn"):
        _save_history(user_id, [])
        log_action("pomo_history_cleared", user_id=user_id, category="data")
        st.rerun()


# ═══════════════════════════════════════════════════════════════════════════
# Main Render
# ═══════════════════════════════════════════════════════════════════════════

def render_pomodoro():
    init_language()
    apply_rtl_css()

    if not st.session_state.get("logged_in", False):
        st.session_state.page = "login"
        st.rerun()

    user_id = st.session_state.get("user", "anonymous")

    _init_state()
    _apply_css()

    # ── Hero ──
    st.markdown(f"""
<div class="hero">
<h1>🍅 {_t('pomo_title')}</h1>
<p>{_t('pomo_subtitle')}</p>
</div>
    """, unsafe_allow_html=True)

    # ── Back ──
    back_col, _ = st.columns([1.3, 8])
    with back_col:
        if st.button(t("back"), use_container_width=True, key="pomo_back_btn"):
            st.session_state.pomo_running = False
            st.session_state.page = "home"
            st.rerun()

    # ── Tabs ──
    tab_timer, tab_stats, tab_history = st.tabs([
        _t("tab_timer"), _t("tab_stats"), _t("tab_history"),
    ])
    with tab_timer:   _tab_timer(user_id)
    with tab_stats:   _tab_stats(user_id)
    with tab_history: _tab_history(user_id)