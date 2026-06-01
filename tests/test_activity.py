"""
═══════════════════════════════════════════════════════════════════════════
Tests for utils/activity.py — audit log, stats, capping
═══════════════════════════════════════════════════════════════════════════
"""

import importlib

import pytest


@pytest.fixture
def activity(mock_streamlit, temp_data_dir, monkeypatch):
    import utils.activity as act_mod
    importlib.reload(act_mod)

    log_file = temp_data_dir / "activity_log.json"
    # Patch with Path objects (code calls .exists() / .mkdir())
    monkeypatch.setattr(act_mod, "LOG_FILE", log_file, raising=False)
    monkeypatch.setattr(act_mod, "DATA_DIR", temp_data_dir, raising=False)

    # Start clean
    act_mod.clear_log()
    return act_mod


# ───────────────────────────────────────────────────────────────────────────
# Logging
# ───────────────────────────────────────────────────────────────────────────

def test_log_action_creates_entry(activity):
    activity.log_action("test_action", user_id="u1", category="system")
    entries = activity.get_log()
    assert len(entries) == 1
    assert entries[0]["action"] == "test_action"


def test_log_multiple_actions(activity):
    for i in range(5):
        activity.log_action(f"action_{i}", user_id="u1", category="data")
    assert len(activity.get_log()) == 5


def test_log_entry_has_timestamp(activity):
    activity.log_action("timed", user_id="u1", category="system")
    entry = activity.get_log()[0]
    assert "timestamp" in entry
    assert isinstance(entry["timestamp"], (int, float))


def test_log_entry_records_user(activity):
    activity.log_action("act", user_id="specific_user", category="auth")
    entry = activity.get_log()[0]
    assert entry.get("user_id") == "specific_user" or entry.get("user") == "specific_user"


def test_log_entry_records_category(activity):
    activity.log_action("act", user_id="u1", category="security")
    entry = activity.get_log()[0]
    assert entry.get("category") == "security"


# ───────────────────────────────────────────────────────────────────────────
# Retrieval & limits
# ───────────────────────────────────────────────────────────────────────────

def test_get_log_with_limit(activity):
    for i in range(10):
        activity.log_action(f"a{i}", user_id="u1", category="data")
    limited = activity.get_log(limit=3)
    assert len(limited) == 3


def test_clear_log_empties(activity):
    activity.log_action("x", user_id="u1", category="data")
    assert len(activity.get_log()) == 1
    activity.clear_log()
    assert len(activity.get_log()) == 0


def test_log_caps_at_500(activity):
    """Activity log should not grow unbounded (cap = 500)."""
    for i in range(550):
        activity.log_action(f"a{i}", user_id="u1", category="data")
    entries = activity.get_log()
    assert len(entries) <= 500


# ───────────────────────────────────────────────────────────────────────────
# Statistics
# ───────────────────────────────────────────────────────────────────────────

def test_get_stats_total(activity):
    for i in range(7):
        activity.log_action(f"a{i}", user_id="u1", category="data")
    stats = activity.get_stats()
    assert stats["total"] == 7


def test_get_stats_has_expected_keys(activity):
    activity.log_action("a", user_id="u1", category="data")
    stats = activity.get_stats()
    assert "total" in stats


def test_stats_empty_log(activity):
    stats = activity.get_stats()
    assert stats["total"] == 0
