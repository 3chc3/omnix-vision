"""
═══════════════════════════════════════════════════════════════════════════
OMNIX VISION — Media Center (Phase 3)
═══════════════════════════════════════════════════════════════════════════
Phase-3 changes:
    ✓ Image Filters: Grayscale, Sepia, Blur, Sharpen, Invert, Brightness, Contrast
    ✓ Image Crop (interactive sliders)
    ✓ Image Resize (preserve aspect ratio option)
    ✓ Image Rotate (90/180/270 + flip H/V)
    ✓ Download processed images
    ✓ Translation + RTL support
    ✓ Activity logging
    ✓ Original gallery / video / audio viewers preserved
═══════════════════════════════════════════════════════════════════════════
Graceful fallback if PIL is not installed.
═══════════════════════════════════════════════════════════════════════════
"""

import os
import io
import base64
from pathlib import Path

import streamlit as st

from utils.language import t, init_language, apply_rtl_css, is_rtl
from utils.activity import log_action

# PIL is optional — graceful fallback
try:
    from PIL import Image, ImageFilter, ImageOps, ImageEnhance
    _HAS_PIL = True
except ImportError:
    _HAS_PIL = False


# ═══════════════════════════════════════════════════════════════════════════
# Paths
# ═══════════════════════════════════════════════════════════════════════════
BASE_DIR    = Path(__file__).resolve().parent.parent
ASSETS_DIR  = BASE_DIR / "assets"

AUDIO_FILE  = ASSETS_DIR / "audio"  / "real.mp3"
VIDEO_FILE  = ASSETS_DIR / "video"  / "real.mp4"
IMAGE_FILES = [
    ASSETS_DIR / "images" / "real1.jpg",
    ASSETS_DIR / "images" / "real2.jpg",
    ASSETS_DIR / "images" / "real3.jpg",
]


# ═══════════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════════

def _ui(html: str):
    st.markdown(html, unsafe_allow_html=True)


def _get_image_b64(path) -> str:
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except OSError:
        return ""


def _apply_sepia(img: "Image.Image") -> "Image.Image":
    """Apply sepia tone effect to RGB image."""
    if not _HAS_PIL:
        return img
    gray = img.convert("L")
    sepia = ImageOps.colorize(gray, black="#3b1f0e", white="#fee9c4")
    return sepia.convert("RGB")


def _apply_filter(img: "Image.Image", filter_name: str,
                  intensity: float = 1.0) -> "Image.Image":
    """Apply named filter to PIL Image."""
    if not _HAS_PIL or img is None:
        return img

    img = img.convert("RGB")  # Normalize

    if filter_name == "Original":
        return img
    if filter_name == "Grayscale":
        return img.convert("L").convert("RGB")
    if filter_name == "Sepia":
        return _apply_sepia(img)
    if filter_name == "Invert":
        return ImageOps.invert(img)
    if filter_name == "Blur":
        radius = max(0.5, intensity * 5)
        return img.filter(ImageFilter.GaussianBlur(radius=radius))
    if filter_name == "Sharpen":
        enhancer = ImageEnhance.Sharpness(img)
        return enhancer.enhance(1 + intensity * 3)
    if filter_name == "Brightness":
        enhancer = ImageEnhance.Brightness(img)
        return enhancer.enhance(intensity)
    if filter_name == "Contrast":
        enhancer = ImageEnhance.Contrast(img)
        return enhancer.enhance(intensity)
    if filter_name == "Saturation":
        enhancer = ImageEnhance.Color(img)
        return enhancer.enhance(intensity)
    if filter_name == "Edge Detect":
        return img.filter(ImageFilter.FIND_EDGES)
    if filter_name == "Emboss":
        return img.filter(ImageFilter.EMBOSS)
    if filter_name == "Smooth":
        return img.filter(ImageFilter.SMOOTH_MORE)
    return img


def _image_to_bytes(img: "Image.Image", fmt: str = "PNG") -> bytes:
    """Convert PIL Image to bytes for download."""
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    return buf.getvalue()


# ═══════════════════════════════════════════════════════════════════════════
# CSS
# ═══════════════════════════════════════════════════════════════════════════

def _apply_css():
    is_ar = is_rtl()
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@400;500;600;700&family=Share+Tech+Mono&display=swap');

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
        padding-left: 1.2rem;
        padding-right: 1.2rem;
        {"direction: rtl;" if is_ar else ""}
    }}

    .stApp {{
        background:
            radial-gradient(ellipse at 12% 10%, rgba(0,212,255,0.11) 0%, transparent 42%),
            radial-gradient(ellipse at 88% 8%,  rgba(168,85,247,0.11) 0%, transparent 42%),
            radial-gradient(ellipse at 50% 96%, rgba(34,197,94,0.06)  0%, transparent 38%),
            linear-gradient(160deg, #020617 0%, #060d1f 55%, #0a0520 100%);
        color: #f8fafc;
        font-family: 'Rajdhani', sans-serif;
    }}

    .omnix-hero {{
        position: relative; overflow: hidden;
        background: linear-gradient(135deg, rgba(2,6,23,0.97), rgba(0,35,55,0.72));
        border: 1px solid rgba(0,212,255,0.25);
        border-radius: 30px;
        padding: 36px 32px;
        text-align: center;
        margin-bottom: 22px;
        box-shadow: 0 0 60px rgba(0,212,255,0.10);
    }}
    .omnix-hero h1 {{
        font-family: 'Orbitron', monospace;
        font-size: 44px;
        font-weight: 900;
        margin: 0;
        letter-spacing: 5px;
        background: linear-gradient(90deg, #00d4ff 0%, #e2e8f0 40%, #a855f7 70%, #00d4ff 100%);
        background-size: 300% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: heroShift 6s linear infinite;
    }}
    @keyframes heroShift {{ to {{ background-position: 300% center; }} }}
    .hero-tagline {{
        color: rgba(148,163,184,0.65);
        font-size: 11px;
        letter-spacing: 3px;
        text-transform: uppercase;
        margin: 10px 0 18px;
        font-family: 'Share Tech Mono', monospace;
    }}
    .hero-pills {{ display: flex; justify-content: center; gap: 8px; flex-wrap: wrap; }}
    .hero-pill {{
        background: rgba(0,212,255,0.06);
        border: 1px solid rgba(0,212,255,0.18);
        border-radius: 999px;
        padding: 4px 12px;
        font-size: 10px;
        color: rgba(0,212,255,0.80);
        font-family: 'Orbitron', monospace;
        letter-spacing: 1px;
    }}

    .feature-card {{
        background: linear-gradient(155deg, rgba(2,6,23,0.97), rgba(10,15,30,0.88));
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 22px;
        padding: 24px 18px 18px;
        text-align: center;
        min-height: 200px;
        transition: all 0.4s cubic-bezier(0.34,1.56,0.64,1);
        display: flex;
        flex-direction: column;
        align-items: center;
    }}
    .feature-card:hover {{
        transform: translateY(-8px);
        border-color: rgba(0,212,255,0.40);
        box-shadow: 0 16px 44px rgba(0,212,255,0.12);
    }}
    .fc-icon {{
        width: 60px; height: 60px;
        border-radius: 18px;
        display: flex; align-items: center; justify-content: center;
        font-size: 28px;
        margin-bottom: 12px;
        background: linear-gradient(135deg, rgba(0,212,255,0.14), rgba(0,212,255,0.04));
        border: 1.5px solid rgba(0,212,255,0.25);
    }}
    .fc-title {{
        font-family: 'Orbitron', monospace;
        font-size: 13px;
        font-weight: 700;
        color: #e2e8f0;
        letter-spacing: 1.5px;
        margin-bottom: 8px;
    }}
    .fc-desc {{ color: #475569; font-size: 12px; line-height: 1.55; flex: 1; }}

    .media-panel {{
        background: linear-gradient(180deg, rgba(2,6,23,0.98), rgba(10,18,35,0.92));
        border: 1px solid rgba(0,212,255,0.14);
        border-radius: 22px;
        padding: 24px;
        margin-top: 16px;
    }}
    .panel-header {{
        font-family: 'Share Tech Mono', monospace;
        font-size: 11px;
        letter-spacing: 3px;
        text-transform: uppercase;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 10px;
    }}
    .panel-dot {{
        width: 7px; height: 7px;
        border-radius: 50%;
        animation: blink 1.2s ease-in-out infinite;
    }}
    @keyframes blink {{ 0%,100% {{opacity:1}} 50% {{opacity:0.15}} }}

    .gallery-grid {{ display: grid; grid-template-columns: repeat(3,1fr); gap: 14px; }}
    .gallery-item {{
        border-radius: 14px;
        overflow: hidden;
        border: 1px solid rgba(255,255,255,0.06);
        aspect-ratio: 4/3;
        transition: 0.3s;
    }}
    .gallery-item:hover {{
        transform: scale(1.03);
        border-color: rgba(0,212,255,0.45);
        box-shadow: 0 16px 40px rgba(0,212,255,0.14);
    }}
    .gallery-item img {{ width: 100%; height: 100%; object-fit: cover; }}

    .info-row {{
        display: flex;
        justify-content: space-between;
        padding: 8px 12px;
        background: rgba(15,23,42,0.55);
        border-radius: 8px;
        margin: 4px 0;
        font-size: 13px;
    }}
    .info-row span:first-child {{ color: #94a3b8; }}
    .info-row span:last-child  {{ color: #00d4ff; font-weight: 700; }}

    .stButton > button {{
        background: linear-gradient(135deg, rgba(0,212,255,0.18), rgba(124,58,237,0.18)) !important;
        color: #e2e8f0 !important;
        border: 1px solid rgba(0,212,255,0.30) !important;
        border-radius: 14px !important;
        padding: 11px 18px !important;
        font-weight: 700 !important;
        font-family: 'Orbitron', monospace !important;
        font-size: 11px !important;
        letter-spacing: 1.5px !important;
        text-transform: uppercase !important;
        min-height: 44px !important;
        transition: 0.28s ease !important;
    }}
    .stButton > button:hover {{
        background: linear-gradient(135deg, rgba(0,212,255,0.30), rgba(124,58,237,0.30)) !important;
        border-color: rgba(0,212,255,0.65) !important;
        box-shadow: 0 0 22px rgba(0,212,255,0.22) !important;
        transform: translateY(-2px) !important;
    }}

    div[data-baseweb="tab-list"] {{
        gap: 6px;
        justify-content: center;
        flex-wrap: wrap;
        background: transparent !important;
    }}
    button[data-baseweb="tab"] {{
        background: rgba(2,6,23,0.80) !important;
        border-radius: 14px !important;
        color: #475569 !important;
        font-weight: 700 !important;
        font-family: 'Rajdhani', sans-serif !important;
        border: 1px solid rgba(0,212,255,0.12) !important;
        padding: 10px 16px !important;
    }}
    button[data-baseweb="tab"][aria-selected="true"] {{
        background: linear-gradient(135deg, rgba(0,212,255,0.22), rgba(124,58,237,0.20)) !important;
        color: #f1f5f9 !important;
        border-color: rgba(0,212,255,0.55) !important;
    }}
    </style>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# Tab: Image Filters
# ═══════════════════════════════════════════════════════════════════════════

def _render_filters_tab(user_id: str):
    _ui(f"""
    <div class="media-panel">
    <div class="panel-header" style="color:#00d4ff;">
    <span class="panel-dot" style="background:#00d4ff;"></span>
    🎨 IMAGE FILTERS & EFFECTS
    </div>
    </div>
    """)

    if not _HAS_PIL:
        st.error("❌ Pillow library required. Install: `pip install Pillow`")
        return

    uploaded = st.file_uploader(
        "Upload an image",
        type=["jpg", "jpeg", "png", "webp"],
        key="filter_upload",
    )

    if not uploaded:
        st.info("📤 Upload an image to apply filters.")
        return

    try:
        img = Image.open(uploaded)
    except Exception as e:
        st.error(f"❌ Could not open image: {e}")
        return

    # Filter selection
    filters_list = [
        "Original", "Grayscale", "Sepia", "Invert",
        "Blur", "Sharpen", "Brightness", "Contrast",
        "Saturation", "Edge Detect", "Emboss", "Smooth",
    ]
    filter_name = st.selectbox("🎨 Choose Filter", filters_list, key="filter_choice")

    # Intensity slider for adjustable filters
    adjustable = ["Blur", "Sharpen", "Brightness", "Contrast", "Saturation"]
    intensity  = 1.0
    if filter_name in adjustable:
        intensity = st.slider("🎚️ Intensity", min_value=0.1, max_value=2.5,
                              value=1.0, step=0.1, key="filter_intensity")

    # Apply filter
    processed = _apply_filter(img, filter_name, intensity)

    # Preview
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Original**")
        st.image(img, use_container_width=True)
    with col2:
        st.markdown(f"**{filter_name}**")
        st.image(processed, use_container_width=True)

    # Info
    st.markdown(f"""
<div class="info-row"><span>📐 {t('size_label') if False else 'Size'}</span><span>{img.size[0]} × {img.size[1]}</span></div>
<div class="info-row"><span>🎨 Mode</span><span>{img.mode}</span></div>
<div class="info-row"><span>📁 Format</span><span>{img.format or 'Unknown'}</span></div>
    """, unsafe_allow_html=True)

    # Download
    st.write("")
    st.download_button(
        label=f"💾 {t('download')} Filtered Image",
        data=_image_to_bytes(processed, "PNG"),
        file_name=f"filtered_{filter_name.lower().replace(' ', '_')}.png",
        mime="image/png",
        use_container_width=True,
        key="download_filter",
    )

    if st.button(f"📝 {t('save')} Action", use_container_width=True, key="log_filter"):
        log_action("image_filter_applied", user_id=user_id, category="data",
                   details=f"{filter_name} (intensity={intensity})")
        st.success(f"✅ Filter logged: {filter_name}")


# ═══════════════════════════════════════════════════════════════════════════
# Tab: Crop & Resize
# ═══════════════════════════════════════════════════════════════════════════

def _render_crop_resize_tab(user_id: str):
    _ui(f"""
    <div class="media-panel">
    <div class="panel-header" style="color:#a855f7;">
    <span class="panel-dot" style="background:#a855f7;"></span>
    ✂️ CROP &amp; RESIZE
    </div>
    </div>
    """)

    if not _HAS_PIL:
        st.error("❌ Pillow library required. Install: `pip install Pillow`")
        return

    uploaded = st.file_uploader(
        "Upload an image",
        type=["jpg", "jpeg", "png", "webp"],
        key="crop_upload",
    )

    if not uploaded:
        st.info("📤 Upload an image to crop or resize.")
        return

    try:
        img = Image.open(uploaded).convert("RGB")
    except Exception as e:
        st.error(f"❌ {e}")
        return

    w, h = img.size

    # Sub-tabs: Crop / Resize / Rotate
    sub1, sub2, sub3 = st.tabs(["✂️ Crop", "📐 Resize", "🔄 Rotate"])

    # ── Crop ──
    with sub1:
        st.markdown(f"**Original size:** {w} × {h}")

        c1, c2 = st.columns(2)
        with c1:
            left   = st.slider("Left (X1)",   0, w,   0,    key="crop_left")
            top    = st.slider("Top (Y1)",    0, h,   0,    key="crop_top")
        with c2:
            right  = st.slider("Right (X2)",  0, w,   w,    key="crop_right")
            bottom = st.slider("Bottom (Y2)", 0, h,   h,    key="crop_bottom")

        if right <= left or bottom <= top:
            st.warning("⚠️ Right > Left and Bottom > Top required.")
            return

        cropped = img.crop((left, top, right, bottom))

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Original**")
            st.image(img, use_container_width=True)
        with col2:
            st.markdown(f"**Cropped ({cropped.size[0]} × {cropped.size[1]})**")
            st.image(cropped, use_container_width=True)

        st.download_button(
            f"💾 {t('download')} Cropped",
            data=_image_to_bytes(cropped, "PNG"),
            file_name="cropped.png",
            mime="image/png",
            use_container_width=True,
            key="download_crop",
        )

        if st.button("📝 Log Crop", use_container_width=True, key="log_crop"):
            log_action("image_cropped", user_id=user_id, category="data",
                       details=f"{cropped.size[0]}x{cropped.size[1]}")

    # ── Resize ──
    with sub2:
        st.markdown(f"**Original size:** {w} × {h}")

        keep_ratio = st.checkbox("🔗 Maintain aspect ratio", value=True, key="resize_keep_ratio")

        c1, c2 = st.columns(2)
        with c1:
            new_w = st.number_input("New width (px)",  min_value=1, max_value=4000,
                                    value=w, step=10, key="resize_w")
        with c2:
            if keep_ratio:
                new_h = int(new_w * (h / w))
                st.number_input("New height (px) — auto", value=new_h,
                                disabled=True, key="resize_h_auto")
            else:
                new_h = st.number_input("New height (px)", min_value=1, max_value=4000,
                                        value=h, step=10, key="resize_h")

        resized = img.resize((int(new_w), int(new_h)), Image.LANCZOS)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Original ({w} × {h})**")
            st.image(img, use_container_width=True)
        with col2:
            st.markdown(f"**Resized ({resized.size[0]} × {resized.size[1]})**")
            st.image(resized, use_container_width=True)

        st.download_button(
            f"💾 {t('download')} Resized",
            data=_image_to_bytes(resized, "PNG"),
            file_name=f"resized_{resized.size[0]}x{resized.size[1]}.png",
            mime="image/png",
            use_container_width=True,
            key="download_resize",
        )

        if st.button("📝 Log Resize", use_container_width=True, key="log_resize"):
            log_action("image_resized", user_id=user_id, category="data",
                       details=f"{w}x{h} -> {resized.size[0]}x{resized.size[1]}")

    # ── Rotate / Flip ──
    with sub3:
        st.markdown(f"**Original size:** {w} × {h}")

        rotation = st.selectbox(
            "🔄 Rotation",
            ["0°", "90° (CW)", "180°", "270° (CCW)"],
            key="rotate_choice",
        )
        flip_h = st.checkbox("↔️ Flip Horizontal", key="flip_h")
        flip_v = st.checkbox("↕️ Flip Vertical",   key="flip_v")

        rotated = img.copy()
        if rotation == "90° (CW)":
            rotated = rotated.rotate(-90, expand=True)
        elif rotation == "180°":
            rotated = rotated.rotate(180, expand=True)
        elif rotation == "270° (CCW)":
            rotated = rotated.rotate(90, expand=True)

        if flip_h:
            rotated = ImageOps.mirror(rotated)
        if flip_v:
            rotated = ImageOps.flip(rotated)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Original**")
            st.image(img, use_container_width=True)
        with col2:
            st.markdown(f"**Result ({rotated.size[0]} × {rotated.size[1]})**")
            st.image(rotated, use_container_width=True)

        st.download_button(
            f"💾 {t('download')} Result",
            data=_image_to_bytes(rotated, "PNG"),
            file_name="rotated.png",
            mime="image/png",
            use_container_width=True,
            key="download_rotate",
        )

        if st.button("📝 Log Rotate", use_container_width=True, key="log_rotate"):
            log_action("image_rotated", user_id=user_id, category="data",
                       details=f"{rotation} flip_h={flip_h} flip_v={flip_v}")


# ═══════════════════════════════════════════════════════════════════════════
# Tab: Gallery / Video / Audio (Original)
# ═══════════════════════════════════════════════════════════════════════════

def _render_gallery():
    _ui(f"""
    <div class="media-panel">
    <div class="panel-header" style="color:#00d4ff;">
    <span class="panel-dot" style="background:#00d4ff;"></span>
    🖼️ IMAGE GALLERY
    </div>
    </div>
    """)

    existing_images = [p for p in IMAGE_FILES if p.exists()]
    if not existing_images:
        st.warning("⚠ No demo images found in assets/images/")
        st.info("Place real1.jpg, real2.jpg, real3.jpg in assets/images/ to see the gallery.")
        return

    cols = st.columns(min(3, len(existing_images)))
    for i, path in enumerate(existing_images):
        with cols[i % 3]:
            b64 = _get_image_b64(path)
            if b64:
                ext = path.suffix.lstrip(".").lower() or "jpeg"
                _ui(f"""
                <div class="gallery-item">
                <img src="data:image/{ext};base64,{b64}" alt="">
                </div>
                """)
                st.caption(f"◆ {path.name}")


def _render_video_viewer():
    _ui(f"""
    <div class="media-panel" style="border-color:rgba(168,85,247,0.18);">
    <div class="panel-header" style="color:#a855f7;">
    <span class="panel-dot" style="background:#a855f7;"></span>
    🎬 VIDEO STREAM
    </div>
    </div>
    """)

    if VIDEO_FILE.exists():
        st.video(str(VIDEO_FILE))
        st.caption(f"◆ {VIDEO_FILE.name}")
    else:
        st.warning("⚠ Video file not found at assets/video/real.mp4")
        upload = st.file_uploader("Or upload a video:", type=["mp4", "mov", "webm"],
                                  key="video_upload_inline")
        if upload:
            st.video(upload)


def _render_audio_viewer():
    _ui(f"""
    <div class="media-panel" style="border-color:rgba(34,197,94,0.18);">
    <div class="panel-header" style="color:#22c55e;">
    <span class="panel-dot" style="background:#22c55e;"></span>
    🎵 AUDIO PLAYBACK
    </div>
    </div>
    """)

    if AUDIO_FILE.exists():
        with open(AUDIO_FILE, "rb") as f:
            st.audio(f.read())
        st.caption(f"◆ {AUDIO_FILE.name}")
    else:
        st.warning("⚠ Audio file not found at assets/audio/real.mp3")
        upload = st.file_uploader("Or upload audio:", type=["mp3", "wav", "ogg"],
                                  key="audio_upload_inline")
        if upload:
            st.audio(upload)


# ═══════════════════════════════════════════════════════════════════════════
# Main Render
# ═══════════════════════════════════════════════════════════════════════════

def render_media():
    init_language()
    apply_rtl_css()

    if not st.session_state.get("logged_in", False):
        st.session_state.page = "login"
        st.rerun()

    user_id = st.session_state.get("user", "anonymous")

    _apply_css()

    # ── Hero ──────────────────────────────────────────────────────────────
    _ui(f"""
    <div class="omnix-hero">
    <h1>{t('media_library').upper()}</h1>
    <div class="hero-tagline">Advanced Multimedia · Filters · Crop · Resize · Rotate</div>
    <div class="hero-pills">
    <span class="hero-pill">🖼 IMAGE</span>
    <span class="hero-pill">🎨 FILTERS</span>
    <span class="hero-pill">✂️ CROP</span>
    <span class="hero-pill">📐 RESIZE</span>
    <span class="hero-pill">🔄 ROTATE</span>
    <span class="hero-pill">🎬 VIDEO</span>
    <span class="hero-pill">🎵 AUDIO</span>
    </div>
    </div>
    """)

    # ── Back Button ───────────────────────────────────────────────────────
    back_col, *_ = st.columns([1.2, 8])
    with back_col:
        if st.button(t("back"), use_container_width=True, key="media_back_btn"):
            st.session_state.page = "home"
            st.rerun()

    # ── PIL Status ────────────────────────────────────────────────────────
    if not _HAS_PIL:
        st.warning(
            "⚠️ **Pillow (PIL) not installed.** Image filters, crop, and resize will not work.\n\n"
            "Install with: `pip install Pillow`"
        )

    # ── Feature Cards ─────────────────────────────────────────────────────
    f1, f2, f3, f4 = st.columns(4)
    features = [
        (f1, "🎨", "FILTERS",      "12 effects (Sepia, Blur, Sharpen...)"),
        (f2, "✂️", "CROP & RESIZE", "Precise control + aspect ratio"),
        (f3, "🖼️", "GALLERY",       "Browse demo images"),
        (f4, "🎬", "PLAYBACK",     "Video and audio streams"),
    ]
    for col, icon, title, desc in features:
        with col:
            _ui(f"""
            <div class="feature-card">
            <div class="fc-icon">{icon}</div>
            <div class="fc-title">{title}</div>
            <div class="fc-desc">{desc}</div>
            </div>
            """)

    st.write("")

    # ── Tabs ──────────────────────────────────────────────────────────────
    tab_filters, tab_crop, tab_gallery, tab_video, tab_audio = st.tabs([
        "🎨 Filters",
        "✂️ Crop & Resize",
        f"🖼️ {t('image_converter')}",
        f"🎬 {t('video_studio')}",
        f"🎵 {t('audio_studio')}",
    ])

    with tab_filters:
        _render_filters_tab(user_id)

    with tab_crop:
        _render_crop_resize_tab(user_id)

    with tab_gallery:
        _render_gallery()

    with tab_video:
        _render_video_viewer()

    with tab_audio:
        _render_audio_viewer()


if __name__ == "__main__":
    render_media()