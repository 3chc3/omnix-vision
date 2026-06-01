"""
═══════════════════════════════════════════════════════════════════════════
OMNIX VISION — Settings Page (Phase 2)
═══════════════════════════════════════════════════════════════════════════
Phase-2 changes:
    ✓ Uses utils/language.py instead of separate T dict
    ✓ Uses st.session_state.language (unified with rest of app)
    ✓ Integrates with auth.py (change_password)
    ✓ Quick links to Security Center & Activity Log
    ✓ Logs config changes to activity_log
═══════════════════════════════════════════════════════════════════════════
"""

import streamlit as st

from utils.language import t, init_language, apply_rtl_css, render_language_selector, is_rtl
from utils.auth     import change_password, get_user_info
from utils.activity import log_action


# ═══════════════════════════════════════════════════════════════════════════
# Settings-specific translation extensions (only what's not already in language.py)
# ═══════════════════════════════════════════════════════════════════════════
SETTINGS_KEYS = {
    "hero_title":        {"en": "Settings ⚙️",                                       "ar": "الإعدادات ⚙️"},
    "hero_sub":          {"en": "Manage your account, preferences, and system options.",
                          "ar": "إدارة حسابك وتفضيلاتك وخيارات النظام."},
    "account_section":   {"en": "👤 Account Settings",                              "ar": "👤 إعدادات الحساب"},
    "display_section":   {"en": "🎨 Display Settings",                              "ar": "🎨 إعدادات العرض"},
    "session_section":   {"en": "🔒 Session & Security",                            "ar": "🔒 الجلسة والأمان"},
    "shortcuts_section": {"en": "🚀 Quick Shortcuts",                               "ar": "🚀 اختصارات سريعة"},
    "info_section":      {"en": "ℹ️ System Info",                                   "ar": "ℹ️ معلومات النظام"},
    "language_section":  {"en": "🌐 Language",                                      "ar": "🌐 اللغة"},
    "density_label":     {"en": "Layout Density",                                   "ar": "كثافة التخطيط"},
    "comfortable":       {"en": "Comfortable",                                      "ar": "مريح"},
    "compact":           {"en": "Compact",                                          "ar": "مضغوط"},
    "enable_animations": {"en": "Enable Animations",                                "ar": "تفعيل الحركات"},
    "save_display":      {"en": "💾 Save Display Settings",                         "ar": "💾 حفظ إعدادات العرض"},
    "auto_logout":       {"en": "Auto-logout on close",                             "ar": "تسجيل خروج تلقائي عند الإغلاق"},
    "show_activity_ind": {"en": "Show activity indicator",                          "ar": "إظهار مؤشر النشاط"},
    "logout_now":        {"en": "🚪 Logout Now",                                    "ar": "🚪 تسجيل الخروج الآن"},
    "version_label":     {"en": "Version",                                          "ar": "الإصدار"},
    "platform_label":    {"en": "Platform",                                         "ar": "المنصة"},
    "go_to_security":    {"en": "🛡️ Open Security Center",                          "ar": "🛡️ فتح مركز الأمان"},
    "go_to_activity":    {"en": "📋 Open Activity Log",                             "ar": "📋 فتح سجل النشاط"},
    "security_hint":     {"en": "Manage password and account from Security Center.",
                          "ar": "إدارة كلمة المرور والحساب من مركز الأمان."},
    "display_saved":     {"en": "✅ Display settings saved.",                       "ar": "✅ تم حفظ إعدادات العرض."},
    "quick_change_pw":   {"en": "Quick Change Password",                            "ar": "تغيير سريع لكلمة المرور"},
}


def _tt(key: str) -> str:
    """Settings-specific translate helper (falls back to global t)."""
    from utils.language import get_language_code
    lang = get_language_code()
    if key in SETTINGS_KEYS:
        return SETTINGS_KEYS[key].get(lang, SETTINGS_KEYS[key].get("en", key))
    return t(key)


# ═══════════════════════════════════════════════════════════════════════════
# Main Render
# ═══════════════════════════════════════════════════════════════════════════
def render_settings():
    init_language()
    apply_rtl_css()

    # ── Auth Guard ────────────────────────────────────────────────────────
    if not st.session_state.get("logged_in", False):
        st.session_state.page = "login"
        st.rerun()

    # ── Init Display Defaults ─────────────────────────────────────────────
    st.session_state.setdefault("layout_density",     "Comfortable")
    st.session_state.setdefault("animations_enabled", True)
    st.session_state.setdefault("auto_logout_pref",   False)
    st.session_state.setdefault("show_activity_pref", True)

    is_ar = is_rtl()

    # ──────────────────────────────────────────────────────────────────────
    # CSS
    # ──────────────────────────────────────────────────────────────────────
    st.markdown(f"""
    <style>
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
    }}

    .top-bar {{
        background: rgba(15,23,42,0.82);
        border: 1px solid rgba(56,189,248,0.28);
        border-radius: 18px;
        padding: 14px 18px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 18px;
        box-shadow: 0 0 28px rgba(56,189,248,0.10);
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

    .hero {{
        background:
            radial-gradient(circle at top, rgba(168,85,247,0.16), transparent 38%),
            linear-gradient(135deg, rgba(15,23,42,0.96), rgba(8,47,73,0.58));
        border: 1px solid rgba(56,189,248,0.38);
        border-radius: 32px;
        padding: 38px 28px;
        text-align: center;
        box-shadow: 0 0 48px rgba(56,189,248,0.16);
        margin-bottom: 24px;
    }}
    .hero h1 {{
        color: #c084fc;
        font-size: 42px;
        font-weight: 950;
        margin: 0;
        text-shadow: 0 0 24px rgba(192,132,252,0.42);
    }}
    .hero p {{ color: #cbd5e1; margin-top: 12px; font-size: 15px; }}

    .panel {{
        background: linear-gradient(145deg, rgba(15,23,42,0.92), rgba(2,6,23,0.78));
        border: 1px solid rgba(56,189,248,0.28);
        border-radius: 24px;
        padding: 24px;
        margin-bottom: 18px;
        box-shadow: 0 0 25px rgba(56,189,248,0.08);
    }}
    .panel-title {{
        color: #22d3ee;
        font-size: 18px;
        font-weight: 950;
        margin-bottom: 16px;
        {"text-align: right;" if is_ar else ""}
    }}

    .line {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid rgba(148,163,184,0.11);
        padding: 9px 0;
        gap: 12px;
        {"flex-direction: row-reverse;" if is_ar else ""}
    }}
    .line span:first-child {{ color: #94a3b8; font-weight: 760; }}
    .line span:last-child  {{ color: #38bdf8; font-weight: 950; }}

    .hint-box {{
        background: rgba(56,189,248,0.07);
        border: 1px solid rgba(56,189,248,0.18);
        border-radius: 12px;
        padding: 10px 14px;
        color: #7dd3fc;
        font-size: 13px;
        margin-top: 8px;
        {"text-align: right;" if is_ar else ""}
    }}

    .stButton > button {{
        background: linear-gradient(135deg, #0ea5e9 0%, #7c3aed 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 14px !important;
        padding: 12px 18px !important;
        font-weight: 700 !important;
        font-family: 'Rajdhani', sans-serif !important;
        min-height: 46px;
        box-shadow: 0 4px 18px rgba(14,165,233,0.18) !important;
        transition: 0.25s ease !important;
    }}
    .stButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 28px rgba(124,58,237,0.35) !important;
    }}
    .stButton > button[kind="secondary"] {{
        background: linear-gradient(135deg, #ef4444 0%, #991b1b 100%) !important;
        box-shadow: 0 4px 18px rgba(239,68,68,0.20) !important;
    }}

    .stTextInput > div > div > input {{
        background: rgba(2,6,23,0.84) !important;
        color: #e0f2fe !important;
        border: 1px solid rgba(56,189,248,0.35) !important;
        border-radius: 14px !important;
        padding: 12px 14px !important;
        {"direction: rtl; text-align: right;" if is_ar else ""}
    }}

    label[data-testid="stWidgetLabel"] p {{
        {"direction: rtl; text-align: right;" if is_ar else ""}
        color: #a5f3fc !important;
        font-weight: 800 !important;
    }}
    </style>
    """, unsafe_allow_html=True)

    # ──────────────────────────────────────────────────────────────────────
    # Top Bar
    # ──────────────────────────────────────────────────────────────────────
    st.markdown(f"""
<div class="top-bar">
<div class="top-title">{t("neon_ui")}</div>
<div class="top-badge">{t("settings")}</div>
</div>
    """, unsafe_allow_html=True)

    # ──────────────────────────────────────────────────────────────────────
    # Hero
    # ──────────────────────────────────────────────────────────────────────
    st.markdown(f"""
<div class="hero">
<h1>{_tt("hero_title")}</h1>
<p>{_tt("hero_sub")}</p>
</div>
    """, unsafe_allow_html=True)

    # ──────────────────────────────────────────────────────────────────────
    # Back Button
    # ──────────────────────────────────────────────────────────────────────
    back_col, _ = st.columns([1.3, 8])
    with back_col:
        if st.button(t("back"), use_container_width=True, key="settings_back_btn"):
            st.session_state.page = "home"
            st.rerun()

    st.write("")

    # Get current user info
    user_id   = st.session_state.get("user", "anonymous")
    user_info = get_user_info(user_id) if user_id else {}
    cur_username = (user_info or {}).get("username", user_id)

    # ══════════════════════════════════════════════════════════════════════
    # Row 1 : Account + Quick Shortcuts  |  Language
    # ══════════════════════════════════════════════════════════════════════
    col_left, col_right = st.columns([1.3, 0.9])

    # ── Account Panel ─────────────────────────────────────────────────────
    with col_left:
        st.markdown(f'<div class="panel">'
                    f'<div class="panel-title">{_tt("account_section")}</div>',
                    unsafe_allow_html=True)

        st.markdown(f"""
<div class="line"><span>{t("user_id")}</span><span>{user_id}</span></div>
<div class="line"><span>{t("username")}</span><span>{cur_username}</span></div>
        """, unsafe_allow_html=True)

        st.markdown(
            f'<div class="hint-box">💡 {_tt("security_hint")}</div>',
            unsafe_allow_html=True
        )

        # Quick change password (also available in Security Center)
        with st.expander(f"🔑 {_tt('quick_change_pw')}"):
            old_pw = st.text_input(t("old_password"), type="password",
                                    key="set_old_pw")
            new_pw = st.text_input(t("new_password"), type="password",
                                    key="set_new_pw")
            confirm_pw = st.text_input(t("confirm_password"), type="password",
                                        key="set_confirm_pw")

            if st.button(t("save"), use_container_width=True, key="set_change_pw_btn"):
                if not old_pw or not new_pw or not confirm_pw:
                    st.error(f"❌ {t('password')} ✗")
                elif new_pw != confirm_pw:
                    st.error(f"❌ {t('passwords_dont_match')}")
                elif len(new_pw) < 4:
                    st.error(f"❌ {t('password_too_short')}")
                else:
                    success, msg = change_password(user_id, old_pw, new_pw)
                    if success:
                        log_action("password_changed_from_settings",
                                   user_id=user_id, category="security")
                        st.success(f"✅ {t('password_changed')}")
                    else:
                        st.error(f"❌ {msg}")

        st.markdown("</div>", unsafe_allow_html=True)

        # ── Quick Shortcuts Panel ─────────────────────────────────────────
        st.markdown(f'<div class="panel">'
                    f'<div class="panel-title">{_tt("shortcuts_section")}</div>',
                    unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        sc1, sc2 = st.columns(2)
        with sc1:
            if st.button(_tt("go_to_security"), use_container_width=True,
                         key="goto_security_btn"):
                log_action("open_security_center",
                           user_id=user_id, category="navigation")
                st.session_state.page = "security_center"
                st.rerun()
        with sc2:
            if st.button(_tt("go_to_activity"), use_container_width=True,
                         key="goto_activity_btn"):
                log_action("open_activity_log",
                           user_id=user_id, category="navigation")
                st.session_state.page = "activity_log"
                st.rerun()

    # ── Language + Display Panels ─────────────────────────────────────────
    with col_right:
        st.markdown(f'<div class="panel">'
                    f'<div class="panel-title">{_tt("language_section")}</div>',
                    unsafe_allow_html=True)
        render_language_selector("settings_language_selector")
        st.markdown("</div>", unsafe_allow_html=True)

        # ── Display Panel ─────────────────────────────────────────────────
        st.markdown(f'<div class="panel">'
                    f'<div class="panel-title">{_tt("display_section")}</div>',
                    unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        density_options = [_tt("comfortable"), _tt("compact")]
        cur_density_idx = 0 if st.session_state.layout_density == "Comfortable" else 1

        density = st.selectbox(
            _tt("density_label"),
            density_options,
            index=cur_density_idx,
            key="settings_density_select"
        )

        animations = st.toggle(
            _tt("enable_animations"),
            value=st.session_state.animations_enabled,
            key="settings_anim_toggle"
        )

        if st.button(_tt("save_display"), use_container_width=True,
                     key="save_display_btn"):
            st.session_state.layout_density = (
                "Comfortable" if density == density_options[0] else "Compact"
            )
            st.session_state.animations_enabled = animations
            log_action("display_settings_saved",
                       user_id=user_id, category="system",
                       details=f"density={density}, anim={animations}")
            st.success(f"✅ {_tt('display_saved')}")

    # ══════════════════════════════════════════════════════════════════════
    # Row 2 : Session  |  System Info
    # ══════════════════════════════════════════════════════════════════════
    col_session, col_info = st.columns(2)

    # ── Session Panel ─────────────────────────────────────────────────────
    with col_session:
        st.markdown(f'<div class="panel">'
                    f'<div class="panel-title">{_tt("session_section")}</div>',
                    unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.toggle(
            _tt("auto_logout"),
            value=st.session_state.auto_logout_pref,
            key="set_auto_logout_toggle"
        )
        st.toggle(
            _tt("show_activity_ind"),
            value=st.session_state.show_activity_pref,
            key="set_show_activity_toggle"
        )

        st.write("")

        if st.button(_tt("logout_now"), use_container_width=True,
                     type="secondary", key="settings_logout_btn"):
            log_action("logout", user_id=user_id, category="auth")
            # Clear sensitive session keys but keep language preference
            preserved_lang = st.session_state.get("language", "English")
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.session_state.language  = preserved_lang
            st.session_state.page      = "login"
            st.session_state.logged_in = False
            st.rerun()

    # ── System Info Panel ─────────────────────────────────────────────────
    with col_info:
        lang_display = st.session_state.get("language", "English")

        st.markdown(f"""
<div class="panel">
<div class="panel-title">{_tt("info_section")}</div>
<div class="line"><span>{_tt("version_label")}</span><span>v2.0</span></div>
<div class="line"><span>{_tt("platform_label")}</span><span>{t("app_name")}</span></div>
<div class="line"><span>{t("language")}</span><span>{lang_display}</span></div>
<div class="line"><span>{t("user_id")}</span><span>{user_id}</span></div>
<div class="line"><span>{t("username")}</span><span>{cur_username}</span></div>
</div>
        """, unsafe_allow_html=True)