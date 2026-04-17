"""Gorgias HTTP client built on the shared MCPHttpClient base.

Adds Gorgias-specific defaults (Accept JSON, basic auth from env vars).
Auth credentials are loaded from `.env` via python-dotenv at import time.
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Make `infra.common` importable regardless of how the MCP is launched.
# Layout: <repo>/gorgias_mcp/src/gorgias_mcp/client.py → repo = parents[3]
_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from infra.common.http_mcp import MCPHttpClient  # noqa: E402

load_dotenv()

GORGIAS_DOMAIN = os.getenv("GORGIAS_DOMAIN", "impulse-nutrition-vitavea")
GORGIAS_EMAIL = os.getenv("GORGIAS_EMAIL", "achabrat@havea.com")
GORGIAS_API_KEY = os.getenv("GORGIAS_API_KEY", "")

BASE_URL = f"https://{GORGIAS_DOMAIN}.gorgias.com/api"


class GorgiasClient(MCPHttpClient):
    def default_headers(self):
        h = super().default_headers()
        h.setdefault("Accept", "application/json")
        return h


_client: GorgiasClient = None  # type: ignore[assignment]


def get_client() -> GorgiasClient:
    """Lazy singleton so tests can override credentials before first use."""
    global _client
    if _client is None:
        _client = GorgiasClient(
            base_url=BASE_URL,
            auth=(GORGIAS_EMAIL, GORGIAS_API_KEY),
            timeout=30.0,
            retries=2,
        )
    return _client


def reset_client() -> None:
    """For tests."""
    global _client
    _client = None  # type: ignore[assignment]
