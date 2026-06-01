"""
═══════════════════════════════════════════════════════════════════════════
OMNIX VISION — Camera AI (Phase 4)
═══════════════════════════════════════════════════════════════════════════
Phase-4 changes:
    ✓ Full translation (EN/AR + RTL)
    ✓ Activity logging
    ✓ Removed dependency on styles/* (uses inline CSS)
    ✓ Graceful fallback if OpenCV/MediaPipe missing
    ✓ Snapshot saving with timestamp
    ✓ Live pose + hand detection
═══════════════════════════════════════════════════════════════════════════
"""

import os
import time
from pathlib import Path

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
# Paths
# ═══════════════════════════════════════════════════════════════════════════
BASE_DIR     = Path(__file__).resolve().parent.parent
SNAPSHOT_DIR = BASE_DIR / "assets" / "images"
SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)


# ═══════════════════════════════════════════════════════════════════════════
# Page Translations
# ═══════════════════════════════════════════════════════════════════════════

CAM_KEYS = {
    "cam_title":      {"en": "AI VISION CENTER",       "ar": "مركز الرؤية الذكية"},
    "cam_subtitle":   {"en": "Real-time camera + pose + hand detection",
                       "ar": "كاميرا حية + كشف الوضعية + اليد"},
    "start_camera":   {"en": "▶ Start Camera",         "ar": "▶ بدء الكاميرا"},
    "stop_camera":    {"en": "⏹ Stop Camera",          "ar": "⏹ إيقاف الكاميرا"},
    "take_snapshot":  {"en": "📸 Take Snapshot",       "ar": "📸 التقاط لقطة"},
    "detection_mode": {"en": "Detection Mode",         "ar": "وضع الكشف"},
    "mode_hand_body": {"en": "Hand + Body",            "ar": "اليد + الجسم"},
    "mode_hand_only": {"en": "Hand Only",              "ar": "اليد فقط"},
    "mode_body_only": {"en": "Body Only",              "ar": "الجسم فقط"},
    "snapshot_saved": {"en": "✅ Snapshot saved!",     "ar": "✅ تم حفظ اللقطة!"},
    "camera_failed":  {"en": "❌ Failed to open camera.", "ar": "❌ فشل فتح الكاميرا."},
    "cv_missing": {
        "en": "⚠️ OpenCV / MediaPipe not installed. Install: pip install opencv-python mediapipe",
        "ar": "⚠️ OpenCV / MediaPipe غير مثبت. ثبّت: pip install opencv-python mediapipe",
    },
    "press_start":     {"en": "Press Start Camera to begin",  "ar": "اضغط بدء الكاميرا للبدء"},
    "snapshots_total": {"en": "Total Snapshots",              "ar": "إجمالي اللقطات"},
    "last_snap_label": {"en": "Last Snapshot",                "ar": "آخر لقطة"},
    "coach_no_person": {"en": "🧍 Please step into camera view", "ar": "🧍 من فضلك ادخل في مجال الكاميرا"},
    "coach_center":    {"en": "🎯 Move toward center",        "ar": "🎯 تحرّك نحو المركز"},
    "coach_ok":        {"en": "✅ You're well-positioned",    "ar": "✅ موضعك ممتاز"},
    "coach_raise":     {"en": "✋ Raise your hand",            "ar": "✋ ارفع يدك"},
    "live_view":       {"en": "Live View",                    "ar": "العرض المباشر"},
    "no_snapshot":     {"en": "No snapshot yet",              "ar": "لا توجد لقطة بعد"},
}


def _t(key: str) -> str:
    from utils.language import get_language_code
    lang = get_language_code()
    if key in CAM_KEYS:
        return CAM_KEYS[key].get(lang, CAM_KEYS[key].get("en", key))
    return t(key)


# ═══════════════════════════════════════════════════════════════════════════
# State Management
# ═══════════════════════════════════════════════════════════════════════════

def init_camera_state():
    defaults = {
        "camera_running":         False,
        "camera_initialized":     False,
        "camera_last_snapshot":   _t("no_snapshot"),
        "camera_snapshot_count":  0,
        "camera_status_text":     _t("press_start"),
        "camera_detection_mode":  "Hand + Body",
        "camera_take_snapshot":   False,
        "camera_ai_state": {
            "person_detected": False,
            "pose_visible":    False,
            "right_hand_up":   False,
            "left_hand_up":    False,
            "body_centered":   False,
            "message":         "Camera not started",
            "status_color":    "#4fc3ff",
        },
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ═══════════════════════════════════════════════════════════════════════════
# CSS
# ═══════════════════════════════════════════════════════════════════════════

def _apply_camera_css():
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
            radial-gradient(ellipse at 90% 5%, rgba(168,85,247,0.10) 0%, transparent 40%),
            linear-gradient(160deg, #020617 0%, #060d1f 55%, #0a0520 100%);
        font-family: 'Rajdhani', sans-serif;
        color: #f8fafc;
    }}

    .block-container {{
        max-width: 1180px;
        padding-top: 1.2rem;
        {"direction: rtl;" if is_ar else ""}
    }}

    .cam-hero {{
        background: linear-gradient(135deg, rgba(2,6,23,0.97), rgba(0,40,60,0.55));
        border: 1px solid rgba(0,212,255,0.30);
        border-radius: 30px;
        padding: 38px 32px;
        text-align: center;
        margin-bottom: 22px;
        box-shadow: 0 0 60px rgba(0,212,255,0.10);
    }}
    .cam-hero h1 {{
        font-family: 'Orbitron', monospace;
        font-size: 38px;
        font-weight: 900;
        margin: 0;
        letter-spacing: 3px;
        background: linear-gradient(90deg, #00d4ff, #a855f7, #00d4ff);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: shimmer 4s linear infinite;
    }}
    @keyframes shimmer {{ to {{ background-position: 200% center; }} }}
    .cam-hero p {{
        color: #94a3b8;
        margin-top: 10px;
        font-size: 13px;
        letter-spacing: 1.5px;
    }}

    .stat-card {{
        background: linear-gradient(145deg, rgba(2,6,23,0.95), rgba(15,23,42,0.78));
        border: 1px solid rgba(0,212,255,0.20);
        border-radius: 16px;
        padding: 14px 18px;
        text-align: center;
        transition: 0.25s ease;
    }}
    .stat-card:hover {{
        border-color: rgba(0,212,255,0.50);
        transform: translateY(-3px);
    }}
    .stat-label {{
        font-family: 'Orbitron', monospace;
        font-size: 10px;
        letter-spacing: 1.5px;
        color: #475569;
        text-transform: uppercase;
        margin-bottom: 6px;
    }}
    .stat-val {{
        font-family: 'Orbitron', monospace;
        font-size: 22px;
        font-weight: 900;
        color: #00d4ff;
    }}
    .stat-val.green {{ color: #22c55e; }}
    .stat-val.red   {{ color: #ef4444; }}
    .stat-val.small {{ font-size: 13px; }}

    .panel {{
        background: linear-gradient(145deg, rgba(15,23,42,0.92), rgba(2,6,23,0.78));
        border: 1px solid rgba(0,212,255,0.22);
        border-radius: 22px;
        padding: 22px;
        margin-bottom: 18px;
    }}
    .panel-title {{
        color: #00d4ff;
        font-family: 'Orbitron', monospace;
        font-size: 16px;
        font-weight: 900;
        margin-bottom: 12px;
        letter-spacing: 1px;
        {"text-align: right;" if is_ar else ""}
    }}

    .signal-row {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 14px;
        background: rgba(2,6,23,0.55);
        border-radius: 10px;
        margin: 6px 0;
        font-size: 13.5px;
        {"flex-direction: row-reverse;" if is_ar else ""}
    }}
    .signal-row span:first-child {{ color: #cbd5e1; }}
    .badge {{
        padding: 4px 12px;
        border-radius: 999px;
        font-family: 'Orbitron', monospace;
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 1px;
    }}
    .badge.on {{
        background: rgba(34,197,94,0.18);
        color: #22c55e;
        border: 1px solid rgba(34,197,94,0.45);
    }}
    .badge.off {{
        background: rgba(239,68,68,0.16);
        color: #ef4444;
        border: 1px solid rgba(239,68,68,0.45);
    }}

    .coach-box {{
        background: linear-gradient(135deg, rgba(0,212,255,0.10), rgba(2,6,23,0.95));
        border: 1px solid rgba(0,212,255,0.35);
        border-radius: 14px;
        padding: 14px 18px;
        margin: 12px 0;
        font-size: 14px;
        color: #e0f2fe;
        font-weight: 600;
        text-align: center;
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
        min-height: 46px !important;
        box-shadow: 0 4px 18px rgba(14,165,233,0.20) !important;
        transition: 0.25s ease !important;
    }}
    .stButton > button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 28px rgba(124,58,237,0.35) !important;
    }}
    .stButton > button[kind="secondary"] {{
        background: linear-gradient(135deg, #ef4444 0%, #991b1b 100%) !important;
        box-shadow: 0 4px 18px rgba(239,68,68,0.20) !important;
    }}
    </style>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# Camera Loop
# ═══════════════════════════════════════════════════════════════════════════

def _process_frame(frame, hands, pose, detection_mode: str) -> dict:
    """Process one frame and return analysis dict."""
    h, w = frame.shape[:2]
    rgb  = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    state = {
        "person_detected": False,
        "pose_visible":    False,
        "right_hand_up":   False,
        "left_hand_up":    False,
        "body_centered":   False,
        "message":         "",
        "status_color":    "#4fc3ff",
    }

    # Pose detection
    if detection_mode in ("Hand + Body", "Body Only"):
        pose_results = pose.process(rgb)
        if pose_results.pose_landmarks:
            state["person_detected"] = True
            state["pose_visible"]    = True

            # Body-centered check (nose roughly in center 1/3)
            nose = pose_results.pose_landmarks.landmark[0]
            if 0.3 < nose.x < 0.7:
                state["body_centered"] = True

            # Draw skeleton
            mp.solutions.drawing_utils.draw_landmarks(
                frame,
                pose_results.pose_landmarks,
                mp.solutions.pose.POSE_CONNECTIONS,
            )

    # Hand detection
    if detection_mode in ("Hand + Body", "Hand Only"):
        hands_results = hands.process(rgb)
        if hands_results.multi_hand_landmarks and hands_results.multi_handedness:
            state["person_detected"] = True
            for landmarks, handedness in zip(
                hands_results.multi_hand_landmarks,
                hands_results.multi_handedness,
            ):
                label = handedness.classification[0].label  # mirrored

                # Hand "raised" if wrist is in upper half
                wrist_y = landmarks.landmark[0].y
                if wrist_y < 0.55:
                    if label == "Left":   # user's right
                        state["right_hand_up"] = True
                    else:
                        state["left_hand_up"] = True

                mp.solutions.drawing_utils.draw_landmarks(
                    frame,
                    landmarks,
                    mp.solutions.hands.HAND_CONNECTIONS,
                )

    # Coach message
    if not state["person_detected"]:
        state["message"] = _t("coach_no_person")
        state["status_color"] = "#ff9800"
    elif not state["body_centered"] and state["pose_visible"]:
        state["message"] = _t("coach_center")
        state["status_color"] = "#facc15"
    elif state["right_hand_up"] or state["left_hand_up"]:
        state["message"] = _t("coach_ok")
        state["status_color"] = "#22c55e"
    else:
        state["message"] = _t("coach_raise")
        state["status_color"] = "#38bdf8"

    return state


def _save_snapshot(frame) -> str:
    """Save the current frame and return the filename."""
    ts = time.strftime("%Y%m%d_%H%M%S")
    name = f"snapshot_{ts}.jpg"
    path = SNAPSHOT_DIR / name
    cv2.imwrite(str(path), frame)
    return name


def _camera_loop():
    """Run the live camera loop using OpenCV + MediaPipe."""
    if not _HAS_CV:
        return

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        st.error(_t("camera_failed"))
        st.session_state.camera_running = False
        return

    mp_hands = mp.solutions.hands
    mp_pose  = mp.solutions.pose

    frame_placeholder  = st.empty()
    status_placeholder = st.empty()

    user_id = st.session_state.get("user", "anonymous")

    try:
        with mp_hands.Hands(
            max_num_hands=2,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.5,
        ) as hands, mp_pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        ) as pose:

            while st.session_state.get("camera_running", False):
                ret, frame = cap.read()
                if not ret:
                    break

                frame = cv2.flip(frame, 1)  # mirror

                state = _process_frame(
                    frame, hands, pose,
                    st.session_state.camera_detection_mode,
                )

                # Update session state
                st.session_state.camera_ai_state    = state
                st.session_state.camera_status_text = state["message"]

                # Overlay text
                cv2.putText(
                    frame, state["message"][:50],
                    (12, 36), cv2.FONT_HERSHEY_SIMPLEX,
                    0.7, (255, 255, 255), 2,
                )

                # Take snapshot if requested
                if st.session_state.get("camera_take_snapshot"):
                    fname = _save_snapshot(frame)
                    st.session_state.camera_last_snapshot   = fname
                    st.session_state.camera_snapshot_count += 1
                    st.session_state.camera_take_snapshot   = False
                    log_action("snapshot_saved",
                               user_id=user_id, category="data",
                               details=fname)

                # Display
                frame_placeholder.image(
                    cv2.cvtColor(frame, cv2.COLOR_BGR2RGB),
                    channels="RGB",
                    use_container_width=True,
                )
                _color = state["status_color"]
                _msg   = state["message"]
                status_placeholder.markdown(
                    f"<div class='coach-box' style='border-color:{_color};'>{_msg}</div>",
                    unsafe_allow_html=True,
                )

                time.sleep(0.03)
    finally:
        cap.release()


# ═══════════════════════════════════════════════════════════════════════════
# Main Render
# ═══════════════════════════════════════════════════════════════════════════

def render_camera():
    init_language()
    apply_rtl_css()
    init_camera_state()
    _apply_camera_css()

    if not st.session_state.get("logged_in", False):
        st.session_state.page = "login"
        st.rerun()

    user_id = st.session_state.get("user", "anonymous")

    # ── Hero ──────────────────────────────────────────────────────────────
    st.markdown(f"""
<div class="cam-hero">
<h1>🧠 {_t('cam_title')}</h1>
<p>{_t('cam_subtitle')}</p>
</div>
    """, unsafe_allow_html=True)

    # ── Back ──────────────────────────────────────────────────────────────
    back_col, _ = st.columns([1.3, 8])
    with back_col:
        if st.button(t("back"), use_container_width=True, key="cam_back_btn"):
            st.session_state.camera_running = False
            st.session_state.page = "home"
            st.rerun()

    # ── CV check ──────────────────────────────────────────────────────────
    if not _HAS_CV:
        st.error(_t("cv_missing"))
        return

    # ── Stat Cards ────────────────────────────────────────────────────────
    state = st.session_state.camera_ai_state

    s1, s2, s3, s4 = st.columns(4)

    with s1:
        running = st.session_state.camera_running
        st.markdown(f"""
<div class="stat-card">
<div class="stat-label">{t('camera')}</div>
<div class="stat-val {'green' if running else 'red'}">{'● ON' if running else '● OFF'}</div>
</div>
        """, unsafe_allow_html=True)

    with s2:
        st.markdown(f"""
<div class="stat-card">
<div class="stat-label">{_t('snapshots_total')}</div>
<div class="stat-val">{st.session_state.camera_snapshot_count}</div>
</div>
        """, unsafe_allow_html=True)

    with s3:
        last = st.session_state.camera_last_snapshot
        st.markdown(f"""
<div class="stat-card">
<div class="stat-label">{_t('last_snap_label')}</div>
<div class="stat-val small">{last[:18]}</div>
</div>
        """, unsafe_allow_html=True)

    with s4:
        mode = st.session_state.camera_detection_mode
        st.markdown(f"""
<div class="stat-card">
<div class="stat-label">{_t('detection_mode')}</div>
<div class="stat-val small">{mode}</div>
</div>
        """, unsafe_allow_html=True)

    st.write("")

    # ── Controls ──────────────────────────────────────────────────────────
    c1, c2, c3 = st.columns(3)

    with c1:
        if not st.session_state.camera_running:
            if st.button(_t("start_camera"), use_container_width=True, key="cam_start_btn"):
                st.session_state.camera_running = True
                log_action("camera_started", user_id=user_id, category="data")
                st.rerun()
        else:
            if st.button(_t("stop_camera"), use_container_width=True,
                         type="secondary", key="cam_stop_btn"):
                st.session_state.camera_running = False
                log_action("camera_stopped", user_id=user_id, category="data")
                st.rerun()

    with c2:
        if st.button(_t("take_snapshot"),
                     use_container_width=True,
                     disabled=not st.session_state.camera_running,
                     key="cam_snap_btn"):
            st.session_state.camera_take_snapshot = True

    with c3:
        mode_options = ["Hand + Body", "Hand Only", "Body Only"]
        idx = mode_options.index(st.session_state.camera_detection_mode) \
              if st.session_state.camera_detection_mode in mode_options else 0
        new_mode = st.selectbox(
            _t("detection_mode"),
            mode_options,
            index=idx,
            key="cam_mode_select",
            label_visibility="collapsed",
        )
        if new_mode != st.session_state.camera_detection_mode:
            st.session_state.camera_detection_mode = new_mode

    # ── Layout: Camera feed + status panel ────────────────────────────────
    left_col, right_col = st.columns([1.6, 1.0])

    with left_col:
        st.markdown(f"""
<div class="panel">
<div class="panel-title">📹 {_t('live_view')}</div>
</div>
        """, unsafe_allow_html=True)

        if st.session_state.camera_running:
            _camera_loop()
        else:
            st.info(_t("press_start"))

    with right_col:
        st.markdown(f"""
<div class="panel">
<div class="panel-title">📊 {t('ai_vision')}</div>
</div>
        """, unsafe_allow_html=True)

        signals = [
            (t("person_detected"), state.get("person_detected")),
            (t("pose_visible"),    state.get("pose_visible")),
            (t("right_hand"),      state.get("right_hand_up")),
            (t("left_hand"),       state.get("left_hand_up")),
            (t("body_centered"),   state.get("body_centered")),
        ]
        for label, val in signals:
            badge = '<span class="badge on">● ACTIVE</span>' if val \
                    else '<span class="badge off">● INACTIVE</span>'
            st.markdown(f"""
<div class="signal-row">
<span>{label}</span>{badge}
</div>
            """, unsafe_allow_html=True)