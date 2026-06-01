"""
═══════════════════════════════════════════════════════════════════════════
OMNIX VISION — Dashboard Page (Phase 2)
═══════════════════════════════════════════════════════════════════════════
Phase-2 changes:
    ✓ Full translation support (English + Arabic)
    ✓ Plotly charts for file distribution and activity trends
    ✓ Activity log integration (recent actions panel)
    ✓ RTL layout when Arabic
    ✓ Quick links to Security Center & Activity Log
═══════════════════════════════════════════════════════════════════════════
Falls back gracefully if plotly is not installed.
═══════════════════════════════════════════════════════════════════════════
"""

import os
from datetime import datetime, timedelta
import streamlit as st

from utils.language import t, init_language, apply_rtl_css, is_rtl
from utils.activity import get_log, get_stats

# Plotly is optional — graceful fallback
try:
    import plotly.graph_objects as go
    _HAS_PLOTLY = True
except ImportError:
    _HAS_PLOTLY = False


# ══════════════════════════════════════════════════════════════════════════
# Helpers
# ══════════════════════════════════════════════════════════════════════════

def _count_files(folder_path: str) -> int:
    """Count all files recursively in a folder."""
    if not os.path.exists(folder_path):
        return 0
    total = 0
    for _, _, files in os.walk(folder_path):
        total += len(files)
    return total


def _get_last_file(folder_path: str) -> str:
    """Return the most recently modified filename in a folder."""
    if not os.path.exists(folder_path):
        return "—"
    all_files = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            all_files.append(os.path.join(root, file))
    if not all_files:
        return "—"
    return os.path.basename(max(all_files, key=os.path.getmtime))


def _folder_size_mb(folder_path: str) -> float:
    """Return folder size in MB."""
    if not os.path.exists(folder_path):
        return 0.0
    total = 0
    for root, _, files in os.walk(folder_path):
        for file in files:
            try:
                total += os.path.getsize(os.path.join(root, file))
            except OSError:
                pass
    return round(total / (1024 * 1024), 2)


def _get_current_user() -> str:
    """Return current user_id or 'Unknown'."""
    user = st.session_state.get("user")
    if isinstance(user, dict):
        return user.get("username", "Unknown")
    if isinstance(user, str):
        return user
    return "Unknown"


def _get_camera_state() -> dict:
    """Return camera state with safe defaults."""
    default_state = {
        "camera_running":  False,
        "message":         "No camera state available.",
        "person_detected": False,
        "pose_visible":    False,
        "right_hand":      False,
        "left_hand":       False,
        "body_centered":   False,
        "last_snapshot":   "—",
    }
    state = st.session_state.get("camera_state", default_state)
    if not isinstance(state, dict):
        state = default_state
    for k, v in default_state.items():
        state.setdefault(k, v)
    return state


def _status_badge(value: bool) -> str:
    """Return colored ACTIVE/INACTIVE badge HTML."""
    if value:
        return ('<span style="background:rgba(34,197,94,0.18);color:#22c55e;'
                'border:1px solid rgba(34,197,94,0.48);padding:5px 11px;'
                'border-radius:999px;font-weight:700;font-size:11px;">'
                '● ACTIVE</span>')
    return ('<span style="background:rgba(239,68,68,0.16);color:#ef4444;'
            'border:1px solid rgba(239,68,68,0.48);padding:5px 11px;'
            'border-radius:999px;font-weight:700;font-size:11px;">'
            '● INACTIVE</span>')


# ══════════════════════════════════════════════════════════════════════════
# Charts
# ══════════════════════════════════════════════════════════════════════════

def _render_files_chart(images: int, audio: int, video: int, uploads: int):
    """Render a Plotly donut chart of file distribution."""
    if not _HAS_PLOTLY:
        st.info("📊 Install `plotly` to see interactive charts: `pip install plotly`")
        return

    if images + audio + video + uploads == 0:
        st.info(f"📊 {t('no_activity')}")
        return

    labels = [t("images"), t("audio"), t("video"), t("uploads")]
    values = [images, audio, video, uploads]
    colors = ["#38bdf8", "#a855f7", "#22c55e", "#fb923c"]

    fig = go.Figure(
        data=[go.Pie(
            labels=labels, values=values, hole=0.6,
            marker=dict(colors=colors, line=dict(color="#020617", width=2)),
            textinfo="label+percent",
            textfont=dict(size=12, family="Rajdhani"),
            hovertemplate="%{label}: %{value} (%{percent})<extra></extra>",
        )]
    )
    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="h", y=-0.1, font=dict(color="#cbd5e1", size=11)),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#cbd5e1"),
        margin=dict(t=10, b=10, l=10, r=10),
        height=300,
        annotations=[dict(
            text=f"<b>{sum(values)}</b><br><span style='font-size:11px'>{t('total_files')}</span>",
            x=0.5, y=0.5, font=dict(size=22, color="#38bdf8"),
            showarrow=False,
        )]
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def _render_activity_chart():
    """Render a line chart of activity over the last 7 days."""
    if not _HAS_PLOTLY:
        return

    all_entries = get_log()
    if not all_entries:
        st.info(f"📊 {t('no_activity')}")
        return

    # Group by day (last 7 days)
    today = datetime.now().date()
    days = [today - timedelta(days=i) for i in range(6, -1, -1)]
    counts = {d: 0 for d in days}

    for entry in all_entries:
        try:
            d = datetime.fromtimestamp(entry["timestamp"]).date()
            if d in counts:
                counts[d] += 1
        except (KeyError, OSError, ValueError):
            continue

    x_labels = [d.strftime("%a %d") for d in days]
    y_values = [counts[d] for d in days]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x_labels, y=y_values, mode="lines+markers",
        line=dict(color="#38bdf8", width=3, shape="spline"),
        marker=dict(size=10, color="#a855f7",
                    line=dict(color="#38bdf8", width=2)),
        fill="tozeroy",
        fillcolor="rgba(56,189,248,0.15)",
        hovertemplate="<b>%{x}</b><br>%{y} actions<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#cbd5e1", family="Rajdhani"),
        margin=dict(t=10, b=10, l=10, r=10),
        height=250,
        xaxis=dict(showgrid=False, color="#94a3b8"),
        yaxis=dict(gridcolor="rgba(56,189,248,0.08)", color="#94a3b8"),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# ══════════════════════════════════════════════════════════════════════════
# Main Render
# ══════════════════════════════════════════════════════════════════════════

def render_dashboard():
    init_language()
    apply_rtl_css()

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
        display: flex; justify-content: space-between; align-items: center;
        margin-bottom: 18px;
        box-shadow: 0 0 28px rgba(56,189,248,0.10);
    }}
    .top-title  {{ color: #e0f2fe; font-weight: 950; font-size: 16px; }}
    .top-badge  {{
        background: rgba(56,189,248,0.12);
        border: 1px solid rgba(56,189,248,0.35);
        color: #38bdf8; font-weight: 950;
        padding: 8px 14px; border-radius: 999px; font-size: 13px;
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
        color: #c084fc; font-size: 42px; font-weight: 950;
        margin: 0;
        text-shadow: 0 0 24px rgba(192,132,252,0.42);
    }}
    .hero p {{ color: #cbd5e1; margin-top: 12px; font-size: 15px; }}

    .metric-card {{
        background: linear-gradient(145deg, rgba(15,23,42,0.95), rgba(30,41,59,0.62));
        border: 1px solid rgba(56,189,248,0.27);
        border-radius: 20px;
        padding: 18px;
        min-height: 98px;
        box-shadow: 0 0 20px rgba(56,189,248,0.08);
        transition: all 0.25s ease;
    }}
    .metric-card:hover {{
        transform: translateY(-3px);
        border-color: rgba(56,189,248,0.65);
        box-shadow: 0 0 28px rgba(56,189,248,0.18);
    }}
    .metric-label {{ color: #a5f3fc; font-size: 13px; font-weight: 850; margin-bottom: 10px; }}
    .metric-value {{ color: #f8fafc; font-size: 30px; font-weight: 950; }}
    .metric-sub   {{ color: #94a3b8; font-size: 12px; margin-top: 6px; }}

    .panel {{
        background: linear-gradient(145deg, rgba(15,23,42,0.92), rgba(2,6,23,0.78));
        border: 1px solid rgba(56,189,248,0.28);
        border-radius: 24px;
        padding: 22px;
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
        display: flex; justify-content: space-between; align-items: center;
        border-bottom: 1px solid rgba(148,163,184,0.11);
        padding: 9px 0; gap: 12px;
        {"flex-direction: row-reverse;" if is_ar else ""}
    }}
    .line span:first-child {{ color: #cbd5e1; font-weight: 760; }}
    .line span:last-child  {{ color: #38bdf8; font-weight: 950; }}

    .health-box {{
        background: rgba(2,6,23,0.62);
        border: 1px solid rgba(148,163,184,0.16);
        border-radius: 18px;
        padding: 16px;
        margin-top: 12px;
    }}

    .activity-item {{
        display: flex; gap: 10px; align-items: center;
        padding: 8px 12px;
        background: rgba(2,6,23,0.45);
        border-left: 3px solid #38bdf8;
        border-radius: 8px;
        margin-bottom: 6px;
        font-size: 12.5px;
        {"flex-direction: row-reverse; border-left: none; border-right: 3px solid #38bdf8;" if is_ar else ""}
    }}
    .activity-action {{ color: #f1f5f9; flex: 1; font-weight: 600; }}
    .activity-time   {{ color: #64748b; font-size: 10.5px; font-family: 'Orbitron', monospace; }}

    .stButton > button {{
        background: linear-gradient(135deg, #e0f2fe, #bae6fd) !important;
        color: #0f172a !important;
        border: none !important;
        border-radius: 14px !important;
        padding: 12px 18px !important;
        font-weight: 900 !important;
        box-shadow: 0 0 18px rgba(56,189,248,0.24);
        transition: 0.25s ease !important;
    }}
    .stButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 0 28px rgba(56,189,248,0.38);
    }}
    </style>
    """, unsafe_allow_html=True)

    # ──────────────────────────────────────────────────────────────────────
    # Gather Data
    # ──────────────────────────────────────────────────────────────────────
    base_assets = "assets"

    images_count  = _count_files(os.path.join(base_assets, "images"))
    audio_count   = _count_files(os.path.join(base_assets, "audio"))
    video_count   = _count_files(os.path.join(base_assets, "video"))
    uploads_count = _count_files(os.path.join(base_assets, "uploads"))

    total_files  = images_count + audio_count + video_count + uploads_count
    storage_size = _folder_size_mb(base_assets)

    tasks_count     = len(st.session_state.get("tasks", []))
    snapshots_count = st.session_state.get("snapshots_count", 0)
    last_file       = _get_last_file(os.path.join(base_assets, "uploads"))

    camera_state   = _get_camera_state()
    camera_running = bool(camera_state.get("camera_running", False))

    activity_stats   = get_stats()
    recent_actions   = get_log(limit=5)
    total_actions    = activity_stats["total"]

    # ── System Health Score ───────────────────────────────────────────────
    system_score = 0
    if _get_current_user() != "Unknown":  system_score += 20
    if os.path.exists("assets"):          system_score += 15
    if os.path.exists("pages"):           system_score += 15
    if os.path.exists("data"):            system_score += 10
    if os.path.exists("utils"):           system_score += 10
    if camera_running:                    system_score += 20
    if total_actions > 0:                 system_score += 10
    system_score = min(system_score, 100)

    if system_score >= 80:
        health_label = t("excellent"); health_color = "#22c55e"
    elif system_score >= 50:
        health_label = t("good");      health_color = "#facc15"
    else:
        health_label = t("needs_attention"); health_color = "#ef4444"

    # ──────────────────────────────────────────────────────────────────────
    # Top Bar + Hero
    # ──────────────────────────────────────────────────────────────────────
    st.markdown(f"""
<div class="top-bar">
<div class="top-title">{t("neon_ui")}</div>
<div class="top-badge">{t("ultra_platform")}</div>
</div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
<div class="hero">
<h1>📊 {t("dashboard_title")}</h1>
<p>{t("dashboard_subtitle")}</p>
</div>
    """, unsafe_allow_html=True)

    # ──────────────────────────────────────────────────────────────────────
    # Action Buttons
    # ──────────────────────────────────────────────────────────────────────
    back_col, refresh_col, activity_col, _ = st.columns([1.3, 1.5, 2, 4.5])

    with back_col:
        if st.button(t("back"), use_container_width=True, key="dashboard_back_btn"):
            st.session_state.page = "home"
            st.rerun()

    with refresh_col:
        if st.button(t("refresh"), use_container_width=True,
                     key="dashboard_refresh_btn"):
            st.rerun()

    with activity_col:
        if st.button(f"📋 {t('open_activity_log')}",
                     use_container_width=True,
                     key="dashboard_to_activity_btn"):
            st.session_state.page = "activity_log"
            st.rerun()

    st.write("")

    # ──────────────────────────────────────────────────────────────────────
    # System Health Bar
    # ──────────────────────────────────────────────────────────────────────
    st.markdown(f"""
<div class="panel">
<div class="panel-title">🩺 {t("system_health")}</div>
<div class="health-box">
<div style="display:flex;justify-content:space-between;margin-bottom:10px;{'flex-direction:row-reverse;' if is_ar else ''}">
<div style="color:#e0f2fe;font-weight:950;">{t("system_health")}</div>
<div style="color:{health_color};font-weight:950;">{system_score}% • {health_label}</div>
</div>
<div style="width:100%;height:13px;background:rgba(15,23,42,0.95);border-radius:999px;overflow:hidden;border:1px solid rgba(148,163,184,0.14);">
<div style="width:{system_score}%;height:100%;background:linear-gradient(90deg,#0ea5e9,{health_color});box-shadow:0 0 18px {health_color};border-radius:999px;"></div>
</div>
</div>
</div>
    """, unsafe_allow_html=True)

    # ──────────────────────────────────────────────────────────────────────
    # Metric Cards Row
    # ──────────────────────────────────────────────────────────────────────
    m1, m2, m3, m4 = st.columns(4)

    with m1:
        st.markdown(f"""
<div class="metric-card">
<div class="metric-label">{t("current_user")}</div>
<div class="metric-value" style="font-size:24px;">{_get_current_user()}</div>
<div class="metric-sub">{t("active_session")}</div>
</div>
        """, unsafe_allow_html=True)

    with m2:
        st.markdown(f"""
<div class="metric-card">
<div class="metric-label">{t("tasks")}</div>
<div class="metric-value">{tasks_count}</div>
<div class="metric-sub">{t("saved_data")}</div>
</div>
        """, unsafe_allow_html=True)

    with m3:
        st.markdown(f"""
<div class="metric-card">
<div class="metric-label">{t("total_files")}</div>
<div class="metric-value">{total_files}</div>
<div class="metric-sub">{t("images")}, {t("audio")}, {t("video")}</div>
</div>
        """, unsafe_allow_html=True)

    with m4:
        st.markdown(f"""
<div class="metric-card">
<div class="metric-label">{t("storage")}</div>
<div class="metric-value">{storage_size} MB</div>
<div class="metric-sub">{t("total_size")}</div>
</div>
        """, unsafe_allow_html=True)

    st.write("")

    # ──────────────────────────────────────────────────────────────────────
    # Charts Row
    # ──────────────────────────────────────────────────────────────────────
    chart_left, chart_right = st.columns(2)

    with chart_left:
        st.markdown(f'<div class="panel">'
                    f'<div class="panel-title">📁 {t("file_statistics")}</div>',
                    unsafe_allow_html=True)
        _render_files_chart(images_count, audio_count, video_count, uploads_count)
        st.markdown("</div>", unsafe_allow_html=True)

    with chart_right:
        st.markdown(f'<div class="panel">'
                    f'<div class="panel-title">📈 {t("activity_log")} (7d)</div>',
                    unsafe_allow_html=True)
        _render_activity_chart()
        st.markdown("</div>", unsafe_allow_html=True)

    # ──────────────────────────────────────────────────────────────────────
    # Bottom Row: AI Vision Status + Recent Activity
    # ──────────────────────────────────────────────────────────────────────
    left_col, right_col = st.columns([1.3, 0.88])

    with left_col:
        # AI Vision Panel
        checks = [
            ("👤", t("person_detected"), camera_state.get("person_detected")),
            ("🧍", t("pose_visible"),    camera_state.get("pose_visible")),
            ("✋", t("right_hand"),      camera_state.get("right_hand")),
            ("🤚", t("left_hand"),       camera_state.get("left_hand")),
            ("🎯", t("body_centered"),   camera_state.get("body_centered")),
        ]
        active_count = sum(1 for _, _, v in checks if v)
        readiness    = int((active_count / len(checks)) * 100)

        if readiness >= 80:
            ready_label, ready_color = t("ready"),     "#22c55e"
        elif readiness >= 40:
            ready_label, ready_color = t("partial"),   "#facc15"
        else:
            ready_label, ready_color = t("not_ready"), "#ef4444"

        camera_text = t("running") if camera_running else t("stopped")
        camera_color = "#22c55e" if camera_running else "#ef4444"

        st.markdown(f'<div class="panel">'
                    f'<div class="panel-title">🧠 {t("ai_vision")}</div>',
                    unsafe_allow_html=True)

        st.markdown(f"""
<div class="line"><span>{t("camera")}</span>
<span style="color:{camera_color};">{camera_text}</span></div>
<div class="line"><span>{t("status")}</span>
<span style="color:{ready_color};">{readiness}% • {ready_label}</span></div>
        """, unsafe_allow_html=True)

        for icon, label, value in checks:
            st.markdown(f"""
<div class="line">
<span>{icon} {label}</span>
<span>{_status_badge(value)}</span>
</div>
            """, unsafe_allow_html=True)

        st.markdown(f"""
<div style="margin-top:14px;padding-top:14px;border-top:1px solid rgba(148,163,184,0.12);">
<div style="color:#94a3b8;font-size:12px;margin-bottom:4px;">{t("system_message")}</div>
<div style="color:#e0f2fe;font-size:13px;">{camera_state.get('message', '—')}</div>
</div>
</div>
        """, unsafe_allow_html=True)

    with right_col:
        # Recent Activity Panel
        st.markdown(f'<div class="panel">'
                    f'<div class="panel-title">⚡ {t("last_action")}</div>',
                    unsafe_allow_html=True)

        if not recent_actions:
            st.markdown(f"""
<div style="color:#64748b;text-align:center;padding:20px;font-style:italic;">
📋 {t("no_activity")}
</div>
            """, unsafe_allow_html=True)
        else:
            for entry in recent_actions:
                action = entry.get("action", "—")
                try:
                    ts_human = datetime.fromtimestamp(
                        entry.get("timestamp", 0)
                    ).strftime("%H:%M:%S")
                except (OSError, ValueError):
                    ts_human = "—"

                st.markdown(f"""
<div class="activity-item">
<span class="activity-action">{action}</span>
<span class="activity-time">{ts_human}</span>
</div>
                """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # File Quick Stats Panel
        st.markdown(f"""
<div class="panel">
<div class="panel-title">📊 {t("general_summary")}</div>
<div class="line"><span>{t("images")}</span><span>{images_count}</span></div>
<div class="line"><span>{t("audio")}</span><span>{audio_count}</span></div>
<div class="line"><span>{t("video")}</span><span>{video_count}</span></div>
<div class="line"><span>{t("uploads")}</span><span>{uploads_count}</span></div>
<div class="line"><span>{t("total_actions")}</span><span>{total_actions}</span></div>
<div class="line"><span>{t("last_file")}</span>
<span style="font-size:11px;">{last_file[:20]}</span></div>
</div>
        """, unsafe_allow_html=True)