import streamlit as st

def apply_base_theme():
    st.markdown("""
    <style>
    .stApp {
        background:
            radial-gradient(circle at 15% 20%, rgba(0, 255, 255, 0.10) 0%, transparent 20%),
            radial-gradient(circle at 85% 15%, rgba(168, 85, 247, 0.12) 0%, transparent 22%),
            radial-gradient(circle at 75% 80%, rgba(236, 72, 153, 0.08) 0%, transparent 18%),
            linear-gradient(135deg, #050816 0%, #0b1120 40%, #111c44 100%);
        min-height: 100vh;
        overflow-x: hidden;
    }

    section[data-testid="stSidebar"] {
        display: none;
    }

    header[data-testid="stHeader"] {
        background: transparent;
    }

    .block-container {
        max-width: 1280px;
        padding-top: 1.2rem;
        padding-bottom: 2rem;
    }

    div.stButton > button {
        width: 100%;
        min-height: 52px;
        border-radius: 14px;
        border: 1px solid rgba(0,255,255,0.28);
        background: linear-gradient(135deg, rgba(255,255,255,0.95), rgba(210,240,255,0.95));
        color: #04111f;
        font-size: 16px;
        font-weight: 800;
        box-shadow:
            0 0 14px rgba(0,255,255,0.10),
            0 10px 22px rgba(0,0,0,0.22);
        transition: 0.2s ease;
    }

    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow:
            0 0 18px rgba(0,255,255,0.20),
            0 14px 26px rgba(0,0,0,0.28);
    }

    @keyframes cyberFadeUp {
        0% { opacity: 0; transform: translateY(12px); }
        100% { opacity: 1; transform: translateY(0); }
    }

    @keyframes neonPulse {
        0% { box-shadow: 0 0 0 rgba(0,255,255,0.0); }
        50% { box-shadow: 0 0 24px rgba(0,255,255,0.20); }
        100% { box-shadow: 0 0 0 rgba(0,255,255,0.0); }
    }
    </style>
    """, unsafe_allow_html=True)