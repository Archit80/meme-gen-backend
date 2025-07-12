import json
import coolname
from pathlib import Path

NAME_FILE = Path("ip_names.json")

def load_names():
    if NAME_FILE.exists():
        with open(NAME_FILE, "r") as f:
            return json.load(f)
    return {}

def save_names(data):
    with open(NAME_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_or_create_name(ip: str):
    names = load_names()

    if ip not in names:
        names[ip] = (coolname.generate_slug(2))
        save_names(names)

    return names[ip]
