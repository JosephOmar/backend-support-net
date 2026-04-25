import json
import os
from app.core.config import settings
import threading

def load_state():
    if not os.path.exists(settings.STATE_FILE):
        return {}

    with open(settings.STATE_FILE, "r") as f:
        return json.load(f)


def save_state(state):
    with open(settings.STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

lock = threading.Lock()

def update_export_state(export_id, status):
    with lock:
        state = load_state()
        state[export_id] = status
        save_state(state)