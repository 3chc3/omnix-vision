"""
═══════════════════════════════════════════════════════════════════════════
OMNIX VISION — Activity Log Module
═══════════════════════════════════════════════════════════════════════════
Tracks all user actions for the Activity Log page.

Each entry stores:
    • timestamp   — Unix time (float)
    • user_id     — User ID or "anonymous"
    • action      — Short action key (e.g., "login", "open_camera")
    • details     — Optional details
    • category    — auth | navigation | data | security | system

Storage: data/activity_log.json
─────────────────────────────────────────────────────────────────────────
Max entries: 500 (oldest auto-trimmed)
═══════════════════════════════════════════════════════════════════════════
"""

import json
import time
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
LOG_FILE = DATA_DIR / "activity_log.json"

MAX_ENTRIES = 500


# ═══════════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════════

def _ensure_log_file():
    """Make sure log file exists."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not LOG_FILE.exists():
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)


def _load_log() -> list:
    """Load full activity log."""
    _ensure_log_file()
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def _save_log(entries: list):
    """Save log to disk (trimmed to MAX_ENTRIES)."""
    _ensure_log_file()
    # Keep only the last MAX_ENTRIES (most recent)
    trimmed = entries[-MAX_ENTRIES:]
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(trimmed, f, ensure_ascii=False, indent=2)


# ═══════════════════════════════════════════════════════════════════════════
# Public API
# ═══════════════════════════════════════════════════════════════════════════

def log_action(action: str,
               user_id: str = "anonymous",
               details: str = "",
               category: str = "navigation"):
    """
    Append a new activity entry.

    Args:
        action:   Short identifier (e.g. "login_success", "open_camera")
        user_id:  User ID or "anonymous"
        details:  Optional human-readable note
        category: One of: auth | navigation | data | security | system
    """
    entries = _load_log()
    entries.append({
        "timestamp": time.time(),
        "user_id":   str(user_id) if user_id else "anonymous",
        "action":    action,
        "details":   details,
        "category":  category,
    })
    _save_log(entries)


def get_log(limit: int = None,
            user_id: str = None,
            category: str = None) -> list:
    """
    Retrieve log entries (most recent first).

    Args:
        limit:    Max number of entries to return
        user_id:  Filter by user_id (optional)
        category: Filter by category (optional)
    """
    entries = _load_log()

    if user_id:
        entries = [e for e in entries if e.get("user_id") == user_id]

    if category:
        entries = [e for e in entries if e.get("category") == category]

    # Most recent first
    entries = list(reversed(entries))

    if limit:
        entries = entries[:limit]

    return entries


def clear_log():
    """Wipe the entire activity log."""
    _save_log([])


def get_stats() -> dict:
    """
    Quick statistics about the log.
    Returns: {total, by_category, unique_users, last_action_time}
    """
    entries = _load_log()

    by_cat = {}
    users  = set()
    for e in entries:
        cat = e.get("category", "other")
        by_cat[cat] = by_cat.get(cat, 0) + 1
        users.add(e.get("user_id", "anonymous"))

    last_time = entries[-1]["timestamp"] if entries else None

    return {
        "total":            len(entries),
        "by_category":      by_cat,
        "unique_users":     len(users),
        "last_action_time": last_time,
    }