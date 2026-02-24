import json
import os

class SettingsLoader:
    _instance = None

    def __new__(cls, path="data/settings.json"):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.path = path
            cls._instance._load()
        return cls._instance

    def _load(self):
        if os.path.exists(self.path):
            with open(self.path, "r", encoding="utf-8") as f:
                self._data = json.load(f)
        else:
            self._data = {
                "rates_ttl_seconds": 3600,
                "default_base": "USD",
                "log_path": "logs/actions.log"
            }

    def get(self, key, default=None):
        return self._data.get(key, default)

    def reload(self):
        self._load()