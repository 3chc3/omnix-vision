"""
═══════════════════════════════════════════════════════════════════════════
OMNIX VISION — About Page (Phase 4)
═══════════════════════════════════════════════════════════════════════════
Phase-4 changes:
    ✓ Full translation (EN/AR + RTL)
    ✓ Activity logging on page view
    ✓ Modular structure with helper functions
    ✓ Project features showcase
    ✓ Tech stack listing
    ✓ Credits & roadmap section
═══════════════════════════════════════════════════════════════════════════
"""

import streamlit as st

from utils.language import t, init_language, apply_rtl_css, is_rtl
from utils.activity import log_action


# ═══════════════════════════════════════════════════════════════════════════
# Local translation extensions (page-specific keys)
# ═══════════════════════════════════════════════════════════════════════════

ABOUT_KEYS = {
    "about_hero_title": {
        "en": "About OMNIX VISION",
        "ar": "حول OMNIX VISION",
    },
    "about_hero_subtitle": {
        "en": "AI-Powered Smart Multimedia Platform — Neon Cyber UI",
        "ar": "منصة وسائط ذكية مدعومة بالذكاء الاصطناعي — واجهة سايبر نيون",
    },
    "what_is_it": {
        "en": "What is OMNIX VISION?",
        "ar": "ما هو OMNIX VISION؟",
    },
    "what_is_it_body": {
        "en": (
            "OMNIX VISION is an intelligent multimedia platform that combines "
            "computer vision, multimedia processing, productivity tools, games, "
            "and an AI assistant — all in one beautiful neon-cyber interface. "
            "Designed to be modular, secure, and offline-first."
        ),
        "ar": (
            "OMNIX VISION منصة وسائط ذكية تجمع بين الرؤية الحاسوبية، معالجة الوسائط، "
            "أدوات الإنتاجية، الألعاب، ومساعد ذكي — كلها في واجهة سايبر نيون جميلة. "
            "مصممة لتكون قابلة للتوسع، آمنة، وتعمل بدون إنترنت."
        ),
    },
    "key_features":     {"en": "Key Features",         "ar": "المميزات الرئيسية"},
    "tech_stack":       {"en": "Technology Stack",     "ar": "التقنيات المستخدمة"},
    "credits":          {"en": "Credits",              "ar": "شكر وتقدير"},
    "roadmap":          {"en": "Roadmap",              "ar": "خارطة الطريق"},
    "modules_count":    {"en": "14 Modules",           "ar": "14 وحدة"},
    "languages_label":  {"en": "EN + AR + RTL",        "ar": "EN + AR + RTL"},
    "offline_label":    {"en": "Offline-First",        "ar": "يعمل دون إنترنت"},
    "secure_label":     {"en": "SHA-256 Secure",       "ar": "آمن بـ SHA-256"},

    # Features
    "feat_ai_camera":      {"en": "🤖 AI Camera + Hand Scan",       "ar": "🤖 كاميرا ذكية + فحص يد"},
    "feat_ai_camera_desc": {"en": "Real-time MediaPipe pose & hand detection", "ar": "كشف حي للوضعية واليد عبر MediaPipe"},
    "feat_media":          {"en": "🎬 Media Studio",                "ar": "🎬 استوديو الوسائط"},
    "feat_media_desc":     {"en": "Convert, filter, crop, resize images", "ar": "تحويل، فلترة، قص، تغيير حجم الصور"},
    "feat_tasks":          {"en": "📝 Smart Task Manager",          "ar": "📝 مدير مهام ذكي"},
    "feat_tasks_desc":     {"en": "Priorities, due dates, Pomodoro, tags", "ar": "أولويات، تواريخ، بومودورو، علامات"},
    "feat_calc":           {"en": "🧮 Advanced Calculator",         "ar": "🧮 حاسبة متقدمة"},
    "feat_calc_desc":      {"en": "Scientific, units, graphs, formulas", "ar": "علمية، وحدات، رسوم، صيغ"},
    "feat_games":          {"en": "🎮 Game Center",                 "ar": "🎮 مركز الألعاب"},
    "feat_games_desc":     {"en": "4 games with persistent high scores", "ar": "4 ألعاب مع حفظ النقاط"},
    "feat_assistant":      {"en": "🧠 AI Assistant",                "ar": "🧠 مساعد ذكي"},
    "feat_assistant_desc": {"en": "18 smart response categories",   "ar": "18 فئة ردود ذكية"},
    "feat_security":       {"en": "🛡️ Security Center",             "ar": "🛡️ مركز الأمان"},
    "feat_security_desc":  {"en": "Password mgmt, audit log",       "ar": "إدارة كلمات المرور، سجل تدقيق"},
    "feat_dashboard":      {"en": "📊 Live Dashboard",              "ar": "📊 لوحة تحكم حية"},
    "feat_dashboard_desc": {"en": "Charts, stats, system health",   "ar": "رسوم، إحصائيات، صحة النظام"},

    # Tech
    "tech_python":   {"en": "Python 3.10+",         "ar": "Python 3.10+"},
    "tech_streamlit":{"en": "Streamlit 1.30+",      "ar": "Streamlit 1.30+"},
    "tech_cv":       {"en": "OpenCV + MediaPipe",   "ar": "OpenCV + MediaPipe"},
    "tech_pillow":   {"en": "Pillow (image proc.)", "ar": "Pillow (معالجة صور)"},
    "tech_plotly":   {"en": "Plotly (charts)",      "ar": "Plotly (رسوم بيانية)"},
    "tech_storage":  {"en": "JSON (persistence)",   "ar": "JSON (تخزين)"},

    # Credits
    "credit_team":   {"en": "Development Team",     "ar": "فريق التطوير"},
    "credit_libs":   {"en": "Open-Source Libraries","ar": "مكتبات مفتوحة المصدر"},
    "credit_fonts":  {"en": "Orbitron + Rajdhani (Google Fonts)", "ar": "Orbitron + Rajdhani (خطوط جوجل)"},
    "thanks_msg":    {"en": "Thank you for using OMNIX VISION! 🚀", "ar": "شكراً لاستخدام OMNIX VISION! 🚀"},

    # Roadmap
    "roadmap_v1":      {"en": "✅ v2.0 — Current Release",       "ar": "✅ v2.0 — الإصدار الحالي"},
    "roadmap_v1_desc": {"en": "14 modules, bilingual, secure",   "ar": "14 وحدة، ثنائي اللغة، آمن"},
    "roadmap_v2":      {"en": "🚧 v2.1 — Planned",               "ar": "🚧 v2.1 — مخطط"},
    "roadmap_v2_desc": {"en": "Cloud sync, mobile responsive",   "ar": "مزامنة سحابية، تجاوب موبايل"},
    "roadmap_v3":      {"en": "💡 v3.0 — Future Vision",         "ar": "💡 v3.0 — رؤية مستقبلية"},
    "roadmap_v3_desc": {"en": "Real AI integration, voice cmds", "ar": "تكامل ذكاء اصطناعي حقيقي، أوامر صوتية"},
}


def _t(key: str) -> str:
    """Page-specific translate helper."""
    from utils.language import get_language_code
    lang = get_language_code()
    if key in ABOUT_KEYS:
        return ABOUT_KEYS[key].get(lang, ABOUT_KEYS[key].get("en", key))
    return t(key)


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
        padding: 14px 18px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 18px;
    }}
    .top-title  {{ color: #e0f2fe; font-weight: 950; font-size: 16px; }}
    .top-badge  {{
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
        padding: 44px 32px;
        text-align: center;
        box-shadow: 0 0 48px rgba(56,189,248,0.16);
        margin-bottom: 24px;
    }}
    .hero h1 {{
        font-family: 'Orbitron', monospace;
        font-size: 46px;
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
        margin-top: 14px;
        font-size: 16px;
        letter-spacing: 0.5px;
    }}
    .hero-pills {{
        display: flex;
        justify-content: center;
        gap: 10px;
        margin-top: 20px;
        flex-wrap: wrap;
    }}
    .hero-pill {{
        background: rgba(56,189,248,0.08);
        border: 1px solid rgba(56,189,248,0.25);
        border-radius: 999px;
        padding: 6px 16px;
        font-size: 12px;
        color: #7dd3fc;
        font-family: 'Orbitron', monospace;
        letter-spacing: 1.5px;
    }}

    .section {{
        background: linear-gradient(145deg, rgba(15,23,42,0.92), rgba(2,6,23,0.78));
        border: 1px solid rgba(56,189,248,0.22);
        border-radius: 24px;
        padding: 26px 28px;
        margin-bottom: 20px;
    }}
    .section-title {{
        font-family: 'Orbitron', monospace;
        color: #22d3ee;
        font-size: 22px;
        font-weight: 900;
        margin: 0 0 14px 0;
        letter-spacing: 1px;
        {"text-align: right;" if is_ar else ""}
    }}
    .section-body {{
        color: #cbd5e1;
        font-size: 14.5px;
        line-height: 1.85;
        {"text-align: right;" if is_ar else ""}
    }}

    .feat-card {{
        background: linear-gradient(135deg, rgba(2,6,23,0.85), rgba(15,23,42,0.65));
        border: 1px solid rgba(56,189,248,0.18);
        border-radius: 16px;
        padding: 16px 18px;
        margin-bottom: 10px;
        transition: 0.25s ease;
        {"text-align: right;" if is_ar else ""}
    }}
    .feat-card:hover {{
        border-color: rgba(56,189,248,0.50);
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(56,189,248,0.10);
    }}
    .feat-title {{
        color: #38bdf8;
        font-family: 'Orbitron', monospace;
        font-weight: 700;
        font-size: 14px;
        margin-bottom: 4px;
        letter-spacing: 0.5px;
    }}
    .feat-desc {{
        color: #94a3b8;
        font-size: 12.5px;
        line-height: 1.5;
    }}

    .tech-row {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 10px 16px;
        background: rgba(2,6,23,0.55);
        border-radius: 10px;
        margin-bottom: 8px;
        font-size: 14px;
        {"flex-direction: row-reverse;" if is_ar else ""}
    }}
    .tech-row span:first-child {{ color: #94a3b8; }}
    .tech-row span:last-child  {{ color: #22d3ee; font-weight: 700; font-family: 'Orbitron', monospace; }}

    .roadmap-item {{
        background: linear-gradient(135deg, rgba(2,6,23,0.75), rgba(15,23,42,0.55));
        border-{"right" if is_ar else "left"}: 4px solid #38bdf8;
        border-radius: 12px;
        padding: 14px 18px;
        margin-bottom: 10px;
    }}
    .roadmap-item.v1 {{ border-color: #22c55e; }}
    .roadmap-item.v2 {{ border-color: #facc15; }}
    .roadmap-item.v3 {{ border-color: #a855f7; }}
    .roadmap-title {{
        color: #f1f5f9;
        font-weight: 700;
        font-size: 15px;
        margin-bottom: 4px;
    }}
    .roadmap-desc {{
        color: #94a3b8;
        font-size: 13px;
    }}

    .stButton > button {{
        background: linear-gradient(135deg, #0ea5e9 0%, #7c3aed 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 14px !important;
        padding: 12px 18px !important;
        font-weight: 800 !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-size: 14px !important;
        min-height: 44px !important;
        box-shadow: 0 4px 18px rgba(14,165,233,0.20) !important;
        transition: 0.25s ease !important;
    }}
    .stButton > button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 28px rgba(124,58,237,0.35) !important;
    }}
    </style>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# Main Render
# ═══════════════════════════════════════════════════════════════════════════

def render_about():
    init_language()
    apply_rtl_css()
    _apply_css()

    # Log once per session
    if not st.session_state.get("_about_logged", False):
        log_action("view_about",
                   user_id=st.session_state.get("user", "anonymous"),
                   category="navigation")
        st.session_state._about_logged = True

    # ── Top Bar ───────────────────────────────────────────────────────────
    st.markdown(f"""
<div class="top-bar">
<div class="top-title">{t('neon_ui')}</div>
<div class="top-badge">{t('about_us')}</div>
</div>
    """, unsafe_allow_html=True)

    # ── Hero ──────────────────────────────────────────────────────────────
    st.markdown(f"""
<div class="hero">
<h1>ℹ️ {_t('about_hero_title')}</h1>
<p>{_t('about_hero_subtitle')}</p>
<div class="hero-pills">
<span class="hero-pill">🚀 {_t('modules_count')}</span>
<span class="hero-pill">🌐 {_t('languages_label')}</span>
<span class="hero-pill">💾 {_t('offline_label')}</span>
<span class="hero-pill">🛡️ {_t('secure_label')}</span>
</div>
</div>
    """, unsafe_allow_html=True)

    # ── Back ──────────────────────────────────────────────────────────────
    back_col, _ = st.columns([1.3, 8])
    with back_col:
        if st.button(t("back"), use_container_width=True, key="about_back_btn"):
            st.session_state.page = "login" if not st.session_state.get("logged_in") else "home"
            st.rerun()

    st.write("")

    # ── Section 1: What is it? ────────────────────────────────────────────
    st.markdown(f"""
<div class="section">
<div class="section-title">🌟 {_t('what_is_it')}</div>
<div class="section-body">{_t('what_is_it_body')}</div>
</div>
    """, unsafe_allow_html=True)

    # ── Section 2: Key Features ───────────────────────────────────────────
    st.markdown(f"""
<div class="section">
<div class="section-title">✨ {_t('key_features')}</div>
</div>
    """, unsafe_allow_html=True)

    features = [
        ("feat_ai_camera",  "feat_ai_camera_desc"),
        ("feat_media",      "feat_media_desc"),
        ("feat_tasks",      "feat_tasks_desc"),
        ("feat_calc",       "feat_calc_desc"),
        ("feat_games",      "feat_games_desc"),
        ("feat_assistant",  "feat_assistant_desc"),
        ("feat_security",   "feat_security_desc"),
        ("feat_dashboard",  "feat_dashboard_desc"),
    ]

    col1, col2 = st.columns(2)
    for i, (title_key, desc_key) in enumerate(features):
        col = col1 if i % 2 == 0 else col2
        with col:
            st.markdown(f"""
<div class="feat-card">
<div class="feat-title">{_t(title_key)}</div>
<div class="feat-desc">{_t(desc_key)}</div>
</div>
            """, unsafe_allow_html=True)

    # ── Section 3: Tech Stack ─────────────────────────────────────────────
    st.markdown(f"""
<div class="section">
<div class="section-title">🛠️ {_t('tech_stack')}</div>
</div>
    """, unsafe_allow_html=True)

    tech_items = [
        ("⚡", "Backend",       _t("tech_python")),
        ("🎨", "Framework",     _t("tech_streamlit")),
        ("👁️", "Computer Vision",_t("tech_cv")),
        ("🖼️", "Image Lib",     _t("tech_pillow")),
        ("📊", "Charts",        _t("tech_plotly")),
        ("💾", "Storage",       _t("tech_storage")),
    ]
    for icon, label, tech in tech_items:
        st.markdown(f"""
<div class="tech-row">
<span>{icon} {label}</span>
<span>{tech}</span>
</div>
        """, unsafe_allow_html=True)

    # ── Section 4: Roadmap ────────────────────────────────────────────────
    st.markdown(f"""
<div class="section">
<div class="section-title">🗺️ {_t('roadmap')}</div>
</div>
    """, unsafe_allow_html=True)

    roadmap_items = [
        ("v1", "roadmap_v1", "roadmap_v1_desc"),
        ("v2", "roadmap_v2", "roadmap_v2_desc"),
        ("v3", "roadmap_v3", "roadmap_v3_desc"),
    ]
    for cls, title_key, desc_key in roadmap_items:
        st.markdown(f"""
<div class="roadmap-item {cls}">
<div class="roadmap-title">{_t(title_key)}</div>
<div class="roadmap-desc">{_t(desc_key)}</div>
</div>
        """, unsafe_allow_html=True)

    # ── Section 5: Credits ────────────────────────────────────────────────
    st.markdown(f"""
<div class="section">
<div class="section-title">🙏 {_t('credits')}</div>
<div class="section-body">
<p><strong>{_t('credit_team')}:</strong> OMNIX VISION Development Team</p>
<p><strong>{_t('credit_libs')}:</strong> Streamlit, OpenCV, MediaPipe, Pillow, Plotly, NumPy, Matplotlib</p>
<p><strong>🔤</strong> {_t('credit_fonts')}</p>
<p style="margin-top:14px;color:#22c55e;font-weight:700;font-size:16px;">{_t('thanks_msg')}</p>
</div>
</div>
    """, unsafe_allow_html=True)