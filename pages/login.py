"""
═══════════════════════════════════════════════════════════════════════════
OMNIX VISION — Login Page (Phase 2)
═══════════════════════════════════════════════════════════════════════════
Phase-2 changes:
    ✓ FIXED label_visibility warning (no more empty labels)
    ✓ Connected to auth.py (hashed passwords + brute-force protection)
    ✓ Added Register tab (Create New Account)
    ✓ Uses utils/language.py for translations
    ✓ Logs all login attempts to activity_log
═══════════════════════════════════════════════════════════════════════════
"""

import time
import streamlit as st

# ── Safe imports (styles are optional) ─────────────────────────────────────
try:
    from styles.base_theme        import apply_base_theme
    from styles.neon_cyber_theme  import apply_neon_cyber_theme
    _HAS_STYLES = True
except ImportError:
    _HAS_STYLES = False
    def apply_base_theme():            pass
    def apply_neon_cyber_theme(*a, **k): pass

from utils.language import t, init_language, apply_rtl_css, render_language_selector
from utils.auth     import login_user, register_user
from utils.activity import log_action


# ══════════════════════════════════════════════════════════════════════════
# CSS
# ══════════════════════════════════════════════════════════════════════════

def apply_login_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@400;600;700&display=swap');

    [data-testid="stSidebar"], [data-testid="collapsedControl"] { display: none; }

    /* ── Base ── */
    .stApp {
        background:
            radial-gradient(ellipse at 15% 10%, rgba(56,189,248,0.12) 0%, transparent 42%),
            radial-gradient(ellipse at 85% 8%,  rgba(168,85,247,0.12) 0%, transparent 42%),
            radial-gradient(ellipse at 50% 95%, rgba(34,197,94,0.07)  0%, transparent 38%),
            linear-gradient(160deg, #020617 0%, #060d1f 55%, #0a0520 100%);
        font-family: 'Rajdhani', sans-serif;
    }
    .stApp::before {
        content: '';
        position: fixed; inset: 0;
        background-image: radial-gradient(rgba(56,189,248,0.06) 1px, transparent 1px);
        background-size: 36px 36px;
        pointer-events: none; z-index: 0;
    }

    /* ── Portal Header ── */
    .login-header {
        position: relative;
        background: linear-gradient(135deg, rgba(2,6,23,0.97), rgba(15,23,42,0.75));
        border: 1px solid rgba(56,189,248,0.28);
        border-radius: 28px;
        padding: 36px 32px;
        text-align: center;
        overflow: hidden;
        margin-bottom: 28px;
    }
    .login-header::before {
        content: '';
        position: absolute; top: -60px; left: 50%; transform: translateX(-50%);
        width: 440px; height: 140px;
        background: radial-gradient(ellipse, rgba(56,189,248,0.18), transparent 70%);
        pointer-events: none;
    }
    .login-header::after {
        content: '';
        position: absolute; bottom: 0; left: 0; right: 0; height: 2px;
        background: linear-gradient(90deg, transparent, rgba(56,189,248,0.70), rgba(168,85,247,0.60), transparent);
        animation: scanline 3.5s linear infinite;
    }
    @keyframes scanline { 0%,100%{opacity:0.35} 50%{opacity:1} }

    .login-header-icon {
        font-size: 54px; display: block; margin-bottom: 12px;
        filter: drop-shadow(0 0 20px rgba(56,189,248,0.65));
        animation: iconFloat 3.2s ease-in-out infinite;
    }
    @keyframes iconFloat { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-7px)} }

    .login-header h1 {
        font-family: 'Orbitron', monospace;
        font-size: 32px; font-weight: 900; margin: 0; letter-spacing: 3px;
        background: linear-gradient(90deg, #38bdf8, #a855f7, #38bdf8);
        background-size: 200% auto;
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: shimmer 4.5s linear infinite;
    }
    @keyframes shimmer { to { background-position: 200% center; } }

    .login-header p {
        color: #475569; font-size: 13px; margin-top: 10px;
        font-family: 'Rajdhani', sans-serif; letter-spacing: 1.5px;
    }
    .login-header-pills {
        display: flex; justify-content: center; gap: 10px; margin-top: 16px; flex-wrap: wrap;
    }
    .login-pill {
        background: rgba(56,189,248,0.07); border: 1px solid rgba(56,189,248,0.20);
        border-radius: 999px; padding: 5px 14px;
        font-size: 11px; color: #7dd3fc;
        font-family: 'Orbitron', monospace; letter-spacing: 1px;
    }

    /* ── Method Selector Cards ── */
    .method-card {
        position: relative;
        background: linear-gradient(145deg, rgba(2,6,23,0.97), rgba(15,23,42,0.78));
        border: 1px solid rgba(56,189,248,0.18);
        border-radius: 24px;
        padding: 28px 20px 22px;
        text-align: center;
        min-height: 200px;
        overflow: hidden;
        transition: all 0.35s cubic-bezier(0.34,1.56,0.64,1);
        margin-bottom: 10px;
    }
    .method-card::before {
        content: '';
        position: absolute; top: 0; left: 0; right: 0; height: 2px;
        opacity: 0; transition: opacity 0.35s;
    }
    .method-card:hover { transform: translateY(-8px) scale(1.015); }
    .method-card:hover::before { opacity: 1; }

    .mc-blue:hover   { border-color: rgba(56,189,248,0.65); box-shadow: 0 16px 44px rgba(56,189,248,0.16); }
    .mc-purple:hover { border-color: rgba(168,85,247,0.65); box-shadow: 0 16px 44px rgba(168,85,247,0.16); }
    .mc-green:hover  { border-color: rgba(34,197,94,0.65);  box-shadow: 0 16px 44px rgba(34,197,94,0.16); }

    .mc-blue::before   { background: linear-gradient(90deg, transparent, #38bdf8, transparent); }
    .mc-purple::before { background: linear-gradient(90deg, transparent, #a855f7, transparent); }
    .mc-green::before  { background: linear-gradient(90deg, transparent, #22c55e, transparent); }

    .method-icon {
        font-size: 48px; display: block; margin-bottom: 14px;
        filter: drop-shadow(0 0 14px rgba(56,189,248,0.40));
        transition: transform 0.3s;
    }
    .method-card:hover .method-icon { transform: scale(1.12); }

    .method-title {
        font-family: 'Orbitron', monospace; font-size: 14px; font-weight: 700;
        color: #f1f5f9; margin-bottom: 8px; letter-spacing: 1px;
    }
    .method-desc {
        color: #64748b; font-size: 12.5px; line-height: 1.65;
        font-family: 'Rajdhani', sans-serif;
    }

    /* ── Credentials Form ── */
    .creds-card {
        background: linear-gradient(145deg, rgba(2,6,23,0.97), rgba(15,23,42,0.80));
        border: 1px solid rgba(56,189,248,0.22);
        border-radius: 26px;
        padding: 28px 30px;
        max-width: 500px;
        margin: 0 auto;
    }
    .creds-title {
        font-family: 'Orbitron', monospace; font-size: 18px; font-weight: 700;
        color: #38bdf8; letter-spacing: 2px; margin-bottom: 6px; text-align: center;
    }
    .creds-sub {
        color: #475569; font-size: 13px; text-align: center;
        font-family: 'Rajdhani', sans-serif; letter-spacing: 1px; margin-bottom: 20px;
    }

    /* ── Streamlit Tabs Styling ── */
    div[data-testid="stTabs"] {
        max-width: 500px;
        margin: 0 auto 18px auto;
    }
    div[data-baseweb="tab-list"] {
        background: rgba(2,6,23,0.55) !important;
        border-radius: 14px !important;
        padding: 4px !important;
        border: 1px solid rgba(56,189,248,0.20) !important;
        gap: 4px;
    }
    button[data-baseweb="tab"] {
        background: transparent !important;
        border-radius: 10px !important;
        font-family: 'Orbitron', monospace !important;
        font-weight: 700 !important;
        font-size: 12px !important;
        letter-spacing: 1.5px !important;
        color: #64748b !important;
        padding: 10px 16px !important;
        flex: 1 !important;
        justify-content: center !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #0ea5e9 0%, #7c3aed 100%) !important;
        color: white !important;
        box-shadow: 0 4px 14px rgba(56,189,248,0.20) !important;
    }
    div[data-baseweb="tab-highlight"] { display: none !important; }

    /* ── Inputs ── */
    div.stTextInput > div > div > input {
        background: rgba(56,189,248,0.05) !important;
        border: 1px solid rgba(56,189,248,0.22) !important;
        border-radius: 14px !important;
        color: #e0f2fe !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-size: 15px !important; padding: 11px 16px !important;
    }
    div.stTextInput > div > div > input:focus {
        border-color: rgba(56,189,248,0.60) !important;
        box-shadow: 0 0 18px rgba(56,189,248,0.12) !important;
    }
    div.stTextInput > div > div > input::placeholder { color: #334155 !important; }

    /* Hide label text but keep accessibility (when label_visibility="collapsed") */
    label[data-testid="stWidgetLabel"] {
        font-family: 'Orbitron', monospace !important;
        color: #7dd3fc !important;
        font-size: 11px !important;
        letter-spacing: 2px !important;
        text-transform: uppercase !important;
    }

    /* ── Hand Scan Portal ── */
    .scan-portal {
        background: linear-gradient(145deg, rgba(2,6,23,0.97), rgba(15,23,42,0.80));
        border: 1px solid rgba(0,212,255,0.25);
        border-radius: 26px;
        padding: 36px 30px;
        max-width: 500px;
        margin: 0 auto;
        text-align: center;
    }
    .scan-portal-icon {
        font-size: 72px; display: block; margin-bottom: 16px;
        filter: drop-shadow(0 0 22px rgba(0,212,255,0.60));
        animation: iconFloat 3s ease-in-out infinite;
    }
    .scan-portal-title {
        font-family: 'Orbitron', monospace; font-size: 20px; font-weight: 900;
        color: #00d4ff; letter-spacing: 2px; margin-bottom: 8px;
    }
    .scan-portal-desc {
        color: #475569; font-size: 14px; line-height: 1.7;
        font-family: 'Rajdhani', sans-serif; letter-spacing: 0.5px; margin-bottom: 24px;
    }
    .scan-info-row { display: flex; gap: 12px; margin-bottom: 24px; }
    .scan-chip { flex: 1; border-radius: 14px; padding: 12px; }
    .sc-grant { background: rgba(0,230,118,0.08); border: 1px solid rgba(0,230,118,0.25); }
    .sc-deny  { background: rgba(255,82,82,0.08);  border: 1px solid rgba(255,82,82,0.25); }
    .sc-time  { background: rgba(255,213,79,0.08); border: 1px solid rgba(255,213,79,0.25); }
    .sc-chip-label {
        font-family: 'Orbitron', monospace; font-size: 10px; letter-spacing: 1.5px;
        text-transform: uppercase; margin-bottom: 5px; color: #475569;
    }
    .sc-chip-val { font-family: 'Orbitron', monospace; font-size: 15px; font-weight: 700; }

    /* ── Section label ── */
    .section-label {
        font-family: 'Orbitron', monospace; font-size: 11px; color: #334155;
        letter-spacing: 3px; text-transform: uppercase;
        margin: 0 0 14px; padding-left: 10px;
        border-left: 2px solid rgba(56,189,248,0.35);
    }

    /* ── Buttons ── */
    .stButton > button {
        background: linear-gradient(135deg, #0ea5e9 0%, #7c3aed 100%) !important;
        color: white !important; border: none !important;
        border-radius: 14px !important; padding: 12px 20px !important;
        font-weight: 700 !important; font-family: 'Rajdhani', sans-serif !important;
        font-size: 15px !important; min-height: 48px !important;
        letter-spacing: 0.5px !important; transition: 0.28s ease !important;
        box-shadow: 0 4px 18px rgba(14,165,233,0.18) !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 28px rgba(124,58,237,0.35) !important;
    }

    /* ── User ID Display (after registration) ── */
    .user-id-banner {
        background: linear-gradient(135deg, rgba(34,197,94,0.12), rgba(56,189,248,0.10));
        border: 2px solid rgba(34,197,94,0.45);
        border-radius: 16px;
        padding: 18px 22px;
        text-align: center;
        margin: 16px auto;
        max-width: 500px;
        font-family: 'Orbitron', monospace;
        box-shadow: 0 0 25px rgba(34,197,94,0.15);
    }
    .user-id-label {
        color: #94a3b8;
        font-size: 11px;
        letter-spacing: 2px;
        margin-bottom: 6px;
    }
    .user-id-value {
        color: #22c55e;
        font-size: 36px;
        font-weight: 900;
        letter-spacing: 6px;
        text-shadow: 0 0 18px rgba(34,197,94,0.50);
    }
    .user-id-note {
        color: #cbd5e1;
        font-size: 12px;
        font-family: 'Rajdhani', sans-serif;
        margin-top: 8px;
        letter-spacing: 0.5px;
    }
    </style>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# Method Selector
# ══════════════════════════════════════════════════════════════════════════════
def render_login_method_selector():
    st.markdown(f'<div class="section-label">{t("credentials")} / {t("hand_scan")}</div>',
                unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="method-card mc-blue">
            <span class="method-icon">🔑</span>
            <div class="method-title">{t("credentials").upper()}</div>
            <div class="method-desc">Sign in with your User ID and password.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"🔑 {t('login')}", use_container_width=True, key="btn_creds"):
            st.session_state.auth_mode = "credentials"
            st.rerun()

    with col2:
        st.markdown(f"""
        <div class="method-card mc-purple">
            <span class="method-icon">🖐️</span>
            <div class="method-title">{t("hand_scan").upper()}</div>
            <div class="method-desc">Biometric authentication via camera.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"🖐️ {t('hand_scan')}", use_container_width=True, key="btn_hand"):
            st.session_state.auth_mode = "hand_scan"
            st.rerun()

    with col3:
        st.markdown(f"""
        <div class="method-card mc-green">
            <span class="method-icon">🌟</span>
            <div class="method-title">{t("about_us").upper()}</div>
            <div class="method-desc">Learn more about OMNIX VISION.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"🌟 {t('about_us')}", use_container_width=True, key="btn_about"):
            st.session_state.page = "about"
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# Credentials — Login + Register (Tabs)
# ══════════════════════════════════════════════════════════════════════════════
def render_credentials_login():
    _, center, _ = st.columns([1, 2.2, 1])

    with center:
        st.markdown(f"""
        <div class="creds-card">
            <div class="creds-title">🔐 {t("credentials").upper()}</div>
            <div class="creds-sub">{t("select_module")}</div>
        </div>
        """, unsafe_allow_html=True)

        # Two tabs: Login + Register
        tab_login, tab_register = st.tabs([
            f"🔑 {t('login')}",
            f"✨ {t('register')}",
        ])

        # ── Login Tab ─────────────────────────────────────────────────────
        with tab_login:
            user_id = st.text_input(
                t("user_id"),
                placeholder="1234",
                key="login_user_id",
                max_chars=4,
            )
            password = st.text_input(
                t("password"),
                placeholder="••••••••",
                type="password",
                key="login_password",
            )

            c1, c2 = st.columns(2)
            with c1:
                if st.button(f"🚀 {t('login')}",
                             use_container_width=True,
                             key="btn_login_submit"):
                    if not user_id or not password:
                        st.error(f"❌ {t('login_failed')}")
                    else:
                        success, msg = login_user(user_id, password)
                        if success:
                            st.session_state.logged_in    = True
                            st.session_state.user         = user_id
                            st.session_state.page         = "home"
                            st.session_state.login_method = "password"
                            log_action("login_success",
                                       user_id=user_id,
                                       category="auth")
                            st.success(f"✅ {t('login_success')}")
                            time.sleep(0.8)
                            st.rerun()
                        else:
                            log_action("login_failed",
                                       user_id=user_id,
                                       category="auth",
                                       details=msg)
                            st.error(f"❌ {msg}")

            with c2:
                if st.button(f"← {t('back')}",
                             use_container_width=True,
                             key="btn_login_back"):
                    st.session_state.auth_mode = "select"
                    st.rerun()

        # ── Register Tab ──────────────────────────────────────────────────
        with tab_register:
            reg_username = st.text_input(
                t("username"),
                placeholder="alice",
                key="reg_username",
            )
            reg_password = st.text_input(
                t("new_password"),
                placeholder="At least 4 characters",
                type="password",
                key="reg_password",
            )
            reg_confirm = st.text_input(
                t("confirm_password"),
                placeholder="Re-type password",
                type="password",
                key="reg_confirm",
            )

            c1, c2 = st.columns(2)
            with c1:
                if st.button(f"✨ {t('create_account')}",
                             use_container_width=True,
                             key="btn_register_submit"):
                    if not reg_password or not reg_confirm:
                        st.error(f"❌ {t('password')} ✗")
                    elif reg_password != reg_confirm:
                        st.error(f"❌ {t('passwords_dont_match')}")
                    elif len(reg_password) < 4:
                        st.error(f"❌ {t('password_too_short')}")
                    else:
                        success, msg, new_id = register_user(
                            reg_password,
                            username=reg_username or ""
                        )
                        if success and new_id:
                            log_action("user_registered",
                                       user_id=new_id,
                                       category="auth",
                                       details=f"username={reg_username}")
                            # Show ID banner
                            st.session_state.show_new_id = new_id
                            st.rerun()
                        else:
                            st.error(f"❌ {msg}")

            with c2:
                if st.button(f"← {t('back')}",
                             use_container_width=True,
                             key="btn_register_back"):
                    st.session_state.auth_mode = "select"
                    st.rerun()

        # ── After successful registration: show ID banner ─────────────────
        new_id = st.session_state.get("show_new_id")
        if new_id:
            st.markdown(f"""
<div class="user-id-banner">
<div class="user-id-label">🎉 {t("success").upper()} — {t("user_id").upper()}</div>
<div class="user-id-value">{new_id}</div>
<div class="user-id-note">💾 Save this ID! You'll need it to login.</div>
</div>
            """, unsafe_allow_html=True)
            if st.button(f"✓ {t('confirm')}",
                         use_container_width=True,
                         key="btn_clear_new_id"):
                st.session_state.pop("show_new_id", None)
                st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# Hand Scan Portal
# ══════════════════════════════════════════════════════════════════════════════
def render_hand_scan_login():
    _, center, _ = st.columns([1, 2.2, 1])

    with center:
        st.markdown(f"""
        <div class="scan-portal">
            <span class="scan-portal-icon">🖐️</span>
            <div class="scan-portal-title">{t("hand_scan").upper()}</div>
            <div class="scan-portal-desc">
                Use your hand to authenticate with the biometric scanner.<br>
                The camera reads your hand for 5 seconds to determine access.
            </div>
            <div class="scan-info-row">
                <div class="scan-chip sc-grant">
                    <div class="sc-chip-label">{t("right_hand")}</div>
                    <div class="sc-chip-val" style="color:#00e676;">✅ {t("access_granted").upper()}</div>
                </div>
                <div class="scan-chip sc-deny">
                    <div class="sc-chip-label">{t("left_hand")}</div>
                    <div class="sc-chip-val" style="color:#ff5252;">🚫 {t("access_denied").upper()}</div>
                </div>
                <div class="scan-chip sc-time">
                    <div class="sc-chip-label">Scan Time</div>
                    <div class="sc-chip-val" style="color:#ffd54f;">5 SEC</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.write("")
        c1, c2 = st.columns(2)
        with c1:
            if st.button(f"📷 {t('open')} {t('hand_scan')}",
                         use_container_width=True,
                         key="btn_open_scan"):
                log_action("open_hand_scan",
                           user_id=st.session_state.get("user", "anonymous"),
                           category="auth")
                st.session_state.page = "hand_scan"
                st.rerun()
        with c2:
            if st.button(f"← {t('back')}",
                         use_container_width=True,
                         key="btn_scan_back"):
                st.session_state.auth_mode = "select"
                st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# Main Renderer
# ══════════════════════════════════════════════════════════════════════════════
def render_login():
    # Apply themes if available
    if _HAS_STYLES:
        apply_base_theme()
        apply_neon_cyber_theme("", "")

    init_language()
    apply_rtl_css()
    apply_login_css()

    if "auth_mode" not in st.session_state:
        st.session_state.auth_mode = "select"

    # ── Page Header ───────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="login-header">
        <span class="login-header-icon">🔐</span>
        <h1>OMNIX LOGIN PORTAL</h1>
        <p>SECURE ACCESS · BIOMETRIC SUPPORT · MULTI-METHOD AUTH</p>
        <div class="login-header-pills">
            <span class="login-pill">🔑 {t("credentials")}</span>
            <span class="login-pill">🖐️ {t("hand_scan")}</span>
            <span class="login-pill">🔒 SHA-256</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Language Selector (small, in top-right corner) ────────────────────
    _, lang_col = st.columns([5, 1])
    with lang_col:
        render_language_selector("login_language_selector")

    mode = st.session_state.auth_mode

    if mode == "select":
        render_login_method_selector()
    elif mode == "credentials":
        render_credentials_login()
    elif mode == "hand_scan":
        render_hand_scan_login()
    else:
        st.session_state.auth_mode = "select"
        st.rerun()