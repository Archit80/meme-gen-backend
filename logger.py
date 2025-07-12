import json
from datetime import datetime
from pathlib import Path

LOG_FILE = Path("meme_logs.json")

def log_event(identifier: str, vibe: str, caption: str):
    event = {
        "timestamp": datetime.utcnow().isoformat(),
        "identifier": identifier,
        "vibe": vibe,
        "caption": caption
    }

    logs = []

    if LOG_FILE.exists():
        try:
            with open(LOG_FILE, "r") as f:
                logs = json.load(f)
        except:
            pass  # corrupted log or empty

    logs.append(event)

    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=2)
