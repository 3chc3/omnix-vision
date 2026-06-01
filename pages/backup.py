"""
═══════════════════════════════════════════════════════════════════════════
OMNIX VISION — Backup & Restore (Phase 4 — Round 2)
═══════════════════════════════════════════════════════════════════════════
Features:
    ✓ Export all data/ to ZIP file
    ✓ Import ZIP and restore data
    ✓ Selective file backup (choose which JSON files)
    ✓ List existing backups
    ✓ Auto-timestamp backup names
    ✓ Show file sizes and last modified
    ✓ Full EN/AR translation with RTL
═══════════════════════════════════════════════════════════════════════════
"""

import os
import io
import json
import shutil
import zipfile
import time
from datetime import datetime
from pathlib import Path

import streamlit as st

from utils.language import t, init_language, apply_rtl_css, is_rtl
from utils.activity import log_action


# ═══════════════════════════════════════════════════════════════════════════
# Paths
# ═══════════════════════════════════════════════════════════════════════════
BASE_DIR    = Path(__file__).resolve().parent.parent
DATA_DIR    = BASE_DIR / "data"
BACKUP_DIR  = BASE_DIR / "data" / "backups"
DATA_DIR.mkdir(parents=True, exist_ok=True)
BACKUP_DIR.mkdir(parents=True, exist_ok=True)


# ═══════════════════════════════════════════════════════════════════════════
# Page Translations
# ═══════════════════════════════════════════════════════════════════════════
BKP_KEYS = {
    "bkp_title":     {"en": "Backup & Restore",   "ar": "النسخ الاحتياطي والاستعادة"},
    "bkp_subtitle":  {"en": "Export, import, and manage your data",
                      "ar": "تصدير واستيراد وإدارة بياناتك"},
    "export_tab":    {"en": "📤 Export",  "ar": "📤 تصدير"},
    "import_tab":    {"en": "📥 Import",  "ar": "📥 استيراد"},
    "manage_tab":    {"en": "📂 Manage",  "ar": "📂 إدارة"},
    "select_files":  {"en": "Select files to include in backup",
                      "ar": "اختر الملفات لتضمينها في النسخة الاحتياطية"},
    "create_backup": {"en": "💾 Create Backup",     "ar": "💾 إنشاء نسخة احتياطية"},
    "download_zip":  {"en": "⬇️ Download Backup",   "ar": "⬇️ تحميل النسخة"},
    "no_files":      {"en": "⚠️ No data files found.", "ar": "⚠️ لا توجد ملفات بيانات."},
    "no_selection":  {"en": "⚠️ Please select at least one file.",
                      "ar": "⚠️ من فضلك اختر ملفاً واحداً على الأقل."},
    "upload_zip":    {"en": "Upload ZIP file to restore",
                      "ar": "ارفع ملف ZIP للاستعادة"},
    "restore_btn":   {"en": "🔄 Restore Now",  "ar": "🔄 استعادة الآن"},
    "confirm_restore": {"en": "⚠️ This will OVERWRITE existing files. Continue?",
                        "ar": "⚠️ سيتم الكتابة فوق الملفات الموجودة. هل تريد المتابعة؟"},
    "yes_restore":   {"en": "✅ Yes, Restore",  "ar": "✅ نعم، استعد"},
    "cancel":        {"en": "❌ Cancel",         "ar": "❌ إلغاء"},
    "restore_success":{"en": "✅ Data restored successfully!",
                       "ar": "✅ تم استعادة البيانات بنجاح!"},
    "restore_failed":{"en": "❌ Restore failed:",  "ar": "❌ فشلت الاستعادة:"},
    "backup_success":{"en": "✅ Backup created!",   "ar": "✅ تم إنشاء النسخة!"},
    "existing_backups":{"en": "Existing Backups",  "ar": "النسخ الموجودة"},
    "no_backups":    {"en": "No backups yet. Create one in the Export tab.",
                      "ar": "لا توجد نسخ احتياطية. أنشئ واحدة في تبويب التصدير."},
    "delete_backup": {"en": "🗑️ Delete",  "ar": "🗑️ حذف"},
    "file_size":     {"en": "Size",       "ar": "الحجم"},
    "modified":      {"en": "Modified",   "ar": "آخر تعديل"},
    "files_inside":  {"en": "Files inside",  "ar": "الملفات داخلها"},
    "stat_total":    {"en": "Total Backups",  "ar": "إجمالي النسخ"},
    "stat_size":     {"en": "Total Size",     "ar": "الحجم الإجمالي"},
    "stat_data":     {"en": "Data Files",     "ar": "ملفات البيانات"},
}


def _t(key: str) -> str:
    from utils.language import get_language_code
    lang = get_language_code()
    if key in BKP_KEYS:
        return BKP_KEYS[key].get(lang, BKP_KEYS[key].get("en", key))
    return t(key)


# ═══════════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════════

def _list_data_files() -> list:
    """Return list of JSON files in data/ (excluding backups subdir)."""
    if not DATA_DIR.exists():
        return []
    return sorted([f for f in DATA_DIR.iterdir()
                   if f.is_file() and f.suffix == ".json"])


def _list_backups() -> list:
    """Return list of backup ZIP files."""
    if not BACKUP_DIR.exists():
        return []
    return sorted(
        [f for f in BACKUP_DIR.iterdir() if f.is_file() and f.suffix == ".zip"],
        key=lambda f: f.stat().st_mtime,
        reverse=True,
    )


def _format_size(bytes_: int) -> str:
    """Convert bytes to human-readable format."""
    for unit in ["B", "KB", "MB", "GB"]:
        if bytes_ < 1024:
            return f"{bytes_:.1f} {unit}"
        bytes_ /= 1024
    return f"{bytes_:.1f} TB"


def _create_backup_zip(selected_files: list) -> tuple:
    """
    Create a ZIP from selected file paths.
    Returns (zip_bytes, filename, zip_path).
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename  = f"omnix_backup_{timestamp}.zip"
    zip_path  = BACKUP_DIR / filename

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        # Add metadata file
        metadata = {
            "created_at":     datetime.now().isoformat(),
            "files":          [f.name for f in selected_files],
            "omnix_version":  "2.0",
        }
        zf.writestr("_metadata.json",
                    json.dumps(metadata, ensure_ascii=False, indent=2))

        for file_path in selected_files:
            zf.write(file_path, arcname=file_path.name)

    zip_bytes = buf.getvalue()

    # Save to backups dir for later access
    with open(zip_path, "wb") as f:
        f.write(zip_bytes)

    return zip_bytes, filename, zip_path


def _restore_from_zip(zip_bytes: bytes) -> tuple:
    """
    Restore data files from a ZIP. Returns (success, message, files_restored).
    """
    try:
        with zipfile.ZipFile(io.BytesIO(zip_bytes), "r") as zf:
            names = zf.namelist()
            json_files = [n for n in names
                          if n.endswith(".json") and n != "_metadata.json"]

            if not json_files:
                return False, "No JSON files in archive", 0

            for name in json_files:
                # Security: prevent path traversal
                if "/" in name or "\\" in name or name.startswith(".."):
                    continue
                content = zf.read(name)
                out_path = DATA_DIR / name
                with open(out_path, "wb") as f:
                    f.write(content)

            return True, f"Restored {len(json_files)} files", len(json_files)
    except zipfile.BadZipFile:
        return False, "Invalid ZIP file", 0
    except Exception as e:
        return False, str(e), 0


# ═══════════════════════════════════════════════════════════════════════════
# CSS
# ═══════════════════════════════════════════════════════════════════════════

def _apply_css():
    is_ar = is_rtl()
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@400;600;700&display=swap');

    [data-testid="stSidebar"], [data-testid="collapsedControl"] {{ display: none; }}

    [data-testid="stAppDeployButton"],
    [data-testid="stToolbar"],
    header[data-testid="stHeader"] {{
        background: transparent !important;
        box-shadow: none !important;
    }}

    .block-container {{
        max-width: 1180px;
        padding-top: 1.2rem;
        {"direction: rtl;" if is_ar else ""}
    }}

    .stApp {{
        background:
            radial-gradient(circle at 10% 10%, rgba(34,197,94,0.12), transparent 30%),
            radial-gradient(circle at 90% 10%, rgba(56,189,248,0.15), transparent 32%),
            linear-gradient(135deg, #020617 0%, #06111f 48%, #111032 100%);
        color: #f8fafc;
        font-family: 'Rajdhani', sans-serif;
    }}

    .hero {{
        background: linear-gradient(135deg, rgba(15,23,42,0.96), rgba(8,47,73,0.58));
        border: 1px solid rgba(34,197,94,0.38);
        border-radius: 30px;
        padding: 34px 28px;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 0 48px rgba(34,197,94,0.14);
    }}
    .hero h1 {{
        color: #4ade80;
        font-size: 36px;
        font-weight: 950;
        margin: 0;
        letter-spacing: 2px;
        text-shadow: 0 0 24px rgba(74,222,128,0.4);
    }}
    .hero p {{ color: #cbd5e1; margin-top: 10px; font-size: 14px; }}

    .metric-card {{
        background: linear-gradient(145deg, rgba(15,23,42,0.95), rgba(30,41,59,0.62));
        border: 1px solid rgba(34,197,94,0.27);
        border-radius: 16px;
        padding: 14px;
        text-align: center;
    }}
    .metric-label {{
        color: #86efac;
        font-size: 10px;
        font-family: 'Orbitron', monospace;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin-bottom: 6px;
    }}
    .metric-value {{
        color: #f8fafc;
        font-size: 26px;
        font-weight: 900;
        font-family: 'Orbitron', monospace;
    }}

    .file-card {{
        background: rgba(15,23,42,0.65);
        border: 1px solid rgba(56,189,248,0.20);
        border-radius: 12px;
        padding: 12px 16px;
        margin: 8px 0;
    }}
    .file-name {{
        color: #f1f5f9;
        font-weight: 800;
        font-size: 14px;
        font-family: 'Orbitron', monospace;
    }}
    .file-meta {{
        color: #94a3b8;
        font-size: 12px;
        margin-top: 4px;
    }}

    .stButton > button {{
        background: linear-gradient(135deg, #22c55e 0%, #15803d 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 10px 16px !important;
        font-weight: 800 !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-size: 14px !important;
        min-height: 42px !important;
        transition: 0.25s ease !important;
        box-shadow: 0 4px 16px rgba(34,197,94,0.18) !important;
    }}
    .stButton > button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 26px rgba(34,197,94,0.32) !important;
    }}
    .stDownloadButton > button {{
        background: linear-gradient(135deg, #0ea5e9 0%, #7c3aed 100%) !important;
        box-shadow: 0 4px 16px rgba(14,165,233,0.20) !important;
    }}
    </style>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# Main Render
# ═══════════════════════════════════════════════════════════════════════════

def render_backup():
    init_language()
    apply_rtl_css()

    if not st.session_state.get("logged_in", False):
        st.session_state.page = "login"
        st.rerun()

    user_id = st.session_state.get("user", "anonymous")

    _apply_css()

    # ── Hero ──────────────────────────────────────────────────────────────
    st.markdown(f"""
<div class="hero">
<h1>💾 {_t('bkp_title')}</h1>
<p>{_t('bkp_subtitle')}</p>
</div>
    """, unsafe_allow_html=True)

    # ── Back ──────────────────────────────────────────────────────────────
    back_col, _ = st.columns([1.3, 8])
    with back_col:
        if st.button(t("back"), use_container_width=True, key="bkp_back_btn"):
            st.session_state.page = "home"
            st.rerun()

    # ── Metrics ───────────────────────────────────────────────────────────
    data_files = _list_data_files()
    backups    = _list_backups()
    total_data_size = sum(f.stat().st_size for f in data_files)
    total_bkp_size  = sum(f.stat().st_size for f in backups)

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"""
<div class="metric-card">
<div class="metric-label">📁 {_t('stat_data')}</div>
<div class="metric-value" style="color:#38bdf8;">{len(data_files)}</div>
</div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
<div class="metric-card">
<div class="metric-label">💾 {_t('stat_total')}</div>
<div class="metric-value" style="color:#22c55e;">{len(backups)}</div>
</div>
        """, unsafe_allow_html=True)
    with m3:
        st.markdown(f"""
<div class="metric-card">
<div class="metric-label">📊 {_t('stat_size')}</div>
<div class="metric-value" style="color:#a855f7;font-size:18px;">{_format_size(total_bkp_size)}</div>
</div>
        """, unsafe_allow_html=True)
    with m4:
        st.markdown(f"""
<div class="metric-card">
<div class="metric-label">📦 Data Total</div>
<div class="metric-value" style="color:#f59e0b;font-size:18px;">{_format_size(total_data_size)}</div>
</div>
        """, unsafe_allow_html=True)

    st.write("")

    # ── Tabs ──────────────────────────────────────────────────────────────
    tab_export, tab_import, tab_manage = st.tabs([
        _t("export_tab"), _t("import_tab"), _t("manage_tab"),
    ])

    # ─────────── TAB 1: Export ───────────
    with tab_export:
        st.markdown(f"### 📤 {_t('select_files')}")

        if not data_files:
            st.warning(_t("no_files"))
        else:
            # Select all toggle
            select_all = st.checkbox("Select All / إختر الكل", value=True,
                                     key="bkp_select_all")

            selected_paths = []
            for f in data_files:
                size_str = _format_size(f.stat().st_size)
                if st.checkbox(
                    f"📄 {f.name} ({size_str})",
                    value=select_all,
                    key=f"bkp_chk_{f.name}",
                ):
                    selected_paths.append(f)

            st.write("")
            if st.button(_t("create_backup"),
                         use_container_width=True,
                         key="bkp_create_btn"):
                if not selected_paths:
                    st.warning(_t("no_selection"))
                else:
                    try:
                        zip_bytes, fname, _ = _create_backup_zip(selected_paths)
                        st.success(f"{_t('backup_success')} ({_format_size(len(zip_bytes))})")
                        log_action("backup_created",
                                   user_id=user_id,
                                   category="data",
                                   details=f"files={len(selected_paths)} size={len(zip_bytes)}")

                        st.download_button(
                            _t("download_zip"),
                            data=zip_bytes,
                            file_name=fname,
                            mime="application/zip",
                            use_container_width=True,
                            key="bkp_dl_btn",
                        )
                    except Exception as e:
                        st.error(f"❌ {e}")

    # ─────────── TAB 2: Import ───────────
    with tab_import:
        st.markdown(f"### 📥 {_t('upload_zip')}")

        uploaded = st.file_uploader(
            _t("upload_zip"),
            type=["zip"],
            key="bkp_upload_zip",
            label_visibility="collapsed",
        )

        if uploaded:
            # Preview ZIP contents
            try:
                with zipfile.ZipFile(uploaded, "r") as zf:
                    names = zf.namelist()
                    json_names = [n for n in names
                                  if n.endswith(".json") and n != "_metadata.json"]

                    # Try read metadata
                    metadata = None
                    if "_metadata.json" in names:
                        try:
                            metadata = json.loads(zf.read("_metadata.json"))
                        except Exception:
                            pass

                st.markdown(f"### 📋 ZIP Contents:")
                if metadata:
                    st.info(f"📅 Created: {metadata.get('created_at', 'unknown')[:19]}")

                for name in json_names:
                    st.markdown(f"<div class='file-card'><div class='file-name'>📄 {name}</div></div>",
                                unsafe_allow_html=True)

                st.warning(_t("confirm_restore"))

                rc1, rc2 = st.columns(2)
                with rc1:
                    if st.button(_t("yes_restore"),
                                 use_container_width=True,
                                 key="bkp_confirm_restore"):
                        uploaded.seek(0)
                        success, msg, count = _restore_from_zip(uploaded.read())
                        if success:
                            st.success(f"{_t('restore_success')} ({msg})")
                            log_action("backup_restored",
                                       user_id=user_id,
                                       category="data",
                                       details=f"files={count}")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(f"{_t('restore_failed')} {msg}")
                with rc2:
                    if st.button(_t("cancel"),
                                 use_container_width=True,
                                 key="bkp_cancel_restore"):
                        st.rerun()
            except Exception as e:
                st.error(f"❌ {e}")

    # ─────────── TAB 3: Manage ───────────
    with tab_manage:
        st.markdown(f"### 📂 {_t('existing_backups')}")

        if not backups:
            st.info(_t("no_backups"))
        else:
            for bkp in backups:
                stat = bkp.stat()
                size_str = _format_size(stat.st_size)
                mtime_str = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")

                # Read inner file count
                inner_count = 0
                try:
                    with zipfile.ZipFile(bkp, "r") as zf:
                        inner_count = sum(1 for n in zf.namelist()
                                          if n.endswith(".json")
                                          and n != "_metadata.json")
                except Exception:
                    pass

                st.markdown(f"""
<div class="file-card">
<div class="file-name">💾 {bkp.name}</div>
<div class="file-meta">
{_t('file_size')}: <b style="color:#38bdf8;">{size_str}</b> · 
{_t('modified')}: <b style="color:#a855f7;">{mtime_str}</b> · 
{_t('files_inside')}: <b style="color:#22c55e;">{inner_count}</b>
</div>
</div>
                """, unsafe_allow_html=True)

                bc1, bc2 = st.columns(2)
                with bc1:
                    with open(bkp, "rb") as f:
                        st.download_button(
                            f"⬇️ {_t('download_zip')}",
                            data=f.read(),
                            file_name=bkp.name,
                            mime="application/zip",
                            use_container_width=True,
                            key=f"bkp_dl_{bkp.name}",
                        )
                with bc2:
                    if st.button(_t("delete_backup"),
                                 use_container_width=True,
                                 key=f"bkp_del_{bkp.name}"):
                        try:
                            bkp.unlink()
                            log_action("backup_deleted",
                                       user_id=user_id,
                                       category="data",
                                       details=bkp.name)
                            st.rerun()
                        except OSError as e:
                            st.error(f"❌ {e}")

                st.write("")