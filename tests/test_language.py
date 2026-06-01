"""
═══════════════════════════════════════════════════════════════════════════
Tests for utils/language.py — translations, RTL, completeness
═══════════════════════════════════════════════════════════════════════════
"""

import importlib

import pytest


@pytest.fixture
def lang(mock_streamlit):
    import utils.language as lang_mod
    importlib.reload(lang_mod)
    return lang_mod


# ───────────────────────────────────────────────────────────────────────────
# Translation completeness
# ───────────────────────────────────────────────────────────────────────────

def test_en_and_ar_have_same_keys(lang):
    en_keys = set(lang.TRANSLATIONS["en"].keys())
    ar_keys = set(lang.TRANSLATIONS["ar"].keys())
    assert en_keys == ar_keys, (
        f"Mismatch — only in EN: {en_keys - ar_keys}; "
        f"only in AR: {ar_keys - en_keys}"
    )


def test_no_missing_arabic_translations(lang):
    missing = lang.missing_translations("ar")
    assert missing == [], f"Missing Arabic translations: {missing}"


def test_has_minimum_key_count(lang):
    """Guard against accidental key loss."""
    assert len(lang.TRANSLATIONS["en"]) >= 280


def test_no_empty_values(lang):
    for code in ("en", "ar"):
        for key, value in lang.TRANSLATIONS[code].items():
            assert value != "", f"Empty value for '{key}' in '{code}'"


# ───────────────────────────────────────────────────────────────────────────
# t() behavior
# ───────────────────────────────────────────────────────────────────────────

def test_t_returns_english_by_default(lang):
    lang.st.session_state["language"] = "English"
    assert lang.t("login") == lang.TRANSLATIONS["en"]["login"]


def test_t_returns_arabic_when_selected(lang):
    lang.st.session_state["language"] = "العربية"
    assert lang.t("login") == lang.TRANSLATIONS["ar"]["login"]


def test_t_falls_back_to_key_when_missing(lang):
    """Unknown keys should return the key itself (or fallback), never crash."""
    result = lang.t("this_key_does_not_exist_xyz")
    assert "this_key_does_not_exist_xyz" in result or result == ""


def test_t_with_explicit_fallback(lang):
    result = lang.t("nonexistent_key_abc", fallback="Default Text")
    assert result in ("Default Text", "nonexistent_key_abc")


# ───────────────────────────────────────────────────────────────────────────
# Language code & RTL
# ───────────────────────────────────────────────────────────────────────────

def test_get_language_code_english(lang):
    lang.st.session_state["language"] = "English"
    assert lang.get_language_code() == "en"


def test_get_language_code_arabic(lang):
    lang.st.session_state["language"] = "العربية"
    assert lang.get_language_code() == "ar"


def test_is_rtl_false_for_english(lang):
    lang.st.session_state["language"] = "English"
    assert lang.is_rtl() is False


def test_is_rtl_true_for_arabic(lang):
    lang.st.session_state["language"] = "العربية"
    assert lang.is_rtl() is True


# ───────────────────────────────────────────────────────────────────────────
# Helper functions
# ───────────────────────────────────────────────────────────────────────────

def test_get_all_keys_returns_list(lang):
    keys = lang.get_all_keys()
    assert isinstance(keys, list)
    assert len(keys) > 0


def test_init_language_sets_default(lang):
    lang.st.session_state.clear()
    lang.init_language()
    assert "language" in lang.st.session_state


def test_common_keys_exist(lang):
    """A handful of keys every page relies on must exist."""
    required = ["back", "login", "logout", "settings", "home_title",
                "camera", "dashboard", "tasks", "calculator"]
    for key in required:
        assert key in lang.TRANSLATIONS["en"], f"Missing required key: {key}"
