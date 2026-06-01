"""
═══════════════════════════════════════════════════════════════════════════
OMNIX VISION — Notifications Center (Phase 4 — Round 2)
═══════════════════════════════════════════════════════════════════════════
Features:
    ✓ Per-user notifications persistence (data/notifications.json)
    ✓ Mark as read / unread / archive / delete
    ✓ 4 priority levels: info, success, warning, error
    ✓ Filter by status and priority
    ✓ Unread badge count
    ✓ Auto-notifications from activity log integration
    ✓ Add manual notification feature
    ✓ Full EN/AR translation with RTL
═══════════════════════════════════════════════════════════════════════════
"""

import json
import time
import uuid
from pathlib import Path
from datetime import datetime

import streamlit as st

from utils.language import t, init_language, apply_rtl_css, is_rtl
from utils.activity import log_action


# ═══════════════════════════════════════════════════════════════════════════
# Paths & Persistence
# ═══════════════════════════════════════════════════════════════════════════
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
NOTIF_FILE = DATA_DIR / "notifications.json"
DATA_DIR.mkdir(parents=True, exist_ok=True)

MAX_NOTIFICATIONS_PER_USER = 200


# ═══════════════════════════════════════════════════════════════════════════
# Page Translations
# ═══════════════════════════════════════════════════════════════════════════
NOTIF_KEYS = {
    "notif_title":     {"en": "Notifications Center",       "ar": "مركز الإشعارات"},
    "notif_subtitle":  {"en": "Stay updated with system alerts and messages",
                        "ar": "ابق على اطلاع بتنبيهات ورسائل النظام"},
    "unread":          {"en": "Unread",       "ar": "غير مقروءة"},
    "read":            {"en": "Read",         "ar": "مقروءة"},
    "archived":        {"en": "Archived",     "ar": "مؤرشفة"},
    "all":             {"en": "All",          "ar": "الكل"},
    "mark_read":       {"en": "Mark as Read", "ar": "تعليم كمقروءة"},
    "mark_unread":     {"en": "Mark Unread",  "ar": "تعليم غير مقروءة"},
    "archive":         {"en": "Archive",      "ar": "أرشفة"},
    "unarchive":       {"en": "Unarchive",    "ar": "إلغاء الأرشفة"},
    "delete":          {"en": "Delete",       "ar": "حذف"},
    "no_notifs":       {"en": "🎉 No notifications. You're all caught up!",
                        "ar": "🎉 لا توجد إشعارات. أنت على اطلاع كامل!"},
    "no_results":      {"en": "No notifications match your filter.",
                        "ar": "لا توجد إشعارات تطابق التصفية."},
    "add_notif":       {"en": "➕ Add Notification",  "ar": "➕ إضافة إشعار"},
    "notif_title_label":  {"en": "Title",   "ar": "العنوان"},
    "notif_message":      {"en": "Message", "ar": "الرسالة"},
    "notif_priority":     {"en": "Priority","ar": "الأولوية"},
    "info":            {"en": "Info",       "ar": "معلومات"},
    "success":         {"en": "Success",    "ar": "نجاح"},
    "warning":         {"en": "Warning",    "ar": "تحذير"},
    "error":           {"en": "Error",      "ar": "خطأ"},
    "create_notif":    {"en": "📨 Create",  "ar": "📨 إنشاء"},
    "notif_created":   {"en": "✅ Notification created!", "ar": "✅ تم إنشاء الإشعار!"},
    "clear_all":       {"en": "🗑️ Clear All",   "ar": "🗑️ مسح الكل"},
    "mark_all_read":   {"en": "👁️ Mark All Read", "ar": "👁️ تعليم الكل كمقروء"},
    "total_notifs":    {"en": "Total",      "ar": "الإجمالي"},
    "just_now":        {"en": "Just now",   "ar": "الآن"},
    "minutes_ago":     {"en": "min ago",    "ar": "د مضت"},
    "hours_ago":       {"en": "h ago",      "ar": "س مضت"},
    "days_ago":        {"en": "d ago",      "ar": "ي مضت"},
}


def _t(key: str) -> str:
    from utils.language import get_language_code
    lang = get_language_code()
    if key in NOTIF_KEYS:
        return NOTIF_KEYS[key].get(lang, NOTIF_KEYS[key].get("en", key))
    return t(key)


# ═══════════════════════════════════════════════════════════════════════════
# Storage
# ═══════════════════════════════════════════════════════════════════════════

def _load_all_notifs() -> dict:
    if not NOTIF_FILE.exists():
        return {}
    try:
        with open(NOTIF_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _save_all_notifs(data: dict):
    try:
        with open(NOTIF_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except OSError:
        pass


def _get_user_notifs(user_id: str) -> list:
    return _load_all_notifs().get(str(user_id), [])


def _save_user_notifs(user_id: str, notifs: list):
    all_data = _load_all_notifs()
    all_data[str(user_id)] = notifs[-MAX_NOTIFICATIONS_PER_USER:]
    _save_all_notifs(all_data)


def add_notification(user_id: str,
                     title: str,
                     message: str,
                     priority: str = "info"):
    """
    Public helper — add a notification for a user.
    Can be called from other modules too.
    """
    notifs = _get_user_notifs(user_id)
    notifs.append({
        "id":         str(uuid.uuid4())[:8],
        "title":      title,
        "message":    message,
        "priority":   priority,    # info | success | warning | error
        "status":     "unread",    # unread | read | archived
        "created_at": time.time(),
    })
    _save_user_notifs(user_id, notifs)


# ═══════════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════════

PRIORITY_CONFIG = {
    "info":    {"color": "#38bdf8", "icon": "ℹ️", "bg": "rgba(56,189,248,0.10)"},
    "success": {"color": "#22c55e", "icon": "✅", "bg": "rgba(34,197,94,0.10)"},
    "warning": {"color": "#f59e0b", "icon": "⚠️", "bg": "rgba(245,158,11,0.10)"},
    "error":   {"color": "#ef4444", "icon": "🚨", "bg": "rgba(239,68,68,0.10)"},
}


def _time_ago(ts: float) -> str:
    """Convert timestamp to '5m ago', '2h ago' etc."""
    diff = time.time() - ts
    if diff < 60:
        return _t("just_now")
    if diff < 3600:
        return f"{int(diff/60)} {_t('minutes_ago')}"
    if diff < 86400:
        return f"{int(diff/3600)} {_t('hours_ago')}"
    return f"{int(diff/86400)} {_t('days_ago')}"


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
        max-width: 1180px;
        padding-top: 1.2rem;
        {"direction: rtl;" if is_ar else ""}
    }}

    .stApp {{
        background:
            radial-gradient(circle at 10% 10%, rgba(56,189,248,0.18), transparent 28%),
            radial-gradient(circle at 90% 10%, rgba(168,85,247,0.20), transparent 32%),
            linear-gradient(135deg, #020617 0%, #06111f 48%, #111032 100%);
        color: #f8fafc;
        font-family: 'Rajdhani', sans-serif;
    }}

    .hero {{
        background: linear-gradient(135deg, rgba(15,23,42,0.96), rgba(8,47,73,0.58));
        border: 1px solid rgba(56,189,248,0.38);
        border-radius: 30px;
        padding: 34px 28px;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 0 48px rgba(56,189,248,0.16);
    }}
    .hero h1 {{
        color: #c084fc;
        font-size: 38px;
        font-weight: 950;
        margin: 0;
        letter-spacing: 2px;
        text-shadow: 0 0 24px rgba(192,132,252,0.4);
    }}
    .hero p {{ color: #cbd5e1; margin-top: 10px; font-size: 14px; }}

    .metric-card {{
        background: linear-gradient(145deg, rgba(15,23,42,0.95), rgba(30,41,59,0.62));
        border: 1px solid rgba(56,189,248,0.27);
        border-radius: 16px;
        padding: 14px;
        text-align: center;
        transition: 0.25s ease;
    }}
    .metric-card:hover {{
        transform: translateY(-3px);
        border-color: rgba(56,189,248,0.65);
    }}
    .metric-label {{
        color: #a5f3fc;
        font-size: 10px;
        font-family: 'Orbitron', monospace;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin-bottom: 6px;
    }}
    .metric-value {{
        color: #f8fafc;
        font-size: 26px;
        font-weight: 900;
        font-family: 'Orbitron', monospace;
    }}

    .notif-card {{
        background: linear-gradient(135deg, rgba(15,23,42,0.85), rgba(2,6,23,0.72));
        border: 1px solid rgba(56,189,248,0.18);
        border-{"right" if is_ar else "left"}: 4px solid var(--prio-color, #38bdf8);
        border-radius: 14px;
        padding: 14px 18px;
        margin-bottom: 10px;
        transition: 0.22s ease;
    }}
    .notif-card.unread {{
        background: linear-gradient(135deg, rgba(56,189,248,0.10), rgba(2,6,23,0.85));
    }}
    .notif-card.archived {{ opacity: 0.55; }}
    .notif-card:hover {{
        border-color: rgba(56,189,248,0.55);
        transform: translateX({"-3px" if is_ar else "3px"});
    }}

    .notif-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 6px;
        {"flex-direction: row-reverse;" if is_ar else ""}
    }}
    .notif-title {{
        color: #f1f5f9;
        font-size: 15px;
        font-weight: 800;
        letter-spacing: 0.3px;
    }}
    .notif-time {{
        color: #64748b;
        font-size: 11px;
        font-family: 'Orbitron', monospace;
    }}
    .notif-message {{
        color: #cbd5e1;
        font-size: 13.5px;
        line-height: 1.55;
        margin-bottom: 8px;
    }}
    .notif-badges {{
        display: flex;
        gap: 6px;
        flex-wrap: wrap;
        {"flex-direction: row-reverse;" if is_ar else ""}
    }}
    .badge {{
        padding: 3px 10px;
        border-radius: 999px;
        font-family: 'Orbitron', monospace;
        font-weight: 700;
        font-size: 10px;
        letter-spacing: 0.5px;
    }}
    .badge-unread {{
        background: rgba(56,189,248,0.20);
        color: #38bdf8;
        border: 1px solid rgba(56,189,248,0.50);
    }}
    .badge-read {{
        background: rgba(148,163,184,0.15);
        color: #94a3b8;
        border: 1px solid rgba(148,163,184,0.35);
    }}
    .badge-archived {{
        background: rgba(168,85,247,0.15);
        color: #c084fc;
        border: 1px solid rgba(168,85,247,0.40);
    }}

    .stButton > button {{
        background: linear-gradient(135deg, #0ea5e9 0%, #7c3aed 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 9px 14px !important;
        font-weight: 700 !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-size: 13px !important;
        min-height: 38px !important;
        transition: 0.25s ease !important;
    }}
    .stButton > button:hover {{
        transform: translateY(-2px) !important;
    }}
    </style>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# Main Render
# ═══════════════════════════════════════════════════════════════════════════

def render_notifications():
    init_language()
    apply_rtl_css()

    if not st.session_state.get("logged_in", False):
        st.session_state.page = "login"
        st.rerun()

    user_id = st.session_state.get("user", "anonymous")

    _apply_css()

    notifs = _get_user_notifs(user_id)

    # Auto-seed welcome notification if first visit
    if not notifs and not st.session_state.get("_notif_seeded"):
        add_notification(
            user_id,
            "Welcome to OMNIX VISION! 🎉",
            "Your notifications center is ready. New alerts will appear here.",
            "success",
        )
        notifs = _get_user_notifs(user_id)
        st.session_state._notif_seeded = True

    # ── Hero ──────────────────────────────────────────────────────────────
    unread_count = sum(1 for n in notifs if n["status"] == "unread")
    bell_icon = "🔔" if unread_count else "🔕"

    st.markdown(f"""
<div class="hero">
<h1>{bell_icon} {_t('notif_title')}</h1>
<p>{_t('notif_subtitle')}</p>
</div>
    """, unsafe_allow_html=True)

    # ── Back ──────────────────────────────────────────────────────────────
    back_col, _ = st.columns([1.3, 8])
    with back_col:
        if st.button(t("back"), use_container_width=True, key="notif_back_btn"):
            st.session_state.page = "home"
            st.rerun()

    # ── Metrics ───────────────────────────────────────────────────────────
    total = len(notifs)
    read_count    = sum(1 for n in notifs if n["status"] == "read")
    arch_count    = sum(1 for n in notifs if n["status"] == "archived")

    m1, m2, m3, m4 = st.columns(4)
    metrics = [
        (m1, _t("total_notifs"), total,        "#38bdf8", "📋"),
        (m2, _t("unread"),       unread_count, "#a855f7", "🔔"),
        (m3, _t("read"),         read_count,   "#22c55e", "👁️"),
        (m4, _t("archived"),     arch_count,   "#94a3b8", "📦"),
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
    tab_list, tab_create = st.tabs([
        f"📬 {_t('all')}",
        f"➕ {_t('add_notif')}",
    ])

    # ─────────── TAB 1: List & Manage ───────────
    with tab_list:
        # Filters
        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            status_filter = st.selectbox(
                _t("read") + "/" + _t("unread"),
                ["all", "unread", "read", "archived"],
                format_func=lambda x: _t("all") if x == "all" else _t(x),
                key="notif_status_filter",
            )
        with fc2:
            prio_filter = st.selectbox(
                _t("notif_priority"),
                ["all", "info", "success", "warning", "error"],
                format_func=lambda x: _t("all") if x == "all" else
                                       f"{PRIORITY_CONFIG[x]['icon']} {_t(x)}",
                key="notif_prio_filter",
            )
        with fc3:
            st.write("")
            if st.button(_t("mark_all_read"),
                         use_container_width=True,
                         key="notif_mark_all_btn"):
                for n in notifs:
                    if n["status"] == "unread":
                        n["status"] = "read"
                _save_user_notifs(user_id, notifs)
                log_action("notifs_marked_all_read", user_id=user_id,
                           category="data")
                st.rerun()

        # Clear all button (separate row)
        if total > 0:
            if st.button(_t("clear_all"),
                         use_container_width=True,
                         key="notif_clear_all_btn"):
                _save_user_notifs(user_id, [])
                log_action("notifs_cleared", user_id=user_id, category="data",
                           details=f"count={total}")
                st.rerun()

        # Apply filters
        filtered = list(notifs)
        if status_filter != "all":
            filtered = [n for n in filtered if n["status"] == status_filter]
        if prio_filter != "all":
            filtered = [n for n in filtered if n["priority"] == prio_filter]

        # Sort: unread first, then by created_at desc
        filtered.sort(key=lambda n: (n["status"] != "unread", -n["created_at"]))

        st.write("")

        # Render
        if not notifs:
            st.info(_t("no_notifs"))
        elif not filtered:
            st.warning(_t("no_results"))
        else:
            for n in filtered:
                prio_cfg = PRIORITY_CONFIG.get(n["priority"],
                                                PRIORITY_CONFIG["info"])
                status_badge_class = f"badge-{n['status']}"
                time_ago = _time_ago(n["created_at"])

                st.markdown(f"""
<div class="notif-card {n['status']}" style="--prio-color:{prio_cfg['color']};">
<div class="notif-header">
<div class="notif-title">{prio_cfg['icon']} {n['title']}</div>
<div class="notif-time">⏱ {time_ago}</div>
</div>
<div class="notif-message">{n['message']}</div>
<div class="notif-badges">
<span class="badge {status_badge_class}">{_t(n['status'])}</span>
<span class="badge" style="background:{prio_cfg['bg']};color:{prio_cfg['color']};border:1px solid {prio_cfg['color']}66;">{_t(n['priority'])}</span>
</div>
</div>
                """, unsafe_allow_html=True)

                # Action buttons
                ac1, ac2, ac3 = st.columns(3)
                with ac1:
                    if n["status"] == "unread":
                        if st.button(f"👁️ {_t('mark_read')}",
                                     use_container_width=True,
                                     key=f"read_{n['id']}"):
                            n["status"] = "read"
                            _save_user_notifs(user_id, notifs)
                            st.rerun()
                    else:
                        if st.button(f"📩 {_t('mark_unread')}",
                                     use_container_width=True,
                                     key=f"unread_{n['id']}"):
                            n["status"] = "unread"
                            _save_user_notifs(user_id, notifs)
                            st.rerun()
                with ac2:
                    if n["status"] != "archived":
                        if st.button(f"📦 {_t('archive')}",
                                     use_container_width=True,
                                     key=f"arch_{n['id']}"):
                            n["status"] = "archived"
                            _save_user_notifs(user_id, notifs)
                            st.rerun()
                    else:
                        if st.button(f"📤 {_t('unarchive')}",
                                     use_container_width=True,
                                     key=f"unarch_{n['id']}"):
                            n["status"] = "read"
                            _save_user_notifs(user_id, notifs)
                            st.rerun()
                with ac3:
                    if st.button(f"🗑️ {_t('delete')}",
                                 use_container_width=True,
                                 key=f"del_{n['id']}"):
                        notifs = [x for x in notifs if x["id"] != n["id"]]
                        _save_user_notifs(user_id, notifs)
                        log_action("notif_deleted", user_id=user_id,
                                   category="data")
                        st.rerun()

                st.write("")

    # ─────────── TAB 2: Create ───────────
    with tab_create:
        st.markdown(f"### {_t('add_notif')}")

        title_input = st.text_input(_t("notif_title_label"),
                                    key="new_notif_title")
        msg_input   = st.text_area(_t("notif_message"),
                                   key="new_notif_msg",
                                   height=100)
        prio_input  = st.selectbox(
            _t("notif_priority"),
            ["info", "success", "warning", "error"],
            format_func=lambda x: f"{PRIORITY_CONFIG[x]['icon']} {_t(x)}",
            key="new_notif_prio",
        )

        if st.button(_t("create_notif"),
                     use_container_width=True,
                     key="create_notif_btn"):
            if title_input.strip() and msg_input.strip():
                add_notification(user_id, title_input.strip(),
                                 msg_input.strip(), prio_input)
                log_action("notif_created", user_id=user_id, category="data",
                           details=title_input[:40])
                st.success(_t("notif_created"))
                time.sleep(0.5)
                st.rerun()
            else:
                st.warning("⚠️ Title and message required")