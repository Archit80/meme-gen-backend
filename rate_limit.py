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

def get_usage(ip: str):
    today = get_today()
    limits = load_limits()

    if ip not in limits or limits[ip]["date"] != today:
        # Reset for new day
        limits[ip] = {"date": today, "count": 0}
        save_limits(limits)

    count = limits[ip]["count"]
    remaining = max(DAILY_LIMIT - count, 0)
    return remaining


def is_allowed(ip: str):
    today = get_today()
    limits = load_limits()

    if ip not in limits or limits[ip]["date"] != today:
        # Reset quota for new day
        limits[ip] = {"date": today, "count": 1}
        save_limits(limits)
        return True

    if limits[ip]["count"] >= DAILY_LIMIT:
        return False

    limits[ip]["count"] += 1
    save_limits(limits)
    return True
