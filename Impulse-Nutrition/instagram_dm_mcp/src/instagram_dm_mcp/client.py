"""Instagram client session management for the MCP server.

Reads/writes the instagrapi session JSON under
`instagram_dm_mcp/data/sessions/{username}_session.json` so restarts
skip the full login flow (which Instagram rate-limits aggressively).

The MCP server and debug scripts both call `login_client(client,
username, password)` to get a logged-in client pointing at the right
session file.
"""

from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

SESSION_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "sessions"


def session_path(username: str) -> Path:
    """Return the on-disk path for a given account's session JSON."""
    SESSION_DIR.mkdir(parents=True, exist_ok=True)
    return SESSION_DIR / f"{username}_session.json"


def login_client(client, username: str, password: str) -> Path:
    """Load a persisted session if present, then login and persist settings.

    Mutates the passed-in instagrapi `Client`. Returns the session file path
    for logging purposes. The persisted session lets Instagram recognise the
    device fingerprint on restart instead of triggering a fresh auth flow
    (which is the main cause of login hangs).
    """
    path = session_path(username)
    if path.exists():
        logger.info(f"Loading existing session from {path}")
        client.load_settings(path)
    client.login(username, password)
    client.dump_settings(path)
    logger.info(f"Session saved to {path}")
    return path
