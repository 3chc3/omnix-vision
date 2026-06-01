"""
═══════════════════════════════════════════════════════════════════════════
OMNIX VISION — Random Tools (Phase 4 — Round 2)
═══════════════════════════════════════════════════════════════════════════
Features:
    ✓ QR Code Generator (with download)
    ✓ Password Generator (configurable length + character sets)
    ✓ Color Picker / Palette Generator
    ✓ UUID Generator (v4)
    ✓ Random Number Generator
    ✓ Lorem Ipsum text generator
    ✓ Full EN/AR translation with RTL
═══════════════════════════════════════════════════════════════════════════
"""

import io
import uuid
import random
import string
import secrets

import streamlit as st

from utils.language import t, init_language, apply_rtl_css, is_rtl
from utils.activity import log_action

# Optional QR
try:
    import qrcode
    from PIL import Image
    _HAS_QR = True
except ImportError:
    _HAS_QR = False


# ═══════════════════════════════════════════════════════════════════════════
# Translations
# ═══════════════════════════════════════════════════════════════════════════
RT_KEYS = {
    "rt_title":       {"en": "Random Tools",     "ar": "أدوات عشوائية"},
    "rt_subtitle":    {"en": "QR codes, passwords, colors, UUIDs, and more",
                       "ar": "أكواد QR، كلمات مرور، ألوان، معرّفات والمزيد"},
    "tab_qr":         {"en": "📱 QR Code",       "ar": "📱 رمز QR"},
    "tab_password":   {"en": "🔐 Password",      "ar": "🔐 كلمة مرور"},
    "tab_color":      {"en": "🎨 Color",         "ar": "🎨 لون"},
    "tab_uuid":       {"en": "🆔 UUID",          "ar": "🆔 معرّف"},
    "tab_number":     {"en": "🔢 Number",        "ar": "🔢 رقم"},
    "tab_text":       {"en": "📝 Lorem Ipsum",   "ar": "📝 نص تجريبي"},

    "qr_text":        {"en": "Text or URL to encode",
                       "ar": "النص أو الرابط المراد ترميزه"},
    "qr_generate":    {"en": "✨ Generate QR",    "ar": "✨ توليد QR"},
    "qr_download":    {"en": "⬇️ Download PNG",   "ar": "⬇️ تحميل PNG"},
    "qr_missing":     {"en": "⚠️ qrcode library not installed. Run: pip install qrcode[pil]",
                       "ar": "⚠️ مكتبة qrcode غير مثبتة. شغّل: pip install qrcode[pil]"},

    "pwd_length":     {"en": "Length",            "ar": "الطول"},
    "pwd_uppercase":  {"en": "Include uppercase (A-Z)",
                       "ar": "يشمل أحرف كبيرة (A-Z)"},
    "pwd_lowercase":  {"en": "Include lowercase (a-z)",
                       "ar": "يشمل أحرف صغيرة (a-z)"},
    "pwd_digits":     {"en": "Include digits (0-9)",
                       "ar": "يشمل أرقام (0-9)"},
    "pwd_symbols":    {"en": "Include symbols (!@#$%)",
                       "ar": "يشمل رموز (!@#$%)"},
    "pwd_exclude":    {"en": "Exclude ambiguous (0,O,1,l,I)",
                       "ar": "استبعاد المتشابهة (0,O,1,l,I)"},
    "pwd_generate":   {"en": "🎲 Generate Password",
                       "ar": "🎲 توليد كلمة مرور"},
    "pwd_count":      {"en": "How many passwords?",
                       "ar": "كم كلمة مرور؟"},
    "pwd_strength":   {"en": "Strength",          "ar": "القوة"},
    "pwd_weak":       {"en": "Weak",              "ar": "ضعيفة"},
    "pwd_medium":     {"en": "Medium",            "ar": "متوسطة"},
    "pwd_strong":     {"en": "Strong",            "ar": "قوية"},
    "pwd_very_strong":{"en": "Very Strong",       "ar": "قوية جداً"},
    "pwd_no_charset": {"en": "⚠️ Select at least one character set",
                       "ar": "⚠️ اختر مجموعة أحرف واحدة على الأقل"},

    "color_pick":     {"en": "Pick a color or generate one",
                       "ar": "اختر لوناً أو ولّد واحداً"},
    "color_random":   {"en": "🎲 Random Color",   "ar": "🎲 لون عشوائي"},
    "color_palette":  {"en": "Generate 5-Color Palette",
                       "ar": "توليد لوحة بـ 5 ألوان"},
    "color_complementary": {"en": "Complementary Colors",
                            "ar": "ألوان مكملة"},

    "uuid_count":     {"en": "How many UUIDs?",   "ar": "كم معرّف؟"},
    "uuid_generate":  {"en": "🎲 Generate UUIDs",  "ar": "🎲 توليد معرّفات"},
    "uuid_format":    {"en": "Format",            "ar": "الصيغة"},
    "uuid_with_dashes":{"en": "With dashes",      "ar": "بشرطات"},
    "uuid_no_dashes": {"en": "Without dashes",    "ar": "بدون شرطات"},
    "uuid_uppercase": {"en": "Uppercase",         "ar": "أحرف كبيرة"},

    "num_min":        {"en": "Minimum value",     "ar": "أقل قيمة"},
    "num_max":        {"en": "Maximum value",     "ar": "أعلى قيمة"},
    "num_count":      {"en": "How many numbers?", "ar": "كم رقم؟"},
    "num_unique":     {"en": "Unique only",       "ar": "فريدة فقط"},
    "num_generate":   {"en": "🎲 Roll Numbers",   "ar": "🎲 رمي الأرقام"},

    "lorem_words":    {"en": "Number of words",   "ar": "عدد الكلمات"},
    "lorem_generate": {"en": "📝 Generate Text",  "ar": "📝 توليد نص"},

    "copy_btn":       {"en": "📋 Copy",            "ar": "📋 نسخ"},
    "result_label":   {"en": "Result",            "ar": "النتيجة"},
}


def _t(key: str) -> str:
    from utils.language import get_language_code
    lang = get_language_code()
    if key in RT_KEYS:
        return RT_KEYS[key].get(lang, RT_KEYS[key].get("en", key))
    return t(key)


# ═══════════════════════════════════════════════════════════════════════════
# CSS
# ═══════════════════════════════════════════════════════════════════════════

def _apply_css():
    is_ar = is_rtl()
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@400;600;700&family=JetBrains+Mono:wght@400;700&display=swap');

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
            radial-gradient(circle at 10% 10%, rgba(168,85,247,0.18), transparent 28%),
            radial-gradient(circle at 90% 10%, rgba(245,158,11,0.15), transparent 32%),
            linear-gradient(135deg, #020617 0%, #06111f 48%, #111032 100%);
        color: #f8fafc;
        font-family: 'Rajdhani', sans-serif;
    }}

    .hero {{
        background: linear-gradient(135deg, rgba(15,23,42,0.96), rgba(8,47,73,0.58));
        border: 1px solid rgba(168,85,247,0.45);
        border-radius: 30px;
        padding: 34px 28px;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 0 48px rgba(168,85,247,0.18);
    }}
    .hero h1 {{
        color: #c084fc;
        font-size: 38px;
        font-weight: 950;
        margin: 0;
        letter-spacing: 2px;
        text-shadow: 0 0 24px rgba(192,132,252,0.5);
    }}
    .hero p {{ color: #cbd5e1; margin-top: 10px; font-size: 14px; }}

    .result-box {{
        background: linear-gradient(145deg, rgba(2,6,23,0.97), rgba(8,47,73,0.55));
        border: 2px solid rgba(168,85,247,0.45);
        border-radius: 16px;
        padding: 18px 22px;
        margin: 12px 0;
        font-family: 'JetBrains Mono', monospace;
        font-size: 16px;
        color: #c084fc;
        word-break: break-all;
        text-align: center;
        box-shadow: 0 0 24px rgba(168,85,247,0.15);
    }}

    .strength-bar {{
        width: 100%;
        height: 10px;
        background: rgba(15,23,42,0.95);
        border-radius: 999px;
        overflow: hidden;
        margin: 8px 0;
        border: 1px solid rgba(148,163,184,0.18);
    }}
    .strength-fill {{
        height: 100%;
        border-radius: 999px;
        transition: 0.3s;
        box-shadow: 0 0 12px currentColor;
    }}

    .color-swatch {{
        width: 100%;
        height: 100px;
        border-radius: 14px;
        margin: 10px 0;
        box-shadow: 0 8px 28px rgba(0,0,0,0.4);
        border: 1px solid rgba(255,255,255,0.10);
    }}

    .color-info {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 13px;
        color: #cbd5e1;
        background: rgba(2,6,23,0.65);
        border: 1px solid rgba(56,189,248,0.18);
        border-radius: 10px;
        padding: 10px 14px;
        margin: 6px 0;
    }}

    .stButton > button {{
        background: linear-gradient(135deg, #a855f7 0%, #7c3aed 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 11px 18px !important;
        font-weight: 800 !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-size: 14px !important;
        min-height: 44px !important;
        box-shadow: 0 4px 16px rgba(168,85,247,0.25) !important;
        transition: 0.25s ease !important;
    }}
    .stButton > button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 26px rgba(168,85,247,0.40) !important;
    }}

    div[data-baseweb="tab-list"] {{
        gap: 8px;
        justify-content: center;
        flex-wrap: wrap;
        background: transparent !important;
    }}
    button[data-baseweb="tab"] {{
        background: rgba(15,23,42,0.72) !important;
        border-radius: 14px !important;
        color: #cbd5e1 !important;
        font-weight: 800 !important;
        border: 1px solid rgba(148,163,184,0.18) !important;
        padding: 10px 16px !important;
    }}
    button[data-baseweb="tab"][aria-selected="true"] {{
        background: linear-gradient(135deg, rgba(168,85,247,0.30), rgba(124,58,237,0.22)) !important;
        color: #ffffff !important;
        border-color: rgba(168,85,247,0.55) !important;
    }}
    </style>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# Tab: QR Code
# ═══════════════════════════════════════════════════════════════════════════

def _tab_qr(user_id: str):
    st.markdown(f"### 📱 {_t('tab_qr')}")

    if not _HAS_QR:
        st.error(_t("qr_missing"))
        return

    text = st.text_area(_t("qr_text"),
                        value="https://github.com/",
                        height=100,
                        key="qr_text_input")

    c1, c2 = st.columns(2)
    with c1:
        box_size = st.slider("Size", 5, 20, 10, key="qr_size")
    with c2:
        border = st.slider("Border", 1, 10, 4, key="qr_border")

    if st.button(_t("qr_generate"), use_container_width=True, key="qr_gen_btn"):
        if not text.strip():
            st.warning("⚠️ Enter some text")
            return

        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=box_size,
                border=border,
            )
            qr.add_data(text)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")

            buf = io.BytesIO()
            img.save(buf, format="PNG")
            png_bytes = buf.getvalue()

            st.image(png_bytes, width=320)
            st.download_button(
                _t("qr_download"),
                data=png_bytes,
                file_name="omnix_qrcode.png",
                mime="image/png",
                use_container_width=True,
                key="qr_dl_btn",
            )

            log_action("qr_generated", user_id=user_id, category="data",
                       details=f"text_len={len(text)}")
        except Exception as e:
            st.error(f"❌ {e}")


# ═══════════════════════════════════════════════════════════════════════════
# Tab: Password Generator
# ═══════════════════════════════════════════════════════════════════════════

def _calc_strength(pwd: str) -> tuple:
    """Return (label_key, score 0-100, color)."""
    score = 0
    if len(pwd) >= 8:  score += 25
    if len(pwd) >= 12: score += 15
    if len(pwd) >= 16: score += 10
    if any(c.islower() for c in pwd): score += 10
    if any(c.isupper() for c in pwd): score += 15
    if any(c.isdigit() for c in pwd): score += 15
    if any(c in string.punctuation for c in pwd): score += 10

    if score < 40:  return "pwd_weak",        score, "#ef4444"
    if score < 70:  return "pwd_medium",      score, "#f59e0b"
    if score < 90:  return "pwd_strong",      score, "#22c55e"
    return "pwd_very_strong", min(score, 100), "#38bdf8"


def _generate_password(length: int,
                       upper: bool, lower: bool,
                       digits: bool, symbols: bool,
                       exclude_ambig: bool) -> str:
    chars = ""
    if upper:   chars += string.ascii_uppercase
    if lower:   chars += string.ascii_lowercase
    if digits:  chars += string.digits
    if symbols: chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"

    if exclude_ambig:
        for a in "0O1lI":
            chars = chars.replace(a, "")

    if not chars:
        return ""
    return "".join(secrets.choice(chars) for _ in range(length))


def _tab_password(user_id: str):
    st.markdown(f"### 🔐 {_t('tab_password')}")

    c1, c2 = st.columns(2)
    with c1:
        length = st.slider(_t("pwd_length"), 4, 64, 16, key="pwd_len")
        count  = st.slider(_t("pwd_count"), 1, 10, 3, key="pwd_count")
    with c2:
        upper    = st.checkbox(_t("pwd_uppercase"), value=True,  key="pwd_up")
        lower    = st.checkbox(_t("pwd_lowercase"), value=True,  key="pwd_low")
        digits   = st.checkbox(_t("pwd_digits"),    value=True,  key="pwd_dig")
        symbols  = st.checkbox(_t("pwd_symbols"),   value=True,  key="pwd_sym")
        excl_amb = st.checkbox(_t("pwd_exclude"),   value=False, key="pwd_amb")

    if st.button(_t("pwd_generate"), use_container_width=True, key="pwd_gen_btn"):
        if not (upper or lower or digits or symbols):
            st.warning(_t("pwd_no_charset"))
            return

        for i in range(count):
            pwd = _generate_password(length, upper, lower, digits, symbols, excl_amb)
            label_key, score, color = _calc_strength(pwd)

            st.markdown(f'<div class="result-box">{pwd}</div>',
                        unsafe_allow_html=True)
            st.markdown(f"""
<div style="display:flex;justify-content:space-between;align-items:center;font-size:12px;color:#94a3b8;margin-bottom:4px;">
<span>{_t('pwd_strength')}: <b style="color:{color};">{_t(label_key)}</b></span>
<span>{score}%</span>
</div>
<div class="strength-bar">
<div class="strength-fill" style="width:{score}%;background:{color};color:{color};"></div>
</div>
            """, unsafe_allow_html=True)
            st.code(pwd, language="text")
            st.write("")

        log_action("passwords_generated", user_id=user_id, category="data",
                   details=f"count={count} len={length}")


# ═══════════════════════════════════════════════════════════════════════════
# Tab: Color
# ═══════════════════════════════════════════════════════════════════════════

def _hex_to_rgb(hex_color: str) -> tuple:
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def _rgb_to_hex(rgb: tuple) -> str:
    return "#" + "".join(f"{c:02x}" for c in rgb)


def _rgb_to_hsl(rgb: tuple) -> tuple:
    r, g, b = [c/255 for c in rgb]
    cmax = max(r, g, b)
    cmin = min(r, g, b)
    delta = cmax - cmin
    L = (cmax + cmin) / 2
    if delta == 0:
        H = 0; S = 0
    else:
        S = delta / (1 - abs(2*L - 1))
        if cmax == r:   H = ((g-b)/delta) % 6
        elif cmax == g: H = (b-r)/delta + 2
        else:           H = (r-g)/delta + 4
        H *= 60
    return (int(H), int(S*100), int(L*100))


def _tab_color(user_id: str):
    st.markdown(f"### 🎨 {_t('tab_color')}")

    if "rt_color" not in st.session_state:
        st.session_state.rt_color = "#a855f7"

    c1, c2 = st.columns([1, 2])
    with c1:
        picked = st.color_picker(_t("color_pick"),
                                 value=st.session_state.rt_color,
                                 key="rt_color_picker")
        st.session_state.rt_color = picked

        if st.button(_t("color_random"),
                     use_container_width=True,
                     key="rt_color_rnd"):
            st.session_state.rt_color = _rgb_to_hex(
                (random.randint(0, 255),
                 random.randint(0, 255),
                 random.randint(0, 255))
            )
            log_action("random_color", user_id=user_id, category="data")
            st.rerun()

    with c2:
        color = st.session_state.rt_color
        rgb = _hex_to_rgb(color)
        hsl = _rgb_to_hsl(rgb)

        st.markdown(f"""
<div class="color-swatch" style="background:{color};"></div>
<div class="color-info">HEX: <b style="color:#c084fc;">{color.upper()}</b></div>
<div class="color-info">RGB: <b style="color:#38bdf8;">rgb({rgb[0]}, {rgb[1]}, {rgb[2]})</b></div>
<div class="color-info">HSL: <b style="color:#22c55e;">hsl({hsl[0]}, {hsl[1]}%, {hsl[2]}%)</b></div>
        """, unsafe_allow_html=True)

    st.write("")
    st.markdown(f"### 🌈 {_t('color_palette')}")

    if st.button(f"🎨 {_t('color_palette')}",
                 use_container_width=True,
                 key="rt_palette_btn"):
        cols = st.columns(5)
        for i, c in enumerate(cols):
            with c:
                hex_c = _rgb_to_hex((random.randint(0, 255),
                                     random.randint(0, 255),
                                     random.randint(0, 255)))
                st.markdown(f"""
<div class="color-swatch" style="background:{hex_c};"></div>
<div class="color-info" style="text-align:center;">{hex_c.upper()}</div>
                """, unsafe_allow_html=True)
        log_action("palette_generated", user_id=user_id, category="data")


# ═══════════════════════════════════════════════════════════════════════════
# Tab: UUID
# ═══════════════════════════════════════════════════════════════════════════

def _tab_uuid(user_id: str):
    st.markdown(f"### 🆔 {_t('tab_uuid')}")

    c1, c2 = st.columns(2)
    with c1:
        count   = st.slider(_t("uuid_count"), 1, 20, 5, key="uuid_count")
        dashes  = st.checkbox(_t("uuid_with_dashes"), value=True, key="uuid_dash")
    with c2:
        upper   = st.checkbox(_t("uuid_uppercase"),    value=False, key="uuid_up")

    if st.button(_t("uuid_generate"),
                 use_container_width=True,
                 key="uuid_gen_btn"):
        for _ in range(count):
            u = str(uuid.uuid4())
            if not dashes: u = u.replace("-", "")
            if upper:      u = u.upper()
            st.markdown(f'<div class="result-box">{u}</div>',
                        unsafe_allow_html=True)
            st.code(u, language="text")
        log_action("uuids_generated", user_id=user_id, category="data",
                   details=f"count={count}")


# ═══════════════════════════════════════════════════════════════════════════
# Tab: Random Number
# ═══════════════════════════════════════════════════════════════════════════

def _tab_number(user_id: str):
    st.markdown(f"### 🔢 {_t('tab_number')}")

    c1, c2 = st.columns(2)
    with c1:
        min_v = st.number_input(_t("num_min"),
                                value=1, step=1, key="num_min")
        max_v = st.number_input(_t("num_max"),
                                value=100, step=1, key="num_max")
    with c2:
        count   = st.slider(_t("num_count"), 1, 50, 5, key="num_count")
        unique  = st.checkbox(_t("num_unique"), value=False, key="num_uniq")

    if st.button(_t("num_generate"),
                 use_container_width=True,
                 key="num_gen_btn"):
        if min_v >= max_v:
            st.error("❌ Min must be less than Max")
            return

        try:
            if unique:
                range_size = int(max_v - min_v + 1)
                if count > range_size:
                    st.warning(f"⚠️ Cannot generate {count} unique numbers in range "
                               f"{min_v}-{max_v} (only {range_size} possible)")
                    return
                numbers = random.sample(range(int(min_v), int(max_v) + 1), count)
            else:
                numbers = [random.randint(int(min_v), int(max_v)) for _ in range(count)]

            nums_str = ", ".join(str(n) for n in numbers)
            st.markdown(f'<div class="result-box">{nums_str}</div>',
                        unsafe_allow_html=True)
            st.code(nums_str, language="text")

            log_action("numbers_generated", user_id=user_id, category="data",
                       details=f"count={count} range={min_v}-{max_v}")
        except Exception as e:
            st.error(f"❌ {e}")


# ═══════════════════════════════════════════════════════════════════════════
# Tab: Lorem Ipsum
# ═══════════════════════════════════════════════════════════════════════════

LOREM_WORDS = (
    "lorem ipsum dolor sit amet consectetur adipiscing elit sed do "
    "eiusmod tempor incididunt ut labore et dolore magna aliqua enim "
    "ad minim veniam quis nostrud exercitation ullamco laboris nisi "
    "aliquip ex ea commodo consequat duis aute irure reprehenderit "
    "voluptate velit esse cillum eu fugiat nulla pariatur excepteur "
    "sint occaecat cupidatat non proident sunt culpa qui officia "
    "deserunt mollit anim id est laborum"
).split()


def _tab_text(user_id: str):
    st.markdown(f"### 📝 {_t('tab_text')}")

    word_count = st.slider(_t("lorem_words"), 10, 500, 50, key="lorem_wc")

    if st.button(_t("lorem_generate"),
                 use_container_width=True,
                 key="lorem_gen_btn"):
        words = [random.choice(LOREM_WORDS) for _ in range(word_count)]
        words[0] = words[0].capitalize()

        # Insert occasional punctuation
        text = []
        for i, w in enumerate(words):
            text.append(w)
            if (i + 1) % random.randint(8, 15) == 0 and i < len(words) - 1:
                text[-1] += random.choice([".", ",", "."])

        result = " ".join(text)
        if not result.endswith("."):
            result += "."

        st.markdown(f'<div class="result-box" style="text-align:left;font-family:Rajdhani;font-size:14px;line-height:1.7;">{result}</div>',
                    unsafe_allow_html=True)
        st.code(result, language="text")
        log_action("lorem_generated", user_id=user_id, category="data",
                   details=f"words={word_count}")


# ═══════════════════════════════════════════════════════════════════════════
# Main Render
# ═══════════════════════════════════════════════════════════════════════════

def render_random_tools():
    init_language()
    apply_rtl_css()

    if not st.session_state.get("logged_in", False):
        st.session_state.page = "login"
        st.rerun()

    user_id = st.session_state.get("user", "anonymous")

    _apply_css()

    # ── Hero ──
    st.markdown(f"""
<div class="hero">
<h1>🎲 {_t('rt_title')}</h1>
<p>{_t('rt_subtitle')}</p>
</div>
    """, unsafe_allow_html=True)

    # ── Back ──
    back_col, _ = st.columns([1.3, 8])
    with back_col:
        if st.button(t("back"), use_container_width=True, key="rt_back_btn"):
            st.session_state.page = "home"
            st.rerun()

    # ── Tabs ──
    tabs = st.tabs([
        _t("tab_qr"), _t("tab_password"), _t("tab_color"),
        _t("tab_uuid"), _t("tab_number"), _t("tab_text"),
    ])
    with tabs[0]: _tab_qr(user_id)
    with tabs[1]: _tab_password(user_id)
    with tabs[2]: _tab_color(user_id)
    with tabs[3]: _tab_uuid(user_id)
    with tabs[4]: _tab_number(user_id)
    with tabs[5]: _tab_text(user_id)