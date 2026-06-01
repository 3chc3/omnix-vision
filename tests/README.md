# 🧪 OMNIX VISION — Tests

Unit tests for the OMNIX VISION platform, covering authentication, the
activity log, the translation system, and the new feature pages.

## Running the tests

From the project root:

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
pytest

# Run with coverage
pytest --cov=utils --cov=pages --cov-report=term-missing

# Run a specific file
pytest tests/test_auth.py -v

# Run a specific test
pytest tests/test_auth.py::test_lockout_after_five_failures -v
```

## What's covered

| File | Module under test | Tests |
|------|-------------------|-------|
| `test_auth.py` | `utils/auth.py` | Hashing, registration, login, lockout, password change, deletion |
| `test_activity.py` | `utils/activity.py` | Logging, stats, 500-entry cap, clearing |
| `test_language.py` | `utils/language.py` | EN/AR key parity, RTL, `t()` behavior, completeness |
| `test_pages.py` | 4 new pages | Notifications, backup roundtrip, password gen, color conversion, pomodoro |

Total: **64 tests**.

## How it works

The tests never launch a real Streamlit server. Instead, `conftest.py`
provides:

- **`mock_streamlit`** — a fake `streamlit` module so imports succeed and
  widget calls return sensible defaults.
- **`temp_data_dir`** — an isolated temp directory so tests never touch real
  user data.
- **`session`** — a fresh `session_state` per test.
- **`AttrDict`** — a dict supporting both `d["key"]` and `d.key` access, just
  like the real `st.session_state`.

This keeps the suite fast (runs in ~1.5s) and side-effect-free.

## Adding tests

1. Create `tests/test_yourmodule.py`.
2. Use the `mock_streamlit` and `temp_data_dir` fixtures as needed.
3. Patch any module-level file paths to point at `temp_data_dir`.
4. Keep tests isolated — no shared global state.
