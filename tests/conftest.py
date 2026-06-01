"""
═══════════════════════════════════════════════════════════════════════════
OMNIX VISION — Pytest Configuration & Fixtures
═══════════════════════════════════════════════════════════════════════════
Provides shared fixtures for testing:
    • mock_streamlit  — a fake streamlit module so pages import cleanly
    • temp_data_dir   — an isolated temp directory for JSON persistence
    • clean_session   — a fresh attribute-dict session_state per test
═══════════════════════════════════════════════════════════════════════════
"""

import shutil
import sys
import tempfile
import types
from pathlib import Path

import pytest


# ───────────────────────────────────────────────────────────────────────────
# AttrDict — supports BOTH dict["key"] and dict.key access
# (Streamlit's SessionState behaves this way; tests need the same.)
# ───────────────────────────────────────────────────────────────────────────
class AttrDict(dict):
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError:
            raise AttributeError(key)

    def setdefault(self, key, default=None):
        if key not in self:
            self[key] = default
        return self[key]


# ───────────────────────────────────────────────────────────────────────────
# A no-op context manager for st.columns(), st.tabs(), st.expander(), etc.
# ───────────────────────────────────────────────────────────────────────────
class _DummyCtx:
    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    # Allow `with col:` and also direct method calls on the returned object
    def __getattr__(self, _name):
        return lambda *a, **k: None


def _build_mock_streamlit():
    """Construct a fake `streamlit` module sufficient for importing pages."""
    st_mod = types.ModuleType("streamlit")

    # Session state
    st_mod.session_state = AttrDict()

    # Simple no-op display functions
    noop_names = [
        "markdown", "write", "error", "success", "warning", "info",
        "caption", "image", "audio", "video", "code", "exception",
        "dataframe", "table", "metric", "divider", "pyplot",
        "plotly_chart", "balloons", "snow", "toast", "rerun",
        "set_page_config", "title", "header", "subheader", "text",
        "json", "latex", "progress", "spinner", "stop", "html",
    ]
    for name in noop_names:
        setattr(st_mod, name, lambda *a, **k: None)

    # Layout helpers that must return iterables / context managers
    st_mod.columns = lambda spec, **k: [
        _DummyCtx() for _ in range(spec if isinstance(spec, int) else len(spec))
    ]
    st_mod.tabs = lambda labels, **k: [_DummyCtx() for _ in labels]
    st_mod.expander = lambda *a, **k: _DummyCtx()
    st_mod.container = lambda *a, **k: _DummyCtx()
    st_mod.empty = lambda *a, **k: _DummyCtx()
    st_mod.form = lambda *a, **k: _DummyCtx()
    st_mod.sidebar = _DummyCtx()

    # Input widgets — return sensible defaults
    st_mod.button = lambda *a, **k: False
    st_mod.checkbox = lambda *a, **k: k.get("value", False)
    st_mod.toggle = lambda *a, **k: k.get("value", False)
    st_mod.text_input = lambda *a, **k: k.get("value", "")
    st_mod.text_area = lambda *a, **k: k.get("value", "")
    st_mod.number_input = lambda *a, **k: k.get("value", 0)
    st_mod.slider = lambda *a, **k: k.get("value", 0)
    st_mod.select_slider = lambda *a, **k: k.get("value", None)
    st_mod.selectbox = lambda label, options, **k: (
        options[k.get("index", 0)] if options else None
    )
    st_mod.multiselect = lambda *a, **k: k.get("default", [])
    st_mod.radio = lambda label, options, **k: (options[0] if options else None)
    st_mod.date_input = lambda *a, **k: k.get("value", None)
    st_mod.time_input = lambda *a, **k: k.get("value", None)
    st_mod.color_picker = lambda *a, **k: k.get("value", "#000000")
    st_mod.file_uploader = lambda *a, **k: None
    st_mod.download_button = lambda *a, **k: False
    st_mod.form_submit_button = lambda *a, **k: False

    # Cache decorators — pass-through
    st_mod.cache_data = lambda *a, **k: (a[0] if a and callable(a[0]) else (lambda f: f))
    st_mod.cache_resource = lambda *a, **k: (a[0] if a and callable(a[0]) else (lambda f: f))

    # components.v1.html
    components_mod = types.ModuleType("streamlit.components")
    v1_mod = types.ModuleType("streamlit.components.v1")
    v1_mod.html = lambda *a, **k: None
    v1_mod.iframe = lambda *a, **k: None
    components_mod.v1 = v1_mod
    st_mod.components = components_mod

    return st_mod, components_mod, v1_mod


@pytest.fixture
def mock_streamlit(monkeypatch):
    """Install a fake streamlit into sys.modules for the duration of a test."""
    st_mod, components_mod, v1_mod = _build_mock_streamlit()
    monkeypatch.setitem(sys.modules, "streamlit", st_mod)
    monkeypatch.setitem(sys.modules, "streamlit.components", components_mod)
    monkeypatch.setitem(sys.modules, "streamlit.components.v1", v1_mod)
    return st_mod


@pytest.fixture
def temp_data_dir():
    """Provide an isolated temporary directory; cleaned up after the test."""
    path = Path(tempfile.mkdtemp(prefix="omnix_test_"))
    yield path
    shutil.rmtree(path, ignore_errors=True)


@pytest.fixture
def clean_session(mock_streamlit):
    """Reset session_state to a fresh logged-in user."""
    mock_streamlit.session_state.clear()
    mock_streamlit.session_state.update({
        "language":  "English",
        "logged_in": True,
        "user":      "test_user",
        "page":      "home",
    })
    return mock_streamlit.session_state
