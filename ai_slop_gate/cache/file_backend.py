import json
from pathlib import Path
from typing import Any


class FileCacheBackend:
    """
    Canonical persistent cache.
    Stores JSON-serializable provider results on disk.
    """

    def __init__(self, root: str = ".ai-slop-cache"):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        return self.root / f"{key}.json"

    def get(self, key: str) -> Any | None:
        path = self._path(key)
        if not path.exists():
            return None
        return json.loads(path.read_text())

    def set(self, key: str, value: Any) -> None:
        path = self._path(key)
        path.write_text(json.dumps(value, default=str))
