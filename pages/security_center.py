"""
═══════════════════════════════════════════════════════════════════════════
OMNIX VISION — Security Center
═══════════════════════════════════════════════════════════════════════════
Provides:
    • Account information display
    • Change password
    • Active session info
    • Delete account
═══════════════════════════════════════════════════════════════════════════
"""

import time
from datetime import datetime
import streamlit as st

from utils.language import t, init_language, apply_rtl_css
from utils.auth     import change_password, get_user_info, delete_user
from utils.activity import log_action


def _format_timestamp(ts):
    """Format unix timestamp to readable date."""
    if not ts:
        return t("never")
    try:
        return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return t("never")


def render_security_center():
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
            radial-gradient(ellipse at 5% 8%, rgba(239,68,68,0.10) 0%, transparent 38%),
            radial-gradient(ellipse at 95% 8%, rgba(56,189,248,0.10) 0%, transparent 38%),
            linear-gradient(160deg, #020617 0%, #0a0a1a 50%, #1a0a0a 100%);
        color: #f8fafc;
        font-family: 'Rajdhani', sans-serif;
    }

    .sec-header {
        background: linear-gradient(135deg, rgba(239,68,68,0.08), rgba(2,6,23,0.95));
        border: 1px solid rgba(239,68,68,0.30);
        border-radius: 24px;
        padding: 28px 32px;
        text-align: center;
        margin-bottom: 24px;
    }
    .sec-header h1 {
        font-family: 'Orbitron', monospace;
        font-size: 36px;
        font-weight: 900;
        margin: 0;
        background: linear-gradient(90deg, #ef4444, #f97316, #ef4444);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: secShimmer 4s linear infinite;
    }
    @keyframes secShimmer { to { background-position: 200% center; } }
    .sec-header p {
        color: #94a3b8;
        margin-top: 8px;
        font-size: 15px;
    }

    .info-card {
        background: linear-gradient(145deg, rgba(2,6,23,0.95), rgba(15,23,42,0.75));
        border: 1px solid rgba(56,189,248,0.20);
        border-radius: 20px;
        padding: 22px 24px;
        margin-bottom: 16px;
    }
    .info-card h3 {
        font-family: 'Orbitron', monospace;
        color: #38bdf8;
        font-size: 14px;
        letter-spacing: 2px;
        margin: 0 0 14px 0;
        text-transform: uppercase;
        border-left: 3px solid #38bdf8;
        padding-left: 10px;
    }
    .info-row {
        display: flex;
        justify-content: space-between;
        padding: 8px 0;
        border-bottom: 1px solid rgba(56,189,248,0.10);
        font-family: 'Rajdhani', sans-serif;
    }
    .info-row:last-child { border-bottom: none; }
    .info-key {
        color: #94a3b8;
        font-size: 13px;
        letter-spacing: 0.5px;
    }
    .info-value {
        color: #f1f5f9;
        font-weight: 600;
        font-size: 13px;
    }

    .danger-card {
        background: linear-gradient(145deg, rgba(40,10,15,0.95), rgba(15,23,42,0.75));
        border: 1px solid rgba(239,68,68,0.35);
        border-radius: 20px;
        padding: 22px 24px;
        margin-bottom: 16px;
    }
    .danger-card h3 {
        font-family: 'Orbitron', monospace;
        color: #ef4444;
        font-size: 14px;
        letter-spacing: 2px;
        margin: 0 0 14px 0;
        text-transform: uppercase;
        border-left: 3px solid #ef4444;
        padding-left: 10px;
    }
    .danger-warn {
        color: #fb7185;
        background: rgba(239,68,68,0.10);
        border: 1px solid rgba(239,68,68,0.25);
        border-radius: 10px;
        padding: 10px 14px;
        font-size: 13px;
        margin-bottom: 12px;
    }

    .stButton > button {
        background: linear-gradient(135deg, #0ea5e9 0%, #7c3aed 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 10px 20px !important;
        font-weight: 700 !important;
        font-family: 'Rajdhani', sans-serif !important;
        letter-spacing: 0.5px !important;
        box-shadow: 0 4px 14px rgba(14,165,233,0.20) !important;
        transition: 0.28s ease !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(124,58,237,0.35) !important;
    }
    .stButton > button[kind="secondary"] {
        background: linear-gradient(135deg, #ef4444 0%, #991b1b 100%) !important;
        box-shadow: 0 4px 14px rgba(239,68,68,0.20) !important;
    }

    .stTextInput input, .stTextInput input[type="password"] {
        background: rgba(2,6,23,0.55) !important;
        border: 1px solid rgba(56,189,248,0.25) !important;
        border-radius: 10px !important;
        color: #f8fafc !important;
        padding: 10px 12px !important;
        font-family: 'Rajdhani', sans-serif !important;
    }
    .stTextInput input:focus {
        border-color: rgba(56,189,248,0.65) !important;
        box-shadow: 0 0 0 2px rgba(56,189,248,0.10) !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── Header ────────────────────────────────────────────────────────────
    st.markdown(f"""
<div class="sec-header">
<h1>&#128737;&#65039; {t("security_title")}</h1>
<p>{t("security_subtitle")}</p>
</div>
    """, unsafe_allow_html=True)

    # ── Back Button ───────────────────────────────────────────────────────
    if st.button(t("back"), key="sec_back_btn"):
        st.session_state.page = "home"
        st.rerun()

    user_id = st.session_state.get("user")
    if not user_id:
        st.warning(t("access_denied"))
        return

    user_info = get_user_info(user_id) or {}

    # ══════════════════════════════════════════════════════════════════════
    # Section 1 : Account Information
    # ══════════════════════════════════════════════════════════════════════
    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.markdown(f"<h3>&#128100; {t('account_info')}</h3>", unsafe_allow_html=True)

    info_rows = [
        (t("user_id"),           str(user_id)),
        (t("username"),          user_info.get("username", "—")),
        (t("account_created"),   _format_timestamp(user_info.get("created_at"))),
        (t("last_login_label"),  _format_timestamp(user_info.get("last_login"))),
    ]
    for key, value in info_rows:
        st.markdown(
            f'<div class="info-row">'
            f'<span class="info-key">{key}</span>'
            f'<span class="info-value">{value}</span>'
            f'</div>',
            unsafe_allow_html=True
        )
    st.markdown('</div>', unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════
    # Section 2 : Active Session
    # ══════════════════════════════════════════════════════════════════════
    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.markdown(f"<h3>&#128274; {t('session_info')}</h3>", unsafe_allow_html=True)

    session_rows = [
        (t("status"),         t("active_session")),
        (t("language"),       st.session_state.get("language", "English")),
        (t("login_method"),   st.session_state.get("login_method", "password")),
    ]
    for key, value in session_rows:
        st.markdown(
            f'<div class="info-row">'
            f'<span class="info-key">{key}</span>'
            f'<span class="info-value">{value}</span>'
            f'</div>',
            unsafe_allow_html=True
        )
    st.markdown('</div>', unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════
    # Section 3 : Change Password
    # ══════════════════════════════════════════════════════════════════════
    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.markdown(f"<h3>&#128273; {t('change_password')}</h3>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        old_pw = st.text_input(t("old_password"), type="password", key="sec_old_pw")
        new_pw = st.text_input(t("new_password"), type="password", key="sec_new_pw")
    with col2:
        confirm_pw = st.text_input(t("confirm_password"), type="password", key="sec_confirm_pw")
        st.write("")  # spacer
        if st.button(f"&#128273; {t('change_password')}", key="sec_change_pw_btn",
                     use_container_width=True):

            if not old_pw or not new_pw or not confirm_pw:
                st.error(t("error") + ": " + t("password") + " ✗")
            elif new_pw != confirm_pw:
                st.error(t("passwords_dont_match"))
            elif len(new_pw) < 4:
                st.error(t("password_too_short"))
            else:
                success, msg = change_password(user_id, old_pw, new_pw)
                if success:
                    log_action("password_changed", user_id=user_id, category="security")
                    st.success(t("password_changed"))
                    time.sleep(1.2)
                    st.rerun()
                else:
                    st.error(msg)

    # ══════════════════════════════════════════════════════════════════════
    # Section 4 : Danger Zone - Delete Account
    # ══════════════════════════════════════════════════════════════════════
    st.markdown('<div class="danger-card">', unsafe_allow_html=True)
    st.markdown(f"<h3>&#9888;&#65039; {t('delete_account')}</h3>", unsafe_allow_html=True)
    st.markdown(f'<div class="danger-warn">{t("delete_warning")}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    del_pw = st.text_input(t("confirm_delete"), type="password", key="sec_del_pw")

    confirm_check = st.checkbox(
        f"{t('confirm')}: {t('delete_warning')}",
        key="sec_del_confirm"
    )

    if st.button(f"&#128465;&#65039; {t('delete_account')}",
                 key="sec_del_btn",
                 type="secondary",
                 disabled=not confirm_check):

        if not del_pw:
            st.error(t("password") + " ✗")
        else:
            success, msg = delete_user(user_id, del_pw)
            if success:
                log_action("account_deleted", user_id=user_id, category="security",
                           details="Account permanently deleted")
                st.success(t("account_deleted"))
                # Clear session
                for k in ("logged_in", "user", "page"):
                    st.session_state[k] = False if k == "logged_in" else None
                st.session_state.page = "login"
                time.sleep(1.5)
                st.rerun()
            else:
                st.error(msg)