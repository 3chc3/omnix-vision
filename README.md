# 🚀 OMNIX VISION

> **AI-Powered Smart Multimedia Platform — Neon Cyber UI**

An intelligent multimedia platform that combines computer vision, multimedia
processing, productivity tools, games, and an AI assistant — all in one
beautiful neon-cyber interface. Designed to be **modular**, **secure**, and
**offline-first** with full bilingual support (English + Arabic + RTL).

---

## ✨ Features

### 🧠 AI & Vision

- **Camera AI** — Real-time pose + hand detection with MediaPipe
- **Hand Scan Authentication** — Right hand grants, left hand denies (5-second scan)
- **AI Assistant** — 18 keyword-based response categories with chat history
- **Live Dashboard** — Plotly charts, 7-day activity trends, system health

### ⚡ Productivity

- **Smart Tasks Manager** — Priorities, due dates, tags, search, filters
- **Pomodoro Studio** — Standalone timer with auto-cycling and statistics
- **Advanced Calculator** — 8 tabs: Basic, Scientific, Solver, Graph, Units, Number Systems, Formulas, History
- **Notifications Center** — Per-user alerts with priority and archive

### 🎬 Media & Entertainment

- **Media Library** — Gallery with 12 image filters + crop + resize + rotate
- **Media Converter** — Image/Audio/Video conversion (FFmpeg-powered)
- **Game Center** — 4 games with persistent per-user high scores:
  - 🚀 Space Defender · ⭐ Neon Catcher · 🐍 Snake · 🧱 Breakout
- **Random Tools** — QR codes, password generator, color palettes, UUIDs

### 🛡️ Security & System

- **Security Center** — Password change, account management
- **Activity Log** — Full audit trail with category filtering
- **Backup & Restore** — ZIP export/import of all user data
- **Settings** — Language switcher, preferences

---

## 🎯 Highlights

| Aspect | Detail |
| --- | --- |
| 📦 Modules | **18 fully integrated pages** |
| 🌐 Languages | **English + Arabic with full RTL support** (288 translation keys) |
| 🔒 Security | **SHA-256 password hashing** + brute-force lockout (5-attempt) |
| 💾 Storage | **JSON-based persistence** (offline-first, no external DB) |
| 🎨 Design | **Neon-cyber theme** with Orbitron + Rajdhani fonts |
| ⚙️ Stack | **Python 3.10+ · Streamlit · OpenCV · MediaPipe · Pillow · Plotly** |

---

## 📥 Installation

### Prerequisites

- Python **3.10 or higher**
- (Optional) **FFmpeg** for audio/video conversion features

### Quick Start

```bash
# Clone the repository
git clone <your-repo-url>
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

Open your browser at <http://localhost:8501> 🎉

### Optional: FFmpeg for media conversion

Audio and video conversion in the Media Converter module requires FFmpeg.

- **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH
- **macOS**: `brew install ffmpeg`
- **Linux**: `sudo apt install ffmpeg`

Without FFmpeg the app still works — those tabs simply show a friendly warning.

---

## 🚦 First Steps

1. **Register** a new account on the Login page (you'll see your User ID — save it).
2. **Log in** with your User ID + password.
3. From the **Home** hub, explore all 18 modules organized into 4 categories:
   - 🧠 **AI & Vision**
   - ⚡ **Productivity**
   - 🎬 **Media & Fun**
   - 🛡️ **System**
4. Switch language with the **🌐 dropdown** at the top — full RTL support included.

---

## 📁 Project Structure

```text
My_projrct/
├── app.py                        # Router with all 18 pages
├── requirements.txt              # Python dependencies
├── README.md                     # ← this file
├── LICENSE                       # MIT
├── CHANGELOG.md                  # Version history
├── CONTRIBUTING.md               # Development guide
├── .gitignore
├── .streamlit/
│   └── config.toml               # Theme + server config
├── data/                         # JSON persistence (auto-created)
│   ├── users.json
│   ├── activity_log.json
│   ├── tasks.json
│   ├── notifications.json
│   ├── high_scores.json
│   ├── chat_history.json
│   ├── calc_history.json
│   ├── pomodoro_log.json
│   └── backups/
├── pages/                        # 18 page modules
├── utils/                        # auth, language, activity, storage
├── styles/                       # Optional centralized CSS
│   └── main.css
└── assets/                       # Audio, images, video, uploads
```

---

## 🔐 Security Notes

- Passwords are stored as **SHA-256 hashes** with **per-user salt** — never in plain text.

- Failed login attempts trigger a **5-minute lockout after 5 attempts**.
- Legacy plain-text passwords are **automatically upgraded** on next login.
- All authentication events are recorded in the **Activity Log**.
- ZIP restore in Backup module protects against **path-traversal attacks**.

> ⚠️ This is a personal/educational project. For production deployment with
> multiple users, consider adding HTTPS, rate-limiting at the proxy layer,
> and a real database backend.

---

## 🌐 Translation System

OMNIX VISION supports English and Arabic out of the box with 288 translation
keys. To add a new language:

1. Open `utils/language.py`.
2. Add a new code (e.g., `"fr"`) to the `LANGUAGES` dict.
3. Add a matching block in `TRANSLATIONS` with all keys translated.
4. The selector will pick it up automatically.

To verify completeness:

```python
from utils.language import missing_translations
print(missing_translations("ar"))  # should be []
```

---

## 🛠️ Adding a New Page

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the full step-by-step guide, but
in short:

1. Create `pages/your_page.py` with a `render_your_page()` function.
2. Register it in `app.py` inside `_safe_import()`.
3. Add a button in `pages/home.py` setting `st.session_state.page = "your_page"`.
4. Add translation keys to `utils/language.py` (both EN and AR).

---

## 📊 Tech Stack

| Layer | Technology |
| --- | --- |
| **Frontend** | Streamlit 1.30+ with custom neon-cyber CSS |
| **Computer Vision** | OpenCV 4.8+ · MediaPipe 0.10+ |
| **Image Processing** | Pillow 10+ |
| **Charts** | Plotly 5+ · Matplotlib 3.7+ |
| **Storage** | JSON files (UTF-8, ASCII-safe) |
| **Security** | hashlib SHA-256 + secrets |
| **QR / Random** | qrcode[pil] · secrets |

---

## 🗺️ Roadmap

### ✅ v2.0 — Current

- 18 modules with full bilingual support
- Secure authentication and audit logging
- JSON-based persistence

### 🚧 v2.1 — Planned

- Cloud sync (optional Supabase / Firebase backend)
- Mobile-responsive CSS tweaks
- Email notifications via SMTP
- Two-factor authentication (TOTP)

### 💡 v3.0 — Future

- Real AI integration (OpenAI / Anthropic API for assistant)
- Voice commands
- Plugin system for custom pages
- Multi-tenant deployment mode

See full history in [`CHANGELOG.md`](CHANGELOG.md).

---

## 📜 License

MIT — see [`LICENSE`](LICENSE) for details.

You can use, modify, and distribute OMNIX VISION freely — even commercially.
Just keep the copyright notice.

---

## 🙏 Credits

- **Streamlit** — the framework that makes this UI possible
- **MediaPipe** — Google's incredible CV models
- **Plotly** — beautiful interactive charts
- **Google Fonts** — Orbitron and Rajdhani typefaces

---

## 💬 Support

- 🐛 **Bug reports** — open a GitHub issue
- 💡 **Feature requests** — open a GitHub issue
- 🔒 **Security issues** — email maintainers privately

---

## Built with 💜 by the OMNIX VISION team

⭐ Star this repo if you find it useful!
