"""
═══════════════════════════════════════════════════════════════════════════
OMNIX VISION — Media Converter (Phase 4)
═══════════════════════════════════════════════════════════════════════════
Phase-4 changes:
    ✓ Full translation (EN/AR + RTL)
    ✓ Activity logging
    ✓ Removed styles/* dependency
    ✓ 5 tabs preserved: Image Convert, Image Process, Audio, Video, History
    ✓ FFmpeg auto-detection (optional - audio/video features need it)
    ✓ Graceful fallback for missing PIL/FFmpeg
═══════════════════════════════════════════════════════════════════════════
"""

import os
import shutil
import zipfile
import tempfile
import subprocess
from io import BytesIO
from datetime import datetime
from pathlib import Path

import streamlit as st

from utils.language import t, init_language, apply_rtl_css, is_rtl
from utils.activity import log_action

# Optional PIL
try:
    from PIL import Image, ImageEnhance, ImageFilter
    _HAS_PIL = True
except ImportError:
    _HAS_PIL = False


# ═══════════════════════════════════════════════════════════════════════════
# Page Translations
# ═══════════════════════════════════════════════════════════════════════════

MC_KEYS = {
    "mc_title":         {"en": "MEDIA CONVERTER",        "ar": "محوّل الوسائط"},
    "mc_subtitle":      {"en": "Image · Audio · Video · All-in-One Studio",
                         "ar": "صور · صوت · فيديو · استوديو متكامل"},
    "image_converter":  {"en": "Image Converter",        "ar": "محوّل الصور"},
    "image_processor":  {"en": "Image Processor",        "ar": "معالج الصور"},
    "audio_studio":     {"en": "Audio Studio",           "ar": "استوديو الصوت"},
    "video_studio":     {"en": "Video Studio",           "ar": "استوديو الفيديو"},
    "history_tab":      {"en": "History",                "ar": "السجل"},
    "upload_image":     {"en": "Upload Image",           "ar": "رفع صورة"},
    "upload_audio":     {"en": "Upload Audio",           "ar": "رفع ملف صوتي"},
    "upload_video":     {"en": "Upload Video",           "ar": "رفع فيديو"},
    "output_format":    {"en": "Output Format",          "ar": "صيغة الإخراج"},
    "quality":          {"en": "Quality",                "ar": "الجودة"},
    "convert_btn":      {"en": "🔄 Convert",             "ar": "🔄 تحويل"},
    "download_result":  {"en": "💾 Download Result",     "ar": "💾 تحميل النتيجة"},
    "no_history":       {"en": "No conversions yet.",    "ar": "لا يوجد تحويلات بعد."},
    "clear_history":    {"en": "🗑️ Clear History",       "ar": "🗑️ مسح السجل"},
    "ffmpeg_missing":   {
        "en": "⚠️ FFmpeg not found. Audio/Video conversion requires FFmpeg installed on your system.",
        "ar": "⚠️ FFmpeg غير موجود. تحويل الصوت/الفيديو يحتاج FFmpeg مثبت على نظامك.",
    },
    "pil_missing": {
        "en": "⚠️ Pillow not installed. Run: pip install Pillow",
        "ar": "⚠️ Pillow غير مثبت. شغّل: pip install Pillow",
    },
    "processing":       {"en": "⏳ Processing...",        "ar": "⏳ جاري المعالجة..."},
    "conversion_done":  {"en": "✅ Conversion complete!", "ar": "✅ اكتمل التحويل!"},
    "conversion_failed":{"en": "❌ Conversion failed.",    "ar": "❌ فشل التحويل."},
    "rotate":           {"en": "Rotate",                  "ar": "تدوير"},
    "flip":             {"en": "Flip",                    "ar": "قلب"},
    "filter":           {"en": "Filter",                  "ar": "فلتر"},
    "brightness":       {"en": "Brightness",              "ar": "السطوع"},
    "contrast":         {"en": "Contrast",                "ar": "التباين"},
    "saturation":       {"en": "Saturation",              "ar": "التشبع"},
    "audio_volume":     {"en": "Volume",                  "ar": "مستوى الصوت"},
    "audio_speed":      {"en": "Speed",                   "ar": "السرعة"},
    "video_resolution": {"en": "Resolution",              "ar": "الدقة"},
    "trim_start":       {"en": "Trim Start (sec)",        "ar": "بداية القص (ث)"},
    "trim_duration":    {"en": "Duration (sec)",          "ar": "المدة (ث)"},
    "stats_total":      {"en": "Total Conversions",       "ar": "إجمالي التحويلات"},
    "stats_images":     {"en": "Images Processed",        "ar": "صور معالجة"},
    "stats_audio":      {"en": "Audio Processed",         "ar": "ملفات صوتية"},
    "stats_video":      {"en": "Videos Processed",        "ar": "ملفات فيديو"},
}


def _t(key: str) -> str:
    from utils.language import get_language_code
    lang = get_language_code()
    if key in MC_KEYS:
        return MC_KEYS[key].get(lang, MC_KEYS[key].get("en", key))
    return t(key)


# ═══════════════════════════════════════════════════════════════════════════
# FFmpeg detection
# ═══════════════════════════════════════════════════════════════════════════

def _get_ffmpeg_path() -> str:
    """Find FFmpeg executable."""
    # Try PATH first
    path = shutil.which("ffmpeg")
    if path:
        return path
    # Common Windows locations
    common_paths = [
        r"C:\ffmpeg\bin\ffmpeg.exe",
        r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
        "/usr/bin/ffmpeg",
        "/usr/local/bin/ffmpeg",
    ]
    for p in common_paths:
        if os.path.exists(p):
            return p
    return ""


def _ffmpeg_available() -> bool:
    return bool(_get_ffmpeg_path())


def _run_ffmpeg(command: list) -> tuple:
    """Run ffmpeg command and return (success, stderr)."""
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
        return result.returncode == 0, result.stderr
    except subprocess.TimeoutExpired:
        return False, "Timeout"
    except Exception as e:
        return False, str(e)


# ═══════════════════════════════════════════════════════════════════════════
# File Helpers
# ═══════════════════════════════════════════════════════════════════════════

def _save_uploaded_file(uploaded_file, suffix: str) -> str:
    """Save uploaded file to temp location and return path."""
    fd, path = tempfile.mkstemp(suffix=suffix)
    with os.fdopen(fd, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return path


def _read_output_file(path: str) -> bytes:
    with open(path, "rb") as f:
        return f.read()


def _cleanup(*paths):
    for p in paths:
        try:
            if p and os.path.exists(p):
                os.remove(p)
        except OSError:
            pass


def _image_to_bytes(img, output_format: str, quality: int = 90) -> bytes:
    """Convert PIL Image to bytes in specified format."""
    buf = BytesIO()
    save_kwargs = {}
    fmt = output_format.upper()

    if fmt == "JPG":
        fmt = "JPEG"
        if img.mode in ("RGBA", "LA", "P"):
            img = img.convert("RGB")
        save_kwargs["quality"] = quality
    elif fmt == "WEBP":
        save_kwargs["quality"] = quality
    elif fmt == "PNG":
        save_kwargs["optimize"] = True

    img.save(buf, format=fmt, **save_kwargs)
    return buf.getvalue()


def _image_mime(fmt: str) -> str:
    return {
        "PNG":  "image/png",
        "JPG":  "image/jpeg",
        "JPEG": "image/jpeg",
        "WEBP": "image/webp",
        "BMP":  "image/bmp",
    }.get(fmt.upper(), "application/octet-stream")


def _audio_mime(fmt: str) -> str:
    return {
        "MP3": "audio/mpeg",
        "WAV": "audio/wav",
        "OGG": "audio/ogg",
        "M4A": "audio/mp4",
    }.get(fmt.upper(), "audio/mpeg")


def _video_mime(fmt: str) -> str:
    return {
        "MP4":  "video/mp4",
        "WEBM": "video/webm",
        "MOV":  "video/quicktime",
        "AVI":  "video/x-msvideo",
    }.get(fmt.upper(), "video/mp4")


# ═══════════════════════════════════════════════════════════════════════════
# History (in session state)
# ═══════════════════════════════════════════════════════════════════════════

def _init_state():
    if "mc_history" not in st.session_state:
        st.session_state.mc_history = []


def _add_history(tool: str, details: str):
    st.session_state.mc_history.append({
        "Time":    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Tool":    tool,
        "Details": details,
    })


# ═══════════════════════════════════════════════════════════════════════════
# CSS
# ═══════════════════════════════════════════════════════════════════════════

def _apply_css():
    is_ar = is_rtl()
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@400;600;700&display=swap');

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
        padding: 38px 28px;
        text-align: center;
        box-shadow: 0 0 48px rgba(56,189,248,0.16);
        margin-bottom: 22px;
    }}
    .hero h1 {{
        font-family: 'Orbitron', monospace;
        font-size: 42px;
        font-weight: 900;
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
    .hero p {{ color: #cbd5e1; margin-top: 12px; font-size: 14px; }}

    .glass-card {{
        background: linear-gradient(145deg, rgba(15,23,42,0.92), rgba(2,6,23,0.78));
        border: 1px solid rgba(56,189,248,0.22);
        border-radius: 22px;
        padding: 24px;
        margin-bottom: 18px;
    }}
    .section-title {{
        color: #22d3ee;
        font-family: 'Orbitron', monospace;
        font-size: 18px;
        font-weight: 900;
        margin-bottom: 8px;
        letter-spacing: 1px;
        {"text-align: right;" if is_ar else ""}
    }}
    .section-note {{
        color: #94a3b8;
        font-size: 13px;
        margin-bottom: 14px;
        {"text-align: right;" if is_ar else ""}
    }}

    .stat-card {{
        background: rgba(2,6,23,0.65);
        border: 1px solid rgba(56,189,248,0.20);
        border-radius: 16px;
        padding: 14px 18px;
        text-align: center;
    }}
    .stat-card-label {{
        color: #94a3b8;
        font-size: 10px;
        font-family: 'Orbitron', monospace;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin-bottom: 6px;
    }}
    .stat-card-val {{
        color: #38bdf8;
        font-family: 'Orbitron', monospace;
        font-size: 24px;
        font-weight: 900;
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
        font-size: 13px !important;
    }}
    button[data-baseweb="tab"][aria-selected="true"] {{
        background: linear-gradient(135deg, rgba(56,189,248,0.25), rgba(168,85,247,0.22)) !important;
        color: #ffffff !important;
        border-color: rgba(56,189,248,0.55) !important;
    }}

    .stButton > button {{
        background: linear-gradient(135deg, #0ea5e9 0%, #7c3aed 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 14px !important;
        padding: 11px 18px !important;
        font-weight: 800 !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-size: 14px !important;
        min-height: 44px !important;
        box-shadow: 0 4px 16px rgba(14,165,233,0.20) !important;
        transition: 0.25s ease !important;
    }}
    .stButton > button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 26px rgba(124,58,237,0.35) !important;
    }}
    .stDownloadButton > button {{
        background: linear-gradient(135deg, #22c55e 0%, #15803d 100%) !important;
    }}
    </style>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# Tab 1: Image Converter
# ═══════════════════════════════════════════════════════════════════════════

def _tab_image_converter(user_id: str):
    st.markdown(f'<div class="glass-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">🖼️ {_t("image_converter")}</div>',
                unsafe_allow_html=True)
    st.markdown(
        '<div class="section-note">Upload an image and convert it to PNG, JPG, WEBP, or BMP.</div>',
        unsafe_allow_html=True
    )

    if not _HAS_PIL:
        st.error(_t("pil_missing"))
        st.markdown('</div>', unsafe_allow_html=True)
        return

    uploaded = st.file_uploader(
        _t("upload_image"),
        type=["png", "jpg", "jpeg", "webp", "bmp"],
        key="img_converter_upload",
    )

    if uploaded:
        try:
            img = Image.open(uploaded)
        except Exception as e:
            st.error(f"❌ {e}")
            st.markdown('</div>', unsafe_allow_html=True)
            return

        col_orig, col_settings = st.columns([1, 1])

        with col_orig:
            st.image(img, caption=f"Original: {img.size[0]}×{img.size[1]} {img.mode}",
                     use_container_width=True)

        with col_settings:
            output_format = st.selectbox(
                _t("output_format"),
                ["PNG", "JPG", "WEBP", "BMP"],
                key="img_out_fmt",
            )
            quality = st.slider(
                _t("quality"),
                min_value=10, max_value=100, value=90,
                key="img_quality",
            )

            if st.button(_t("convert_btn"), use_container_width=True,
                         key="img_convert_btn"):
                try:
                    img_bytes = _image_to_bytes(img, output_format, quality)
                    st.success(_t("conversion_done"))
                    st.download_button(
                        _t("download_result"),
                        data=img_bytes,
                        file_name=f"converted.{output_format.lower()}",
                        mime=_image_mime(output_format),
                        use_container_width=True,
                        key="img_convert_dl",
                    )
                    _add_history("Image Convert",
                                 f"{img.format} → {output_format} (Q{quality})")
                    log_action("image_converted", user_id=user_id, category="data",
                               details=f"{img.format}->{output_format}")
                except Exception as e:
                    st.error(f"{_t('conversion_failed')} {e}")

    st.markdown('</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# Tab 2: Image Processor
# ═══════════════════════════════════════════════════════════════════════════

def _tab_image_processor(user_id: str):
    st.markdown(f'<div class="glass-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">🎨 {_t("image_processor")}</div>',
                unsafe_allow_html=True)
    st.markdown(
        '<div class="section-note">Apply filters, adjustments, rotation, and effects.</div>',
        unsafe_allow_html=True
    )

    if not _HAS_PIL:
        st.error(_t("pil_missing"))
        st.markdown('</div>', unsafe_allow_html=True)
        return

    uploaded = st.file_uploader(
        _t("upload_image"),
        type=["png", "jpg", "jpeg", "webp", "bmp"],
        key="img_proc_upload",
    )

    if not uploaded:
        st.markdown('</div>', unsafe_allow_html=True)
        return

    try:
        img = Image.open(uploaded).convert("RGB")
    except Exception as e:
        st.error(f"❌ {e}")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    # Controls
    c1, c2, c3 = st.columns(3)
    with c1:
        brightness = st.slider(_t("brightness"), 0.1, 2.0, 1.0, 0.1, key="proc_bright")
        contrast   = st.slider(_t("contrast"),   0.1, 2.0, 1.0, 0.1, key="proc_contrast")
    with c2:
        saturation = st.slider(_t("saturation"), 0.0, 2.0, 1.0, 0.1, key="proc_sat")
        rotation   = st.selectbox(_t("rotate"),
                                  ["None", "90° CW", "180°", "270° CW"],
                                  key="proc_rot")
    with c3:
        filt = st.selectbox(_t("filter"),
                            ["None", "Blur", "Sharpen", "Grayscale", "Edge Detect", "Emboss"],
                            key="proc_filter")
        flip = st.selectbox(_t("flip"),
                            ["None", "Horizontal", "Vertical"],
                            key="proc_flip")

    # Apply transformations
    processed = img

    # Adjustments
    if brightness != 1.0:
        processed = ImageEnhance.Brightness(processed).enhance(brightness)
    if contrast != 1.0:
        processed = ImageEnhance.Contrast(processed).enhance(contrast)
    if saturation != 1.0:
        processed = ImageEnhance.Color(processed).enhance(saturation)

    # Filter
    if filt == "Blur":
        processed = processed.filter(ImageFilter.GaussianBlur(radius=3))
    elif filt == "Sharpen":
        processed = processed.filter(ImageFilter.SHARPEN)
    elif filt == "Grayscale":
        processed = processed.convert("L").convert("RGB")
    elif filt == "Edge Detect":
        processed = processed.filter(ImageFilter.FIND_EDGES)
    elif filt == "Emboss":
        processed = processed.filter(ImageFilter.EMBOSS)

    # Rotate
    if rotation == "90° CW":
        processed = processed.rotate(-90, expand=True)
    elif rotation == "180°":
        processed = processed.rotate(180, expand=True)
    elif rotation == "270° CW":
        processed = processed.rotate(90, expand=True)

    # Flip
    if flip == "Horizontal":
        processed = processed.transpose(Image.FLIP_LEFT_RIGHT)
    elif flip == "Vertical":
        processed = processed.transpose(Image.FLIP_TOP_BOTTOM)

    # Preview
    pcol1, pcol2 = st.columns(2)
    with pcol1:
        st.image(img, caption="Original", use_container_width=True)
    with pcol2:
        st.image(processed, caption="Processed", use_container_width=True)

    # Download
    if st.button(f"💾 {_t('download_result')}", use_container_width=True,
                 key="proc_dl_btn"):
        try:
            png_bytes = _image_to_bytes(processed, "PNG", 95)
            st.download_button(
                _t("download_result"),
                data=png_bytes,
                file_name="processed.png",
                mime="image/png",
                use_container_width=True,
                key="proc_dl_actual",
            )
            _add_history("Image Process",
                         f"B={brightness} C={contrast} S={saturation} F={filt} R={rotation}")
            log_action("image_processed", user_id=user_id, category="data",
                       details=f"filter={filt} rotation={rotation}")
        except Exception as e:
            st.error(f"❌ {e}")

    st.markdown('</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# Tab 3: Audio Studio
# ═══════════════════════════════════════════════════════════════════════════

def _tab_audio_studio(user_id: str):
    st.markdown(f'<div class="glass-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">🎵 {_t("audio_studio")}</div>',
                unsafe_allow_html=True)
    st.markdown(
        '<div class="section-note">Convert audio formats, adjust volume and speed (requires FFmpeg).</div>',
        unsafe_allow_html=True
    )

    if not _ffmpeg_available():
        st.warning(_t("ffmpeg_missing"))
        st.info("Download FFmpeg from: https://ffmpeg.org/download.html")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    uploaded = st.file_uploader(
        _t("upload_audio"),
        type=["mp3", "wav", "ogg", "m4a", "flac"],
        key="audio_upload",
    )

    if not uploaded:
        st.markdown('</div>', unsafe_allow_html=True)
        return

    st.audio(uploaded, format="audio/mpeg")

    c1, c2, c3 = st.columns(3)
    with c1:
        output_fmt = st.selectbox(
            _t("output_format"),
            ["MP3", "WAV", "OGG", "M4A"],
            key="audio_out_fmt",
        )
    with c2:
        volume = st.slider(_t("audio_volume"),
                           0.1, 3.0, 1.0, 0.1,
                           key="audio_vol")
    with c3:
        speed = st.slider(_t("audio_speed"),
                          0.5, 2.0, 1.0, 0.1,
                          key="audio_speed")

    if st.button(_t("convert_btn"), use_container_width=True, key="audio_conv_btn"):
        with st.spinner(_t("processing")):
            input_ext  = uploaded.name.rsplit(".", 1)[-1].lower()
            input_path = _save_uploaded_file(uploaded, f".{input_ext}")
            output_path = tempfile.mktemp(suffix=f".{output_fmt.lower()}")

            ffmpeg = _get_ffmpeg_path()
            cmd = [
                ffmpeg, "-y", "-i", input_path,
                "-filter:a", f"volume={volume},atempo={max(0.5, min(2.0, speed))}",
                "-vn",
                output_path,
            ]

            success, err = _run_ffmpeg(cmd)
            if success:
                st.success(_t("conversion_done"))
                audio_bytes = _read_output_file(output_path)
                st.download_button(
                    _t("download_result"),
                    data=audio_bytes,
                    file_name=f"converted.{output_fmt.lower()}",
                    mime=_audio_mime(output_fmt),
                    use_container_width=True,
                    key="audio_dl",
                )
                _add_history("Audio Convert",
                             f"{input_ext.upper()} → {output_fmt} V={volume} S={speed}")
                log_action("audio_converted", user_id=user_id, category="data",
                           details=f"{input_ext}->{output_fmt}")
            else:
                st.error(f"{_t('conversion_failed')} {err[:200]}")

            _cleanup(input_path, output_path)

    st.markdown('</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# Tab 4: Video Studio
# ═══════════════════════════════════════════════════════════════════════════

def _tab_video_studio(user_id: str):
    st.markdown(f'<div class="glass-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">🎬 {_t("video_studio")}</div>',
                unsafe_allow_html=True)
    st.markdown(
        '<div class="section-note">Convert formats, change resolution, trim videos (requires FFmpeg).</div>',
        unsafe_allow_html=True
    )

    if not _ffmpeg_available():
        st.warning(_t("ffmpeg_missing"))
        st.markdown('</div>', unsafe_allow_html=True)
        return

    uploaded = st.file_uploader(
        _t("upload_video"),
        type=["mp4", "mov", "webm", "avi", "mkv"],
        key="video_upload",
    )

    if not uploaded:
        st.markdown('</div>', unsafe_allow_html=True)
        return

    c1, c2 = st.columns(2)
    with c1:
        output_fmt = st.selectbox(
            _t("output_format"),
            ["MP4", "WEBM", "MOV", "AVI"],
            key="video_out_fmt",
        )
        resolution = st.selectbox(
            _t("video_resolution"),
            ["Original", "1920x1080", "1280x720", "854x480", "640x360"],
            key="video_res",
        )
    with c2:
        trim_start    = st.number_input(_t("trim_start"),
                                        min_value=0.0, value=0.0, step=1.0,
                                        key="video_trim_start")
        trim_duration = st.number_input(_t("trim_duration"),
                                        min_value=0.0, value=0.0, step=1.0,
                                        help="0 = full length",
                                        key="video_trim_dur")

    if st.button(_t("convert_btn"), use_container_width=True, key="video_conv_btn"):
        with st.spinner(_t("processing")):
            input_ext  = uploaded.name.rsplit(".", 1)[-1].lower()
            input_path = _save_uploaded_file(uploaded, f".{input_ext}")
            output_path = tempfile.mktemp(suffix=f".{output_fmt.lower()}")

            ffmpeg = _get_ffmpeg_path()
            cmd = [ffmpeg, "-y"]

            if trim_start > 0:
                cmd += ["-ss", str(trim_start)]

            cmd += ["-i", input_path]

            if trim_duration > 0:
                cmd += ["-t", str(trim_duration)]

            if resolution != "Original":
                w, h = resolution.split("x")
                cmd += ["-vf", f"scale={w}:{h}"]

            # Codec
            if output_fmt == "MP4":
                cmd += ["-c:v", "libx264", "-c:a", "aac"]
            elif output_fmt == "WEBM":
                cmd += ["-c:v", "libvpx-vp9", "-c:a", "libopus"]

            cmd += [output_path]

            success, err = _run_ffmpeg(cmd)
            if success:
                st.success(_t("conversion_done"))
                video_bytes = _read_output_file(output_path)
                st.download_button(
                    _t("download_result"),
                    data=video_bytes,
                    file_name=f"converted.{output_fmt.lower()}",
                    mime=_video_mime(output_fmt),
                    use_container_width=True,
                    key="video_dl",
                )
                _add_history("Video Convert",
                             f"{input_ext.upper()} → {output_fmt} {resolution}")
                log_action("video_converted", user_id=user_id, category="data",
                           details=f"{input_ext}->{output_fmt} {resolution}")
            else:
                st.error(f"{_t('conversion_failed')} {err[:200]}")

            _cleanup(input_path, output_path)

    st.markdown('</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# Tab 5: History
# ═══════════════════════════════════════════════════════════════════════════

def _tab_history(user_id: str):
    st.markdown(f'<div class="glass-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">📜 {_t("history_tab")}</div>',
                unsafe_allow_html=True)

    history = st.session_state.mc_history

    if not history:
        st.info(_t("no_history"))
    else:
        # Stats
        img_count = sum(1 for h in history if "Image" in h["Tool"])
        aud_count = sum(1 for h in history if "Audio" in h["Tool"])
        vid_count = sum(1 for h in history if "Video" in h["Tool"])

        s1, s2, s3, s4 = st.columns(4)
        with s1:
            st.markdown(f"""
<div class="stat-card">
<div class="stat-card-label">{_t('stats_total')}</div>
<div class="stat-card-val">{len(history)}</div>
</div>""", unsafe_allow_html=True)
        with s2:
            st.markdown(f"""
<div class="stat-card">
<div class="stat-card-label">{_t('stats_images')}</div>
<div class="stat-card-val" style="color:#22c55e;">{img_count}</div>
</div>""", unsafe_allow_html=True)
        with s3:
            st.markdown(f"""
<div class="stat-card">
<div class="stat-card-label">{_t('stats_audio')}</div>
<div class="stat-card-val" style="color:#a855f7;">{aud_count}</div>
</div>""", unsafe_allow_html=True)
        with s4:
            st.markdown(f"""
<div class="stat-card">
<div class="stat-card-label">{_t('stats_video')}</div>
<div class="stat-card-val" style="color:#f59e0b;">{vid_count}</div>
</div>""", unsafe_allow_html=True)

        st.write("")
        st.dataframe(history, use_container_width=True)

        if st.button(_t("clear_history"), use_container_width=True,
                     key="mc_hist_clear"):
            st.session_state.mc_history = []
            log_action("mc_history_cleared", user_id=user_id, category="data")
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# Main Render
# ═══════════════════════════════════════════════════════════════════════════

def render_media_converter():
    init_language()
    apply_rtl_css()

    if not st.session_state.get("logged_in", False):
        st.session_state.page = "login"
        st.rerun()

    user_id = st.session_state.get("user", "anonymous")

    _init_state()
    _apply_css()

    # ── Top Bar ───────────────────────────────────────────────────────────
    st.markdown(f"""
<div class="top-bar">
<div class="top-title">{t('neon_ui')}</div>
<div class="top-badge">{_t('mc_title')}</div>
</div>
    """, unsafe_allow_html=True)

    # ── Hero ──────────────────────────────────────────────────────────────
    st.markdown(f"""
<div class="hero">
<h1>🎞️ {_t('mc_title')}</h1>
<p>{_t('mc_subtitle')}</p>
</div>
    """, unsafe_allow_html=True)

    # ── Back ──────────────────────────────────────────────────────────────
    back_col, _ = st.columns([1.3, 8])
    with back_col:
        if st.button(t("back"), use_container_width=True, key="mc_back_btn"):
            st.session_state.page = "home"
            st.rerun()

    # ── Tools availability info ──
    if not _HAS_PIL or not _ffmpeg_available():
        warnings = []
        if not _HAS_PIL:
            warnings.append(_t("pil_missing"))
        if not _ffmpeg_available():
            warnings.append(_t("ffmpeg_missing"))
        for w in warnings:
            st.warning(w)

    # ── Tabs ──────────────────────────────────────────────────────────────
    tabs = st.tabs([
        f"🖼️ {_t('image_converter')}",
        f"🎨 {_t('image_processor')}",
        f"🎵 {_t('audio_studio')}",
        f"🎬 {_t('video_studio')}",
        f"📜 {_t('history_tab')}",
    ])

    with tabs[0]:
        _tab_image_converter(user_id)
    with tabs[1]:
        _tab_image_processor(user_id)
    with tabs[2]:
        _tab_audio_studio(user_id)
    with tabs[3]:
        _tab_video_studio(user_id)
    with tabs[4]:
        _tab_history(user_id)