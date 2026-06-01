import streamlit as st

def apply_neon_cyber_theme(page_title: str, page_subtitle: str = ""):
    st.markdown(f"""
    <style>
    .cyber-topbar {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 18px;
        padding: 14px 18px;
        border-radius: 20px;
        background: rgba(8, 15, 32, 0.55);
        border: 1px solid rgba(0,255,255,0.16);
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        box-shadow:
            0 0 18px rgba(0,255,255,0.08),
            inset 0 1px 0 rgba(255,255,255,0.04);
        animation: cyberFadeUp 0.6s ease;
    }}

    .cyber-brand {{
        color: #e6fbff;
        font-size: 18px;
        font-weight: 800;
        letter-spacing: 0.4px;
        text-shadow: 0 0 10px rgba(0,255,255,0.12);
    }}

    .cyber-hero {{
        position: relative;
        overflow: hidden;
        background: linear-gradient(180deg, rgba(8,15,32,0.72), rgba(14,24,56,0.68));
        border: 1px solid rgba(0,255,255,0.18);
        border-radius: 30px;
        padding: 34px 28px;
        text-align: center;
        backdrop-filter: blur(18px);
        -webkit-backdrop-filter: blur(18px);
        box-shadow:
            0 0 28px rgba(0,255,255,0.08),
            0 18px 46px rgba(0,0,0,0.30);
        margin-bottom: 24px;
        animation: cyberFadeUp 0.7s ease;
    }}

    .cyber-hero::before {{
        content: "";
        position: absolute;
        top: -140%;
        left: -25%;
        width: 45%;
        height: 320%;
        transform: rotate(24deg);
        background: linear-gradient(
            to right,
            rgba(255,255,255,0.00),
            rgba(0,255,255,0.10),
            rgba(255,255,255,0.00)
        );
        animation: cyberSweep 6.5s linear infinite;
        pointer-events: none;
    }}

    .cyber-title {{
        font-size: 52px;
        font-weight: 900;
        margin-bottom: 10px;
        line-height: 1.08;
        letter-spacing: -0.6px;
        background: linear-gradient(90deg, #ffffff, #8ef9ff, #7c9dff, #c084fc, #ffffff);
        background-size: 220% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 18px rgba(0,255,255,0.08);
        animation: cyberGradient 7s linear infinite;
    }}

    .cyber-subtitle {{
        color: #d9f6ff;
        font-size: 18px;
        line-height: 1.9;
        max-width: 900px;
        margin: 0 auto;
    }}

    .cyber-card {{
        position: relative;
        overflow: hidden;
        background: linear-gradient(180deg, rgba(7,14,28,0.72), rgba(14,22,44,0.72));
        border: 1px solid rgba(0,255,255,0.18);
        border-radius: 24px;
        padding: 24px 20px;
        text-align: center;
        min-height: 228px;
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        box-shadow:
            0 0 18px rgba(0,255,255,0.08),
            0 14px 34px rgba(0,0,0,0.24);
        transition: 0.3s ease;
        margin-bottom: 10px;
        animation: cyberFadeUp 0.8s ease;
    }}

    .cyber-card::before {{
        content: "";
        position: absolute;
        top: -150%;
        left: -38%;
        width: 52%;
        height: 320%;
        transform: rotate(24deg);
        background: linear-gradient(
            to right,
            rgba(255,255,255,0.00),
            rgba(0,255,255,0.12),
            rgba(255,255,255,0.00)
        );
        transition: 0.5s ease;
        pointer-events: none;
    }}

    .cyber-card:hover {{
        transform: translateY(-8px) scale(1.02);
        box-shadow:
            0 0 28px rgba(0,255,255,0.16),
            0 20px 40px rgba(0,0,0,0.28);
        border-color: rgba(0,255,255,0.28);
    }}

    .cyber-card:hover::before {{
        left: 120%;
    }}

    .cyber-icon-wrap {{
        width: 88px;
        height: 88px;
        margin: 0 auto 14px auto;
        border-radius: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(180deg, rgba(0,255,255,0.10), rgba(124,58,237,0.10));
        border: 1px solid rgba(0,255,255,0.16);
        box-shadow: 0 0 18px rgba(0,255,255,0.08);
        transition: 0.3s ease;
    }}

    .cyber-icon {{
        font-size: 46px;
        transition: 0.3s ease;
    }}

    .cyber-card:hover .cyber-icon-wrap {{
        transform: scale(1.08);
        animation: neonPulse 1.2s infinite;
    }}

    .cyber-card:hover .cyber-icon {{
        transform: scale(1.14) rotate(4deg);
        filter: drop-shadow(0 0 10px rgba(0,255,255,0.65));
    }}

    .cyber-card-title {{
        color: white;
        font-size: 24px;
        font-weight: 800;
        margin-bottom: 8px;
    }}

    .cyber-card-desc {{
        color: #d7edff;
        font-size: 15px;
        line-height: 1.8;
    }}

    .cyber-panel {{
        background: linear-gradient(180deg, rgba(7,14,28,0.72), rgba(14,22,44,0.72));
        border: 1px solid rgba(0,255,255,0.16);
        border-radius: 24px;
        padding: 22px;
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        box-shadow:
            0 0 20px rgba(0,255,255,0.08),
            0 14px 34px rgba(0,0,0,0.24);
        margin-top: 18px;
        margin-bottom: 18px;
        animation: cyberFadeUp 0.8s ease;
    }}

    .cyber-section-title {{
        color: white;
        font-size: 25px;
        font-weight: 800;
        margin-bottom: 8px;
    }}

    .cyber-section-desc {{
        color: #d7edff;
        font-size: 16px;
        line-height: 1.85;
    }}

    .cyber-info {{
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(0,255,255,0.12);
        border-radius: 18px;
        padding: 14px 16px;
        color: #e8f8ff;
        font-size: 15px;
        line-height: 1.8;
        margin-top: 12px;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.03);
    }}

    @keyframes cyberGradient {{
        0% {{ background-position: 0% center; }}
        100% {{ background-position: 220% center; }}
    }}

    @keyframes cyberSweep {{
        0% {{ left: -35%; }}
        100% {{ left: 130%; }}
    }}
    </style>

    <div class="cyber-topbar">
        <div class="cyber-brand">Neon Cyber UI</div>
        <div class="cyber-brand">Ultra Platform</div>
    </div>

    <div class="cyber-hero">
        <div class="cyber-title">{page_title}</div>
        <div class="cyber-subtitle">{page_subtitle}</div>
    </div>
    """, unsafe_allow_html=True)