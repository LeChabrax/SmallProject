"""Instagram client factory for impulse_nutrition_fr and veille accounts.

Replaces the gspread / instagrapi boilerplate that was duplicated in every
script under `instagram_dm_mcp/`. Scripts should do:

    from infra.common.instagram_client import get_ig_client, sleep_random
    cl = get_ig_client("impulse")

Sessions are persisted as JSON next to the instagram_dm_mcp module so the
existing `*_session.json` files keep working without relogin.
"""

from __future__ import annotations

import os
import random
import time
from functools import lru_cache
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv

# Session files now live under instagram_dm_mcp/data/sessions/ (gitignored via
# the `data/` entry). The `.env` with Instagram credentials stays at the
# instagram_dm_mcp root for backwards compat.
_MCP_ROOT = Path(__file__).resolve().parent.parent.parent / "instagram_dm_mcp"
_SESSION_DIR = _MCP_ROOT / "data" / "sessions"
_SESSION_DIR.mkdir(parents=True, exist_ok=True)

# Load from repo-root .env first, then fall back to the subfolder .env.
load_dotenv(_MCP_ROOT.parent / ".env")
load_dotenv(_MCP_ROOT / ".env", override=False)

_ACCOUNTS = {
    "impulse": {
        "username_env": "INSTAGRAM_USERNAME",
        "password_env": "INSTAGRAM_PASSWORD",
        "default_username": "impulse_nutrition_fr",
    },
    "veille": {
        "username_env": "INSTAGRAM_VEILLE_USERNAME",
        "password_env": "INSTAGRAM_VEILLE_PASSWORD",
        "default_username": "antman.lass",
    },
}

Account = Literal["impulse", "veille"]


@lru_cache(maxsize=2)
def get_ig_client(account: Account = "impulse"):
    """Return a cached, logged-in instagrapi `Client` for the given account.

    Uses the persisted session JSON if present, otherwise performs a fresh
    login with credentials from `.env`. The client is memoized per account so
    scripts that call this function multiple times reuse the same session.
    """
    from instagrapi import Client

    if account not in _ACCOUNTS:
        raise ValueError(f"unknown account: {account!r}")

    cfg = _ACCOUNTS[account]
    username = os.getenv(cfg["username_env"], cfg["default_username"])
    password = os.getenv(cfg["password_env"])
    if not password:
        raise RuntimeError(
            f"missing env var {cfg['password_env']} for Instagram account "
            f"{account!r}"
        )

    session_file = _SESSION_DIR / f"{username}_session.json"
    cl = Client()
    if session_file.exists():
        cl.load_settings(session_file)
    cl.login(username, password)
    cl.dump_settings(session_file)
    return cl


def sleep_random(min_s: float = 2.0, max_s: float = 5.0) -> None:
    """Sleep for a random duration in [min_s, max_s].

    Use between Instagram API calls to avoid triggering rate-limit flags.
    Recommended values:
        - between threads in a read loop: sleep_random(3, 8)
        - every 10 threads in a batch:    sleep_random(15, 30)
        - before send_message/like:       sleep_random(4, 10)
    """
    time.sleep(random.uniform(min_s, max_s))
