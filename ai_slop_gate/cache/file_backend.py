import json
from pathlib import Path

class FileCacheBackend:
    def __init__(self, root=".ai-slop-cache"):
        self.root = Path(root)
        self.root.mkdir(exist_ok=True)

    def _path(self, key):
        return self.root / f"{key}.json"

    def get(self, key):
        path = self._path(key)
        if not path.exists():
            return None
        return json.loads(path.read_text())

    def set(self, key, value, ttl=None):
        path = self._path(key)
        path.write_text(json.dumps(value))
