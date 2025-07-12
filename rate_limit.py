import json
from datetime import datetime
from pathlib import Path

RATE_LIMIT_FILE = Path("rate_limit.json")
DAILY_LIMIT = 10 # Maximum requests allowed per IP per day

def get_today():
    return datetime.utcnow().strftime("%Y-%m-%d")

def load_limits():
    if RATE_LIMIT_FILE.exists():
        with open(RATE_LIMIT_FILE, "r") as f:
            return json.load(f)
    return {}

def save_limits(data):
    with open(RATE_LIMIT_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_usage(identifier: str):
    today = get_today()
    limits = load_limits()

    if identifier not in limits or limits[identifier]["date"] != today:
        # Reset for new day
        limits[identifier] = {"date": today, "count": 0}
        save_limits(limits)

    count = limits[identifier]["count"]
    remaining = max(DAILY_LIMIT - count, 0)
    return remaining


def is_allowed(identifier: str):
    today = get_today()
    limits = load_limits()

    if identifier not in limits or limits[identifier]["date"] != today:
        # Reset quota for new day
        limits[identifier] = {"date": today, "count": 1}
        save_limits(limits)
        return True

    if limits[identifier]["count"] >= DAILY_LIMIT:
        return False

    limits[identifier]["count"] += 1
    save_limits(limits)
    return True
