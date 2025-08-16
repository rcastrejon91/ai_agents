import json
import os
import time

PATH = os.getenv("ROBOT_TELEMETRY_PATH", "data/robot_status.json")


def save_telemetry(payload: dict):
    os.makedirs(os.path.dirname(PATH), exist_ok=True)
    payload["updated_at"] = int(time.time())
    json.dump(payload, open(PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=2)


def load_telemetry():
    if not os.path.exists(PATH):
        return {"components": [], "updated_at": 0}
    return json.load(open(PATH, "r", encoding="utf-8"))
