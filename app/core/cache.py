# core/cache.py
import time
from typing import Any, Dict

class SimpleCache:
    def __init__(self):
        self.store: Dict[str, Any] = {}
        self.timestamps: Dict[str, float] = {}

    def get(self, key: str, ttl: int):
        now = time.time()

        if key in self.store:
            if now - self.timestamps[key] < ttl:
                return self.store[key]

        return None

    def set(self, key: str, value: Any):
        self.store[key] = value
        self.timestamps[key] = time.time()


cache = SimpleCache()