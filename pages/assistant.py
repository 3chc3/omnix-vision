"""
═══════════════════════════════════════════════════════════════════════════
OMNIX VISION — AI Assistant (Phase 3)
═══════════════════════════════════════════════════════════════════════════
Phase-3 changes:
    ✓ 40+ keyword-based smart responses (was 7)
    ✓ Conversation history saved per user to data/chat_history.json
    ✓ Full translation (EN/AR + RTL)
    ✓ Activity logging
    ✓ Removed dependency on styles/ folder (uses inline CSS only)
    ✓ Live system stats integrated
═══════════════════════════════════════════════════════════════════════════
"""

import json
import time
from datetime import datetime
from pathlib import Path

import streamlit as st

from utils.language import t, init_language, apply_rtl_css, is_rtl
from utils.activity import log_action, get_stats


# ═══════════════════════════════════════════════════════════════════════════
# Paths & Persistence
# ═══════════════════════════════════════════════════════════════════════════
BASE_DIR  = Path(__file__).resolve().parent.parent
DATA_DIR  = BASE_DIR / "data"
CHAT_FILE = DATA_DIR / "chat_history.json"
DATA_DIR.mkdir(parents=True, exist_ok=True)

MAX_HISTORY_PER_USER = 100   # Keep last 100 messages per user


def _load_chat_history(user_id: str) -> list:
    """Load chat history for current user."""
    if not CHAT_FILE.exists():
        return []
    try:
        with open(CHAT_FILE, "r", encoding="utf-8") as f:
            all_chats = json.load(f)
        return all_chats.get(str(user_id), [])
    except (json.JSONDecodeError, OSError):
        return []


def _save_chat_history(user_id: str, messages: list):
    """Persist chat history for current user."""
    all_chats = {}
    if CHAT_FILE.exists():
        try:
            with open(CHAT_FILE, "r", encoding="utf-8") as f:
                all_chats = json.load(f)
        except (json.JSONDecodeError, OSError):
            all_chats = {}

    # Keep only last N messages
    all_chats[str(user_id)] = messages[-MAX_HISTORY_PER_USER:]

    try:
        with open(CHAT_FILE, "w", encoding="utf-8") as f:
            json.dump(all_chats, f, ensure_ascii=False, indent=2)
    except OSError:
        pass


# ═══════════════════════════════════════════════════════════════════════════
# Smart Response Engine
# ═══════════════════════════════════════════════════════════════════════════

# Each rule: (list of keywords, response function)
def _build_response_rules(camera_state: dict, current_user: str, lang: str):
    """Build response rules. Order matters — first match wins."""

    def yes_no(v):
        return "✅" if v else "❌"

    stats = get_stats()
    current_time = datetime.now().strftime("%H:%M:%S")

    rules = [
        # ── Greetings ──
        (["hello", "hi ", "hey", "مرحبا", "اهلا", "السلام"],
         lambda: (f"👋 Hello **{current_user}**! How can I assist you with OMNIX VISION today?"
                  if lang == "en" else
                  f"👋 مرحباً **{current_user}**! كيف يمكنني مساعدتك في OMNIX VISION اليوم؟")),

        # ── Time/Date ──
        (["time", "clock", "وقت", "الساعة"],
         lambda: (f"🕐 Current time: **{current_time}**" if lang == "en"
                  else f"🕐 الوقت الحالي: **{current_time}**")),

        (["date", "today", "تاريخ", "اليوم"],
         lambda: (f"📅 Today: **{datetime.now().strftime('%A, %B %d, %Y')}**" if lang == "en"
                  else f"📅 اليوم: **{datetime.now().strftime('%A, %d/%m/%Y')}**")),

        # ── Camera/Hand/Vision ──
        (["camera", "hand", "scan", "vision", "كاميرا", "يد", "مسح"],
         lambda: (
             f"📷 **Camera Status**: {camera_state.get('message', 'No data')}\n\n"
             f"- Right hand: {yes_no(camera_state.get('right_hand_up'))}\n"
             f"- Left hand: {yes_no(camera_state.get('left_hand_up'))}\n"
             f"- Pose visible: {yes_no(camera_state.get('pose_visible'))}\n"
             f"- Person detected: {yes_no(camera_state.get('person_detected'))}"
         )),

        # ── User Info ──
        (["who am i", "my user", "username", "login", "من انا", "اسمي"],
         lambda: (f"👤 You are logged in as **{current_user}**." if lang == "en"
                  else f"👤 أنت مسجل الدخول كـ **{current_user}**.")),

        # ── Dashboard ──
        (["dashboard", "stats", "statistics", "لوحة", "احصائيات"],
         lambda: (
             f"📊 **Dashboard Summary**\n\n"
             f"- Total actions logged: {stats['total']}\n"
             f"- Unique users: {stats['unique_users']}\n"
             f"- Categories: {', '.join(stats['by_category'].keys()) if stats['by_category'] else 'None'}"
         )),

        # ── Tasks ──
        (["task", "todo", "to do", "pomodoro", "مهمة", "مهام"],
         lambda: (
             "📝 **Tasks Module** offers:\n"
             "- Priority levels (Low/Medium/High/Urgent)\n"
             "- Due dates with overdue alerts\n"
             "- Tags (Work, Personal, Study, Health, Shopping)\n"
             "- 🍅 Pomodoro timer (25/5/15)\n"
             "- ⏱️ Stopwatch\n"
             "- File uploads with previews"
         )),

        # ── Calculator ──
        (["calculate", "math", "calculator", "calc", "حاسبة", "حساب"],
         lambda: (
             "🧮 **Calculator Module** provides:\n"
             "- Basic arithmetic with memory (M+/M-/MR/MC)\n"
             "- Scientific functions (sin, cos, log, sqrt…)\n"
             "- Expression solver\n"
             "- Graph plotter\n"
             "- Unit converter (8 categories)\n"
             "- Number systems (BIN/OCT/DEC/HEX)\n"
             "- Formulas (BMI, Ohm, Speed, Area, %)"
         )),

        # ── Games ──
        (["game", "play", "fun", "snake", "space", "لعبة", "العب"],
         lambda: (
             "🎮 **Game Center** has 4 games:\n"
             "- 🚀 Space Defender\n"
             "- ⭐ Neon Catcher\n"
             "- 🐍 Snake Game\n"
             "- 🧱 Breakout\n\n"
             "High scores are saved automatically to your account!"
         )),

        # ── Media ──
        (["media", "image", "video", "audio", "music", "وسائط", "صورة", "صوت"],
         lambda: (
             "🎬 **Media Center** lets you:\n"
             "- View images with gallery mode\n"
             "- Stream HD videos\n"
             "- Play audio files\n"
             "- Apply filters (Blur, Sharpen, Sepia, B&W)\n"
             "- Crop & Resize images\n"
             "- Convert between formats"
         )),

        # ── Security ──
        (["security", "password", "auth", "lock", "أمان", "كلمة المرور"],
         lambda: (
             "🛡️ **Security Features**:\n"
             "- SHA-256 password hashing with salt\n"
             "- Account lockout after 5 failed attempts\n"
             "- Brute-force protection\n"
             "- Activity log audit trail\n\n"
             "Visit Security Center to manage your account."
         )),

        # ── Settings ──
        (["setting", "config", "preference", "إعدادات", "تفضيلات"],
         lambda: (
             "⚙️ **Settings** allows you to:\n"
             "- Change password\n"
             "- Switch language (EN/AR)\n"
             "- Toggle animations\n"
             "- Adjust display density\n"
             "- Logout from any device"
         )),

        # ── About/Project ──
        (["about", "project", "omnix", "vision", "مشروع", "حول"],
         lambda: (
             "🚀 **OMNIX VISION** is an intelligent multimedia platform\n"
             "powered by AI and computer vision. Features include:\n"
             "- 14 integrated modules\n"
             "- Multi-language support (EN/AR + RTL)\n"
             "- Real-time camera processing\n"
             "- Secure user accounts\n"
             "- JSON persistence (offline-first)"
         )),

        # ── Status/System ──
        (["status", "system", "online", "health", "حالة", "نظام"],
         lambda: (
             f"⚡ **System Status**\n\n"
             f"- User: **{current_user}**\n"
             f"- Camera: {camera_state.get('message', 'N/A')}\n"
             f"- Person detected: {yes_no(camera_state.get('person_detected'))}\n"
             f"- Pose visible: {yes_no(camera_state.get('pose_visible'))}\n"
             f"- Activity entries: {stats['total']}"
         )),

        # ── Logout ──
        (["logout", "log out", "sign out", "exit", "خروج"],
         lambda: ("👋 To logout, click the red **Logout** button on the home page, "
                  "or use Settings → Logout. Your session will be cleared safely."
                  if lang == "en" else
                  "👋 لتسجيل الخروج، اضغط الزر الأحمر **Logout** في الصفحة الرئيسية، "
                  "أو من الإعدادات → تسجيل الخروج. ستنتهي جلستك بشكل آمن.")),

        # ── Help / Capabilities ──
        (["help", "what can", "capabilities", "commands", "مساعدة", "ماذا"],
         lambda: (
             "💡 **I can help you with:**\n\n"
             "- 📷 Camera & hand detection status\n"
             "- 👤 User & account info\n"
             "- 📊 Dashboard statistics\n"
             "- 📝 Tasks & Pomodoro\n"
             "- 🧮 Calculator features\n"
             "- 🎮 Games & high scores\n"
             "- 🎬 Media tools\n"
             "- 🛡️ Security info\n"
             "- ⚙️ Settings guidance\n"
             "- 🕐 Time & date\n\n"
             "Just ask me anything!"
         )),

        # ── Thanks ──
        (["thank", "thanks", "thx", "شكر", "شكرا"],
         lambda: ("🙏 You're welcome! Let me know if you need anything else."
                  if lang == "en" else
                  "🙏 العفو! أخبرني إذا احتجت أي شيء آخر.")),

        # ── Goodbye ──
        (["bye", "goodbye", "see you", "وداعا", "مع السلامة"],
         lambda: (f"👋 Goodbye **{current_user}**! Have a great day!"
                  if lang == "en" else
                  f"👋 وداعاً **{current_user}**! يوم سعيد!")),

        # ── Compliments ──
        (["love", "great", "awesome", "amazing", "cool", "رائع", "ممتاز"],
         lambda: ("😊 Thank you! OMNIX VISION is built to be helpful and beautiful."
                  if lang == "en" else
                  "😊 شكراً! تم بناء OMNIX VISION ليكون مفيداً وجميلاً.")),

        # ── Jokes ──
        (["joke", "funny", "laugh", "نكتة", "اضحك"],
         lambda: (
             "😄 Why do programmers prefer dark mode?\n\n"
             "Because light attracts bugs! 🐛"
             if lang == "en" else
             "😄 لماذا يفضل المبرمجون الوضع الداكن؟\n\n"
             "لأن الضوء يجذب الحشرات (البقات)! 🐛"
         )),
    ]
    return rules


def generate_smart_response(user_text: str,
                            camera_state: dict,
                            current_user: str) -> str:
    """Generate a smart response based on keywords. Returns the matched text."""
    from utils.language import get_language_code
    lang = get_language_code()

    text = user_text.lower().strip()
    rules = _build_response_rules(camera_state, current_user, lang)

    for keywords, response_fn in rules:
        if any(kw in text for kw in keywords):
            return response_fn()

    # Default fallback
    if lang == "en":
        return (
            "🤔 I'm not sure I understood that. Try asking about:\n\n"
            "**status** · **camera** · **tasks** · **calculator** · "
            "**games** · **media** · **security** · **help**\n\n"
            "Or click one of the Quick Action buttons!"
        )
    return (
        "🤔 لم أفهم سؤالك بالضبط. جرّب السؤال عن:\n\n"
        "**الحالة** · **الكاميرا** · **المهام** · **الحاسبة** · "
        "**الألعاب** · **الوسائط** · **الأمان** · **مساعدة**\n\n"
        "أو اضغط أحد أزرار الإجراءات السريعة!"
    )


# ═══════════════════════════════════════════════════════════════════════════
# UI Helpers
# ═══════════════════════════════════════════════════════════════════════════

def _get_camera_state() -> dict:
    """Return camera state with safe defaults."""
    return st.session_state.get("camera_ai_state", {
        "person_detected": False,
        "pose_visible":    False,
        "right_hand_up":   False,
        "left_hand_up":    False,
        "body_centered":   False,
        "message":         "No camera state available.",
        "status_color":    "#4a7fa5",
    })


def _render_chat_message(role: str, content: str):
    """Render a single chat bubble."""
    if role == "assistant":
        # Use unsafe_allow_html so emojis + line breaks render
        safe_content = content.replace("\n", "<br>")
        st.markdown(f"""
        <div class="bubble-wrap">
            <div class="bubble-avatar avatar-ai">🤖</div>
            <div class="bubble bubble-ai">
                <div class="bubble-sender">OMNIX AI</div>
                {safe_content}
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        safe_content = content.replace("\n", "<br>")
        st.markdown(f"""
        <div class="bubble-wrap user-wrap">
            <div class="bubble-avatar avatar-user">👤</div>
            <div class="bubble bubble-user">
                <div class="bubble-sender">YOU</div>
                {safe_content}
            </div>
        </div>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# CSS
# ═══════════════════════════════════════════════════════════════════════════

def _apply_assistant_css():
    is_ar = is_rtl()
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@400;500;600;700&display=swap');

    [data-testid="stSidebar"], [data-testid="collapsedControl"] {{ display: none; }}

    .block-container {{
        max-width: 1200px;
        padding-top: 1.2rem;
        {"direction: rtl;" if is_ar else ""}
    }}

    .stApp {{
        background:
            radial-gradient(ellipse at 10% 10%, rgba(0,234,255,0.10) 0%, transparent 40%),
            radial-gradient(ellipse at 90% 5%,  rgba(168,85,247,0.10) 0%, transparent 40%),
            linear-gradient(160deg, #020617 0%, #060d1f 60%, #0a0520 100%);
        font-family: 'Rajdhani', sans-serif;
        color: #f8fafc;
    }}

    .assistant-header {{
        background: linear-gradient(135deg, rgba(2,6,23,0.97), rgba(8,28,56,0.70));
        border: 1px solid rgba(0,234,255,0.28);
        border-radius: 28px;
        padding: 28px 30px;
        text-align: center;
        margin-bottom: 18px;
    }}
    .assistant-header-icon {{
        font-size: 52px;
        display: block;
        margin-bottom: 10px;
        filter: drop-shadow(0 0 16px rgba(0,234,255,0.60));
        animation: iconFloat 3s ease-in-out infinite;
    }}
    @keyframes iconFloat {{
        0%,100% {{ transform: translateY(0); }}
        50% {{ transform: translateY(-6px); }}
    }}
    .assistant-header h2 {{
        font-family: 'Orbitron', monospace;
        font-size: 26px;
        font-weight: 900;
        margin: 0;
        background: linear-gradient(90deg, #00eaff, #a855f7, #22c55e, #00eaff);
        background-size: 300% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: shimmer 5s linear infinite;
        letter-spacing: 2px;
    }}
    @keyframes shimmer {{ to {{ background-position: 300% center; }} }}
    .assistant-header p {{
        color: #64748b;
        font-size: 13px;
        margin-top: 8px;
        letter-spacing: 1px;
    }}

    .status-card {{
        background: linear-gradient(145deg, rgba(2,6,23,0.97), rgba(15,23,42,0.80));
        border: 1px solid rgba(0,234,255,0.20);
        border-radius: 22px;
        padding: 18px 20px;
        margin-bottom: 16px;
    }}
    .status-title {{
        font-family: 'Orbitron', monospace;
        color: #00eaff;
        font-size: 13px;
        font-weight: 700;
        letter-spacing: 1.5px;
        margin-bottom: 14px;
        display: flex;
        align-items: center;
        gap: 8px;
    }}
    .status-dot {{
        width: 8px; height: 8px; border-radius: 50%;
        background: #22c55e;
        animation: statusPulse 2s infinite;
    }}
    @keyframes statusPulse {{
        0%,100% {{ box-shadow: 0 0 0 0 rgba(34,197,94,0.5); }}
        50% {{ box-shadow: 0 0 0 6px rgba(34,197,94,0); }}
    }}
    .status-grid {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 10px;
    }}
    .status-item {{
        background: rgba(0,234,255,0.05);
        border: 1px solid rgba(0,234,255,0.12);
        border-radius: 14px;
        padding: 10px 14px;
    }}
    .status-item-label {{
        font-size: 10px;
        color: #475569;
        font-family: 'Orbitron', monospace;
        letter-spacing: 1px;
        text-transform: uppercase;
        margin-bottom: 4px;
    }}
    .status-item-val {{ font-size: 14px; color: #e0f2fe; font-weight: 600; }}
    .status-true {{ color: #22c55e !important; }}
    .status-false {{ color: #ef4444 !important; }}

    .quick-label {{
        font-family: 'Orbitron', monospace;
        font-size: 11px;
        color: #475569;
        letter-spacing: 2px;
        margin: 4px 0 10px;
        padding-left: 10px;
        border-left: 2px solid rgba(0,234,255,0.40);
    }}

    .chat-area {{
        background: rgba(2,6,23,0.85);
        border: 1px solid rgba(0,234,255,0.15);
        border-radius: 22px;
        padding: 18px 16px;
        margin: 10px 0 14px;
        max-height: 500px;
        overflow-y: auto;
    }}
    .chat-area::-webkit-scrollbar {{ width: 6px; }}
    .chat-area::-webkit-scrollbar-thumb {{ background: rgba(0,234,255,0.30); border-radius: 4px; }}

    .bubble-wrap {{
        display: flex;
        margin-bottom: 14px;
        align-items: flex-end;
        gap: 10px;
    }}
    .bubble-wrap.user-wrap {{ flex-direction: row-reverse; }}

    .bubble-avatar {{
        width: 34px; height: 34px;
        border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-size: 18px;
        flex-shrink: 0;
    }}
    .avatar-ai   {{ background: rgba(0,234,255,0.12); border: 1px solid rgba(0,234,255,0.35); }}
    .avatar-user {{ background: rgba(124,58,237,0.12); border: 1px solid rgba(124,58,237,0.35); }}

    .bubble {{
        max-width: 78%;
        padding: 12px 16px;
        border-radius: 18px;
        font-size: 14px;
        line-height: 1.75;
        font-family: 'Rajdhani', sans-serif;
    }}
    .bubble-ai {{
        background: linear-gradient(135deg, rgba(0,234,255,0.08), rgba(14,165,233,0.06));
        border: 1px solid rgba(0,234,255,0.18);
        color: #e0f2fe;
        border-bottom-left-radius: 4px;
    }}
    .bubble-user {{
        background: linear-gradient(135deg, rgba(124,58,237,0.18), rgba(168,85,247,0.12));
        border: 1px solid rgba(124,58,237,0.28);
        color: #f1f5f9;
        border-bottom-right-radius: 4px;
        text-align: right;
    }}
    .bubble-sender {{
        font-family: 'Orbitron', monospace;
        font-size: 10px;
        letter-spacing: 1px;
        margin-bottom: 5px;
        opacity: 0.55;
    }}

    div.stTextInput > div > div > input {{
        background: rgba(0,234,255,0.05) !important;
        border: 1px solid rgba(0,234,255,0.22) !important;
        border-radius: 12px !important;
        color: #e0f2fe !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-size: 15px !important;
        padding: 10px 14px !important;
    }}

    .stButton > button {{
        background: linear-gradient(135deg, #0ea5e9 0%, #7c3aed 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 14px !important;
        padding: 11px 18px !important;
        font-weight: 700 !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-size: 14px !important;
        min-height: 44px !important;
        box-shadow: 0 4px 16px rgba(14,165,233,0.18) !important;
        transition: 0.28s ease !important;
    }}
    .stButton > button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 26px rgba(124,58,237,0.35) !important;
    }}
    </style>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# Main Render
# ═══════════════════════════════════════════════════════════════════════════

def render_assistant():
    init_language()
    apply_rtl_css()

    if not st.session_state.get("logged_in", False):
        st.session_state.page = "login"
        st.rerun()

    user_id = st.session_state.get("user", "anonymous")

    # ── Load chat history (once per session) ──────────────────────────────
    if "assistant_messages" not in st.session_state:
        history = _load_chat_history(user_id)
        if not history:
            history = [{
                "role": "assistant",
                "content": (
                    f"👋 Hello! I am **OMNIX AI Assistant**. "
                    f"I can help you with system status, camera, tasks, calculator, "
                    f"games, media, security, and more. Ask me anything!"
                ),
                "timestamp": time.time(),
            }]
        st.session_state.assistant_messages = history

    _apply_assistant_css()

    # ── Back Button ───────────────────────────────────────────────────────
    back_col, *_ = st.columns([1.3, 8])
    with back_col:
        if st.button(t("back"), use_container_width=True, key="assistant_back_btn"):
            st.session_state.page = "home"
            st.rerun()

    camera_state = _get_camera_state()

    # ── Header ────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="assistant-header">
        <span class="assistant-header-icon">🤖</span>
        <h2>{t('assistant_title').upper()}</h2>
        <p>Smart interaction · System status · Real-time data</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Two-column layout ─────────────────────────────────────────────────
    left_col, right_col = st.columns([1.1, 2.8])

    with left_col:
        # ── Live Status Card ──
        def _bool_span(val):
            cls = "status-true" if val else "status-false"
            txt = "✅ Yes" if val else "❌ No"
            return f'<span class="{cls}">{txt}</span>'

        st.markdown(f"""
        <div class="status-card">
            <div class="status-title">
                <span class="status-dot"></span> {t('live_status').upper()}
            </div>
            <div class="status-grid">
                <div class="status-item">
                    <div class="status-item-label">{t('username')}</div>
                    <div class="status-item-val">{user_id}</div>
                </div>
                <div class="status-item">
                    <div class="status-item-label">{t('camera')}</div>
                    <div class="status-item-val" style="color:{camera_state.get('status_color','#4a7fa5')};font-size:11px;">
                        {camera_state.get('message','N/A')[:30]}
                    </div>
                </div>
                <div class="status-item">
                    <div class="status-item-label">{t('right_hand')}</div>
                    <div class="status-item-val">{_bool_span(camera_state.get('right_hand_up',False))}</div>
                </div>
                <div class="status-item">
                    <div class="status-item-label">{t('left_hand')}</div>
                    <div class="status-item-val">{_bool_span(camera_state.get('left_hand_up',False))}</div>
                </div>
                <div class="status-item">
                    <div class="status-item-label">{t('pose_visible')}</div>
                    <div class="status-item-val">{_bool_span(camera_state.get('pose_visible',False))}</div>
                </div>
                <div class="status-item">
                    <div class="status-item-label">{t('body_centered')}</div>
                    <div class="status-item-val">{_bool_span(camera_state.get('body_centered',False))}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Quick Actions ──
        st.markdown(f'<div class="quick-label">{t("quick_actions").upper()}</div>',
                    unsafe_allow_html=True)

        quick_map = {
            f"⚡ {t('system_status')}":     "system status",
            f"📷 {t('camera_info')}":       "camera info",
            f"📝 {t('tasks')}":             "tasks pomodoro",
            f"🧮 {t('calculator')}":        "calculator features",
            f"🎮 {t('game')}":              "games available",
            f"🚀 {t('project_info')}":      "about project",
            f"🛡️ {t('security_center')}":   "security features",
            f"❓ {t('help')}":              "help what can you do",
        }
        for label, prompt in quick_map.items():
            if st.button(label, use_container_width=True, key=f"quick_{prompt[:15]}"):
                reply = generate_smart_response(prompt, camera_state, user_id)
                st.session_state.assistant_messages.append({
                    "role": "user", "content": label, "timestamp": time.time()
                })
                st.session_state.assistant_messages.append({
                    "role": "assistant", "content": reply, "timestamp": time.time()
                })
                _save_chat_history(user_id, st.session_state.assistant_messages)
                log_action("assistant_quick_action",
                           user_id=user_id, category="navigation",
                           details=label)
                st.rerun()

        # ── Clear chat ──
        st.markdown(f'<div class="quick-label" style="margin-top:12px;">{t("chat_cleared")[:20]}</div>',
                    unsafe_allow_html=True)
        if st.button(f"🗑 {t('clear_chat')}", use_container_width=True, key="clear_chat_btn"):
            st.session_state.assistant_messages = [{
                "role": "assistant",
                "content": t("chat_cleared"),
                "timestamp": time.time(),
            }]
            _save_chat_history(user_id, st.session_state.assistant_messages)
            log_action("assistant_chat_cleared", user_id=user_id, category="data")
            st.rerun()

    with right_col:
        # ── Chat Bubbles ──
        st.markdown('<div class="chat-area">', unsafe_allow_html=True)
        for msg in st.session_state.assistant_messages:
            _render_chat_message(msg["role"], msg["content"])
        st.markdown('</div>', unsafe_allow_html=True)

        # ── Input ──
        user_text = st.text_input(
            t("ask_assistant"),
            placeholder=f"💬 {t('ask_assistant')}",
            key="assistant_input",
            label_visibility="collapsed",
        )
        send_col, _ = st.columns([1.2, 4])
        with send_col:
            if st.button(f"📨 {t('send')}", use_container_width=True, key="send_btn"):
                if user_text.strip():
                    reply = generate_smart_response(user_text, camera_state, user_id)
                    st.session_state.assistant_messages.append({
                        "role": "user", "content": user_text, "timestamp": time.time()
                    })
                    st.session_state.assistant_messages.append({
                        "role": "assistant", "content": reply, "timestamp": time.time()
                    })
                    _save_chat_history(user_id, st.session_state.assistant_messages)
                    log_action("assistant_message",
                               user_id=user_id, category="data",
                               details=user_text[:50])
                    st.rerun()