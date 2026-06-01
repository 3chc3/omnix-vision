# Contributing to OMNIX VISION

Thank you for your interest in improving OMNIX VISION! This document explains
how the project is organized and how to add features, fix bugs, or extend
translations.

---

## 🛠️ Development Setup

### Prerequisites

- Python 3.10 or higher
- Git
- (Optional) FFmpeg in PATH for audio/video conversion features

### Local Setup

```bash
git clone <your-fork-url>
cd My_projrct

# Create virtual environment
python -m venv .venv

# Activate (Windows PowerShell)
.venv\Scripts\Activate.ps1

# Activate (Linux/macOS)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

---

## 📁 Project Structure

```text
My_projrct/
├── app.py                    # Router with PAGE_HANDLERS dict
├── requirements.txt          # All Python dependencies
├── README.md
├── LICENSE
├── CHANGELOG.md
├── CONTRIBUTING.md           # ← this file
├── .gitignore
├── .streamlit/
│   └── config.toml           # Streamlit theme & server config
├── data/                     # JSON persistence (created at runtime)
│   ├── users.json            # SHA-256 hashed credentials
│   ├── activity_log.json     # Audit trail
│   ├── tasks.json            # Per-user tasks
│   ├── high_scores.json      # Per-user game scores
│   ├── chat_history.json     # Per-user assistant chats
│   ├── calc_history.json     # Per-user calculator
│   ├── notifications.json    # Per-user notifications
│   ├── pomodoro_log.json     # Per-user pomodoro sessions
│   └── backups/              # ZIP backups
├── pages/                    # 18 page modules
│   ├── login.py
│   ├── home.py               # Hub with module buttons
│   ├── dashboard.py          # Charts and stats
│   ├── hand_scan.py
│   ├── camera.py
│   ├── assistant.py
│   ├── about.py
│   ├── media.py
│   ├── media_converter.py
│   ├── tasks.py
│   ├── calculator.py
│   ├── game.py
│   ├── settings.py
│   ├── security_center.py
│   ├── activity_log.py
│   ├── notifications.py
│   ├── backup.py
│   ├── random_tools.py
│   └── pomodoro.py
├── utils/                    # Shared helpers
│   ├── auth.py               # SHA-256 hashing + lockout
│   ├── language.py           # i18n (288 keys EN/AR)
│   ├── activity.py           # Activity log
│   └── storage.py            # JSON helpers (if used)
├── styles/                   # Optional shared CSS
│   └── main.css
└── assets/
    ├── audio/
    ├── images/
    ├── video/
    └── uploads/              # User-uploaded files
```

---

## ✍️ Coding Conventions

### Python Style

- **PEP 8** with a soft 100-char line limit.
- Type hints encouraged but not required.
- Docstrings: triple-quoted `"""..."""` describing purpose, not parameters.
- Avoid one-line lambdas for non-trivial logic.

### Streamlit Patterns

Every page renderer must:

1. Call `init_language()` and `apply_rtl_css()` from `utils.language`.
2. Guard with `if not st.session_state.get("logged_in", False): redirect → login`.
3. Use `st.session_state.setdefault(key, default)` for state init.
4. Log major actions with `log_action(action, user_id, category, details)`.
5. Use `label_visibility="collapsed"` instead of `""` for unlabeled inputs.

### Translation Keys

- Add new keys to **both** `en` and `ar` blocks in `utils/language.py`.
- For page-specific keys, prefer a local `_t()` helper inside the page module.
- Keys are snake_case ASCII; values may contain any Unicode.
- After adding keys, verify with:

```python
from utils.language import missing_translations
print(missing_translations("ar"))  # should print []
```

### CSS

- Each page injects its own CSS via `st.markdown(..., unsafe_allow_html=True)`.
- Use the neon-cyber color palette:
  - Primary: `#38bdf8` (cyan)
  - Accent:  `#a855f7` (purple)
  - Success: `#22c55e` (green)
  - Warning: `#f59e0b` (amber)
  - Error:   `#ef4444` (red)
- Background base: `linear-gradient(135deg, #020617, #06111f, #111032)`.
- Fonts: `'Orbitron'` for headings/numbers, `'Rajdhani'` for body.

---

## 🌐 Adding a New Page

1. Create `pages/your_page.py` with this skeleton:

```python
import streamlit as st
from utils.language import t, init_language, apply_rtl_css, is_rtl
from utils.activity import log_action

def render_your_page():
    init_language()
    apply_rtl_css()

    if not st.session_state.get("logged_in", False):
        st.session_state.page = "login"
        st.rerun()

    user_id = st.session_state.get("user", "anonymous")

    # ── CSS ──
    st.markdown("""<style>...</style>""", unsafe_allow_html=True)

    # ── Back button ──
    back_col, _ = st.columns([1.3, 8])
    with back_col:
        if st.button(t("back"), use_container_width=True, key="yp_back"):
            st.session_state.page = "home"
            st.rerun()

    # ── Your content ──
    st.title("Hello!")
```

1. Register in `app.py` inside `_safe_import()`:

```python
"your_page": ("pages.your_page", "render_your_page"),
```

1. Add a button in `pages/home.py` that sets `st.session_state.page = "your_page"`.

1. Add the page name to `utils/language.py` in both EN and AR blocks.

---

## 🐛 Reporting Issues

Open an issue with:

- A clear title.
- Steps to reproduce.
- Expected vs actual behavior.
- Python version, OS, and `pip list` output.
- Screenshot if visual.

For security issues, do **not** open a public issue — email the maintainers.

---

## 🚀 Pull Request Checklist

Before opening a PR:

- [ ] Code runs locally without errors.
- [ ] New translation keys added to **both** EN and AR.
- [ ] `missing_translations("ar")` returns empty list.
- [ ] No hardcoded credentials or test data.
- [ ] No `print()` debug statements left over.
- [ ] CHANGELOG.md updated under `[Unreleased]`.
- [ ] Files saved as UTF-8 with LF line endings (CRLF on Windows is OK).

---

## 📜 License

By contributing, you agree your contributions will be licensed under the same
MIT license as the project.
