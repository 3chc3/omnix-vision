"""
═══════════════════════════════════════════════════════════════════════════
OMNIX VISION — Home Hub (Phase 4 — Round 3)
═══════════════════════════════════════════════════════════════════════════
Phase-4 changes:
    ✓ Updated to include all 4 new pages from Round 2:
      - 🔔 Notifications
      - 💾 Backup & Restore
      - 🎲 Random Tools
      - 🍅 Pomodoro Studio
    ✓ Module grid organized into 4 rows (4 cards each = 16 visible modules)
    ✓ Quick stats banner showing notifications + activity counts
    ✓ Unread notifications badge on bell icon
═══════════════════════════════════════════════════════════════════════════
"""

import streamlit as st

from utils.language import t, init_language, apply_rtl_css, is_rtl, render_language_selector
from utils.activity import log_action, get_stats


# ═══════════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════════

def _get_unread_notif_count(user_id: str) -> int:
    """Try to count unread notifications. Returns 0 if module unavailable."""
    try:
        from pages.notifications import _get_user_notifs
        notifs = _get_user_notifs(user_id)
        return sum(1 for n in notifs if n.get("status") == "unread")
    except Exception:
        return 0


# ═══════════════════════════════════════════════════════════════════════════
# CSS
# ═══════════════════════════════════════════════════════════════════════════

def _apply_css():
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
        padding-left: 1rem;
        padding-right: 1rem;
        {"direction: rtl;" if is_ar else ""}
    }}

    .stApp {{
        background:
            radial-gradient(circle at 10% 10%, rgba(56,189,248,0.18), transparent 28%),
            radial-gradient(circle at 90% 10%, rgba(168,85,247,0.20), transparent 32%),
            radial-gradient(circle at 50% 100%, rgba(34,197,94,0.08), transparent 30%),
            linear-gradient(135deg, #020617 0%, #06111f 48%, #111032 100%);
        color: #f8fafc;
        font-family: 'Rajdhani', sans-serif;
    }}

    .top-bar {{
        background: rgba(15,23,42,0.82);
        border: 1px solid rgba(56,189,248,0.28);
        border-radius: 18px;
        padding: 12px 18px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 16px;
    }}
    .top-title  {{ color: #e0f2fe; font-weight: 950; font-size: 16px; }}
    .top-info {{
        display: flex;
        gap: 12px;
        align-items: center;
    }}
    .top-badge {{
        background: rgba(56,189,248,0.12);
        border: 1px solid rgba(56,189,248,0.35);
        color: #38bdf8;
        font-weight: 800;
        padding: 6px 12px;
        border-radius: 999px;
        font-size: 12px;
    }}
    .top-badge.notif {{
        background: rgba(239,68,68,0.12);
        border-color: rgba(239,68,68,0.45);
        color: #ef4444;
    }}

    .hero {{
        background:
            radial-gradient(circle at top, rgba(168,85,247,0.18), transparent 38%),
            linear-gradient(135deg, rgba(15,23,42,0.96), rgba(8,47,73,0.58));
        border: 1px solid rgba(56,189,248,0.38);
        border-radius: 30px;
        padding: 36px 28px;
        text-align: center;
        margin-bottom: 22px;
        box-shadow: 0 0 48px rgba(56,189,248,0.16);
    }}
    .hero h1 {{
        font-family: 'Orbitron', monospace;
        font-size: 44px;
        font-weight: 950;
        margin: 0;
        letter-spacing: 3px;
        background: linear-gradient(90deg, #38bdf8, #a855f7, #22c55e, #38bdf8);
        background-size: 300% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: shimmer 5s linear infinite;
    }}
    @keyframes shimmer {{ to {{ background-position: 300% center; }} }}
    .hero p {{
        color: #cbd5e1;
        margin-top: 10px;
        font-size: 14px;
        letter-spacing: 1px;
    }}

    .section-label {{
        font-family: 'Orbitron', monospace;
        color: #38bdf8;
        font-size: 12px;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin: 18px 0 10px;
        padding-{"right" if is_ar else "left"}: 12px;
        border-{"right" if is_ar else "left"}: 3px solid rgba(56,189,248,0.55);
    }}

    .module-card {{
        background: linear-gradient(145deg, rgba(2,6,23,0.96), rgba(15,23,42,0.80));
        border: 1px solid rgba(56,189,248,0.18);
        border-radius: 18px;
        padding: 18px 14px;
        text-align: center;
        min-height: 160px;
        transition: 0.35s cubic-bezier(0.34,1.56,0.64,1);
        margin-bottom: 8px;
    }}
    .module-card:hover {{
        transform: translateY(-6px) scale(1.02);
        border-color: rgba(56,189,248,0.65);
        box-shadow: 0 16px 44px rgba(56,189,248,0.18);
    }}
    .module-icon {{
        font-size: 42px;
        margin-bottom: 10px;
        display: block;
        filter: drop-shadow(0 0 14px rgba(56,189,248,0.40));
    }}
    .module-title {{
        font-family: 'Orbitron', monospace;
        color: #f1f5f9;
        font-size: 13px;
        font-weight: 700;
        margin-bottom: 4px;
        letter-spacing: 0.5px;
    }}
    .module-desc {{
        color: #94a3b8;
        font-size: 11px;
        line-height: 1.5;
    }}

    .stButton > button {{
        background: linear-gradient(135deg, #0ea5e9 0%, #7c3aed 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 10px 14px !important;
        font-weight: 700 !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-size: 13px !important;
        min-height: 42px !important;
        box-shadow: 0 4px 16px rgba(14,165,233,0.20) !important;
        transition: 0.25s ease !important;
    }}
    .stButton > button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 26px rgba(124,58,237,0.35) !important;
    }}
    .stButton > button[kind="secondary"] {{
        background: linear-gradient(135deg, #ef4444 0%, #991b1b 100%) !important;
        box-shadow: 0 4px 16px rgba(239,68,68,0.20) !important;
    }}
    </style>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# Module Definitions
# ═══════════════════════════════════════════════════════════════════════════

def _get_modules() -> list:
    """Return list of all available modules grouped by category."""
    return [
        # Category: AI & Vision
        ("ai_vision", [
            ("camera",          "🧠", t("camera"),         "AI pose + hand detection"),
            ("hand_scan",       "🖐️", t("hand_scan"),       "Hand-based authentication"),
            ("assistant",       "🤖", t("assistant"),       "Smart AI assistant"),
            ("dashboard",       "📊", t("dashboard"),       "Charts & system health"),
        ]),
        # Category: Productivity
        ("productivity", [
            ("tasks",           "📝", t("tasks"),           "Tasks + Pomodoro"),
            ("calculator",      "🧮", t("calculator"),      "Math & conversions"),
            ("pomodoro",        "🍅", t("standalone_pomo"),  "Focus timer studio"),
            ("notifications",   "🔔", t("notifications"),    "System alerts"),
        ]),
        # Category: Media
        ("media", [
            ("media",           "🎬", t("media_library"),    "Gallery & filters"),
            ("media_converter", "🎞️", t("media_converter"),  "Convert files"),
            ("game",            "🎮", t("game"),             "Game center"),
            ("random_tools",    "🎲", t("random_tools"),     "QR, passwords…"),
        ]),
        # Category: System
        ("system", [
            ("security_center", "🛡️", t("security_center"),  "Account safety"),
            ("activity_log",    "📋", t("activity_log"),     "Audit trail"),
            ("backup",          "💾", t("backup_restore"),   "Export & import"),
            ("settings",        "⚙️", t("settings"),         "Preferences"),
        ]),
    ]


# ═══════════════════════════════════════════════════════════════════════════
# Render Section
# ═══════════════════════════════════════════════════════════════════════════

def _render_module_row(modules: list, row_key: str):
    """Render 4 module cards side by side."""
    cols = st.columns(4)
    for i, (page_key, icon, title, desc) in enumerate(modules):
        with cols[i]:
            st.markdown(f"""
<div class="module-card">
<span class="module-icon">{icon}</span>
<div class="module-title">{title}</div>
<div class="module-desc">{desc}</div>
</div>
            """, unsafe_allow_html=True)
            if st.button(
                t("open"),
                use_container_width=True,
                key=f"home_open_{page_key}_{row_key}",
            ):
                st.session_state.page = page_key
                log_action(f"navigate_to_{page_key}",
                           user_id=st.session_state.get("user", "anonymous"),
                           category="navigation")
                st.rerun()


# ═══════════════════════════════════════════════════════════════════════════
# Main Render
# ═══════════════════════════════════════════════════════════════════════════

def render_home():
    init_language()
    apply_rtl_css()

    if not st.session_state.get("logged_in", False):
        st.session_state.page = "login"
        st.rerun()

    user_id = st.session_state.get("user", "anonymous")

    _apply_css()

    # ── Quick stats ──
    unread_count = _get_unread_notif_count(user_id)
    activity_stats = get_stats()

    # ── Top Bar ──
    notif_indicator = f"🔔 {unread_count}" if unread_count > 0 else "🔕"
    st.markdown(f"""
<div class="top-bar">
<div class="top-title">⚡ {t('neon_ui')}</div>
<div class="top-info">
<span class="top-badge">👤 {user_id}</span>
<span class="top-badge {'notif' if unread_count else ''}">{notif_indicator}</span>
<span class="top-badge">📋 {activity_stats['total']}</span>
</div>
</div>
    """, unsafe_allow_html=True)

    # ── Hero ──
    st.markdown(f"""
<div class="hero">
<h1>🚀 OMNIX VISION</h1>
<p>{t('ultra_platform')} · 16 {t('modules_count') if False else 'Modules'}</p>
</div>
    """, unsafe_allow_html=True)

    # ── Top utility row ──
    top_c1, top_c2, top_c3, top_c4 = st.columns([1, 1, 1, 5])
    with top_c1:
        render_language_selector(key="home_lang_select")
    with top_c2:
        if st.button(f"ℹ️ {t('about_us')}",
                     use_container_width=True,
                     key="home_about_btn"):
            st.session_state.page = "about"
            st.rerun()
    with top_c3:
        if st.button(f"🚪 {t('logout')}",
                     use_container_width=True,
                     type="secondary",
                     key="home_logout_btn"):
            log_action("logout", user_id=user_id, category="auth")
            # Clear session
            for key in list(st.session_state.keys()):
                if key != "language":
                    del st.session_state[key]
            st.session_state.page = "login"
            st.session_state.logged_in = False
            st.rerun()

    # ── Module Grid ──
    section_labels = {
        "ai_vision":    "🧠 AI & Vision",
        "productivity": "⚡ Productivity",
        "media":        "🎬 Media & Fun",
        "system":       "🛡️ System",
    }

    modules = _get_modules()
    for cat_key, mods in modules:
        st.markdown(
            f'<div class="section-label">{section_labels.get(cat_key, cat_key)}</div>',
            unsafe_allow_html=True,
        )
        _render_module_row(mods, cat_key)