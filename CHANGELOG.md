# Changelog

All notable changes to OMNIX VISION are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.0.0] — 2026-05-28

A complete overhaul transforming OMNIX VISION from a prototype into a
production-ready bilingual multimedia platform with 18 modules.

### Added

#### New Pages (4)

- 🔔 **Notifications Center** — per-user notifications with 4 priority levels, read/unread/archive states, filtering, and manual creation.

- 💾 **Backup & Restore** — ZIP-based export of all JSON data, secure restore with path-traversal protection, and backup management UI.

- 🎲 **Random Tools** — six utilities: QR generator, password generator with strength meter, color picker with palettes, UUID generator, random numbers, and Lorem Ipsum text.

- 🍅 **Pomodoro Studio** — standalone timer with phase auto-cycling, per-user session history, daily/weekly statistics, and streak counter.

#### Existing Page Enhancements

- 📝 **Tasks** — rewritten with priorities (Low/Medium/High/Urgent), due dates with overdue alerts, 6 colored tags, completion checkboxes, search, filters, built-in Pomodoro, stopwatch, and JSON persistence.

- 🎮 **Game Center** — high scores now persist per user in `data/high_scores.json` with manual score submission.

- 🤖 **AI Assistant** — expanded from 7 to 18 keyword response categories, bilingual smart responses, conversation history saved per user.

- 🧮 **Calculator** — operation history and memory persist between sessions in `data/calc_history.json`; activity logging for every calculation.

- 🎨 **Media Center** — 12 image filters with intensity sliders, interactive crop with 4 sliders, smart resize with aspect-ratio lock, rotate/flip, download buttons for all processed images.

- ℹ️ **About** — completely rebuilt with project features showcase, tech stack listing, roadmap (v2.0/v2.1/v3.0), and credits sections.

- 📷 **Camera** — three detection modes (Hand+Body / Hand / Body), timestamped snapshots to `assets/images/`, coaching messages.

- 🖐️ **Hand Scan** — five-second authentication: right hand grants access, left hand denies, with frame-counting decision logic.

- 🎞️ **Media Converter** — five tabs covering image conversion, image processing, audio studio (FFmpeg), video studio (FFmpeg), and history.

#### Infrastructure

- 🛡️ **SHA-256 password hashing** with per-user salt and 5-attempt brute-force lockout (5-minute cooldown).

- 📊 **Activity Log** module — JSON audit trail with 500-entry cap, categories (auth/navigation/data/security/system), and statistics.

- 🌐 **Translation system** — unified `utils/language.py` with 288 keys in English and Arabic, full RTL layout support, page-specific `_t()` helpers.

- 📈 **Dashboard** — Plotly donut chart for file distribution and 7-day activity line chart, system health score, recent activity panel.

- 🔄 **Auto-rerun timers** — Pomodoro and stopwatch use sub-second polling for smooth countdown.

- 📥 **CSV export** for calculator history.
- 🎨 **Unified neon-cyber design system** across all 18 modules.

### Changed

- All pages now use `utils.language.t()` instead of local translation dicts.
- All JSON files write with `encoding="utf-8"` and `ensure_ascii=False` for proper Arabic support.

- `app.py` rewritten with error handling: failed page imports show a clear error and offer return-to-home.

- Removed dependency on `styles/base_theme.py` and `styles/neon_cyber_theme.py` (which were missing in deployments) — each page is now self-contained with inline CSS.

- File uploads moved to `assets/uploads/` consistently across modules.

### Fixed

- `st.text_input("")` empty-label warnings — all inputs now have proper labels or `label_visibility="collapsed"`.

- Home page "Coming Soon" placeholders replaced with working Security Center and Activity Log buttons.

- Translation keys with broken references (e.g., `Multimedia Center_dev`) now resolve correctly to `media_library`.

- Session state access works with both `[key]` and `.key` patterns.
- Pomodoro/stopwatch pause-resume now correctly compensates elapsed time.

### Security

- Passwords stored as SHA-256 hashes with per-user salt (never plain text).
- Legacy plain-text passwords automatically upgraded on next login.
- Account lockout after 5 failed login attempts.
- ZIP restore protects against path-traversal attacks.
- All authentication events logged to activity log.

---

## [1.0.0] — Initial Release

### Added in 1.0.0

- Basic Streamlit multipage prototype with login, home, and a few demo pages.
- Plain-text password storage (since replaced).
- Single-language English UI.
- Hardcoded high scores in session state (now persisted per user).
- Basic camera + hand scan demo without coaching feedback.

### Removed in 2.0.0

- Hardcoded test credentials (`omar` / `1234`).
- Local `T` dictionaries scattered across pages.
- Dependency on non-existent `styles/*` theme files.

---

## Versioning Policy

- **MAJOR** — breaking changes to JSON schema, session state, or page API.
- **MINOR** — new pages or features that are backward-compatible.
- **PATCH** — bug fixes, translation additions, performance improvements.

---

## Roadmap

### [2.1.0] — Planned

- Cloud sync option (optional Supabase / Firebase backend).
- Mobile-responsive CSS tweaks for all pages.
- Email notifications (with SMTP config).
- Two-factor authentication (TOTP).

### [3.0.0] — Future Vision

- Real AI integration (OpenAI / Anthropic API support for assistant).
- Voice commands.
- Plugin system for custom pages.
- Multi-tenant deployment mode.
