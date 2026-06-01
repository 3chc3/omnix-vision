"""
═══════════════════════════════════════════════════════════════════════════
Tests for utils/auth.py — SHA-256 hashing, registration, login, lockout
═══════════════════════════════════════════════════════════════════════════
"""

import importlib

import pytest


@pytest.fixture
def auth(mock_streamlit, temp_data_dir, monkeypatch):
    """Import auth with an isolated users.json path."""
    import utils.auth as auth_mod
    importlib.reload(auth_mod)

    # Redirect the users file to the temp dir (must be a Path, code calls .exists())
    users_file = temp_data_dir / "users.json"
    monkeypatch.setattr(auth_mod, "USERS_FILE", users_file, raising=False)
    monkeypatch.setattr(auth_mod, "DATA_DIR", temp_data_dir, raising=False)

    return auth_mod


# ───────────────────────────────────────────────────────────────────────────
# Password hashing
# ───────────────────────────────────────────────────────────────────────────

def test_hash_is_not_plaintext(auth):
    hashed = auth._hash_password("mypassword123")
    assert "mypassword123" not in hashed
    assert len(hashed) > 20


def test_hash_includes_salt(auth):
    """Two hashes of the same password should differ (random salt)."""
    h1 = auth._hash_password("samepass")
    h2 = auth._hash_password("samepass")
    assert h1 != h2


def test_verify_correct_password(auth):
    stored = auth._hash_password("correct horse")
    assert auth._verify_password("correct horse", stored) is True


def test_verify_wrong_password(auth):
    stored = auth._hash_password("correct horse")
    assert auth._verify_password("wrong horse", stored) is False


# ───────────────────────────────────────────────────────────────────────────
# Registration
# ───────────────────────────────────────────────────────────────────────────

def test_register_returns_user_id(auth):
    ok, _msg, result = auth.register_user("strongpass", "alice")
    assert ok is True
    assert result  # a non-empty user id


def test_registered_user_can_login(auth):
    ok, _msg, user_id = auth.register_user("mypass123", "bob")
    assert ok
    login_ok, _ = auth.login_user(user_id, "mypass123")
    assert login_ok is True


def test_login_with_wrong_password_fails(auth):
    ok, _msg, user_id = auth.register_user("rightpass", "carol")
    assert ok
    login_ok, _ = auth.login_user(user_id, "wrongpass")
    assert login_ok is False


def test_login_unknown_user_fails(auth):
    login_ok, _ = auth.login_user("nonexistent_id", "whatever")
    assert login_ok is False


# ───────────────────────────────────────────────────────────────────────────
# Password change
# ───────────────────────────────────────────────────────────────────────────

def test_change_password_success(auth):
    ok, _msg, user_id = auth.register_user("oldpass", "dave")
    assert ok
    changed, _ = auth.change_password(user_id, "oldpass", "newpass456")
    assert changed is True
    # Old password no longer works
    assert auth.login_user(user_id, "oldpass")[0] is False
    # New password works
    assert auth.login_user(user_id, "newpass456")[0] is True


def test_change_password_wrong_old_fails(auth):
    ok, _msg, user_id = auth.register_user("origpass", "erin")
    assert ok
    changed, _ = auth.change_password(user_id, "wrongold", "newpass")
    assert changed is False


# ───────────────────────────────────────────────────────────────────────────
# Lockout after repeated failures
# ───────────────────────────────────────────────────────────────────────────

def test_lockout_after_five_failures(auth):
    ok, _msg, user_id = auth.register_user("secret", "frank")
    assert ok
    # 5 wrong attempts
    for _ in range(5):
        auth.login_user(user_id, "wrong")
    # 6th attempt — even with CORRECT password — should be blocked
    blocked_ok, _ = auth.login_user(user_id, "secret")
    assert blocked_ok is False


def test_reset_lockout_restores_access(auth):
    ok, _msg, user_id = auth.register_user("secret2", "grace")
    assert ok
    for _ in range(5):
        auth.login_user(user_id, "wrong")
    auth.reset_lockout(user_id)
    restored_ok, _ = auth.login_user(user_id, "secret2")
    assert restored_ok is True


# ───────────────────────────────────────────────────────────────────────────
# User info & deletion
# ───────────────────────────────────────────────────────────────────────────

def test_get_user_info(auth):
    ok, _msg, user_id = auth.register_user("infopass", "heidi")
    assert ok
    info = auth.get_user_info(user_id)
    assert info is not None


def test_delete_user(auth):
    ok, _msg, user_id = auth.register_user("delpass", "ivan")
    assert ok
    deleted, _ = auth.delete_user(user_id, "delpass")
    assert deleted is True
    # Can no longer login
    assert auth.login_user(user_id, "delpass")[0] is False
