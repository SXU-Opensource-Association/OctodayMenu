from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from math import ceil
from threading import Lock


WINDOW = timedelta(minutes=15)
MAX_FAILURES = 5
_failures: dict[str, list[datetime]] = defaultdict(list)
_lock = Lock()


class LoginRateLimitError(Exception):
    def __init__(self, retry_after_seconds: int) -> None:
        super().__init__("登录尝试过于频繁，请稍后再试")
        self.retry_after_seconds = retry_after_seconds


def login_key(email: str, ip_address: str | None) -> str:
    return f"{email.strip().lower()}|{ip_address or 'unknown'}"


def enforce_login_limit(key: str, now: datetime | None = None) -> None:
    current = now or datetime.now(timezone.utc)
    with _lock:
        recent = [attempt for attempt in _failures[key] if current - attempt < WINDOW]
        _failures[key] = recent
        if len(recent) >= MAX_FAILURES:
            retry_after = max(1, ceil((recent[0] + WINDOW - current).total_seconds()))
            raise LoginRateLimitError(retry_after)


def record_login_failure(key: str, now: datetime | None = None) -> None:
    current = now or datetime.now(timezone.utc)
    with _lock:
        _failures[key] = [attempt for attempt in _failures[key] if current - attempt < WINDOW]
        _failures[key].append(current)


def reset_login_failures(key: str) -> None:
    with _lock:
        _failures.pop(key, None)
