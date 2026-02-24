import json
import os

class DatabaseManager:
    _instance = None

    def __new__(cls, path="data"):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.path = path
        return cls._instance

    def read_json(self, filename):
        full_path = os.path.join(self.path, filename)
        if not os.path.exists(full_path):
            return [] if filename != "rates.json" else {}
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            return json.loads(content) if content else ([] if filename != "rates.json" else {})

    def write_json(self, filename, data):
        full_path = os.path.join(self.path, filename)
        with open(full_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)