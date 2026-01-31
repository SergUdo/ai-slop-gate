from typing import Any, Optional


class CacheBackend:
    """
    Canonical cache backend interface.
    """

    def get(self, key: str) -> Optional[Any]:
        raise NotImplementedError

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        raise NotImplementedError
