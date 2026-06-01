"""
═══════════════════════════════════════════════════════════════════════════
OMNIX VISION — Main App Router (Phase 4 — Round 2)
═══════════════════════════════════════════════════════════════════════════
Phase-4 changes:
    ✓ Registered 4 new pages: notifications, backup, random_tools, pomodoro
    ✓ Error handling for missing modules
    ✓ Session state initialization
═══════════════════════════════════════════════════════════════════════════
"""

import streamlit as st

# ── Page config (must be first) ───────────────────────────────────────────
st.set_page_config(
    page_title="OMNIX VISION",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ── Page imports with graceful error handling ────────────────────────────
def _safe_import():
    """Import all page render functions, return dict."""
    handlers = {}

    page_modules = {
        "login":          ("pages.login",            "render_login"),
        "home":           ("pages.home",             "render_home"),
        "dashboard":      ("pages.dashboard",        "render_dashboard"),
        "hand_scan":      ("pages.hand_scan",        "render_hand_scan"),
        "camera":         ("pages.camera",           "render_camera"),
        "assistant":      ("pages.assistant",        "render_assistant"),
        "about":          ("pages.about",            "render_about"),
        "media":          ("pages.media",            "render_media"),
        "media_converter":("pages.media_converter",  "render_media_converter"),
        "tasks":          ("pages.tasks",            "render_tasks"),
        "calculator":     ("pages.calculator",       "render_calculator"),
        "game":           ("pages.game",             "render_game"),
        "settings":       ("pages.settings",         "render_settings"),
        "security_center":("pages.security_center",  "render_security_center"),
        "activity_log":   ("pages.activity_log",     "render_activity_log"),
        # New round 2 pages
        "notifications":  ("pages.notifications",    "render_notifications"),
        "backup":         ("pages.backup",           "render_backup"),
        "random_tools":   ("pages.random_tools",     "render_random_tools"),
        "pomodoro":       ("pages.pomodoro",         "render_pomodoro"),
    }

    for page_key, (mod_path, func_name) in page_modules.items():
        try:
            mod = __import__(mod_path, fromlist=[func_name])
            handlers[page_key] = getattr(mod, func_name)
        except ImportError as e:
            print(f"⚠️ Could not load {page_key}: {e}")
            handlers[page_key] = None
        except AttributeError as e:
            print(f"⚠️ Missing function in {page_key}: {e}")
            handlers[page_key] = None

    return handlers


PAGE_HANDLERS = _safe_import()


# ── Initialize session state ──────────────────────────────────────────────
def _init_session():
    defaults = {
        "page":       "login",
        "logged_in":  False,
        "user":       None,
        "language":   "English",
        "auth_mode":  "select",
    }
    for k, v in defaults.items():
        st.session_state.setdefault(k, v)


# ── Main router ───────────────────────────────────────────────────────────
def main():
    _init_session()

    current_page = st.session_state.get("page", "login")
    handler      = PAGE_HANDLERS.get(current_page)

    if handler is None:
        st.error(f"❌ Page '{current_page}' not found or failed to load.")
        st.info("Available pages: " + ", ".join(
            k for k, v in PAGE_HANDLERS.items() if v is not None
        ))
        if st.button("🏠 Go Home"):
            st.session_state.page = "home" if st.session_state.logged_in else "login"
            st.rerun()
        return

    try:
        handler()
    except Exception as e:
        st.error(f"❌ Error rendering page '{current_page}':")
        st.exception(e)
        if st.button("🏠 Go Home"):
            st.session_state.page = "home" if st.session_state.logged_in else "login"
            st.rerun()


if __name__ == "__main__":
    main()