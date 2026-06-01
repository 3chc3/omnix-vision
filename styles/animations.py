import streamlit as st

def apply_particles():
    st.markdown("""
    <style>
    .particle {
        position: fixed;
        width: 5px;
        height: 5px;
        background: white;
        border-radius: 50%;
        animation: float 10s infinite;
    }

    @keyframes float {
        0% {transform: translateY(0);}
        100% {transform: translateY(-800px);}
    }
    </style>
    """, unsafe_allow_html=True)