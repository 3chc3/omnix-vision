import streamlit as st

def apply_global_theme(title, subtitle=""):
    st.markdown(f"""
    <style>
    .stApp {{
        background:
            radial-gradient(circle at 10% 10%, rgba(255,255,255,0.1), transparent),
            linear-gradient(135deg, #0f172a, #1d4ed8, #0891b2);
        min-height: 100vh;
    }}

    section[data-testid="stSidebar"] {{
        display: none;
    }}

    .hero {{
        text-align: center;
        padding: 40px 20px;
        color: white;
        margin-bottom: 20px;
    }}

    .hero h1 {{
        font-size: 48px;
        font-weight: 900;
        margin-bottom: 10px;
    }}

    .hero p {{
        font-size: 18px;
        color: #e2e8f0;
    }}

    .card {{
        background: rgba(255,255,255,0.12);
        padding: 25px;
        border-radius: 20px;
        text-align: center;
        margin: 10px;
        backdrop-filter: blur(10px);
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        transition: 0.3s;
    }}

    .card:hover {{
        transform: translateY(-5px);
    }}

    div.stButton > button {{
        width: 100%;
        border-radius: 12px;
        padding: 12px;
        font-size: 16px;
        font-weight: bold;
        background: linear-gradient(135deg, #ffffff, #dbeafe);
        color: #0f172a;
        border: none;
    }}

    div.stButton > button:hover {{
        transform: scale(1.03);
    }}
    </style>

    <div class="hero">
        <h1>{title}</h1>
        <p>{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)