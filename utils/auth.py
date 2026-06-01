"""
═══════════════════════════════════════════════════════════════════════════
OMNIX VISION — Authentication Module (Secure)
═══════════════════════════════════════════════════════════════════════════
Provides:
    • Secure password hashing using SHA-256 + per-user salt
    • User registration with auto-generated 4-digit IDs
    • Brute-force protection (5 attempts → 5 minute lockout)
    • Login / logout tracking
    • Password change

Storage: data/users.json
─────────────────────────────────────────────────────────────────────────
Backwards-compatible with old plain-text passwords:
    On first successful login of a legacy account, the password is
    automatically re-hashed and saved.
═══════════════════════════════════════════════════════════════════════════
"""

import json
import random
import hashlib
import secrets
import time
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────
BASE_DIR   = Path(__file__).resolve().parent.parent
DATA_DIR   = BASE_DIR / "data"
USERS_FILE = DATA_DIR / "users.json"

# ── Security Settings ──────────────────────────────────────────────────────
MAX_FAILED_ATTEMPTS = 5            # Lock account after N failed attempts
LOCKOUT_DURATION    = 5 * 60       # Lockout duration in seconds (5 minutes)
SALT_BYTES          = 16           # Salt length

# ═══════════════════════════════════════════════════════════════════════════
# File Helpers
# ═══════════════════════════════════════════════════════════════════════════

def ensure_users_file():
    """Make sure data folder and users file exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not USERS_FILE.exists():
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f, ensure_ascii=False, indent=4)


def load_users() -> dict:
    """Load all users from JSON. Returns empty dict on error."""
    ensure_users_file()
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_users(users: dict):
    """Save users dict to JSON with UTF-8 encoding."""
    ensure_users_file()
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=4)


# ═══════════════════════════════════════════════════════════════════════════
# Password Hashing
# ═══════════════════════════════════════════════════════════════════════════

def _hash_password(password: str, salt: str = None) -> str:
    """
    Hash a password with SHA-256 + salt.
    Returns format:  "salt:hash"
    If salt is None, a new random salt is generated.
    """
    if salt is None:
        salt = secrets.token_hex(SALT_BYTES)
    digest = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()
    return f"{salt}:{digest}"


def _verify_password(password: str, stored: str) -> bool:
    """
    Verify a plain password against a stored hash.
    Supports BOTH new format (salt:hash) and legacy plain-text.
    """
    if not isinstance(stored, str):
        return False

    # New format: salt:hash
    if ":" in stored and len(stored.split(":")[0]) == SALT_BYTES * 2:
        salt, _ = stored.split(":", 1)
        return _hash_password(password, salt) == stored

    # Legacy plain-text fallback
    return password == stored


# ═══════════════════════════════════════════════════════════════════════════
# ID Generation
# ═══════════════════════════════════════════════════════════════════════════

def generate_id(users: dict) -> str:
    """Generate a unique 4-digit user ID not present in users."""
    while True:
        new_id = str(random.randint(1000, 9999))
        if new_id not in users:
            return new_id


# ═══════════════════════════════════════════════════════════════════════════
# Public API
# ═══════════════════════════════════════════════════════════════════════════

def register_user(password: str, username: str = "") -> tuple:
    """
    Register a new user with a hashed password.
    Returns: (success: bool, message: str, user_id: str | None)
    """
    if not password or len(password) < 4:
        return False, "Password must be at least 4 characters.", None

    users = load_users()
    user_id = generate_id(users)

    users[user_id] = {
        "username":        username or f"user_{user_id}",
        "password":        _hash_password(password),
        "created_at":      time.time(),
        "last_login":      None,
        "failed_attempts": 0,
        "lockout_until":   0,
    }

    save_users(users)
    return True, f"Your ID is: {user_id}", user_id


def login_user(user_id: str, password: str) -> tuple:
    """
    Authenticate a user. Implements brute-force protection.
    Returns: (success: bool, message: str)
    """
    users = load_users()

    # Check ID exists
    if user_id not in users:
        return False, "ID not found"

    user = users[user_id]
    now  = time.time()

    # Ensure required fields exist (for old accounts)
    user.setdefault("failed_attempts", 0)
    user.setdefault("lockout_until", 0)

    # Check lockout
    if user["lockout_until"] > now:
        remaining = int(user["lockout_until"] - now)
        mins, secs = divmod(remaining, 60)
        return False, f"Account locked. Try again in {mins}m {secs}s."

    # Verify password
    if not _verify_password(password, user.get("password", "")):
        user["failed_attempts"] += 1

        # Trigger lockout?
        if user["failed_attempts"] >= MAX_FAILED_ATTEMPTS:
            user["lockout_until"]   = now + LOCKOUT_DURATION
            user["failed_attempts"] = 0
            save_users(users)
            return False, (
                f"Too many failed attempts. "
                f"Locked for {LOCKOUT_DURATION // 60} minutes."
            )

        save_users(users)
        remaining_attempts = MAX_FAILED_ATTEMPTS - user["failed_attempts"]
        return False, f"Wrong password. {remaining_attempts} attempts left."

    # ── Success ───────────────────────────────────────────────────────────
    user["failed_attempts"] = 0
    user["lockout_until"]   = 0
    user["last_login"]      = now

    # Auto-upgrade legacy plain-text password to hashed
    stored = user.get("password", "")
    if ":" not in stored or len(stored.split(":")[0]) != SALT_BYTES * 2:
        user["password"] = _hash_password(password)

    save_users(users)
    return True, "Login successful"


def change_password(user_id: str, old_password: str, new_password: str) -> tuple:
    """
    Change a user's password.
    Returns: (success: bool, message: str)
    """
    if not new_password or len(new_password) < 4:
        return False, "New password must be at least 4 characters."

    users = load_users()
    if user_id not in users:
        return False, "User not found."

    if not _verify_password(old_password, users[user_id].get("password", "")):
        return False, "Old password is incorrect."

    users[user_id]["password"]        = _hash_password(new_password)
    users[user_id]["password_changed_at"] = time.time()
    save_users(users)

    return True, "Password updated successfully."


def get_user_info(user_id: str) -> dict | None:
    """Return user info (without sensitive password hash)."""
    users = load_users()
    if user_id not in users:
        return None
    info = users[user_id].copy()
    info.pop("password", None)
    return info


def delete_user(user_id: str, password: str) -> tuple:
    """
    Permanently delete a user account (requires password confirmation).
    Returns: (success: bool, message: str)
    """
    users = load_users()
    if user_id not in users:
        return False, "User not found."

    if not _verify_password(password, users[user_id].get("password", "")):
        return False, "Password incorrect. Account NOT deleted."

    del users[user_id]
    save_users(users)
    return True, "Account deleted successfully."


def reset_lockout(user_id: str) -> bool:
    """Manually clear lockout for a user (admin / settings)."""
    users = load_users()
    if user_id not in users:
        return False
    users[user_id]["failed_attempts"] = 0
    users[user_id]["lockout_until"]   = 0
    save_users(users)
    return True