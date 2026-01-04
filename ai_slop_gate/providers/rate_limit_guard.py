import time
from typing import Any, Optional


class RateLimitGuard:
    def __init__(self, provider, interval_sec: float):
        self.provider = provider
        self.interval_sec = interval_sec
        self._last_call: dict[str, float] = {}

    def _key(self) -> str:
        if hasattr(self.provider, "rate_limit_key"):
            return self.provider.rate_limit_key()
        return self.provider.name

    def analyze(self, *args, **kwargs) -> Any:
        key = self._key()
        now = time.time()
        last = self._last_call.get(key)

        if last is not None and now - last < self.interval_sec:
            return self.provider.analyze(*args, **kwargs)

        self._last_call[key] = now
        return self.provider.analyze(*args, **kwargs)
