"""
═══════════════════════════════════════════════════════════════════════════
OMNIX VISION — Hand Scan Authentication (Phase 4)
═══════════════════════════════════════════════════════════════════════════
Phase-4 changes:
    ✓ Full translation (EN/AR + RTL)
    ✓ Activity logging
    ✓ Removed dependency on styles/* (uses inline CSS)
    ✓ Graceful fallback if OpenCV/MediaPipe missing
    ✓ All scan logic preserved

Logic:
    User shows hand for 5 seconds to camera.
    • Right hand raised → Access GRANTED → goes to home
    • Left hand raised  → Access DENIED  → back to login
═══════════════════════════════════════════════════════════════════════════
"""

import time
import streamlit as st

from utils.language import t, init_language, apply_rtl_css, is_rtl
from utils.activity import log_action


# Optional CV imports
try:
    import cv2
    import mediapipe as mp
    _HAS_CV = True
except ImportError:
    _HAS_CV = False


# ═══════════════════════════════════════════════════════════════════════════
# Page-specific translation
# ═══════════════════════════════════════════════════════════════════════════
SCAN_KEYS = {
    "scan_title":     {"en": "HAND SCAN AUTH",
                       "ar": "مصادقة فحص اليد"},
    "scan_subtitle":  {"en": "Raise your hand for 5 seconds to authenticate",
                       "ar": "ارفع يدك لمدة 5 ثوانٍ للمصادقة"},
    "right_hand_grants": {"en": "Right Hand → GRANT", "ar": "اليد اليمنى → السماح"},
    "left_hand_denies":  {"en": "Left Hand → DENY",   "ar": "اليد اليسرى → الرفض"},
    "scan_duration":     {"en": "Scan Duration: 5s",  "ar": "مدة المسح: 5 ثوانٍ"},
    "start_scan":     {"en": "▶ Start Scan",  "ar": "▶ ابدأ المسح"},
    "reset_scan":     {"en": "⟳ Reset",        "ar": "⟳ إعادة"},
    "scanning":       {"en": "Scanning…",       "ar": "جاري المسح…"},
    "waiting":        {"en": "Waiting to start", "ar": "بانتظار البدء"},
    "remaining":      {"en": "Time Remaining",  "ar": "الوقت المتبقي"},
    "right_count":    {"en": "Right Frames",    "ar": "إطارات يمنى"},
    "left_count":     {"en": "Left Frames",     "ar": "إطارات يسرى"},
    "access_granted": {"en": "✅ ACCESS GRANTED", "ar": "✅ تم السماح بالوصول"},
    "access_denied":  {"en": "🚫 ACCESS DENIED",  "ar": "🚫 تم رفض الوصول"},
    "inconclusive":   {"en": "⚠️ Inconclusive Result", "ar": "⚠️ نتيجة غير حاسمة"},
    "redirect_home":  {"en": "Redirecting to Home…",  "ar": "إعادة التوجيه للصفحة الرئيسية…"},
    "redirect_login": {"en": "Returning to Login…",   "ar": "العودة لتسجيل الدخول…"},
    "cv_missing":     {
        "en": "⚠️ OpenCV / MediaPipe not installed. Install: pip install opencv-python mediapipe",
        "ar": "⚠️ OpenCV / MediaPipe غير مثبت. ثبّت: pip install opencv-python mediapipe",
    },
    "camera_failed": {
        "en": "❌ Failed to open camera. Check device permissions.",
        "ar": "❌ فشل فتح الكاميرا. تحقق من أذونات الجهاز.",
    },
    "show_hand_msg": {
        "en": "👋 Show your hand clearly to the camera",
        "ar": "👋 أظهر يدك بوضوح أمام الكاميرا",
    },
}


def _t(key: str) -> str:
    from utils.language import get_language_code
    lang = get_language_code()
    if key in SCAN_KEYS:
        return SCAN_KEYS[key].get(lang, SCAN_KEYS[key].get("en", key))
    return t(key)


# ═══════════════════════════════════════════════════════════════════════════
# State Management
# ═══════════════════════════════════════════════════════════════════════════

def init_hand_scan_state():
    defaults = {
        "hand_phase":            "waiting",
        "hand_scan_started":     False,
        "hand_scan_start_time":  None,
        "hand_right_count":      0,
        "hand_left_count":       0,
        "hand_result":           None,
        "hand_scan_run":         False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_hand_scan():
    st.session_state.hand_phase           = "waiting"
    st.session_state.hand_scan_started    = False
    st.session_state.hand_scan_start_time = None
    st.session_state.hand_right_count     = 0
    st.session_state.hand_left_count      = 0
    st.session_state.hand_result          = None
    st.session_state.hand_scan_run        = False


# ═══════════════════════════════════════════════════════════════════════════
# CSS
# ═══════════════════════════════════════════════════════════════════════════

def _apply_scan_css():
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

    .stApp {{
        background:
            radial-gradient(ellipse at 10% 10%, rgba(0,212,255,0.12) 0%, transparent 42%),
            radial-gradient(ellipse at 90% 5%, rgba(0,255,136,0.08) 0%, transparent 38%),
            linear-gradient(160deg, #020617 0%, #040f1e 60%, #020617 100%);
        font-family: 'Rajdhani', sans-serif;
        color: #f8fafc;
    }}
    .stApp::before {{
        content: '';
        position: fixed; inset: 0;
        background-image: radial-gradient(rgba(0,212,255,0.05) 1px, transparent 1px);
        background-size: 36px 36px;
        pointer-events: none; z-index: 0;
    }}

    .block-container {{
        max-width: 1180px;
        padding-top: 1.2rem;
        {"direction: rtl;" if is_ar else ""}
    }}

    .scan-hero {{
        background: linear-gradient(135deg, rgba(2,6,23,0.97), rgba(0,40,60,0.70));
        border: 1px solid rgba(0,212,255,0.30);
        border-radius: 30px;
        padding: 38px 32px;
        text-align: center;
        position: relative;
        overflow: hidden;
        margin-bottom: 22px;
        box-shadow: 0 0 60px rgba(0,212,255,0.15);
    }}
    .scan-hero::before {{
        content: '';
        position: absolute; bottom: 0; left: 0; right: 0; height: 2px;
        background: linear-gradient(90deg, transparent, #00d4ff, #00ff88, transparent);
        animation: scanline 3s linear infinite;
    }}
    @keyframes scanline {{ 0%,100% {{opacity:0.35}} 50% {{opacity:1}} }}
    .scan-hero h1 {{
        font-family: 'Orbitron', monospace;
        font-size: 38px;
        font-weight: 900;
        margin: 0;
        letter-spacing: 4px;
        background: linear-gradient(90deg, #00d4ff, #00ff88, #00d4ff);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: shimmer 4s linear infinite;
    }}
    @keyframes shimmer {{ to {{ background-position: 200% center; }} }}
    .scan-hero p {{
        color: #94a3b8;
        margin-top: 12px;
        font-size: 13px;
        letter-spacing: 2px;
        text-transform: uppercase;
    }}

    .info-chips {{
        display: flex;
        gap: 14px;
        margin-bottom: 18px;
        flex-wrap: wrap;
    }}
    .info-chip {{
        flex: 1;
        min-width: 180px;
        background: linear-gradient(145deg, rgba(2,6,23,0.95), rgba(15,23,42,0.78));
        border: 1px solid rgba(0,212,255,0.22);
        border-radius: 18px;
        padding: 14px 18px;
        text-align: center;
    }}
    .info-chip.grant {{ border-color: rgba(0,255,136,0.35); }}
    .info-chip.deny  {{ border-color: rgba(255,82,82,0.35); }}
    .info-chip.time  {{ border-color: rgba(255,213,79,0.35); }}

    .chip-label {{
        font-family: 'Orbitron', monospace;
        font-size: 10px;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        color: #475569;
        margin-bottom: 5px;
    }}
    .chip-val {{
        font-family: 'Orbitron', monospace;
        font-size: 15px;
        font-weight: 700;
    }}
    .chip-val.grant {{ color: #00ff88; }}
    .chip-val.deny  {{ color: #ff5252; }}
    .chip-val.time  {{ color: #ffd54f; }}

    .stat-grid {{
        display: grid;
        grid-template-columns: 1fr 1fr 1fr;
        gap: 12px;
        margin-bottom: 18px;
    }}
    .stat-cell {{
        background: rgba(2,6,23,0.85);
        border: 1px solid rgba(0,212,255,0.20);
        border-radius: 16px;
        padding: 14px 18px;
        text-align: center;
    }}
    .stat-cell-label {{
        font-family: 'Orbitron', monospace;
        font-size: 10px;
        letter-spacing: 1.5px;
        color: #475569;
        margin-bottom: 6px;
    }}
    .stat-cell-val {{
        font-family: 'Orbitron', monospace;
        font-size: 28px;
        font-weight: 900;
        color: #00d4ff;
    }}

    .result-banner {{
        border-radius: 22px;
        padding: 30px 24px;
        text-align: center;
        margin: 18px 0;
        font-family: 'Orbitron', monospace;
        font-size: 22px;
        font-weight: 900;
        letter-spacing: 2px;
        animation: resultPop 0.5s cubic-bezier(0.34,1.56,0.64,1);
    }}
    .result-banner.granted {{
        background: linear-gradient(135deg, rgba(0,255,136,0.18), rgba(2,6,23,0.95));
        border: 2px solid rgba(0,255,136,0.55);
        color: #00ff88;
        box-shadow: 0 0 40px rgba(0,255,136,0.25);
    }}
    .result-banner.denied {{
        background: linear-gradient(135deg, rgba(255,82,82,0.18), rgba(2,6,23,0.95));
        border: 2px solid rgba(255,82,82,0.55);
        color: #ff5252;
        box-shadow: 0 0 40px rgba(255,82,82,0.25);
    }}
    .result-banner.warn {{
        background: linear-gradient(135deg, rgba(255,213,79,0.18), rgba(2,6,23,0.95));
        border: 2px solid rgba(255,213,79,0.55);
        color: #ffd54f;
        box-shadow: 0 0 40px rgba(255,213,79,0.25);
    }}
    @keyframes resultPop {{
        from {{ transform: scale(0.85); opacity: 0; }}
        to {{ transform: scale(1); opacity: 1; }}
    }}

    .stButton > button {{
        background: linear-gradient(135deg, #0ea5e9 0%, #7c3aed 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 14px !important;
        padding: 12px 20px !important;
        font-weight: 800 !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-size: 15px !important;
        min-height: 48px !important;
        box-shadow: 0 4px 20px rgba(14,165,233,0.18) !important;
        transition: 0.28s ease !important;
    }}
    .stButton > button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 28px rgba(124,58,237,0.35) !important;
    }}
    .stButton > button[kind="secondary"] {{
        background: linear-gradient(135deg, #ef4444 0%, #991b1b 100%) !important;
        box-shadow: 0 4px 20px rgba(239,68,68,0.18) !important;
    }}
    </style>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# Scan Logic (with MediaPipe if available)
# ═══════════════════════════════════════════════════════════════════════════

def _run_scan_loop(frame_placeholder, status_placeholder,
                   timer_placeholder, scan_duration: int = 5):
    """Run hand scan only after detecting a hand."""

    if not _HAS_CV:
        return None

    mp_hands = mp.solutions.hands
    mp_draw = mp.solutions.drawing_utils
    mp_style = mp.solutions.drawing_styles

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        status_placeholder.error(_t("camera_failed"))
        return None

    right_count = 0
    left_count = 0

    # يبدأ فارغ وينطلق فقط بعد اكتشاف اليد
    start_time = None

    with mp_hands.Hands(
        max_num_hands=2,
        min_detection_confidence=0.6,
        min_tracking_confidence=0.5,
    ) as hands:
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                # Mirror for natural UX
                frame = cv2.flip(frame, 1)

                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = hands.process(rgb_frame)

                hand_detected = False

                if results.multi_hand_landmarks and results.multi_handedness:
                    hand_detected = True

                    # يبدأ العد فقط عند أول ظهور لليد
                    if start_time is None:
                        start_time = time.time()

                    for hand_landmarks, handedness in zip(
                        results.multi_hand_landmarks,
                        results.multi_handedness,
                    ):
                        label = handedness.classification[0].label

                        # تصحيح اتجاه اليد
                        if label == "Right":
                            right_count += 1
                        elif label == "Left":
                            left_count += 1

                        mp_draw.draw_landmarks(
                            frame,
                            hand_landmarks,
                            mp_hands.HAND_CONNECTIONS,
                            mp_style.get_default_hand_landmarks_style(),
                            mp_style.get_default_hand_connections_style(),
                        )

                # إذا لم تُكتشف يد بعد → لا يبدأ العد
                if start_time is None:
                    remaining = scan_duration
                    status_placeholder.info(_t("show_hand_msg"))
                else:
                    elapsed = time.time() - start_time
                    remaining = max(0, scan_duration - elapsed)
                    status_placeholder.info(_t("scanning"))

                # انتهاء المسح بعد 5 ثواني من أول اكتشاف يد
                if start_time is not None and remaining <= 0:
                    break

                # Overlay
                cv2.putText(
                    frame,
                    f"Time: {remaining:.1f}s",
                    (12, 36),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.0,
                    (255, 255, 0),
                    2,
                )

                cv2.putText(
                    frame,
                    f"R:{right_count}  L:{left_count}",
                    (12, 72),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.75,
                    (0, 255, 200),
                    2,
                )

                frame_placeholder.image(
                    cv2.cvtColor(frame, cv2.COLOR_BGR2RGB),
                    channels="RGB",
                    use_container_width=True,
                )

                timer_placeholder.markdown(
                    f"""
                    <div class='stat-cell-val' style='font-size:30px;'>
                        ⏱️ {remaining:.1f}s
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                time.sleep(0.03)

        finally:
            cap.release()

    return {
        "right": right_count,
        "left": left_count
    }


# ═══════════════════════════════════════════════════════════════════════════
# Main Render
# ═══════════════════════════════════════════════════════════════════════════

def render_hand_scan():
    init_language()
    apply_rtl_css()
    init_hand_scan_state()
    _apply_scan_css()

    # ── Hero ──────────────────────────────────────────────────────────────
    st.markdown(f"""
<div class="scan-hero">
<h1>🖐️ {_t('scan_title')}</h1>
<p>{_t('scan_subtitle')}</p>
</div>
    """, unsafe_allow_html=True)

    # ── Back ──────────────────────────────────────────────────────────────
    back_col, _ = st.columns([1.3, 8])
    with back_col:
        if st.button(t("back"), use_container_width=True, key="scan_back_btn"):
            reset_hand_scan()
            st.session_state.page      = "login"
            st.session_state.auth_mode = "select"
            st.rerun()

    # ── Info Chips ────────────────────────────────────────────────────────
    st.markdown(f"""
<div class="info-chips">
<div class="info-chip grant">
<div class="chip-label">{_t('right_hand_grants')}</div>
<div class="chip-val grant">✅ GRANT</div>
</div>
<div class="info-chip deny">
<div class="chip-label">{_t('left_hand_denies')}</div>
<div class="chip-val deny">🚫 DENY</div>
</div>
<div class="info-chip time">
<div class="chip-label">{_t('scan_duration')}</div>
<div class="chip-val time">⏱ 5 SEC</div>
</div>
</div>
    """, unsafe_allow_html=True)

    # ── CV availability check ─────────────────────────────────────────────
    if not _HAS_CV:
        st.error(_t("cv_missing"))
        st.info(
            "💡 Hand Scan requires `opencv-python` and `mediapipe`. "
            "Install them and reload the page."
        )
        if st.button(t("back"), use_container_width=True, key="scan_back_no_cv"):
            st.session_state.page      = "login"
            st.session_state.auth_mode = "select"
            st.rerun()
        return

    # ── Stats Grid ────────────────────────────────────────────────────────
    st.markdown(f"""
<div class="stat-grid">
<div class="stat-cell">
<div class="stat-cell-label">{_t('right_count')}</div>
<div class="stat-cell-val" style="color:#00ff88;">{st.session_state.hand_right_count}</div>
</div>
<div class="stat-cell">
<div class="stat-cell-label">{_t('left_count')}</div>
<div class="stat-cell-val" style="color:#ff5252;">{st.session_state.hand_left_count}</div>
</div>
<div class="stat-cell">
<div class="stat-cell-label">{_t('status')}</div>
<div class="stat-cell-val" style="font-size:14px;">{st.session_state.hand_phase.upper()}</div>
</div>
</div>
    """, unsafe_allow_html=True)

    # ── Controls ──────────────────────────────────────────────────────────
    c1, c2 = st.columns(2)
    with c1:
        start_clicked = st.button(
            _t("start_scan"),
            use_container_width=True,
            key="scan_start_btn",
            disabled=st.session_state.hand_phase == "scanning",
        )
    with c2:
        if st.button(_t("reset_scan"),
                     use_container_width=True,
                     type="secondary",
                     key="scan_reset_btn"):
            reset_hand_scan()
            st.rerun()

    # ── Frame placeholders ────────────────────────────────────────────────
    timer_placeholder  = st.empty()
    status_placeholder = st.empty()
    frame_placeholder  = st.empty()

    # ── Show instruction if waiting ──
    if st.session_state.hand_phase == "waiting":
        status_placeholder.info(_t("show_hand_msg"))

    # ── Trigger scan ──────────────────────────────────────────────────────
    if start_clicked and st.session_state.hand_phase != "scanning":
        st.session_state.hand_phase = "scanning"
        log_action("hand_scan_started",
                   user_id=st.session_state.get("user", "anonymous"),
                   category="auth")

        result = _run_scan_loop(frame_placeholder, status_placeholder, timer_placeholder)

        if result is not None:
            st.session_state.hand_right_count = result["right"]
            st.session_state.hand_left_count  = result["left"]

            # Decision
            r, l = result["right"], result["left"]
            if r > l and r >= 8:
                st.session_state.hand_result = "granted"
            elif l > r and l >= 8:
                st.session_state.hand_result = "denied"
            else:
                st.session_state.hand_result = "inconclusive"

            st.session_state.hand_phase = "completed"
            log_action("hand_scan_completed",
                       user_id=st.session_state.get("user", "anonymous"),
                       category="auth",
                       details=f"R={r}, L={l}, result={st.session_state.hand_result}")

        st.rerun()

    # ── Show result if completed ──────────────────────────────────────────
    if st.session_state.hand_phase == "completed":
        result = st.session_state.hand_result

        if result == "granted":
            st.markdown(f"""
<div class="result-banner granted">
{_t('access_granted')}<br>
<span style="font-size:14px;letter-spacing:1px;font-weight:400;color:#94a3b8;">
{_t('redirect_home')}
</span>
</div>
            """, unsafe_allow_html=True)

            # Mark as logged in
            st.session_state.logged_in    = True
            st.session_state.login_method = "hand_scan"
            if not st.session_state.get("user"):
                st.session_state.user = "hand_user"

            log_action("hand_scan_access_granted",
                       user_id=st.session_state.user,
                       category="auth")

            time.sleep(2.0)
            st.session_state.page = "home"
            reset_hand_scan()
            st.rerun()

        elif result == "denied":
            st.markdown(f"""
<div class="result-banner denied">
{_t('access_denied')}<br>
<span style="font-size:14px;letter-spacing:1px;font-weight:400;color:#94a3b8;">
{_t('redirect_login')}
</span>
</div>
            """, unsafe_allow_html=True)

            log_action("hand_scan_access_denied",
                       user_id=st.session_state.get("user", "anonymous"),
                       category="auth")

            time.sleep(2.0)
            st.session_state.page      = "login"
            st.session_state.auth_mode = "select"
            reset_hand_scan()
            st.rerun()

        else:  # inconclusive
            st.markdown(f"""
<div class="result-banner warn">
{_t('inconclusive')}<br>
<span style="font-size:14px;letter-spacing:1px;font-weight:400;color:#94a3b8;">
{_t('reset_timer')} ➤
</span>
</div>
            """, unsafe_allow_html=True)