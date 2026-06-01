import streamlit as st

def apply_media_theme():
    st.markdown("""
    <style>
    .media-card {
        background: rgba(255,255,255,0.1);
        border-radius: 20px;
        padding: 30px;
        text-align: center;
        backdrop-filter: blur(10px);
        transition: 0.3s;
    }

    .media-card:hover {
        transform: scale(1.05);
        box-shadow: 0 0 30px rgba(255,255,255,0.2);
    }

    .media-title {
        font-size: 28px;
        color: white;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)