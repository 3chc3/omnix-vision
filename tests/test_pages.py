"""
═══════════════════════════════════════════════════════════════════════════
Tests for page helper logic (notifications, backup, random_tools, pomodoro)
═══════════════════════════════════════════════════════════════════════════
These test the pure-logic helpers, not the Streamlit rendering.
═══════════════════════════════════════════════════════════════════════════
"""

import importlib
import io
import json
import zipfile
from pathlib import Path

import pytest

# ═══════════════════════════════════════════════════════════════════════════
# Notifications
# ═══════════════════════════════════════════════════════════════════════════

@pytest.fixture
def notif(mock_streamlit, temp_data_dir, monkeypatch):
    import pages.notifications as mod
    importlib.reload(mod)
    monkeypatch.setattr(mod, "DATA_DIR", temp_data_dir, raising=False)
    monkeypatch.setattr(mod, "NOTIF_FILE", temp_data_dir / "notif.json", raising=False)
    return mod


def test_add_notification(notif):
    notif.add_notification("u1", "Title", "Body", "info")
    items = notif._get_user_notifs("u1")
    assert len(items) == 1
    assert items[0]["title"] == "Title"
    assert items[0]["status"] == "unread"


def test_notification_user_isolation(notif):
    notif.add_notification("u1", "A", "msg", "info")
    notif.add_notification("u2", "B", "msg", "error")
    assert len(notif._get_user_notifs("u1")) == 1
    assert len(notif._get_user_notifs("u2")) == 1


def test_notification_priorities(notif):
    for prio in ("info", "success", "warning", "error"):
        notif.add_notification("u1", f"T-{prio}", "m", prio)
    items = notif._get_user_notifs("u1")
    assert {i["priority"] for i in items} == {"info", "success", "warning", "error"}


def test_time_ago_just_now(notif):
    import time
    label = notif._time_ago(time.time())
    assert isinstance(label, str) and len(label) > 0


# ═══════════════════════════════════════════════════════════════════════════
# Backup
# ═══════════════════════════════════════════════════════════════════════════

@pytest.fixture
def backup(mock_streamlit, temp_data_dir, monkeypatch):
    import pages.backup as mod
    importlib.reload(mod)
    monkeypatch.setattr(mod, "DATA_DIR", temp_data_dir, raising=False)
    bdir = temp_data_dir / "backups"
    bdir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(mod, "BACKUP_DIR", bdir, raising=False)
    return mod


def test_format_size(backup):
    assert backup._format_size(0) == "0.0 B"
    assert backup._format_size(1024) == "1.0 KB"
    assert backup._format_size(1024 * 1024) == "1.0 MB"


def test_list_data_files(backup, temp_data_dir):
    (temp_data_dir / "a.json").write_text("{}", encoding="utf-8")
    (temp_data_dir / "b.json").write_text("{}", encoding="utf-8")
    files = backup._list_data_files()
    assert len(files) >= 2


def test_create_backup_zip(backup, temp_data_dir):
    tf = temp_data_dir / "data.json"
    tf.write_text('{"key": "value"}', encoding="utf-8")
    zip_bytes, fname, zpath = backup._create_backup_zip([tf])
    assert zip_bytes[:2] == b"PK"          # ZIP magic number
    assert fname.startswith("omnix_backup_")
    assert zpath.exists()


def test_restore_roundtrip(backup, temp_data_dir):
    tf = temp_data_dir / "data.json"
    tf.write_text('{"original": true}', encoding="utf-8")
    zip_bytes, _, _ = backup._create_backup_zip([tf])

    # Corrupt the file, then restore
    tf.write_text('{"corrupted": true}', encoding="utf-8")
    ok, msg, count = backup._restore_from_zip(zip_bytes)
    assert ok is True
    assert count == 1
    assert json.loads(tf.read_text()) == {"original": True}


def test_restore_rejects_bad_zip(backup):
    ok, msg, count = backup._restore_from_zip(b"not a zip file")
    assert ok is False


def test_restore_blocks_path_traversal(backup, temp_data_dir):
    """A ZIP containing ../evil.json must not escape DATA_DIR."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("../evil.json", '{"hacked": true}')
        zf.writestr("safe.json", '{"ok": true}')
    ok, msg, count = backup._restore_from_zip(buf.getvalue())
    # Only the safe file should be restored; evil one skipped
    assert not (temp_data_dir.parent / "evil.json").exists()


# ═══════════════════════════════════════════════════════════════════════════
# Random Tools
# ═══════════════════════════════════════════════════════════════════════════

@pytest.fixture
def rtools(mock_streamlit):
    import pages.random_tools as mod
    importlib.reload(mod)
    return mod


def test_password_length(rtools):
    pwd = rtools._generate_password(20, True, True, True, True, False)
    assert len(pwd) == 20


def test_password_respects_charset(rtools):
    # digits only
    pwd = rtools._generate_password(30, False, False, True, False, False)
    assert pwd.isdigit()


def test_password_empty_charset(rtools):
    pwd = rtools._generate_password(10, False, False, False, False, False)
    assert pwd == ""


def test_password_strength_strong(rtools):
    _, score, _ = rtools._calc_strength("Abcd1234!@#$XYZ")
    assert score >= 70


def test_password_strength_weak(rtools):
    _, score, _ = rtools._calc_strength("abc")
    assert score < 40


def test_hex_to_rgb(rtools):
    assert rtools._hex_to_rgb("#ff0000") == (255, 0, 0)
    assert rtools._hex_to_rgb("#00ff00") == (0, 255, 0)
    assert rtools._hex_to_rgb("#0000ff") == (0, 0, 255)


def test_rgb_to_hex(rtools):
    assert rtools._rgb_to_hex((255, 0, 0)) == "#ff0000"
    assert rtools._rgb_to_hex((0, 0, 0)) == "#000000"


def test_rgb_hex_roundtrip(rtools):
    for rgb in [(123, 45, 67), (255, 255, 255), (0, 128, 255)]:
        assert rtools._hex_to_rgb(rtools._rgb_to_hex(rgb)) == rgb


def test_rgb_to_hsl_red(rtools):
    h, s, l = rtools._rgb_to_hsl((255, 0, 0))
    assert h == 0           # red hue
    assert s == 100         # fully saturated


# ═══════════════════════════════════════════════════════════════════════════
# Pomodoro
# ═══════════════════════════════════════════════════════════════════════════

@pytest.fixture
def pomo(mock_streamlit, temp_data_dir, monkeypatch):
    import pages.pomodoro as mod
    importlib.reload(mod)
    monkeypatch.setattr(mod, "DATA_DIR", temp_data_dir, raising=False)
    monkeypatch.setattr(mod, "POMO_LOG", temp_data_dir / "pomo.json", raising=False)
    return mod


def test_pomo_empty_history(pomo):
    assert pomo._load_history("u1") == []


def test_pomo_add_session(pomo):
    pomo._add_session("u1", "work", 25, "Studying")
    hist = pomo._load_history("u1")
    assert len(hist) == 1
    assert hist[0]["phase"] == "work"
    assert hist[0]["duration_min"] == 25


def test_pomo_user_isolation(pomo):
    pomo._add_session("u1", "work", 25, "A")
    pomo._add_session("u2", "short", 5, "B")
    assert len(pomo._load_history("u1")) == 1
    assert len(pomo._load_history("u2")) == 1


def test_pomo_phase_durations(pomo):
    pomo.st.session_state.update({
        "pomo_phase": "work",
        "pomo_work_min": 25,
        "pomo_short_min": 5,
        "pomo_long_min": 15,
    })
    assert pomo._phase_duration() == 25 * 60
    pomo.st.session_state["pomo_phase"] = "short"
    assert pomo._phase_duration() == 5 * 60
    pomo.st.session_state["pomo_phase"] = "long"
    assert pomo._phase_duration() == 15 * 60


def test_pomo_phase_colors(pomo):
    pomo.st.session_state["pomo_phase"] = "work"
    assert pomo._phase_color().startswith("#")
