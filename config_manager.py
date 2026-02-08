import json
import os
import sys
from pathlib import Path

CONFIG_DIR = Path.home() / ".luca"
CONFIG_FILE = CONFIG_DIR / "config.json"

class ConfigManager:
    def __init__(self):
        self._ensure_config_dir()

    def _ensure_config_dir(self):
        if not CONFIG_DIR.exists():
            CONFIG_DIR.mkdir(parents=True)

    def load_config(self):
        if not CONFIG_FILE.exists():
            return None
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return None

    def save_config(self, data):
        with open(CONFIG_FILE, "w") as f:
            json.dump(data, f, indent=4)

    def ensure_setup(self):
        config = self.load_config()
        if not config:
            print("LucaCli is not configured. Please run 'luca --setup' first.")
            sys.exit(1)
        return config
