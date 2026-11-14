"""
JARVIS — In-Memory Async TTL Cache
Developer: Shadow
"""

from __future__ import annotations

import asyncio
import time
from typing import Generic, TypeVar

K = TypeVar("K")
V = TypeVar("V")


class AsyncTTLCache(Generic[K, V]):
    """Lightweight coroutine-safe TTL cache for prefixes and guild settings."""

    def __init__(self, ttl_seconds: float = 300.0, max_size: int = 10_000) -> None:
        self.ttl_seconds = ttl_seconds
        self.max_size = max_size
        self._store: dict[K, tuple[V, float]] = {}
        self._lock = asyncio.Lock()

    async def get(self, key: K) -> V | None:
        async with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            value, expires_at = entry
            if time.monotonic() > expires_at:
                self._store.pop(key, None)
                return None
            return value

    async def set(self, key: K, value: V) -> None:
        async with self._lock:
            if len(self._store) >= self.max_size and key not in self._store:
                oldest_key = next(iter(self._store))
                self._store.pop(oldest_key, None)
            self._store[key] = (value, time.monotonic() + self.ttl_seconds)

    async def invalidate(self, key: K) -> None:
        async with self._lock:
            self._store.pop(key, None)

    async def clear(self) -> None:
        async with self._lock:
            self._store.clear()
