from pathlib import Path
import base64
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent.parent

def play_sound(relative_path: str):
    file_path = BASE_DIR / relative_path
    if not file_path.exists():
        return

    try:
        with open(file_path, "rb") as f:
            data = f.read()
        b64 = base64.b64encode(data).decode()
        st.markdown(
            f"""
            <audio autoplay style="display:none;">
                <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """,
            unsafe_allow_html=True,
        )
    except Exception:
        pass

def click_sound():
    play_sound("assets/audio/click.mp3")

def success_sound():
    play_sound("assets/audio/success.mp3")