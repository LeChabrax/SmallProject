"""Anti-fragile path resolution for scripts scattered across the repo.

Before this helper every script hardcoded its own `Path(__file__).parents[N]`
depth, which broke every time a script moved (the last reorg shuffled
scripts from instagram_dm_mcp/scripts/ into infra/scripts/instagram/ and
tools/veille_kolsquare/scripts/, silently breaking ~14 paths at once).

Markers:

- `find_project_root()` walks up from the caller until it finds `.mcp.json`
  (the Impulse-Nutrition project's MCP config, unique to its root). Doesn't
  care how deep the caller lives.
- `INSTAGRAM_DATA_DIR` is the canonical home for session JSON, progress
  JSON, logs, downloads and cached conversations — always
  `<project_root>/instagram_dm_mcp/data/` regardless of the caller's depth.

Why `.mcp.json` rather than `.git/`: the enclosing git repo sits one level
above Impulse-Nutrition/ (it's a multi-project monorepo), so `.git/` would
land on the wrong directory. `.mcp.json` is unique to this project.

Usage in a script:

    import sys
    from pathlib import Path

    # 4-line bootstrap so we can import infra.common even before sys.path
    # is wired. Must run BEFORE any `from infra.common.*` import.
    _here = Path(__file__).resolve()
    for _p in (_here, *_here.parents):
        if (_p / ".mcp.json").exists():
            sys.path.insert(0, str(_p))
            break

    from infra.common.paths import INSTAGRAM_DATA_DIR
    from infra.common.instagram_client import get_ig_client

    LOG_DIR = INSTAGRAM_DATA_DIR / "logs"
"""

from __future__ import annotations

import inspect
from pathlib import Path


_PROJECT_ROOT_MARKER = ".mcp.json"


def find_project_root(start: Path | str | None = None) -> Path:
    """Return the Impulse-Nutrition project root (the directory containing `.mcp.json`).

    If `start` is None, starts from the caller's `__file__`. Walks up until
    the marker is found. Raises RuntimeError if none exists above.
    """
    if start is None:
        frame = inspect.stack()[1]
        start = Path(frame.filename).resolve()
    else:
        start = Path(start).resolve()
    if start.is_file():
        start = start.parent
    for candidate in (start, *start.parents):
        if (candidate / _PROJECT_ROOT_MARKER).exists():
            return candidate
    raise RuntimeError(
        f"No {_PROJECT_ROOT_MARKER} found above {start}. Are you inside the "
        f"Impulse-Nutrition repo?"
    )


# Canonical data home for Instagram batch scripts (logs, progress,
# conversations) under the ongoing `infra/data/<domain>/` convention.
# Sessions are a special case: they stay under
# `instagram_dm_mcp/data/sessions/` because `infra/common/instagram_client.py`
# and the MCP server both read from that path at runtime — moving sessions
# would require coordinating a live MCP restart.
PROJECT_ROOT = find_project_root(__file__)
INSTAGRAM_DATA_DIR = PROJECT_ROOT / "infra" / "data" / "instagram"
INSTAGRAM_SESSION_DIR = PROJECT_ROOT / "instagram_dm_mcp" / "data" / "sessions"
