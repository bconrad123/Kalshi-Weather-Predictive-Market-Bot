import json
from pathlib import Path
from datetime import date, datetime
import os
DATA_FILE = Path("predictions.json")

def load_data():
    if DATA_FILE.exists():
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def log_morning_prediction(city, model_prob, market_price, edge):
    data = load_data()
    today = str(date.today())
    key = f"{today}_{city}"
    data[key] = {
        "date": today,
        "city": city,
        "morning": {
            "timestamp": datetime.now().isoformat(),
            "ensemble_prob": model_prob,
            "market_price": market_price,
            "edge": (abs(edge)),
            "event":None,
            "night": None
        }
       
    }
    save_data(data)

def log_night_result(city, actual_outcome, settled_price=None):
    data = load_data()
    today = str(date.today())
    key = f"{today}_{city}"
    if key not in data:
        raise KeyError(f"No morning prediction found for {key}")
    data[key]["night"] = {
        "timestamp": datetime.now().isoformat(),
        "actual_outcome": actual_outcome,
        "settled_price": settled_price,
        "correct": (actual_outcome == 1 and data[key]["morning"]["edge"] > 0)
    }
    save_data(data)


DATA_FILE = Path("predictions.json")

def load_data():
    """Load the full JSON store, returning {} if the file doesn't exist yet."""
    if DATA_FILE.exists():
        with open(DATA_FILE, "r") as f:
            content = f.read().strip()
            return json.loads(content) if content else {}
    return {}

def save_data(data, merge=True):
    """
    Save data to the JSON file.

    merge=True (default): loads whatever is currently on disk, updates it
        with `data`, and writes the combined result. Use this for normal
        updates (e.g., log_night_result updating one key) so you never
        clobber other days/cities you're not touching.
    merge=False: overwrites the file entirely with `data`. Use this only
        when you intentionally want to replace the whole store (e.g.,
        a cleanup/migration script).

    Writes atomically: writes to a temp file first, then renames it over
    the real file, so a crash mid-write can't leave you with a truncated
    or corrupted predictions.json.
    """
    if merge:
        existing = load_data()
        existing.update(data)
        data = existing

    tmp_path = DATA_FILE.with_suffix(".tmp")
    with open(tmp_path, "w") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp_path, DATA_FILE)  # atomic on POSIX and Windows