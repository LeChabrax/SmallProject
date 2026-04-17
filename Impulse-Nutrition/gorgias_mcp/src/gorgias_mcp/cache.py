"""Tiny TTL cache for the MCP process lifetime.

FastMCP keeps the Python process alive across stdio tool calls, so a
module-level cache survives between tool invocations. We only cache things
that are stable in practice (Gorgias users, view list).
"""

import time
from functools import wraps
from threading import Lock
from typing import Any, Callable, Dict, Tuple


def ttl_cache(seconds: float) -> Callable:
    """Decorator caching the wrapped fn's result keyed on positional args.

    Not safe for kwargs-only calls — use only on simple read functions.
    """

    def decorator(fn: Callable) -> Callable:
        store: Dict[Tuple, Tuple[float, Any]] = {}
        lock = Lock()

        @wraps(fn)
        def wrapper(*args, **kwargs):
            key = (args, tuple(sorted(kwargs.items())))
            now = time.monotonic()
            with lock:
                cached = store.get(key)
                if cached and (now - cached[0]) < seconds:
                    return cached[1]
            value = fn(*args, **kwargs)
            with lock:
                store[key] = (now, value)
            return value

        def invalidate():
            with lock:
                store.clear()

        wrapper.invalidate = invalidate  # type: ignore[attr-defined]
        return wrapper

    return decorator
