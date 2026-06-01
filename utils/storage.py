import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_FILE = DATA_DIR / "app_data.json"

DEFAULT_DATA = {
    "notes_list": [],
    "luck_value": None,
    "calc_expression": "",
    "calc_result": "0",
    "calc_history": []
}

def ensure_data_file():
    DATA_DIR.mkdir(exist_ok=True)

    if not DATA_FILE.exists():
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_DATA, f, ensure_ascii=False, indent=4)

def load_data():
    ensure_data_file()

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        data = DEFAULT_DATA.copy()

    for key, value in DEFAULT_DATA.items():
        if key not in data:
            data[key] = value

    return data

def save_data(data):
    ensure_data_file()

    clean_data = {}
    for key in DEFAULT_DATA.keys():
        clean_data[key] = data.get(key, DEFAULT_DATA[key])

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(clean_data, f, ensure_ascii=False, indent=4)