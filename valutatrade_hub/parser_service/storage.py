import json
import os
from shutil import move
from datetime import datetime
from .config import config

class RatesStorage:
    def __init__(self):
        self.history_file = config.HISTORY_FILE_PATH
        self.rates_file = config.RATES_FILE_PATH

    def save_history(self, pair_id, record):
        history = []
        if os.path.exists(self.history_file):
            with open(self.history_file, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    history = json.loads(content)
        history.append(record)
        tmp_file = self.history_file + ".tmp"
        with open(tmp_file, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2)
        move(tmp_file, self.history_file)

    def update_rates_snapshot(self, rates_dict):
        snapshot = {"pairs": {}, "last_refresh": datetime.utcnow().isoformat() + "Z"}
        for pair, info in rates_dict.items():
            snapshot["pairs"][pair] = info
        tmp_file = self.rates_file + ".tmp"
        with open(tmp_file, "w", encoding="utf-8") as f:
            json.dump(snapshot, f, indent=2)
        move(tmp_file, self.rates_file)