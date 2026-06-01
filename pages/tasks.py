"""
═══════════════════════════════════════════════════════════════════════════
OMNIX VISION — Tasks Manager (Phase 3)
═══════════════════════════════════════════════════════════════════════════
Complete rewrite with:
    ✓ Priorities (Low / Medium / High / Urgent)
    ✓ Due dates with overdue/due-today warnings
    ✓ Tags / Categories (6 colored tags)
    ✓ Completion checkboxes
    ✓ Search bar
    ✓ Filters (status, priority, tag)
    ✓ Pomodoro timer (work / short break / long break)
    ✓ Stopwatch
    ✓ File uploads with type detection
    ✓ JSON persistence (data/tasks.json)
    ✓ Full EN/AR translation + RTL
    ✓ Activity log integration
═══════════════════════════════════════════════════════════════════════════
"""

import os
import json
import time
import uuid
from pathlib import Path
from datetime import datetime, date, timedelta

import streamlit as st

from utils.language import t, init_language, apply_rtl_css, is_rtl
from utils.activity import log_action


# ═══════════════════════════════════════════════════════════════════════════
# Paths
# ═══════════════════════════════════════════════════════════════════════════
BASE_DIR    = Path(__file__).resolve().parent.parent
DATA_DIR    = BASE_DIR / "data"
TASKS_FILE  = DATA_DIR / "tasks.json"
UPLOAD_DIR  = BASE_DIR / "assets" / "uploads"

DATA_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# ═══════════════════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════════════════

PRIORITY_CONFIG = {
    "low":    {"color": "#22c55e", "icon": "🟢", "order": 1},
    "medium": {"color": "#38bdf8", "icon": "🔵", "order": 2},
    "high":   {"color": "#f59e0b", "icon": "🟡", "order": 3},
    "urgent": {"color": "#ef4444", "icon": "🔴", "order": 4},
}

TAG_CONFIG = {
    "work":     {"color": "#38bdf8", "icon": "💼"},
    "personal": {"color": "#a855f7", "icon": "👤"},
    "study":    {"color": "#22c55e", "icon": "📚"},
    "health":   {"color": "#ef4444", "icon": "❤️"},
    "shopping": {"color": "#f59e0b", "icon": "🛒"},
    "other":    {"color": "#94a3b8", "icon": "📌"},
}


# ═══════════════════════════════════════════════════════════════════════════
# Storage Helpers
# ═══════════════════════════════════════════════════════════════════════════

def _load_tasks() -> list:
    """Load tasks list from JSON file."""
    if not TASKS_FILE.exists():
        return []
    try:
        with open(TASKS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def _save_tasks(tasks: list):
    """Persist tasks list to JSON file."""
    try:
        with open(TASKS_FILE, "w", encoding="utf-8") as f:
            json.dump(tasks, f, ensure_ascii=False, indent=2)
    except OSError as e:
        st.error(f"❌ Failed to save: {e}")


def _new_task(text: str,
              priority: str = "medium",
              due_date: str = "",
              tag: str = "other") -> dict:
    """Create a fresh task dict."""
    return {
        "id":           str(uuid.uuid4())[:8],
        "text":         text.strip(),
        "priority":     priority,
        "due_date":     due_date,   # ISO format: YYYY-MM-DD, or ""
        "tag":          tag,
        "completed":    False,
        "created_at":   time.time(),
        "completed_at": None,
    }


# ═══════════════════════════════════════════════════════════════════════════
# Date Helpers
# ═══════════════════════════════════════════════════════════════════════════

def _due_status(due_str: str) -> tuple:
    """
    Return (label_key, color, days_diff) for a due date.
    label_key is one of: overdue, due_today, due_soon, '' (no/far due)
    """
    if not due_str:
        return ("", "#94a3b8", None)
    try:
        due = datetime.strptime(due_str, "%Y-%m-%d").date()
    except ValueError:
        return ("", "#94a3b8", None)

    today = date.today()
    diff = (due - today).days

    if diff < 0:
        return ("overdue", "#ef4444", diff)
    if diff == 0:
        return ("due_today", "#f59e0b", 0)
    if diff <= 3:
        return ("due_soon", "#facc15", diff)
    return ("", "#94a3b8", diff)


def _format_due(due_str: str) -> str:
    """Format due date as 'Today', 'Tomorrow', 'Mon, Jan 5', etc."""
    if not due_str:
        return t("no_due_date")
    try:
        due = datetime.strptime(due_str, "%Y-%m-%d").date()
    except ValueError:
        return due_str

    today = date.today()
    diff = (due - today).days

    if diff == 0:   return t("today")
    if diff == 1:   return t("tomorrow")
    if diff == -1:  return t("yesterday")

    return due.strftime("%a, %b %d")


# ═══════════════════════════════════════════════════════════════════════════
# File Helpers
# ═══════════════════════════════════════════════════════════════════════════

def _get_file_type(filename: str) -> str:
    ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
    if ext in ("jpg", "jpeg", "png", "webp", "gif"): return "Image"
    if ext in ("mp3", "wav", "ogg"):                  return "Audio"
    if ext in ("mp4", "mov", "webm", "avi"):          return "Video"
    if ext in ("pdf", "txt", "docx", "doc"):          return "Document"
    return "Other"


def _file_icon(file_type: str) -> str:
    return {
        "Image":    "🖼️",
        "Audio":    "🎵",
        "Video":    "🎬",
        "Document": "📄",
        "Other":    "📦",
    }.get(file_type, "📦")


def _save_uploaded_file(uploaded_file) -> str:
    """Save uploaded file and return its path."""
    file_path = UPLOAD_DIR / uploaded_file.name
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return str(file_path)


# ═══════════════════════════════════════════════════════════════════════════
# Session Init
# ═══════════════════════════════════════════════════════════════════════════

def _init_state():
    """Initialize all session state defaults for this page."""
    # Tasks
    if "tasks" not in st.session_state:
        st.session_state.tasks = _load_tasks()

    # Files
    st.session_state.setdefault("uploaded_files_info", [])

    # Filters
    st.session_state.setdefault("filter_status",   "all")
    st.session_state.setdefault("filter_priority", "all")
    st.session_state.setdefault("filter_tag",      "all")
    st.session_state.setdefault("search_query",    "")

    # Pomodoro
    st.session_state.setdefault("pomo_running",   False)
    st.session_state.setdefault("pomo_start",     None)
    st.session_state.setdefault("pomo_paused_at", None)
    st.session_state.setdefault("pomo_phase",     "work")  # work | break | long_break
    st.session_state.setdefault("pomo_sessions",  0)
    st.session_state.setdefault("pomo_work_min",  25)
    st.session_state.setdefault("pomo_break_min", 5)
    st.session_state.setdefault("pomo_long_min",  15)

    # Stopwatch
    st.session_state.setdefault("sw_running",   False)
    st.session_state.setdefault("sw_start",     None)
    st.session_state.setdefault("sw_elapsed",   0.0)


# ═══════════════════════════════════════════════════════════════════════════
# CSS
# ═══════════════════════════════════════════════════════════════════════════

def _inject_css():
    is_ar = is_rtl()
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@400;500;600;700&display=swap');

    [data-testid="stSidebar"], [data-testid="collapsedControl"] {{ display: none; }}

    [data-testid="stAppDeployButton"],
    [data-testid="stToolbar"],
    header[data-testid="stHeader"] {{
        background: transparent !important;
        box-shadow: none !important;
    }}

    .block-container {{
        max-width: 1200px;
        padding-top: 1.2rem;
        padding-left: 1.2rem;
        padding-right: 1.2rem;
        {"direction: rtl;" if is_ar else ""}
    }}

    .stApp {{
        background:
            radial-gradient(circle at 10% 10%, rgba(56,189,248,0.16), transparent 28%),
            radial-gradient(circle at 90% 10%, rgba(168,85,247,0.18), transparent 32%),
            radial-gradient(circle at 50% 100%, rgba(34,197,94,0.08), transparent 30%),
            linear-gradient(135deg, #020617 0%, #06111f 48%, #111032 100%);
        color: #f8fafc;
        font-family: 'Rajdhani', sans-serif;
    }}

    /* ── Top Bar ── */
    .top-bar {{
        background: rgba(15,23,42,0.82);
        border: 1px solid rgba(56,189,248,0.28);
        border-radius: 18px;
        padding: 14px 18px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 18px;
    }}
    .top-title {{ color: #e0f2fe; font-weight: 950; font-size: 16px; }}
    .top-badge {{
        background: rgba(56,189,248,0.12);
        border: 1px solid rgba(56,189,248,0.35);
        color: #38bdf8;
        font-weight: 950;
        padding: 8px 14px;
        border-radius: 999px;
        font-size: 13px;
    }}

    /* ── Hero ── */
    .hero {{
        background:
            radial-gradient(circle at top, rgba(168,85,247,0.18), transparent 38%),
            linear-gradient(135deg, rgba(15,23,42,0.96), rgba(8,47,73,0.58));
        border: 1px solid rgba(56,189,248,0.38);
        border-radius: 32px;
        padding: 36px 28px;
        text-align: center;
        box-shadow: 0 0 48px rgba(56,189,248,0.16);
        margin-bottom: 22px;
    }}
    .hero h1 {{
        color: #c084fc;
        font-size: 42px;
        font-weight: 950;
        margin: 0;
        text-shadow: 0 0 24px rgba(192,132,252,0.42);
        letter-spacing: 2px;
    }}
    .hero p {{ color: #cbd5e1; margin-top: 12px; font-size: 15px; }}

    /* ── Metric Cards ── */
    .metric-card {{
        background: linear-gradient(145deg, rgba(15,23,42,0.95), rgba(30,41,59,0.62));
        border: 1px solid rgba(56,189,248,0.27);
        border-radius: 18px;
        padding: 16px;
        text-align: center;
        transition: 0.25s ease;
    }}
    .metric-card:hover {{
        transform: translateY(-3px);
        border-color: rgba(56,189,248,0.65);
        box-shadow: 0 0 24px rgba(56,189,248,0.18);
    }}
    .metric-label {{
        color: #a5f3fc;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin-bottom: 8px;
    }}
    .metric-value {{
        color: #f8fafc;
        font-size: 28px;
        font-weight: 950;
        line-height: 1;
    }}
    .metric-sub {{ color: #94a3b8; font-size: 11px; margin-top: 4px; }}

    /* ── Panel ── */
    .panel {{
        background: linear-gradient(145deg, rgba(15,23,42,0.92), rgba(2,6,23,0.78));
        border: 1px solid rgba(56,189,248,0.22);
        border-radius: 22px;
        padding: 22px;
        margin-bottom: 18px;
    }}
    .panel-title {{
        color: #22d3ee;
        font-size: 17px;
        font-weight: 900;
        margin-bottom: 14px;
        letter-spacing: 0.5px;
        {"text-align: right;" if is_ar else ""}
    }}

    /* ── Task Card ── */
    .task-card {{
        background: linear-gradient(135deg, rgba(15,23,42,0.85), rgba(2,6,23,0.72));
        border: 1px solid rgba(56,189,248,0.18);
        border-{"right" if is_ar else "left"}: 4px solid var(--prio-color, #38bdf8);
        border-radius: 14px;
        padding: 14px 16px;
        margin-bottom: 10px;
        transition: 0.22s ease;
    }}
    .task-card:hover {{
        border-color: rgba(56,189,248,0.55);
        transform: translateX({"-3px" if is_ar else "3px"});
    }}
    .task-card.completed {{
        opacity: 0.55;
    }}
    .task-card.completed .task-text {{
        text-decoration: line-through;
        color: #64748b;
    }}
    .task-card.overdue {{
        background: linear-gradient(135deg, rgba(239,68,68,0.10), rgba(2,6,23,0.72));
    }}

    .task-text {{
        color: #f1f5f9;
        font-size: 15px;
        font-weight: 700;
        line-height: 1.5;
        margin-bottom: 6px;
    }}
    .task-meta {{
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        align-items: center;
        font-size: 11px;
        {"flex-direction: row-reverse;" if is_ar else ""}
    }}
    .task-chip {{
        padding: 3px 10px;
        border-radius: 999px;
        font-family: 'Orbitron', monospace;
        font-weight: 700;
        font-size: 10px;
        letter-spacing: 0.5px;
        display: inline-flex;
        align-items: center;
        gap: 4px;
    }}

    /* ── Pomodoro ── */
    .pomo-display {{
        background: radial-gradient(circle, rgba(239,68,68,0.15), rgba(2,6,23,0.95));
        border: 2px solid rgba(239,68,68,0.45);
        border-radius: 24px;
        padding: 36px 24px;
        text-align: center;
        margin-bottom: 16px;
        box-shadow: 0 0 40px rgba(239,68,68,0.20);
    }}
    .pomo-display.work {{
        border-color: rgba(239,68,68,0.55);
        background: radial-gradient(circle, rgba(239,68,68,0.15), rgba(2,6,23,0.95));
    }}
    .pomo-display.break {{
        border-color: rgba(34,197,94,0.55);
        background: radial-gradient(circle, rgba(34,197,94,0.15), rgba(2,6,23,0.95));
    }}
    .pomo-display.long_break {{
        border-color: rgba(56,189,248,0.55);
        background: radial-gradient(circle, rgba(56,189,248,0.15), rgba(2,6,23,0.95));
    }}
    .pomo-label {{
        font-family: 'Orbitron', monospace;
        font-size: 12px;
        color: #94a3b8;
        letter-spacing: 3px;
        text-transform: uppercase;
        margin-bottom: 12px;
    }}
    .pomo-time {{
        font-family: 'Orbitron', monospace;
        font-size: 72px;
        font-weight: 900;
        color: #f1f5f9;
        line-height: 1;
        text-shadow: 0 0 24px rgba(239,68,68,0.45);
        letter-spacing: 4px;
    }}
    .pomo-sessions {{
        margin-top: 14px;
        color: #94a3b8;
        font-family: 'Orbitron', monospace;
        font-size: 11px;
        letter-spacing: 2px;
    }}

    /* ── Stopwatch ── */
    .sw-display {{
        background: radial-gradient(circle, rgba(168,85,247,0.15), rgba(2,6,23,0.95));
        border: 2px solid rgba(168,85,247,0.45);
        border-radius: 24px;
        padding: 30px 24px;
        text-align: center;
        margin-bottom: 16px;
    }}
    .sw-time {{
        font-family: 'Orbitron', monospace;
        font-size: 56px;
        font-weight: 900;
        color: #c084fc;
        line-height: 1;
        text-shadow: 0 0 18px rgba(192,132,252,0.45);
        letter-spacing: 3px;
    }}

    /* ── Buttons ── */
    .stButton > button {{
        background: linear-gradient(135deg, #0ea5e9 0%, #7c3aed 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 14px !important;
        padding: 11px 18px !important;
        font-weight: 800 !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-size: 14px !important;
        min-height: 44px;
        box-shadow: 0 4px 16px rgba(14,165,233,0.20);
        transition: 0.22s ease !important;
    }}
    .stButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 26px rgba(124,58,237,0.35);
    }}
    .stButton > button[kind="secondary"] {{
        background: linear-gradient(135deg, #ef4444 0%, #991b1b 100%) !important;
        box-shadow: 0 4px 16px rgba(239,68,68,0.20);
    }}

    /* ── Inputs ── */
    .stTextInput > div > div > input,
    .stTextArea textarea {{
        background: rgba(2,6,23,0.84) !important;
        color: #e0f2fe !important;
        border: 1px solid rgba(56,189,248,0.30) !important;
        border-radius: 12px !important;
        padding: 10px 14px !important;
        font-family: 'Rajdhani', sans-serif !important;
        {"direction: rtl; text-align: right;" if is_ar else ""}
    }}

    div[data-testid="stFileUploader"] {{
        background: rgba(15,23,42,0.50);
        border: 1px dashed rgba(56,189,248,0.35);
        border-radius: 16px;
        padding: 12px;
    }}

    /* ── Tabs ── */
    div[data-baseweb="tab-list"] {{
        gap: 8px;
        justify-content: center;
        flex-wrap: wrap;
        background: transparent;
    }}
    button[data-baseweb="tab"] {{
        background: rgba(15,23,42,0.72) !important;
        border-radius: 14px !important;
        color: #cbd5e1 !important;
        font-weight: 800 !important;
        border: 1px solid rgba(148,163,184,0.18) !important;
        padding: 10px 14px !important;
        font-size: 13px !important;
    }}
    button[data-baseweb="tab"][aria-selected="true"] {{
        background: linear-gradient(135deg, rgba(56,189,248,0.25), rgba(168,85,247,0.22)) !important;
        color: #ffffff !important;
        border-color: rgba(56,189,248,0.55) !important;
    }}
    </style>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# Render: Task Card
# ═══════════════════════════════════════════════════════════════════════════

def _render_task_card(task: dict, index: int, user_id: str):
    """Render one task card with checkbox + delete button."""
    prio_cfg = PRIORITY_CONFIG.get(task["priority"], PRIORITY_CONFIG["medium"])
    tag_cfg  = TAG_CONFIG.get(task["tag"], TAG_CONFIG["other"])

    due_label_key, due_color, days_diff = _due_status(task.get("due_date", ""))
    is_overdue = due_label_key == "overdue" and not task["completed"]

    classes = ["task-card"]
    if task["completed"]:
        classes.append("completed")
    if is_overdue:
        classes.append("overdue")

    # Due-date chip text
    if task.get("due_date"):
        due_chip_html = (
            f'<span class="task-chip" style="background:{due_color}22;color:{due_color};'
            f'border:1px solid {due_color}55;">📅 {_format_due(task["due_date"])}</span>'
        )
        if due_label_key:
            due_chip_html += (
                f'<span class="task-chip" style="background:{due_color}33;color:{due_color};'
                f'border:1px solid {due_color}66;">⚠️ {t(due_label_key)}</span>'
            )
    else:
        due_chip_html = ""

    chk_col, body_col, del_col = st.columns([0.07, 0.85, 0.08])

    with chk_col:
        st.write("")
        completed = st.checkbox(
            "done",
            value=task["completed"],
            key=f"task_chk_{task['id']}",
            label_visibility="collapsed",
        )
        if completed != task["completed"]:
            task["completed"]    = completed
            task["completed_at"] = time.time() if completed else None
            _save_tasks(st.session_state.tasks)
            log_action(
                "task_completed" if completed else "task_uncompleted",
                user_id=user_id,
                category="data",
                details=task["text"][:50],
            )
            st.rerun()

    with body_col:
        st.markdown(f"""
<div class="{' '.join(classes)}" style="--prio-color: {prio_cfg['color']};">
<div class="task-text">{task['text']}</div>
<div class="task-meta">
<span class="task-chip" style="background:{prio_cfg['color']}22;color:{prio_cfg['color']};border:1px solid {prio_cfg['color']}55;">
{prio_cfg['icon']} {t('priority_' + task['priority'])}
</span>
<span class="task-chip" style="background:{tag_cfg['color']}22;color:{tag_cfg['color']};border:1px solid {tag_cfg['color']}55;">
{tag_cfg['icon']} {t('tag_' + task['tag'])}
</span>
{due_chip_html}
</div>
</div>
        """, unsafe_allow_html=True)

    with del_col:
        st.write("")
        if st.button("🗑️", key=f"task_del_{task['id']}", use_container_width=True):
            st.session_state.tasks = [x for x in st.session_state.tasks if x["id"] != task["id"]]
            _save_tasks(st.session_state.tasks)
            log_action("task_deleted", user_id=user_id,
                       category="data", details=task["text"][:50])
            st.rerun()


# ═══════════════════════════════════════════════════════════════════════════
# Render: Pomodoro Timer
# ═══════════════════════════════════════════════════════════════════════════

def _get_pomo_duration() -> int:
    """Return current phase duration in seconds."""
    if st.session_state.pomo_phase == "work":
        return st.session_state.pomo_work_min * 60
    if st.session_state.pomo_phase == "long_break":
        return st.session_state.pomo_long_min * 60
    return st.session_state.pomo_break_min * 60


def _render_pomodoro(user_id: str):
    """Render Pomodoro timer panel."""
    phase = st.session_state.pomo_phase
    duration = _get_pomo_duration()

    # Calculate elapsed
    if st.session_state.pomo_running and st.session_state.pomo_start:
        elapsed = time.time() - st.session_state.pomo_start
    elif st.session_state.pomo_paused_at and st.session_state.pomo_start:
        elapsed = st.session_state.pomo_paused_at - st.session_state.pomo_start
    else:
        elapsed = 0

    remaining = max(0, int(duration - elapsed))

    # Auto-advance phase when done
    if remaining == 0 and st.session_state.pomo_running:
        st.session_state.pomo_running = False
        st.session_state.pomo_start   = None

        if phase == "work":
            st.session_state.pomo_sessions += 1
            # Long break every 4 work sessions
            next_phase = "long_break" if st.session_state.pomo_sessions % 4 == 0 else "break"
            st.session_state.pomo_phase = next_phase
            log_action("pomodoro_work_complete", user_id=user_id, category="data",
                       details=f"sessions={st.session_state.pomo_sessions}")
        else:
            st.session_state.pomo_phase = "work"

        st.success(f"🎉 {t('session_complete')}")

    # Time display
    minutes = remaining // 60
    seconds = remaining % 60
    time_str = f"{minutes:02d}:{seconds:02d}"

    phase_label_map = {
        "work":       t("pomodoro_work"),
        "break":      t("pomodoro_break"),
        "long_break": t("pomodoro_long_break"),
    }

    st.markdown(f"""
<div class="pomo-display {phase}">
<div class="pomo-label">🍅 {phase_label_map[phase]}</div>
<div class="pomo-time">{time_str}</div>
<div class="pomo-sessions">{t('sessions_done')}: {st.session_state.pomo_sessions}</div>
</div>
    """, unsafe_allow_html=True)

    # Controls
    c1, c2, c3 = st.columns(3)

    with c1:
        if not st.session_state.pomo_running:
            label = t("start_timer") if st.session_state.pomo_start is None else t("resume_timer")
            if st.button(f"▶ {label}", use_container_width=True, key="pomo_start_btn"):
                if st.session_state.pomo_paused_at and st.session_state.pomo_start:
                    # Resume: shift start to compensate for pause
                    pause_duration = time.time() - st.session_state.pomo_paused_at
                    st.session_state.pomo_start += pause_duration
                    st.session_state.pomo_paused_at = None
                else:
                    st.session_state.pomo_start = time.time()
                st.session_state.pomo_running = True
                log_action("pomodoro_started", user_id=user_id, category="data",
                           details=f"phase={phase}")
                st.rerun()
        else:
            if st.button(f"⏸ {t('pause_timer')}", use_container_width=True, key="pomo_pause_btn"):
                st.session_state.pomo_paused_at = time.time()
                st.session_state.pomo_running   = False
                st.rerun()

    with c2:
        if st.button(f"⏹ {t('reset_timer')}", use_container_width=True, key="pomo_reset_btn"):
            st.session_state.pomo_running   = False
            st.session_state.pomo_start     = None
            st.session_state.pomo_paused_at = None
            st.rerun()

    with c3:
        next_phase_label = {
            "work":       t("pomodoro_break"),
            "break":      t("pomodoro_work"),
            "long_break": t("pomodoro_work"),
        }[phase]
        if st.button(f"⏭ {next_phase_label}", use_container_width=True, key="pomo_skip_btn"):
            st.session_state.pomo_running   = False
            st.session_state.pomo_start     = None
            st.session_state.pomo_paused_at = None
            st.session_state.pomo_phase     = (
                "break" if phase == "work" else "work"
            )
            st.rerun()

    # Settings expander
    with st.expander(f"⚙️ {t('pomodoro')} {t('settings')}"):
        c1, c2, c3 = st.columns(3)
        with c1:
            st.session_state.pomo_work_min = st.number_input(
                t("work_duration"),
                min_value=1, max_value=60,
                value=st.session_state.pomo_work_min,
                key="pomo_work_input",
            )
        with c2:
            st.session_state.pomo_break_min = st.number_input(
                t("break_duration"),
                min_value=1, max_value=30,
                value=st.session_state.pomo_break_min,
                key="pomo_break_input",
            )
        with c3:
            st.session_state.pomo_long_min = st.number_input(
                t("long_break_duration"),
                min_value=5, max_value=60,
                value=st.session_state.pomo_long_min,
                key="pomo_long_input",
            )

    # Auto-rerun every 1s while running
    if st.session_state.pomo_running:
        time.sleep(1)
        st.rerun()


# ═══════════════════════════════════════════════════════════════════════════
# Render: Stopwatch
# ═══════════════════════════════════════════════════════════════════════════

def _render_stopwatch():
    """Render stopwatch panel."""
    if st.session_state.sw_running and st.session_state.sw_start:
        current = st.session_state.sw_elapsed + (time.time() - st.session_state.sw_start)
    else:
        current = st.session_state.sw_elapsed

    hours   = int(current // 3600)
    minutes = int((current % 3600) // 60)
    seconds = int(current % 60)
    centi   = int((current * 100) % 100)

    time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}.{centi:02d}"

    st.markdown(f"""
<div class="sw-display">
<div class="pomo-label">⏱️ {t('stopwatch')}</div>
<div class="sw-time">{time_str}</div>
</div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)

    with c1:
        if not st.session_state.sw_running:
            label = t("start_timer") if st.session_state.sw_elapsed == 0 else t("resume_timer")
            if st.button(f"▶ {label}", use_container_width=True, key="sw_start_btn"):
                st.session_state.sw_start   = time.time()
                st.session_state.sw_running = True
                st.rerun()
        else:
            if st.button(f"⏸ {t('pause_timer')}", use_container_width=True, key="sw_pause_btn"):
                st.session_state.sw_elapsed += time.time() - st.session_state.sw_start
                st.session_state.sw_start    = None
                st.session_state.sw_running  = False
                st.rerun()

    with c2:
        if st.button(f"⏹ {t('reset_timer')}", use_container_width=True, key="sw_reset_btn"):
            st.session_state.sw_running = False
            st.session_state.sw_start   = None
            st.session_state.sw_elapsed = 0.0
            st.rerun()

    with c3:
        st.write("")  # spacer

    if st.session_state.sw_running:
        time.sleep(1)
        st.rerun()


# ═══════════════════════════════════════════════════════════════════════════
# Main Render
# ═══════════════════════════════════════════════════════════════════════════

def render_tasks():
    """Main entry point for Tasks page."""
    # Auth guard
    if not st.session_state.get("logged_in", False):
        st.session_state.page = "login"
        st.rerun()

    init_language()
    apply_rtl_css()
    _init_state()
    _inject_css()

    user_id = st.session_state.get("user", "anonymous")

    # ── Top Bar ───────────────────────────────────────────────────────────
    st.markdown(f"""
<div class="top-bar">
<div class="top-title">{t('neon_ui')}</div>
<div class="top-badge">{t('tasks_title')}</div>
</div>
    """, unsafe_allow_html=True)

    # ── Hero ──────────────────────────────────────────────────────────────
    st.markdown(f"""
<div class="hero">
<h1>📝 {t('tasks_title')}</h1>
<p>{t('tasks_subtitle')}</p>
</div>
    """, unsafe_allow_html=True)

    # ── Back ──────────────────────────────────────────────────────────────
    back_col, _ = st.columns([1.3, 8])
    with back_col:
        if st.button(t("back"), use_container_width=True, key="tasks_back_btn"):
            st.session_state.page = "home"
            st.rerun()

    st.write("")

    # ── Metrics ───────────────────────────────────────────────────────────
    all_tasks   = st.session_state.tasks
    total       = len(all_tasks)
    completed   = sum(1 for t_ in all_tasks if t_["completed"])
    pending     = total - completed
    overdue     = sum(
        1 for t_ in all_tasks
        if not t_["completed"] and _due_status(t_.get("due_date", ""))[0] == "overdue"
    )

    m1, m2, m3, m4 = st.columns(4)

    metrics = [
        (m1, t("total"),     total,     "#38bdf8", "📋"),
        (m2, t("active"),    pending,   "#a855f7", "⚡"),
        (m3, t("completed"), completed, "#22c55e", "✅"),
        (m4, t("overdue"),   overdue,   "#ef4444", "🚨"),
    ]
    for col, label, value, color, icon in metrics:
        with col:
            st.markdown(f"""
<div class="metric-card">
<div class="metric-label">{icon} {label}</div>
<div class="metric-value" style="color:{color};">{value}</div>
</div>
            """, unsafe_allow_html=True)

    st.write("")

    # ── Tabs ──────────────────────────────────────────────────────────────
    tab_tasks, tab_pomo, tab_sw, tab_files, tab_summary = st.tabs([
        f"📝 {t('tasks')}",
        f"🍅 {t('pomodoro')}",
        f"⏱️ {t('stopwatch')}",
        f"📁 {t('files_library')}",
        f"📊 {t('summary')}",
    ])

    # ════════════════ TAB 1: Tasks ════════════════════════════════════════
    with tab_tasks:
        # ─ Add Task Panel ─
        st.markdown(f'<div class="panel"><div class="panel-title">➕ {t("add_task")}</div>',
                    unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        task_text = st.text_input(
            t("task_text"),
            placeholder=t("task_placeholder"),
            key="task_input_box",
        )

        c1, c2, c3 = st.columns(3)
        with c1:
            prio = st.selectbox(
                t("priority"),
                ["low", "medium", "high", "urgent"],
                index=1,
                format_func=lambda x: f"{PRIORITY_CONFIG[x]['icon']} {t('priority_' + x)}",
                key="task_prio_select",
            )
        with c2:
            due = st.date_input(
                t("due_date"),
                value=None,
                key="task_due_input",
            )
        with c3:
            tag = st.selectbox(
                t("tag"),
                list(TAG_CONFIG.keys()),
                format_func=lambda x: f"{TAG_CONFIG[x]['icon']} {t('tag_' + x)}",
                key="task_tag_select",
            )

        if st.button(f"➕ {t('add_task')}", use_container_width=True, key="add_task_btn"):
            if task_text.strip():
                due_str = due.isoformat() if due else ""
                new = _new_task(task_text, prio, due_str, tag)
                st.session_state.tasks.append(new)
                _save_tasks(st.session_state.tasks)
                log_action("task_added", user_id=user_id, category="data",
                           details=task_text[:50])
                st.success(f"✅ {t('task_added')}")
                time.sleep(0.6)
                st.rerun()

        st.write("")

        # ─ Filters Panel ─
        st.markdown(f'<div class="panel"><div class="panel-title">🔍 {t("search")} & {t("filter_status")}</div>',
                    unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.session_state.search_query = st.text_input(
            t("search"),
            value=st.session_state.search_query,
            placeholder=t("search_tasks"),
            key="search_input",
        )

        fc1, fc2, fc3, fc4 = st.columns(4)
        with fc1:
            status_filter = st.selectbox(
                t("filter_status"),
                ["all", "pending", "completed", "overdue"],
                format_func=lambda x: t("filter_all") if x == "all" else t(x),
                key="status_filter_select",
            )
        with fc2:
            prio_filter = st.selectbox(
                t("filter_priority"),
                ["all", "low", "medium", "high", "urgent"],
                format_func=lambda x: t("filter_all") if x == "all" else f"{PRIORITY_CONFIG[x]['icon']} {t('priority_' + x)}",
                key="prio_filter_select",
            )
        with fc3:
            tag_filter = st.selectbox(
                t("filter_tag"),
                ["all"] + list(TAG_CONFIG.keys()),
                format_func=lambda x: t("filter_all") if x == "all" else f"{TAG_CONFIG[x]['icon']} {t('tag_' + x)}",
                key="tag_filter_select",
            )
        with fc4:
            st.write("")
            if st.button(f"🗑️ {t('clear_completed')}", use_container_width=True,
                         key="clear_completed_btn"):
                st.session_state.tasks = [tk for tk in st.session_state.tasks if not tk["completed"]]
                _save_tasks(st.session_state.tasks)
                log_action("tasks_cleared_completed", user_id=user_id, category="data")
                st.rerun()

        # ─ Apply filters ─
        filtered = list(all_tasks)
        q = st.session_state.search_query.strip().lower()
        if q:
            filtered = [tk for tk in filtered if q in tk["text"].lower()]

        if status_filter == "pending":
            filtered = [tk for tk in filtered if not tk["completed"]]
        elif status_filter == "completed":
            filtered = [tk for tk in filtered if tk["completed"]]
        elif status_filter == "overdue":
            filtered = [tk for tk in filtered
                        if not tk["completed"]
                        and _due_status(tk.get("due_date", ""))[0] == "overdue"]

        if prio_filter != "all":
            filtered = [tk for tk in filtered if tk["priority"] == prio_filter]

        if tag_filter != "all":
            filtered = [tk for tk in filtered if tk["tag"] == tag_filter]

        # ─ Sort: incomplete first, then by priority, then by due date ─
        def _sort_key(tk):
            return (
                tk["completed"],
                -PRIORITY_CONFIG.get(tk["priority"], {}).get("order", 0),
                tk.get("due_date", "9999-12-31") or "9999-12-31",
            )
        filtered.sort(key=_sort_key)

        # ─ Render task list ─
        st.write("")
        st.markdown(f'<div class="panel"><div class="panel-title">📋 {t("all_tasks")} ({len(filtered)})</div>',
                    unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        if not all_tasks:
            st.info(f"📝 {t('no_tasks')}")
        elif not filtered:
            st.warning(f"🔍 {t('no_results')}")
        else:
            for i, task in enumerate(filtered):
                _render_task_card(task, i, user_id)

    # ════════════════ TAB 2: Pomodoro ═════════════════════════════════════
    with tab_pomo:
        _render_pomodoro(user_id)

    # ════════════════ TAB 3: Stopwatch ════════════════════════════════════
    with tab_sw:
        _render_stopwatch()

    # ════════════════ TAB 4: Files ════════════════════════════════════════
    with tab_files:
        st.markdown(f'<div class="panel"><div class="panel-title">📤 {t("upload_files")}</div>',
                    unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        uploaded_files = st.file_uploader(
            t("upload_files"),
            accept_multiple_files=True,
            type=["jpg", "jpeg", "png", "webp", "gif",
                  "mp3", "wav", "ogg",
                  "mp4", "mov", "webm",
                  "pdf", "txt", "docx"],
            key="tasks_file_uploader",
            label_visibility="collapsed",
        )

        if uploaded_files:
            added = 0
            for uf in uploaded_files:
                exists = any(f["name"] == uf.name for f in st.session_state.uploaded_files_info)
                if not exists:
                    path = _save_uploaded_file(uf)
                    st.session_state.uploaded_files_info.append({
                        "name":  uf.name,
                        "path":  path,
                        "type":  _get_file_type(uf.name),
                        "size":  uf.size,
                    })
                    added += 1
            if added:
                log_action("files_uploaded", user_id=user_id, category="data",
                           details=f"count={added}")
                st.success(f"✅ {added} file(s) uploaded")

        st.write("")

        # File list
        if st.session_state.uploaded_files_info:
            st.markdown(f'<div class="panel"><div class="panel-title">📁 {t("files_library")}</div>',
                        unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            for idx, fi in enumerate(st.session_state.uploaded_files_info):
                size_kb = fi["size"] / 1024
                size_str = f"{size_kb:.1f} KB" if size_kb < 1024 else f"{size_kb/1024:.1f} MB"

                c_info, c_del = st.columns([0.92, 0.08])
                with c_info:
                    st.markdown(f"""
<div class="task-card" style="--prio-color:#94a3b8;">
<div class="task-text">{_file_icon(fi['type'])} {fi['name']}</div>
<div class="task-meta">
<span class="task-chip" style="background:rgba(56,189,248,0.15);color:#38bdf8;border:1px solid rgba(56,189,248,0.40);">{fi['type']}</span>
<span class="task-chip" style="background:rgba(148,163,184,0.15);color:#94a3b8;border:1px solid rgba(148,163,184,0.30);">{size_str}</span>
</div>
</div>
                    """, unsafe_allow_html=True)
                with c_del:
                    st.write("")
                    if st.button("🗑️", key=f"file_del_{idx}", use_container_width=True):
                        try:
                            if os.path.exists(fi["path"]):
                                os.remove(fi["path"])
                        except OSError:
                            pass
                        st.session_state.uploaded_files_info.pop(idx)
                        st.rerun()

                # Preview
                if fi["type"] == "Image" and os.path.exists(fi["path"]):
                    st.image(fi["path"], width=280)
                elif fi["type"] == "Audio" and os.path.exists(fi["path"]):
                    with open(fi["path"], "rb") as f:
                        st.audio(f.read())
                elif fi["type"] == "Video" and os.path.exists(fi["path"]):
                    st.video(fi["path"])

    # ════════════════ TAB 5: Summary ═════════════════════════════════════
    with tab_summary:
        st.markdown(f'<div class="panel"><div class="panel-title">📊 {t("summary")}</div>',
                    unsafe_allow_html=True)

        # Stats by priority
        prio_counts = {p: 0 for p in PRIORITY_CONFIG}
        for tk in all_tasks:
            if not tk["completed"]:
                prio_counts[tk["priority"]] = prio_counts.get(tk["priority"], 0) + 1

        # Stats by tag
        tag_counts = {t_: 0 for t_ in TAG_CONFIG}
        for tk in all_tasks:
            if not tk["completed"]:
                tag_counts[tk["tag"]] = tag_counts.get(tk["tag"], 0) + 1

        completion_rate = round((completed / total * 100), 1) if total else 0

        st.markdown(f"""
<div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;margin:14px 0;">
<div style="padding:14px;background:rgba(34,197,94,0.10);border:1px solid rgba(34,197,94,0.30);border-radius:12px;">
<div style="color:#94a3b8;font-size:11px;letter-spacing:1.5px;text-transform:uppercase;">Completion Rate</div>
<div style="color:#22c55e;font-size:32px;font-weight:900;font-family:'Orbitron',monospace;margin-top:6px;">{completion_rate}%</div>
</div>
<div style="padding:14px;background:rgba(168,85,247,0.10);border:1px solid rgba(168,85,247,0.30);border-radius:12px;">
<div style="color:#94a3b8;font-size:11px;letter-spacing:1.5px;text-transform:uppercase;">🍅 {t('sessions_done')}</div>
<div style="color:#c084fc;font-size:32px;font-weight:900;font-family:'Orbitron',monospace;margin-top:6px;">{st.session_state.pomo_sessions}</div>
</div>
</div>
        """, unsafe_allow_html=True)

        # Priority breakdown
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"**{t('priority')}**")
        for p, count in prio_counts.items():
            cfg = PRIORITY_CONFIG[p]
            st.markdown(f"""
<div style="display:flex;justify-content:space-between;padding:6px 12px;background:rgba(15,23,42,0.55);border-radius:8px;margin:4px 0;border-left:3px solid {cfg['color']};">
<span style="color:{cfg['color']};">{cfg['icon']} {t('priority_' + p)}</span>
<span style="color:#f1f5f9;font-weight:700;">{count}</span>
</div>
            """, unsafe_allow_html=True)

        # Tag breakdown
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"**{t('tags')}**")
        for tg, count in tag_counts.items():
            cfg = TAG_CONFIG[tg]
            st.markdown(f"""
<div style="display:flex;justify-content:space-between;padding:6px 12px;background:rgba(15,23,42,0.55);border-radius:8px;margin:4px 0;border-left:3px solid {cfg['color']};">
<span style="color:{cfg['color']};">{cfg['icon']} {t('tag_' + tg)}</span>
<span style="color:#f1f5f9;font-weight:700;">{count}</span>
</div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)