"""
Settings manager - persists to JSON file
"""
import json
import os
from pathlib import Path


DEFAULTS = {
    "work_interval_min": 20,       # minutes between breaks
    "break_duration_sec": 20,      # seconds for break
    "look_distance_m": 6,          # metres (20 feet)
    "start_with_windows": False,
    "start_minimized": False,       # start in background
    "skip_fullscreen": True,        # skip alert during fullscreen apps
    "sound_enabled": True,
    "theme": "dark",
}


class Settings:
    def __init__(self):
        self._path = Path(os.getenv("APPDATA", ".")) / "EyeRest" / "settings.json"
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._data = dict(DEFAULTS)
        self._load()

    def _load(self):
        if self._path.exists():
            try:
                with open(self._path, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                    self._data.update(saved)
            except Exception:
                pass

    def save(self):
        try:
            with open(self._path, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2)
        except Exception:
            pass

    def get(self, key, default=None):
        return self._data.get(key, default)

    def set(self, key, value):
        self._data[key] = value
        self.save()

    def all(self):
        return dict(self._data)
