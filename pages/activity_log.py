"""
═══════════════════════════════════════════════════════════════════════════
OMNIX VISION — Activity Log Page
═══════════════════════════════════════════════════════════════════════════
Provides:
    • Statistics overview (total actions, unique users, last action)
    • Filterable activity timeline
    • Category filter (Auth, Navigation, Data, Security, System)
    • Clear log button
═══════════════════════════════════════════════════════════════════════════
"""

from datetime import datetime
import streamlit as st

from utils.language import t, init_language, apply_rtl_css
from utils.activity import get_log, get_stats, clear_log, log_action


# ── Category Configuration ─────────────────────────────────────────────────
CATEGORY_ICONS = {
    "auth":       "🔐",
    "navigation": "🧭",
    "data":       "💾",
    "security":   "🛡️",
    "system":     "⚙️",
    "other":      "📝",
}

CATEGORY_COLORS = {
    "auth":       "#38bdf8",
    "navigation": "#22c55e",
    "data":       "#a855f7",
    "security":   "#ef4444",
    "system":     "#f59e0b",
    "other":      "#94a3b8",
}


def _format_timestamp(ts):
    """Format unix timestamp to readable date."""
    if not ts:
        return "—"
    try:
        return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return "—"


def _format_relative(ts):
    """Format unix timestamp as 'X minutes ago'."""
    if not ts:
        return "—"
    try:
        diff = datetime.now().timestamp() - ts
        if diff < 60:
            return f"{int(diff)}s ago"
        elif diff < 3600:
            return f"{int(diff / 60)}m ago"
        elif diff < 86400:
            return f"{int(diff / 3600)}h ago"
        else:
            return f"{int(diff / 86400)}d ago"
    except Exception:
        return "—"


def render_activity_log():
    init_language()
    apply_rtl_css()

    # ── Styles ────────────────────────────────────────────────────────────
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@400;500;600;700&display=swap');

    [data-testid="stSidebar"], [data-testid="collapsedControl"] { display: none; }

    .block-container {
        max-width: 1100px;
        padding-top: 1.2rem;
    }

    .stApp {
        background:
            radial-gradient(ellipse at 5% 8%, rgba(20,184,166,0.10) 0%, transparent 38%),
            radial-gradient(ellipse at 95% 8%, rgba(56,189,248,0.10) 0%, transparent 38%),
            linear-gradient(160deg, #020617 0%, #0a1a1a 50%, #020617 100%);
        color: #f8fafc;
        font-family: 'Rajdhani', sans-serif;
    }

    .log-header {
        background: linear-gradient(135deg, rgba(20,184,166,0.08), rgba(2,6,23,0.95));
        border: 1px solid rgba(20,184,166,0.30);
        border-radius: 24px;
        padding: 28px 32px;
        text-align: center;
        margin-bottom: 24px;
    }
    .log-header h1 {
        font-family: 'Orbitron', monospace;
        font-size: 36px;
        font-weight: 900;
        margin: 0;
        background: linear-gradient(90deg, #14b8a6, #38bdf8, #14b8a6);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: logShimmer 4s linear infinite;
    }
    @keyframes logShimmer { to { background-position: 200% center; } }
    .log-header p {
        color: #94a3b8;
        margin-top: 8px;
        font-size: 15px;
    }

    .stat-card {
        background: linear-gradient(145deg, rgba(2,6,23,0.95), rgba(15,23,42,0.75));
        border: 1px solid rgba(56,189,248,0.20);
        border-radius: 18px;
        padding: 18px 22px;
        text-align: center;
        transition: 0.3s ease;
        height: 100%;
    }
    .stat-card:hover {
        transform: translateY(-3px);
        border-color: rgba(56,189,248,0.55);
    }
    .stat-icon {
        font-size: 28px;
        margin-bottom: 8px;
        filter: drop-shadow(0 0 8px rgba(56,189,248,0.4));
    }
    .stat-label {
        font-family: 'Orbitron', monospace;
        color: #64748b;
        font-size: 10px;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 6px;
    }
    .stat-value {
        font-family: 'Orbitron', monospace;
        font-size: 22px;
        font-weight: 700;
        color: #38bdf8;
    }
    .stat-value-small {
        font-family: 'Rajdhani', sans-serif;
        font-size: 14px;
        font-weight: 600;
        color: #f1f5f9;
    }

    .timeline-card {
        background: linear-gradient(145deg, rgba(2,6,23,0.95), rgba(15,23,42,0.75));
        border: 1px solid rgba(56,189,248,0.15);
        border-radius: 20px;
        padding: 24px;
        margin-top: 16px;
        min-height: 200px;
    }

    .timeline-item {
        display: flex;
        align-items: flex-start;
        gap: 14px;
        padding: 12px 14px;
        background: rgba(2,6,23,0.50);
        border-left: 3px solid rgba(56,189,248,0.40);
        border-radius: 10px;
        margin-bottom: 8px;
        transition: 0.25s ease;
    }
    .timeline-item:hover {
        background: rgba(2,6,23,0.75);
        border-left-width: 5px;
        transform: translateX(3px);
    }
    .timeline-icon {
        font-size: 22px;
        flex-shrink: 0;
        margin-top: 2px;
    }
    .timeline-body { flex: 1; min-width: 0; }
    .timeline-action {
        font-family: 'Rajdhani', sans-serif;
        color: #f1f5f9;
        font-weight: 600;
        font-size: 14px;
        margin-bottom: 3px;
        word-break: break-word;
    }
    .timeline-meta {
        color: #64748b;
        font-size: 11px;
        font-family: 'Rajdhani', sans-serif;
        letter-spacing: 0.5px;
    }
    .timeline-time {
        color: #38bdf8;
        font-family: 'Orbitron', monospace;
        font-size: 10px;
        white-space: nowrap;
        margin-left: 8px;
        flex-shrink: 0;
    }

    .timeline-category {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 999px;
        font-size: 9px;
        font-family: 'Orbitron', monospace;
        letter-spacing: 1px;
        text-transform: uppercase;
        margin-right: 6px;
    }

    .empty-state {
        text-align: center;
        padding: 40px 20px;
        color: #64748b;
        font-family: 'Rajdhani', sans-serif;
        font-size: 16px;
    }
    .empty-state .empty-icon {
        font-size: 56px;
        margin-bottom: 12px;
        opacity: 0.4;
    }

    .stButton > button {
        background: linear-gradient(135deg, #14b8a6 0%, #0ea5e9 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 10px 18px !important;
        font-weight: 700 !important;
        font-family: 'Rajdhani', sans-serif !important;
        letter-spacing: 0.5px !important;
        box-shadow: 0 4px 14px rgba(20,184,166,0.20) !important;
        transition: 0.28s ease !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(20,184,166,0.40) !important;
    }
    .stButton > button[kind="secondary"] {
        background: linear-gradient(135deg, #ef4444 0%, #991b1b 100%) !important;
    }

    div[data-testid="stSelectbox"] {
        background: rgba(2,6,23,0.50);
        border-radius: 12px;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── Header ────────────────────────────────────────────────────────────
    st.markdown(f"""
<div class="log-header">
<h1>&#128203; {t("activity_title")}</h1>
<p>{t("activity_subtitle")}</p>
</div>
    """, unsafe_allow_html=True)

    # ── Back Button ───────────────────────────────────────────────────────
    if st.button(t("back"), key="log_back_btn"):
        st.session_state.page = "home"
        st.rerun()

    # ══════════════════════════════════════════════════════════════════════
    # Statistics Overview
    # ══════════════════════════════════════════════════════════════════════
    stats = get_stats()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
<div class="stat-card">
<div class="stat-icon">&#128202;</div>
<div class="stat-label">{t("total_actions")}</div>
<div class="stat-value">{stats["total"]}</div>
</div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
<div class="stat-card">
<div class="stat-icon">&#128100;</div>
<div class="stat-label">{t("unique_users")}</div>
<div class="stat-value">{stats["unique_users"]}</div>
</div>
        """, unsafe_allow_html=True)

    with col3:
        last_time = _format_relative(stats["last_action_time"])
        st.markdown(f"""
<div class="stat-card">
<div class="stat-icon">&#9201;&#65039;</div>
<div class="stat-label">{t("last_action")}</div>
<div class="stat-value-small">{last_time}</div>
</div>
        """, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════
    # Filters
    # ══════════════════════════════════════════════════════════════════════
    st.markdown("<br>", unsafe_allow_html=True)
    filter_col, action_col = st.columns([3, 1])

    with filter_col:
        category_options = {
            t("filter_all"):           None,
            t("auth_category"):        "auth",
            t("navigation_category"):  "navigation",
            t("data_category"):        "data",
            t("security_category"):    "security",
            t("system_category"):      "system",
        }
        selected_label    = st.selectbox(t("filter_category"),
                                         list(category_options.keys()),
                                         key="log_filter")
        selected_category = category_options[selected_label]

    with action_col:
        st.write("")
        if st.button(f"&#128465;&#65039; {t('clear_log')}",
                     key="log_clear_btn", type="secondary",
                     use_container_width=True):
            clear_log()
            log_action("log_cleared",
                       user_id=st.session_state.get("user", "anonymous"),
                       category="system")
            st.success(t("log_cleared"))
            st.rerun()

    # ══════════════════════════════════════════════════════════════════════
    # Timeline
    # ══════════════════════════════════════════════════════════════════════
    entries = get_log(limit=200, category=selected_category)

    st.markdown('<div class="timeline-card">', unsafe_allow_html=True)

    if not entries:
        st.markdown(f"""
<div class="empty-state">
<div class="empty-icon">&#128221;</div>
<div>{t("no_activity")}</div>
</div>
        """, unsafe_allow_html=True)
    else:
        for entry in entries:
            ts       = entry.get("timestamp", 0)
            user_id  = entry.get("user_id", "anonymous")
            action   = entry.get("action", "—")
            details  = entry.get("details", "")
            category = entry.get("category", "other")

            icon  = CATEGORY_ICONS.get(category, "📝")
            color = CATEGORY_COLORS.get(category, "#94a3b8")

            time_relative = _format_relative(ts)
            time_abs      = _format_timestamp(ts)

            details_html = f' &middot; {details}' if details else ''

            st.markdown(f"""
<div class="timeline-item" style="border-left-color:{color};">
<div class="timeline-icon">{icon}</div>
<div class="timeline-body">
<div class="timeline-action">
<span class="timeline-category" style="background:{color}22;color:{color};">{category}</span>
{action}
</div>
<div class="timeline-meta">
&#128100; {user_id} &middot; {time_abs}{details_html}
</div>
</div>
<div class="timeline-time">{time_relative}</div>
</div>
            """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)