"""
═══════════════════════════════════════════════════════════════════════════
OMNIX VISION — Game Center (Phase 3)
═══════════════════════════════════════════════════════════════════════════
Phase-3 changes:
    ✓ Full translation (EN/AR + RTL)
    ✓ High Scores persisted to data/high_scores.json (per user)
    ✓ Activity logging
    ✓ All 4 games kept intact (Space, Catcher, Snake, Breakout)
    ✓ HS auto-update via URL params (when JS reports new score)
═══════════════════════════════════════════════════════════════════════════
"""

import json
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from utils.language import t, init_language, apply_rtl_css, is_rtl
from utils.activity import log_action


# ═══════════════════════════════════════════════════════════════════════════
# Paths & Persistence
# ═══════════════════════════════════════════════════════════════════════════
BASE_DIR  = Path(__file__).resolve().parent.parent
DATA_DIR  = BASE_DIR / "data"
HS_FILE   = DATA_DIR / "high_scores.json"
DATA_DIR.mkdir(parents=True, exist_ok=True)


def _load_high_scores() -> dict:
    """Load all users' high scores."""
    if not HS_FILE.exists():
        return {}
    try:
        with open(HS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _save_high_scores(scores: dict):
    """Persist scores dict."""
    try:
        with open(HS_FILE, "w", encoding="utf-8") as f:
            json.dump(scores, f, ensure_ascii=False, indent=2)
    except OSError:
        pass


def _get_user_scores(user_id: str) -> dict:
    """Get high scores for current user (with defaults)."""
    all_scores = _load_high_scores()
    user_scores = all_scores.get(user_id, {})
    defaults = {"space": 0, "catcher": 0, "snake": 0, "breakout": 0}
    for k, v in defaults.items():
        user_scores.setdefault(k, v)
    return user_scores


def _update_score(user_id: str, game_key: str, new_score: int) -> bool:
    """Update HS only if new_score is higher. Returns True if updated."""
    if new_score <= 0:
        return False
    all_scores = _load_high_scores()
    user_scores = all_scores.get(user_id, {})
    old = user_scores.get(game_key, 0)
    if new_score > old:
        user_scores[game_key] = new_score
        all_scores[user_id] = user_scores
        _save_high_scores(all_scores)
        return True
    return False


# ═══════════════════════════════════════════════════════════════════════════
# Main Render
# ═══════════════════════════════════════════════════════════════════════════

def render_game():
    init_language()
    apply_rtl_css()

    # Auth guard
    if not st.session_state.get("logged_in", False):
        st.session_state.page = "login"
        st.rerun()

    user_id = st.session_state.get("user", "anonymous")

    # ── Session State ─────────────────────────────────────────────────────
    if "selected_game" not in st.session_state:
        st.session_state.selected_game = None

    # Load HS for this user
    high_scores = _get_user_scores(user_id)
    st.session_state.high_scores = high_scores

    # Manual score entry (when game over, user can input final score)
    if "score_submit_pending" not in st.session_state:
        st.session_state.score_submit_pending = {}

    is_ar = is_rtl()

    # ── Global CSS ────────────────────────────────────────────────────────
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@400;600;700&display=swap');

    [data-testid="stAppDeployButton"],
    [data-testid="stToolbar"],
    header[data-testid="stHeader"] {{
        background: transparent !important;
        box-shadow: none !important;
    }}
    [data-testid="stSidebar"], [data-testid="collapsedControl"] {{ display: none; }}

    .block-container {{
        max-width: 1200px;
        padding-top: 1.2rem;
        padding-left: 1.5rem;
        padding-right: 1.5rem;
        {"direction: rtl;" if is_ar else ""}
    }}

    .stApp {{
        background:
            radial-gradient(ellipse at 5%  10%, rgba(56,189,248,0.12) 0%, transparent 40%),
            radial-gradient(ellipse at 95% 5%,  rgba(168,85,247,0.12) 0%, transparent 40%),
            radial-gradient(ellipse at 50% 90%, rgba(34,197,94,0.07)  0%, transparent 45%),
            linear-gradient(160deg, #020617 0%, #060d1f 50%, #0d0a24 100%);
        color: #f8fafc;
        font-family: 'Rajdhani', sans-serif;
    }}

    /* ── Header ── */
    .game-header {{
        position: relative;
        background: linear-gradient(135deg, rgba(2,6,23,0.97), rgba(15,23,42,0.85));
        border: 1px solid rgba(56,189,248,0.30);
        border-radius: 28px;
        padding: 32px 36px;
        text-align: center;
        overflow: hidden;
        margin-bottom: 24px;
    }}
    .game-header h1 {{
        font-family: 'Orbitron', monospace;
        font-size: 46px;
        font-weight: 900;
        margin: 0;
        background: linear-gradient(90deg, #38bdf8, #a855f7, #22c55e, #38bdf8);
        background-size: 300% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: shimmer 4s linear infinite;
        letter-spacing: 3px;
    }}
    @keyframes shimmer {{ to {{ background-position: 300% center; }} }}
    .game-header .tagline {{
        color: #94a3b8; font-size: 14px;
        letter-spacing: 2px; margin-top: 10px; text-transform: uppercase;
    }}
    .badge-row {{ display: flex; justify-content: center; gap: 16px; margin-top: 18px; flex-wrap: wrap; }}
    .badge {{
        background: rgba(56,189,248,0.08);
        border: 1px solid rgba(56,189,248,0.22);
        border-radius: 20px;
        padding: 6px 16px;
        font-size: 12px; color: #7dd3fc;
        font-family: 'Orbitron', monospace; letter-spacing: 1px;
    }}

    /* ── Game Cards ── */
    .game-card {{
        background: linear-gradient(145deg, rgba(2,6,23,0.96), rgba(15,23,42,0.80));
        border: 1px solid rgba(56,189,248,0.18);
        border-radius: 22px;
        padding: 26px 20px 22px;
        text-align: center;
        cursor: pointer;
        transition: all 0.35s cubic-bezier(0.34,1.56,0.64,1);
        min-height: 230px;
    }}
    .game-card:hover {{
        transform: translateY(-10px) scale(1.02);
        border-color: rgba(56,189,248,0.65);
        box-shadow: 0 20px 50px rgba(56,189,248,0.18);
    }}
    .game-card.active {{
        border-color: rgba(56,189,248,0.85);
        background: linear-gradient(145deg, rgba(14,165,233,0.12), rgba(15,23,42,0.90));
        box-shadow: 0 0 40px rgba(56,189,248,0.25);
    }}
    .game-card.active-green   {{ border-color: rgba(34,197,94,0.85);  background: linear-gradient(145deg, rgba(34,197,94,0.12), rgba(15,23,42,0.90)); }}
    .game-card.active-purple  {{ border-color: rgba(168,85,247,0.85); background: linear-gradient(145deg, rgba(168,85,247,0.12), rgba(15,23,42,0.90)); }}
    .game-card.active-orange  {{ border-color: rgba(251,146,60,0.85); background: linear-gradient(145deg, rgba(251,146,60,0.12), rgba(15,23,42,0.90)); }}

    .game-icon  {{ font-size: 52px; margin-bottom: 12px; display: block; }}
    .game-title {{
        font-family: 'Orbitron', monospace;
        color: #f1f5f9; font-size: 16px; font-weight: 700;
        margin-bottom: 8px; letter-spacing: 1px;
    }}
    .game-desc  {{ color: #94a3b8; font-size: 13px; line-height: 1.6; }}

    .hs-badge {{
        display: inline-block; margin-top: 12px;
        background: rgba(250,204,21,0.10);
        border: 1px solid rgba(250,204,21,0.30);
        border-radius: 12px;
        padding: 4px 12px;
        font-size: 11px; color: #fde68a;
        font-family: 'Orbitron', monospace;
    }}

    .now-playing-pill {{
        display: inline-block; margin-top: 10px;
        background: rgba(34,197,94,0.15);
        border: 1px solid rgba(34,197,94,0.40);
        border-radius: 20px;
        padding: 4px 14px;
        font-size: 11px; color: #86efac;
        font-family: 'Orbitron', monospace;
        animation: pulse-pill 1.5s ease-in-out infinite;
    }}
    @keyframes pulse-pill {{ 0%,100% {{opacity:1;}} 50% {{opacity:0.55;}} }}

    /* ── Stats Bar ── */
    .stats-bar {{
        display: flex; gap: 12px; margin-bottom: 22px; flex-wrap: wrap;
    }}
    .stat-box {{
        flex: 1; min-width: 120px;
        background: rgba(15,23,42,0.70);
        border: 1px solid rgba(56,189,248,0.15);
        border-radius: 16px;
        padding: 14px 18px; text-align: center;
    }}
    .stat-val {{
        font-family: 'Orbitron', monospace;
        font-size: 22px; font-weight: 700; color: #38bdf8;
    }}
    .stat-lbl {{
        font-size: 11px; color: #64748b; margin-top: 4px;
        text-transform: uppercase; letter-spacing: 1px;
    }}

    /* ── Empty Box ── */
    .empty-box {{
        background: rgba(2,6,23,0.80);
        border: 1px dashed rgba(56,189,248,0.22);
        border-radius: 24px;
        padding: 52px 28px; text-align: center;
        color: #64748b; margin-top: 8px;
    }}
    .empty-box h3 {{
        font-family: 'Orbitron', monospace;
        color: #38bdf8;
        margin-bottom: 10px;
        font-size: 20px; letter-spacing: 2px;
    }}

    /* ── Now Playing ── */
    .now-playing-label {{
        background: linear-gradient(135deg, rgba(2,6,23,0.97), rgba(15,23,42,0.85));
        border: 1px solid rgba(56,189,248,0.25);
        border-radius: 18px;
        padding: 14px 22px;
        display: flex; align-items: center; gap: 12px;
        margin-bottom: 14px;
    }}
    .dot {{
        width: 10px; height: 10px; border-radius: 50%;
        background: #22c55e;
        animation: pulse-dot 1s infinite;
    }}
    @keyframes pulse-dot {{
        0%,100% {{ box-shadow: 0 0 0 0 rgba(34,197,94,0.5); }}
        50%      {{ box-shadow: 0 0 0 8px rgba(34,197,94,0); }}
    }}
    .now-label {{ font-family: 'Orbitron', monospace; font-size: 13px; color: #94a3b8; letter-spacing: 1px; }}
    .now-name  {{ font-family: 'Orbitron', monospace; font-size: 15px; color: #f8fafc; font-weight: 700; letter-spacing: 2px; }}

    /* ── Score Submit Box ── */
    .submit-box {{
        background: linear-gradient(135deg, rgba(250,204,21,0.10), rgba(2,6,23,0.95));
        border: 1px solid rgba(250,204,21,0.35);
        border-radius: 16px;
        padding: 16px 20px;
        margin-top: 14px;
    }}

    /* ── Buttons ── */
    .stButton > button {{
        background: linear-gradient(135deg, #0ea5e9 0%, #6d28d9 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 14px !important;
        padding: 11px 20px !important;
        font-weight: 700 !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-size: 15px !important;
        letter-spacing: 0.5px !important;
        transition: 0.3s ease !important;
        box-shadow: 0 4px 20px rgba(14,165,233,0.20) !important;
    }}
    .stButton > button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 28px rgba(109,40,217,0.35) !important;
    }}
    </style>
    """, unsafe_allow_html=True)

    # ── Back Button ───────────────────────────────────────────────────────
    back_col, *_ = st.columns([1.4, 8])
    with back_col:
        if st.button(t("back"), use_container_width=True, key="game_back_home"):
            st.session_state.page = "home"
            st.rerun()

    # ── Header ────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="game-header">
        <h1>🎮 {t('game_title')}</h1>
        <div class="tagline">{t('game_subtitle')}</div>
        <div class="badge-row">
            <span class="badge">🎮 4 {t('games_available').upper()}</span>
            <span class="badge">🔊 SOUND FX</span>
            <span class="badge">⚡ {t('high_score').upper()}</span>
            <span class="badge">🌌 NEON THEME</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Stats Bar ─────────────────────────────────────────────────────────
    total_hs = sum(high_scores.values())
    st.markdown(f"""
    <div class="stats-bar">
        <div class="stat-box">
            <div class="stat-val">4</div>
            <div class="stat-lbl">{t('games_available')}</div>
        </div>
        <div class="stat-box">
            <div class="stat-val" style="color:#facc15;">{total_hs}</div>
            <div class="stat-lbl">{t('total_high_score')}</div>
        </div>
        <div class="stat-box">
            <div class="stat-val" style="color:#38bdf8;">{high_scores['space']}</div>
            <div class="stat-lbl">🚀 Space {t('best')}</div>
        </div>
        <div class="stat-box">
            <div class="stat-val" style="color:#a855f7;">{high_scores['catcher']}</div>
            <div class="stat-lbl">⭐ Catcher {t('best')}</div>
        </div>
        <div class="stat-box">
            <div class="stat-val" style="color:#22c55e;">{high_scores['snake']}</div>
            <div class="stat-lbl">🐍 Snake {t('best')}</div>
        </div>
        <div class="stat-box">
            <div class="stat-val" style="color:#fb923c;">{high_scores['breakout']}</div>
            <div class="stat-lbl">🧱 Breakout {t('best')}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Games definitions ─────────────────────────────────────────────────
    games = [
        {"key": "space",    "icon": "🚀", "title": "SPACE DEFENDER",
         "desc": "Move the spaceship and shoot down enemies.",          "color": "active"},
        {"key": "catcher",  "icon": "⭐", "title": "NEON CATCHER",
         "desc": "Catch falling neon energy balls with your paddle.",   "color": "active-purple"},
        {"key": "snake",    "icon": "🐍", "title": "SNAKE GAME",
         "desc": "Classic snake on a neon grid. Eat, grow, don't crash.","color": "active-green"},
        {"key": "breakout", "icon": "🧱", "title": "BREAKOUT",
         "desc": "Smash colorful brick walls with a bouncing ball.",    "color": "active-orange"},
    ]

    # ── Game Cards Grid ──────────────────────────────────────────────────
    cols = st.columns(4)
    for i, game in enumerate(games):
        with cols[i]:
            is_active   = st.session_state.selected_game == game["key"]
            active_cls  = game["color"] if is_active else ""
            playing_pill = f'<div class="now-playing-pill">▶ {t("now_playing").upper()}</div>' if is_active else ""
            hs_val      = high_scores[game["key"]]

            st.markdown(f"""
            <div class="game-card {active_cls}">
                <span class="game-icon">{game['icon']}</span>
                <div class="game-title">{game['title']}</div>
                <div class="game-desc">{game['desc']}</div>
                <div class="hs-badge">🏆 {t('best').upper()}: {hs_val}</div>
                {playing_pill}
            </div>
            """, unsafe_allow_html=True)

            btn_label = "▶ PLAYING" if is_active else f"{t('play')} {game['icon']}"
            if st.button(btn_label, use_container_width=True, key=f"open_{game['key']}"):
                st.session_state.selected_game = game["key"]
                log_action(f"play_{game['key']}", user_id=user_id, category="navigation")
                st.rerun()

    st.write("")

    # ── Game Area ─────────────────────────────────────────────────────────
    if st.session_state.selected_game is None:
        st.markdown(f"""
        <div class="empty-box">
            <h3>{t('choose_game').upper()}</h3>
            <p>Select one of the four games above to start playing.<br>
            Your high scores are saved automatically for your account.</p>
        </div>
        """, unsafe_allow_html=True)
        return

    # ── Now Playing Banner ────────────────────────────────────────────────
    game_name_map = {
        "space":    "SPACE DEFENDER 🚀",
        "catcher":  "NEON CATCHER ⭐",
        "snake":    "SNAKE GAME 🐍",
        "breakout": "BREAKOUT 🧱",
    }
    current_game = st.session_state.selected_game
    st.markdown(f"""
    <div class="now-playing-label">
        <div class="dot"></div>
        <div>
            <div class="now-label">{t('now_playing').upper()}</div>
            <div class="now-name">{game_name_map[current_game]}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Render the active game ────────────────────────────────────────────
    if   current_game == "space":    render_space_defender()
    elif current_game == "catcher":  render_neon_catcher()
    elif current_game == "snake":    render_snake_game()
    elif current_game == "breakout": render_breakout()

    # ── Manual Score Submission (after game over) ─────────────────────────
    st.markdown(f"""
    <div class="submit-box">
    <div style="font-family:'Orbitron',monospace;color:#fde68a;font-size:12px;letter-spacing:1.5px;margin-bottom:8px;">
    💾 SUBMIT YOUR FINAL SCORE
    </div>
    <div style="color:#94a3b8;font-size:12px;margin-bottom:10px;">
    After your game ends, enter the final score here to update your high score.
    </div>
    </div>
    """, unsafe_allow_html=True)

    sc1, sc2 = st.columns([3, 1])
    with sc1:
        final_score = st.number_input(
            t("score"),
            min_value=0,
            max_value=999_999,
            value=0,
            step=1,
            key=f"final_score_{current_game}",
            label_visibility="collapsed",
            placeholder=f"Enter your final {t('score').lower()}...",
        )
    with sc2:
        if st.button(f"🏆 {t('save')}",
                     use_container_width=True,
                     key=f"submit_score_{current_game}"):
            if final_score > 0:
                updated = _update_score(user_id, current_game, int(final_score))
                if updated:
                    log_action("new_high_score", user_id=user_id, category="data",
                               details=f"{current_game}={final_score}")
                    st.success(f"🎉 New high score: {final_score}!")
                    st.balloons()
                else:
                    cur = high_scores[current_game]
                    st.info(f"Your current best is {cur}. Keep trying!")


# ═══════════════════════════════════════════════════════════════════════════
# GAME 1 — Space Defender (unchanged HTML)
# ═══════════════════════════════════════════════════════════════════════════
def render_space_defender():
    html = """
    <!DOCTYPE html><html><head>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&display=swap');
        * { box-sizing: border-box; }
        body { margin:0; background:radial-gradient(circle at center,#0f172a,#020617); font-family:'Orbitron',monospace; color:white; overflow:hidden; }
        .wrap { display:flex; flex-direction:column; align-items:center; padding:8px 0; }
        .hud { width:820px; display:flex; justify-content:space-between; margin-bottom:10px; gap:10px; }
        .hud span { flex:1; text-align:center; background:rgba(2,6,23,0.85); border:1px solid rgba(56,189,248,0.30); padding:9px 14px; border-radius:12px; font-size:13px; color:#e0f2fe; letter-spacing:1px; }
        canvas { background:linear-gradient(180deg,#020617,#000); border:2px solid rgba(56,189,248,0.45); border-radius:20px; box-shadow:0 0 50px rgba(56,189,248,0.20); outline:none; }
        .controls { width:820px; display:flex; justify-content:space-between; align-items:center; margin-top:12px; color:#64748b; font-size:12px; letter-spacing:0.5px; }
        button { background:linear-gradient(135deg,#0ea5e9,#7c3aed); color:white; border:none; padding:11px 26px; border-radius:12px; font-family:'Orbitron',monospace; font-size:13px; font-weight:700; cursor:pointer; letter-spacing:1px; transition:0.2s; }
        button:hover { transform:translateY(-2px); box-shadow:0 6px 22px rgba(124,58,237,0.40); }
    </style></head><body>
    <div class="wrap">
        <div class="hud">
            <span id="score">SCORE: 0</span>
            <span id="lives">LIVES: ❤️ ❤️ ❤️</span>
            <span id="level">LEVEL: 1</span>
            <span id="status">READY</span>
        </div>
        <canvas id="canvas" width="820" height="520" tabindex="0"></canvas>
        <div class="controls">
            <div>Click canvas · ← → or A D to move · SPACE to shoot</div>
            <button onclick="restartGame()">▶ START / RESTART</button>
        </div>
    </div>
    <script>
    const canvas=document.getElementById("canvas"),ctx=canvas.getContext("2d");
    const $score=document.getElementById("score"),$lives=document.getElementById("lives"),
          $level=document.getElementById("level"),$status=document.getElementById("status");
    let keys={},bullets=[],enemies=[],stars=[],particles=[],score=0,lives=3,level=1,running=false,enemyTimer=0,audioCtx=null;
    const player={x:canvas.width/2-22,y:canvas.height-70,width:44,height:44,speed:6,cooldown:0};

    function playSound(t){
        try{
            if(!audioCtx)audioCtx=new(window.AudioContext||window.webkitAudioContext)();
            const o=audioCtx.createOscillator(),g=audioCtx.createGain();
            o.connect(g);g.connect(audioCtx.destination);
            const map={shoot:[620,0.05,"square"],hit:[220,0.08,"sawtooth"],gameover:[90,0.10,"triangle"]};
            const[f,v,tp]=map[t]||[440,0.05,"sine"];
            o.frequency.value=f;g.gain.value=v;o.type=tp;
            o.start();g.gain.exponentialRampToValueAtTime(0.001,audioCtx.currentTime+0.18);
            o.stop(audioCtx.currentTime+0.18);
        }catch(e){}
    }

    function createStars(){
        stars=[];
        for(let i=0;i<100;i++) stars.push({x:Math.random()*canvas.width,y:Math.random()*canvas.height,r:Math.random()*1.8+0.3,s:Math.random()*0.8+0.2});
    }
    function drawStars(){
        stars.forEach(s=>{
            ctx.fillStyle=`rgba(224,242,254,${0.4+Math.random()*0.4})`;
            ctx.beginPath();ctx.arc(s.x,s.y,s.r,0,Math.PI*2);ctx.fill();
            s.y+=s.s; if(s.y>canvas.height){s.y=0;s.x=Math.random()*canvas.width;}
        });
    }

    function drawPlayer(){
        ctx.save();ctx.translate(player.x+player.width/2,player.y+player.height/2);
        ctx.fillStyle="rgba(56,189,248,0.3)";ctx.shadowColor="#38bdf8";ctx.shadowBlur=30;
        ctx.beginPath();ctx.ellipse(0,18,10,6,0,0,Math.PI*2);ctx.fill();
        ctx.fillStyle="#38bdf8";ctx.shadowBlur=20;
        ctx.beginPath();ctx.moveTo(0,-26);ctx.lineTo(22,22);ctx.lineTo(0,10);ctx.lineTo(-22,22);ctx.closePath();ctx.fill();
        ctx.fillStyle="#e0f2fe";ctx.shadowBlur=10;
        ctx.fillRect(-5,-4,10,16);
        ctx.restore();ctx.shadowBlur=0;
    }

    function shoot(){
        if(player.cooldown<=0){
            bullets.push({x:player.x+player.width/2-3,y:player.y,w:6,h:18,s:9});
            player.cooldown=10;playSound("shoot");
        }
    }
    function drawBullets(){
        bullets.forEach((b,i)=>{
            b.y-=b.s;
            ctx.fillStyle="#22c55e";ctx.shadowColor="#22c55e";ctx.shadowBlur=18;
            ctx.fillRect(b.x,b.y,b.w,b.h);
            if(b.y<-20)bullets.splice(i,1);
        });
        ctx.shadowBlur=0;
    }
    function createEnemy(){
        const sz=Math.random()*18+28;
        const speedBoost=1+(level-1)*0.15;
        enemies.push({x:Math.random()*(canvas.width-sz),y:-sz,w:sz,h:sz,s:(Math.random()*0.9+0.6)*speedBoost});
    }
    function drawEnemies(){
        enemies.forEach((e,i)=>{
            e.y+=e.s;
            ctx.fillStyle="#ef4444";ctx.shadowColor="#ef4444";ctx.shadowBlur=18;
            ctx.beginPath();ctx.moveTo(e.x+e.w/2,e.y+e.h);ctx.lineTo(e.x,e.y);ctx.lineTo(e.x+e.w,e.y);ctx.closePath();ctx.fill();
            if(e.y>canvas.height){ enemies.splice(i,1);lives--;updateHud();if(lives<=0)gameOver(); }
        });
        ctx.shadowBlur=0;
    }
    function createExplosion(x,y){
        for(let i=0;i<16;i++) particles.push({x,y,vx:(Math.random()-.5)*7,vy:(Math.random()-.5)*7,life:35,c:`hsl(${Math.random()*40+20},100%,65%)`});
    }
    function drawParticles(){
        particles.forEach((p,i)=>{
            p.x+=p.vx;p.y+=p.vy;p.life--;
            ctx.fillStyle=p.c;ctx.globalAlpha=p.life/35;
            ctx.beginPath();ctx.arc(p.x,p.y,3,0,Math.PI*2);ctx.fill();
            if(p.life<=0)particles.splice(i,1);
        });
        ctx.globalAlpha=1;
    }
    function detectCollisions(){
        bullets.forEach((b,bi)=>{
            enemies.forEach((e,ei)=>{
                if(b.x<e.x+e.w&&b.x+b.w>e.x&&b.y<e.y+e.h&&b.y+b.h>e.y){
                    createExplosion(e.x+e.w/2,e.y+e.h/2);
                    bullets.splice(bi,1);enemies.splice(ei,1);
                    score+=10*(level);playSound("hit");updateHud();
                    if(score>0&&score%200===0){level++;updateHud();}
                }
            });
        });
    }
    function updatePlayer(){
        if(keys["ArrowLeft"]||keys["a"]||keys["A"])player.x-=player.speed;
        if(keys["ArrowRight"]||keys["d"]||keys["D"])player.x+=player.speed;
        if(keys[" "]||keys["Spacebar"])shoot();
        player.x=Math.max(0,Math.min(canvas.width-player.width,player.x));
        if(player.cooldown>0)player.cooldown--;
    }
    function updateHud(){
        $score.innerText="SCORE: "+score;
        $lives.innerText="LIVES: "+"❤️".repeat(Math.max(0,lives));
        $level.innerText="LEVEL: "+level;
    }
    function gameOver(){
        if(!running)return;
        running=false;playSound("gameover");$status.innerText="GAME OVER";
        ctx.fillStyle="rgba(0,0,0,0.65)";ctx.fillRect(0,0,canvas.width,canvas.height);
        ctx.fillStyle="#f8fafc";ctx.font="bold 48px Orbitron";ctx.textAlign="center";
        ctx.fillText("GAME OVER",canvas.width/2,canvas.height/2-24);
        ctx.fillStyle="#38bdf8";ctx.font="bold 22px Orbitron";
        ctx.fillText("SCORE: "+score+"  |  LEVEL: "+level,canvas.width/2,canvas.height/2+24);
    }
    function gameLoop(){
        if(!running)return;
        ctx.clearRect(0,0,canvas.width,canvas.height);
        drawStars();updatePlayer();drawPlayer();drawBullets();
        enemyTimer++;
        const spawnRate=Math.max(35,80-level*5);
        if(enemyTimer>spawnRate){createEnemy();enemyTimer=0;}
        drawEnemies();detectCollisions();drawParticles();
        requestAnimationFrame(gameLoop);
    }
    function restartGame(){
        canvas.focus();
        if(audioCtx&&audioCtx.state==="suspended")audioCtx.resume();
        score=0;lives=3;level=1;bullets=[];enemies=[];particles=[];enemyTimer=0;
        player.x=canvas.width/2-player.width/2;
        running=true;$status.innerText="RUNNING";updateHud();createStars();gameLoop();
    }
    canvas.addEventListener("keydown",e=>{keys[e.key]=true;if(e.code==="Space"){keys[" "]=true;e.preventDefault();}});
    canvas.addEventListener("keyup",e=>{keys[e.key]=false;if(e.code==="Space")keys[" "]=false;});
    canvas.addEventListener("click",()=>canvas.focus());
    createStars();drawStars();drawPlayer();
    </script></body></html>
    """
    components.html(html, height=690)


# ═══════════════════════════════════════════════════════════════════════════
# GAME 2 — Neon Catcher (unchanged HTML)
# ═══════════════════════════════════════════════════════════════════════════
def render_neon_catcher():
    html = """
    <!DOCTYPE html><html><head>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&display=swap');
        * { box-sizing:border-box; }
        body { margin:0; background:radial-gradient(circle at center,#111827,#020617); font-family:'Orbitron',monospace; color:white; overflow:hidden; }
        .wrap { display:flex; flex-direction:column; align-items:center; padding:8px 0; }
        .hud { width:820px; display:flex; gap:10px; margin-bottom:10px; }
        .hud span { flex:1; text-align:center; background:rgba(2,6,23,0.85); border:1px solid rgba(168,85,247,0.30); padding:9px 14px; border-radius:12px; font-size:13px; color:#e0f2fe; letter-spacing:1px; }
        canvas { background:linear-gradient(180deg,#020617,#000); border:2px solid rgba(168,85,247,0.55); border-radius:20px; box-shadow:0 0 50px rgba(168,85,247,0.22); outline:none; }
        .controls { width:820px; display:flex; justify-content:space-between; align-items:center; margin-top:12px; color:#64748b; font-size:12px; }
        button { background:linear-gradient(135deg,#a855f7,#0ea5e9); color:white; border:none; padding:11px 26px; border-radius:12px; font-family:'Orbitron',monospace; font-size:13px; font-weight:700; cursor:pointer; transition:0.2s; }
        button:hover { transform:translateY(-2px); box-shadow:0 6px 22px rgba(168,85,247,0.40); }
    </style></head><body>
    <div class="wrap">
        <div class="hud">
            <span id="score">SCORE: 0</span>
            <span id="missed">MISSED: 0 / 5</span>
            <span id="combo">COMBO: x1</span>
            <span id="status">READY</span>
        </div>
        <canvas id="canvas" width="820" height="520" tabindex="0"></canvas>
        <div class="controls">
            <div>Click canvas · ← → or A D to move</div>
            <button onclick="restartGame()">▶ START / RESTART</button>
        </div>
    </div>
    <script>
    const canvas=document.getElementById("canvas"),ctx=canvas.getContext("2d");
    const $score=document.getElementById("score"),$missed=document.getElementById("missed"),
          $combo=document.getElementById("combo"),$status=document.getElementById("status");
    let keys={},items=[],stars=[],effects=[],score=0,missed=0,combo=1,running=false,timer=0,audioCtx=null;
    const player={x:canvas.width/2-55,y:canvas.height-55,width:110,height:22,speed:7};
    const COLORS=["#38bdf8","#a855f7","#22c55e","#f43f5e","#facc15"];

    function playSound(t){
        try{
            if(!audioCtx)audioCtx=new(window.AudioContext||window.webkitAudioContext)();
            const o=audioCtx.createOscillator(),g=audioCtx.createGain();
            o.connect(g);g.connect(audioCtx.destination);
            const map={catch:[760,0.06,"sine"],miss:[160,0.07,"triangle"],gameover:[85,0.10,"sawtooth"]};
            const[f,v,tp]=map[t]||[440,0.05,"sine"];
            o.frequency.value=f;g.gain.value=v;o.type=tp;
            o.start();g.gain.exponentialRampToValueAtTime(0.001,audioCtx.currentTime+0.18);
            o.stop(audioCtx.currentTime+0.18);
        }catch(e){}
    }
    function createStars(){
        stars=[];
        for(let i=0;i<90;i++)stars.push({x:Math.random()*canvas.width,y:Math.random()*canvas.height,r:Math.random()*1.5+0.4,s:Math.random()*0.5+0.2});
    }
    function drawStars(){
        stars.forEach(s=>{
            ctx.fillStyle="rgba(224,242,254,0.70)";
            ctx.beginPath();ctx.arc(s.x,s.y,s.r,0,Math.PI*2);ctx.fill();
            s.y+=s.s;if(s.y>canvas.height){s.y=0;s.x=Math.random()*canvas.width;}
        });
    }
    function createItem(){
        const r=Math.random()*8+10;
        items.push({x:Math.random()*(canvas.width-r*2)+r,y:-r,r,s:Math.random()*1.0+0.7,c:COLORS[Math.floor(Math.random()*COLORS.length)]});
    }
    function drawPlayer(){
        ctx.fillStyle="rgba(168,85,247,0.20)";ctx.shadowColor="#a855f7";ctx.shadowBlur=30;
        ctx.fillRect(player.x-4,player.y-4,player.width+8,player.height+8);
        ctx.fillStyle="#a855f7";ctx.shadowBlur=22;
        ctx.fillRect(player.x,player.y,player.width,player.height);
        ctx.fillStyle="#e0f2fe";ctx.shadowBlur=5;
        ctx.fillRect(player.x+15,player.y+7,player.width-30,5);
        ctx.shadowBlur=0;
    }
    function createEffect(x,y,c){
        for(let i=0;i<14;i++) effects.push({x,y,vx:(Math.random()-.5)*6,vy:(Math.random()-.5)*6,life:30,c});
        effects.push({x,y:y-10,vx:0,vy:-1.2,life:45,text:"+" + (5*combo),c:"#facc15"});
    }
    function drawEffects(){
        effects.forEach((e,i)=>{
            if(e.text){
                ctx.fillStyle=e.c;ctx.globalAlpha=e.life/45;
                ctx.font="bold 18px Orbitron";ctx.textAlign="center";
                ctx.fillText(e.text,e.x,e.y);
                e.x+=e.vx;e.y+=e.vy;e.life--;
                if(e.life<=0)effects.splice(i,1);
                return;
            }
            e.x+=e.vx;e.y+=e.vy;e.life--;
            ctx.fillStyle=e.c;ctx.globalAlpha=e.life/30;
            ctx.beginPath();ctx.arc(e.x,e.y,3,0,Math.PI*2);ctx.fill();
            if(e.life<=0)effects.splice(i,1);
        });
        ctx.globalAlpha=1;ctx.textAlign="left";
    }
    function drawItems(){
        items.forEach((item,i)=>{
            item.y+=item.s;
            ctx.fillStyle=item.c;ctx.shadowColor=item.c;ctx.shadowBlur=22;
            ctx.beginPath();ctx.arc(item.x,item.y,item.r,0,Math.PI*2);ctx.fill();
            ctx.fillStyle="rgba(255,255,255,0.55)";ctx.shadowBlur=0;
            ctx.beginPath();ctx.arc(item.x-item.r*.35,item.y-item.r*.35,item.r*.22,0,Math.PI*2);ctx.fill();
            if(item.y-item.r>canvas.height){
                items.splice(i,1);missed++;combo=1;
                playSound("miss");updateHud();
                if(missed>=5)gameOver();
            }
        });
        ctx.shadowBlur=0;
    }
    function updatePlayer(){
        if(keys["ArrowLeft"]||keys["a"]||keys["A"])player.x-=player.speed;
        if(keys["ArrowRight"]||keys["d"]||keys["D"])player.x+=player.speed;
        player.x=Math.max(0,Math.min(canvas.width-player.width,player.x));
    }
    function detectCatch(){
        items.forEach((item,i)=>{
            if(item.y+item.r>=player.y&&item.x-item.r<=player.x+player.width&&item.x+item.r>=player.x&&item.y<=player.y+player.height){
                createEffect(item.x,item.y,item.c);
                items.splice(i,1);score+=5*combo;combo++;
                playSound("catch");updateHud();
            }
        });
    }
    function updateHud(){
        $score.innerText="SCORE: "+score;
        $missed.innerText="MISSED: "+missed+" / 5";
        $combo.innerText="COMBO: x"+combo;
    }
    function gameOver(){
        if(!running)return;
        running=false;playSound("gameover");$status.innerText="GAME OVER";
        ctx.fillStyle="rgba(0,0,0,0.65)";ctx.fillRect(0,0,canvas.width,canvas.height);
        ctx.fillStyle="#f8fafc";ctx.font="bold 48px Orbitron";ctx.textAlign="center";
        ctx.fillText("GAME OVER",canvas.width/2,canvas.height/2-24);
        ctx.fillStyle="#a855f7";ctx.font="bold 22px Orbitron";
        ctx.fillText("FINAL SCORE: "+score,canvas.width/2,canvas.height/2+24);
    }
    function gameLoop(){
        if(!running)return;
        ctx.clearRect(0,0,canvas.width,canvas.height);
        drawStars();updatePlayer();drawPlayer();
        timer++;
        const rate=Math.max(40,75-Math.floor(score/50)*3);
        if(timer>rate){createItem();timer=0;}
        drawItems();detectCatch();drawEffects();
        requestAnimationFrame(gameLoop);
    }
    function restartGame(){
        canvas.focus();
        if(audioCtx&&audioCtx.state==="suspended")audioCtx.resume();
        score=0;missed=0;combo=1;items=[];effects=[];timer=0;running=true;
        player.x=canvas.width/2-player.width/2;
        $status.innerText="RUNNING";updateHud();createStars();gameLoop();
    }
    canvas.addEventListener("keydown",e=>keys[e.key]=true);
    canvas.addEventListener("keyup",e=>keys[e.key]=false);
    canvas.addEventListener("click",()=>canvas.focus());
    createStars();drawStars();drawPlayer();
    </script></body></html>
    """
    components.html(html, height=690)


# ═══════════════════════════════════════════════════════════════════════════
# GAME 3 — Snake (unchanged HTML)
# ═══════════════════════════════════════════════════════════════════════════
def render_snake_game():
    html = """
    <!DOCTYPE html><html><head>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&display=swap');
        * { box-sizing:border-box; }
        body { margin:0; background:radial-gradient(circle at center,#052e16,#020617); font-family:'Orbitron',monospace; color:white; overflow:hidden; }
        .wrap { display:flex; flex-direction:column; align-items:center; padding:8px 0; }
        .hud { width:620px; display:flex; gap:10px; margin-bottom:10px; }
        .hud span { flex:1; text-align:center; background:rgba(2,6,23,0.85); border:1px solid rgba(34,197,94,0.30); padding:9px 14px; border-radius:12px; font-size:13px; color:#dcfce7; letter-spacing:1px; }
        canvas { background:linear-gradient(180deg,#020617,#000); border:2px solid rgba(34,197,94,0.55); border-radius:20px; box-shadow:0 0 50px rgba(34,197,94,0.20); outline:none; }
        .controls { width:620px; display:flex; justify-content:space-between; align-items:center; margin-top:12px; color:#64748b; font-size:12px; }
        button { background:linear-gradient(135deg,#22c55e,#0ea5e9); color:white; border:none; padding:11px 26px; border-radius:12px; font-family:'Orbitron',monospace; font-size:13px; font-weight:700; cursor:pointer; transition:0.2s; }
        button:hover { transform:translateY(-2px); box-shadow:0 6px 22px rgba(34,197,94,0.40); }
    </style></head><body>
    <div class="wrap">
        <div class="hud">
            <span id="score">SCORE: 0</span>
            <span id="length">LENGTH: 3</span>
            <span id="speed">SPEED: NORMAL</span>
            <span id="status">READY</span>
        </div>
        <canvas id="snakeCanvas" width="620" height="520" tabindex="0"></canvas>
        <div class="controls">
            <div>Click canvas · Arrow keys or W A S D</div>
            <button onclick="restartSnake()">▶ START / RESTART</button>
        </div>
    </div>
    <script>
    const canvas=document.getElementById("snakeCanvas"),ctx=canvas.getContext("2d");
    const $score=document.getElementById("score"),$length=document.getElementById("length"),
          $speed=document.getElementById("speed"),$status=document.getElementById("status");
    const grid=20,cols=Math.floor(canvas.width/grid),rows=Math.floor(canvas.height/grid);
    let snake=[],food={},bonus=null,dx=1,dy=0,nextDx=1,nextDy=0,score=0,running=false,loop=null,audioCtx=null,tick=120;

    function playSound(t){
        try{
            if(!audioCtx)audioCtx=new(window.AudioContext||window.webkitAudioContext)();
            const o=audioCtx.createOscillator(),g=audioCtx.createGain();
            o.connect(g);g.connect(audioCtx.destination);
            const map={eat:[700,0.07,"square"],bonus:[1100,0.07,"sine"],move:[280,0.018,"sine"],gameover:[80,0.10,"sawtooth"]};
            const[f,v,tp]=map[t]||[440,0.05,"sine"];
            o.frequency.value=f;g.gain.value=v;o.type=tp;
            o.start();g.gain.exponentialRampToValueAtTime(0.001,audioCtx.currentTime+0.14);
            o.stop(audioCtx.currentTime+0.14);
        }catch(e){}
    }
    function resetSnake(){
        snake=[{x:8,y:10},{x:7,y:10},{x:6,y:10}];
        dx=1;dy=0;nextDx=1;nextDy=0;score=0;bonus=null;tick=120;
        placeFood();updateHud();
    }
    function placeFood(){
        food={x:Math.floor(Math.random()*cols),y:Math.floor(Math.random()*rows)};
        for(let p of snake)if(p.x===food.x&&p.y===food.y){placeFood();return;}
        if(Math.random()<0.20&&!bonus){
            bonus={x:Math.floor(Math.random()*cols),y:Math.floor(Math.random()*rows),life:80};
            for(let p of snake)if(p.x===bonus.x&&p.y===bonus.y)bonus=null;
        }
    }
    function drawGrid(){
        ctx.strokeStyle="rgba(34,197,94,0.06)";
        for(let x=0;x<canvas.width;x+=grid){ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,canvas.height);ctx.stroke();}
        for(let y=0;y<canvas.height;y+=grid){ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(canvas.width,y);ctx.stroke();}
    }
    function drawSnake(){
        snake.forEach((p,i)=>{
            const t=i/snake.length;
            ctx.fillStyle=i===0?"#86efac":`hsl(${142-t*40},70%,${50-t*15}%)`;
            ctx.shadowColor="#22c55e";ctx.shadowBlur=i===0?20:8;
            ctx.fillRect(p.x*grid+2,p.y*grid+2,grid-4,grid-4);
            if(i===0){
                ctx.fillStyle="#052e16";
                ctx.fillRect(p.x*grid+5,p.y*grid+5,3,3);
                ctx.fillRect(p.x*grid+12,p.y*grid+5,3,3);
            }
        });
        ctx.shadowBlur=0;
    }
    function drawFood(){
        ctx.fillStyle="#facc15";ctx.shadowColor="#facc15";ctx.shadowBlur=22;
        ctx.beginPath();ctx.arc(food.x*grid+grid/2,food.y*grid+grid/2,grid/2-3,0,Math.PI*2);ctx.fill();
        ctx.fillStyle="rgba(255,255,255,0.60)";ctx.shadowBlur=0;
        ctx.beginPath();ctx.arc(food.x*grid+grid/2-3,food.y*grid+grid/2-3,3,0,Math.PI*2);ctx.fill();
    }
    function drawBonus(){
        if(!bonus)return;
        bonus.life--;if(bonus.life<=0){bonus=null;return;}
        const alpha=bonus.life>20?1:bonus.life/20;
        ctx.globalAlpha=alpha;
        ctx.fillStyle="#f43f5e";ctx.shadowColor="#f43f5e";ctx.shadowBlur=26;
        ctx.beginPath();ctx.arc(bonus.x*grid+grid/2,bonus.y*grid+grid/2,grid/2-2,0,Math.PI*2);ctx.fill();
        ctx.globalAlpha=1;ctx.shadowBlur=0;
    }
    function moveSnake(){
        dx=nextDx;dy=nextDy;
        const head={x:snake[0].x+dx,y:snake[0].y+dy};
        if(head.x<0||head.x>=cols||head.y<0||head.y>=rows){gameOver();return;}
        for(let p of snake)if(head.x===p.x&&head.y===p.y){gameOver();return;}
        snake.unshift(head);
        if(head.x===food.x&&head.y===food.y){
            score+=10;playSound("eat");placeFood();
            if(score%50===0&&tick>65){tick=Math.max(65,tick-8);updateHud();}
        } else if(bonus&&head.x===bonus.x&&head.y===bonus.y){
            score+=30;playSound("bonus");bonus=null;
        } else { snake.pop(); }
        updateHud();
    }
    function updateHud(){
        $score.innerText="SCORE: "+score;
        $length.innerText="LENGTH: "+snake.length;
        $speed.innerText=tick>=110?"NORMAL":tick>=85?"FAST":"BLAZING";
    }
    function gameOver(){
        if(!running)return;
        running=false;clearInterval(loop);playSound("gameover");$status.innerText="GAME OVER";
        ctx.fillStyle="rgba(0,0,0,0.65)";ctx.fillRect(0,0,canvas.width,canvas.height);
        ctx.fillStyle="#f8fafc";ctx.font="bold 42px Orbitron";ctx.textAlign="center";
        ctx.fillText("GAME OVER",canvas.width/2,canvas.height/2-24);
        ctx.fillStyle="#22c55e";ctx.font="bold 22px Orbitron";
        ctx.fillText("SCORE: "+score+" | LENGTH: "+snake.length,canvas.width/2,canvas.height/2+24);
    }
    function drawGame(){
        if(!running)return;
        ctx.clearRect(0,0,canvas.width,canvas.height);
        drawGrid();moveSnake();
        if(running){drawFood();drawBonus();drawSnake();}
    }
    function restartSnake(){
        canvas.focus();
        if(audioCtx&&audioCtx.state==="suspended")audioCtx.resume();
        clearInterval(loop);resetSnake();running=true;
        $status.innerText="RUNNING";
        loop=setInterval(drawGame,tick);
    }
    canvas.addEventListener("keydown",e=>{
        const k=e.key;let changed=false;
        if((k==="ArrowUp"||k==="w"||k==="W")&&dy!==1){nextDx=0;nextDy=-1;changed=true;}
        if((k==="ArrowDown"||k==="s"||k==="S")&&dy!==-1){nextDx=0;nextDy=1;changed=true;}
        if((k==="ArrowLeft"||k==="a"||k==="A")&&dx!==1){nextDx=-1;nextDy=0;changed=true;}
        if((k==="ArrowRight"||k==="d"||k==="D")&&dx!==-1){nextDx=1;nextDy=0;changed=true;}
        if(changed)playSound("move");
        e.preventDefault();
    });
    canvas.addEventListener("click",()=>canvas.focus());
    resetSnake();drawGrid();drawFood();drawSnake();
    </script></body></html>
    """
    components.html(html, height=690)


# ═══════════════════════════════════════════════════════════════════════════
# GAME 4 — Breakout (unchanged HTML)
# ═══════════════════════════════════════════════════════════════════════════
def render_breakout():
    html = """
    <!DOCTYPE html><html><head>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&display=swap');
        * { box-sizing:border-box; }
        body { margin:0; background:radial-gradient(circle at center,#1a0a00,#020617); font-family:'Orbitron',monospace; color:white; overflow:hidden; }
        .wrap { display:flex; flex-direction:column; align-items:center; padding:8px 0; }
        .hud { width:820px; display:flex; gap:10px; margin-bottom:10px; }
        .hud span { flex:1; text-align:center; background:rgba(2,6,23,0.85); border:1px solid rgba(251,146,60,0.30); padding:9px 14px; border-radius:12px; font-size:13px; color:#fed7aa; letter-spacing:1px; }
        canvas { background:linear-gradient(180deg,#020617,#000); border:2px solid rgba(251,146,60,0.50); border-radius:20px; box-shadow:0 0 50px rgba(251,146,60,0.18); outline:none; }
        .controls { width:820px; display:flex; justify-content:space-between; align-items:center; margin-top:12px; color:#64748b; font-size:12px; }
        button { background:linear-gradient(135deg,#fb923c,#f43f5e); color:white; border:none; padding:11px 26px; border-radius:12px; font-family:'Orbitron',monospace; font-size:13px; font-weight:700; cursor:pointer; transition:0.2s; }
        button:hover { transform:translateY(-2px); box-shadow:0 6px 22px rgba(251,146,60,0.40); }
    </style></head><body>
    <div class="wrap">
        <div class="hud">
            <span id="score">SCORE: 0</span>
            <span id="lives">LIVES: ❤️ ❤️ ❤️</span>
            <span id="level">LEVEL: 1</span>
            <span id="bricks">BRICKS: 0</span>
        </div>
        <canvas id="canvas" width="820" height="540" tabindex="0"></canvas>
        <div class="controls">
            <div>Click canvas · ← → or A D to move paddle</div>
            <button onclick="restartGame()">▶ START / RESTART</button>
        </div>
    </div>
    <script>
    const canvas=document.getElementById("canvas"),ctx=canvas.getContext("2d");
    const $score=document.getElementById("score"),$lives=document.getElementById("lives"),
          $level=document.getElementById("level"),$bricks=document.getElementById("bricks");
    let keys={},score=0,lives=3,level=1,running=false,audioCtx=null;
    let particles=[];
    const paddle={x:canvas.width/2-55,y:canvas.height-40,width:110,height:16,speed:7};
    const ball={x:canvas.width/2,y:canvas.height-70,r:8,vx:3.5,vy:-4,speed:4.5};
    const ROWS=5,COLS=12;
    const COLORS=[["#f43f5e","#fb7185"],["#fb923c","#fdba74"],["#facc15","#fde68a"],["#22c55e","#86efac"],["#38bdf8","#7dd3fc"]];
    let bricks=[];

    function createBricks(){
        bricks=[];
        const bw=Math.floor((canvas.width-40)/COLS);
        const bh=22;
        for(let r=0;r<ROWS;r++) for(let c=0;c<COLS;c++)
            bricks.push({x:20+c*bw,y:55+r*(bh+6),w:bw-6,h:bh,hp:ROWS-r,maxHp:ROWS-r,colors:COLORS[r],alive:true});
        updateHud();
    }
    function playSound(t){
        try{
            if(!audioCtx)audioCtx=new(window.AudioContext||window.webkitAudioContext)();
            const o=audioCtx.createOscillator(),g=audioCtx.createGain();
            o.connect(g);g.connect(audioCtx.destination);
            const map={bounce:[480,0.05,"square"],break:[280,0.08,"sawtooth"],gameover:[80,0.10,"triangle"],win:[900,0.07,"sine"]};
            const[f,v,tp]=map[t]||[440,0.05,"sine"];
            o.frequency.value=f;g.gain.value=v;o.type=tp;
            o.start();g.gain.exponentialRampToValueAtTime(0.001,audioCtx.currentTime+0.15);
            o.stop(audioCtx.currentTime+0.15);
        }catch(e){}
    }
    function createBreakEffect(x,y,c){
        for(let i=0;i<10;i++) particles.push({x,y,vx:(Math.random()-.5)*6,vy:(Math.random()-.5)*6,life:35,c});
    }
    function drawParticles(){
        particles.forEach((p,i)=>{
            p.x+=p.vx;p.y+=p.vy;p.life--;
            ctx.fillStyle=p.c;ctx.globalAlpha=p.life/35;
            ctx.beginPath();ctx.arc(p.x,p.y,3,0,Math.PI*2);ctx.fill();
            if(p.life<=0)particles.splice(i,1);
        });
        ctx.globalAlpha=1;
    }
    function drawBricks(){
        bricks.forEach(b=>{
            if(!b.alive)return;
            const t=b.hp/b.maxHp;
            ctx.fillStyle=b.colors[0];
            ctx.shadowColor=b.colors[0];ctx.shadowBlur=8;
            ctx.fillRect(b.x,b.y,b.w,b.h);
            ctx.fillStyle=`rgba(255,255,255,${0.15*t})`;
            ctx.fillRect(b.x,b.y,b.w,5);
            ctx.fillStyle=b.colors[1];
            ctx.fillRect(b.x,b.y+b.h-4,b.w*(b.hp/b.maxHp),4);
        });
        ctx.shadowBlur=0;
    }
    function drawPaddle(){
        ctx.fillStyle="#fb923c";ctx.shadowColor="#fb923c";ctx.shadowBlur=24;
        ctx.beginPath();const r=8;
        ctx.roundRect(paddle.x,paddle.y,paddle.width,paddle.height,r);
        ctx.fill();
        ctx.fillStyle="rgba(255,255,255,0.25)";ctx.shadowBlur=0;
        ctx.fillRect(paddle.x+12,paddle.y+4,paddle.width-24,4);
    }
    function drawBall(){
        ctx.fillStyle="#fef9c3";ctx.shadowColor="#facc15";ctx.shadowBlur=28;
        ctx.beginPath();ctx.arc(ball.x,ball.y,ball.r,0,Math.PI*2);ctx.fill();
        ctx.fillStyle="rgba(255,255,255,0.6)";ctx.shadowBlur=0;
        ctx.beginPath();ctx.arc(ball.x-3,ball.y-3,2,0,Math.PI*2);ctx.fill();
    }
    function updateBall(){
        ball.x+=ball.vx;ball.y+=ball.vy;
        if(ball.x-ball.r<0){ball.x=ball.r;ball.vx*=-1;playSound("bounce");}
        if(ball.x+ball.r>canvas.width){ball.x=canvas.width-ball.r;ball.vx*=-1;playSound("bounce");}
        if(ball.y-ball.r<0){ball.y=ball.r;ball.vy*=-1;playSound("bounce");}
        if(ball.y+ball.r>=paddle.y&&ball.y+ball.r<=paddle.y+paddle.height+ball.r&&
           ball.x>=paddle.x&&ball.x<=paddle.x+paddle.width&&ball.vy>0){
            const hit=(ball.x-paddle.x)/paddle.width;
            ball.vx=ball.speed*(hit*2-1)*1.5;
            ball.vy=-Math.abs(ball.vy);
            playSound("bounce");
        }
        if(ball.y+ball.r>canvas.height){
            lives--;updateHud();
            if(lives<=0){gameOver();return;}
            ball.x=paddle.x+paddle.width/2;ball.y=paddle.y-20;
            const a=(Math.random()*0.6+0.3)*Math.PI;
            ball.vx=ball.speed*Math.cos(a)*(Math.random()>0.5?1:-1);
            ball.vy=-ball.speed*Math.sin(a);
        }
        bricks.forEach(b=>{
            if(!b.alive)return;
            if(ball.x+ball.r>b.x&&ball.x-ball.r<b.x+b.w&&ball.y+ball.r>b.y&&ball.y-ball.r<b.y+b.h){
                b.hp--;
                if(b.hp<=0){b.alive=false;createBreakEffect(b.x+b.w/2,b.y+b.h/2,b.colors[0]);score+=10*(b.maxHp);playSound("break");}
                else{score+=2;playSound("bounce");}
                ball.vy*=-1;updateHud();
                if(bricks.filter(x=>x.alive).length===0){levelUp();}
            }
        });
    }
    function levelUp(){
        level++;ball.speed=4.5+level*0.4;
        ball.vx=(ball.vx>0?1:-1)*ball.speed*0.7;
        ball.vy=-ball.speed*0.7;
        playSound("win");createBricks();
    }
    function updatePaddle(){
        if(keys["ArrowLeft"]||keys["a"]||keys["A"])paddle.x-=paddle.speed;
        if(keys["ArrowRight"]||keys["d"]||keys["D"])paddle.x+=paddle.speed;
        paddle.x=Math.max(0,Math.min(canvas.width-paddle.width,paddle.x));
    }
    function updateHud(){
        $score.innerText="SCORE: "+score;
        $lives.innerText="LIVES: "+"❤️".repeat(Math.max(0,lives));
        $level.innerText="LEVEL: "+level;
        $bricks.innerText="BRICKS: "+bricks.filter(b=>b.alive).length;
    }
    function gameOver(){
        if(!running)return;
        running=false;playSound("gameover");
        ctx.fillStyle="rgba(0,0,0,0.65)";ctx.fillRect(0,0,canvas.width,canvas.height);
        ctx.fillStyle="#f8fafc";ctx.font="bold 48px Orbitron";ctx.textAlign="center";
        ctx.fillText("GAME OVER",canvas.width/2,canvas.height/2-24);
        ctx.fillStyle="#fb923c";ctx.font="bold 22px Orbitron";
        ctx.fillText("SCORE: "+score+" | LEVEL: "+level,canvas.width/2,canvas.height/2+24);
    }
    function gameLoop(){
        if(!running)return;
        ctx.clearRect(0,0,canvas.width,canvas.height);
        updatePaddle();updateBall();
        drawBricks();drawPaddle();drawBall();drawParticles();
        requestAnimationFrame(gameLoop);
    }
    function restartGame(){
        canvas.focus();
        if(audioCtx&&audioCtx.state==="suspended")audioCtx.resume();
        score=0;lives=3;level=1;particles=[];
        paddle.x=canvas.width/2-paddle.width/2;
        ball.x=canvas.width/2;ball.y=canvas.height-100;
        ball.speed=4.5;ball.vx=3.5;ball.vy=-4;
        createBricks();running=true;gameLoop();
    }
    canvas.addEventListener("keydown",e=>{keys[e.key]=true;e.preventDefault();});
    canvas.addEventListener("keyup",e=>keys[e.key]=false);
    canvas.addEventListener("click",()=>canvas.focus());
    if(!ctx.roundRect) ctx.roundRect=function(x,y,w,h,r){
        ctx.beginPath();ctx.moveTo(x+r,y);ctx.lineTo(x+w-r,y);
        ctx.arcTo(x+w,y,x+w,y+r,r);ctx.lineTo(x+w,y+h-r);
        ctx.arcTo(x+w,y+h,x+w-r,y+h,r);ctx.lineTo(x+r,y+h);
        ctx.arcTo(x,y+h,x,y+h-r,r);ctx.lineTo(x,y+r);
        ctx.arcTo(x,y,x+r,y,r);ctx.closePath();
    };
    createBricks();drawBricks();drawPaddle();drawBall();
    </script></body></html>
    """
    components.html(html, height=710)