"""View aliases + maps built from the live Gorgias /api/views response.

The Gorgias V2 `/api/tickets` endpoint rejects raw `?status=` / `?channel=`
filters with a 400. The working alternative is `/api/views/{view_id}/items`,
where each view is a server-side saved filter owned by the Gorgias account.

View IDs are **auto-generated per account**, so they can't be hardcoded.
This module defines alias → resolution rules; the actual IDs are resolved
at runtime from the `/api/views` response (cached via `tools._views_maps`).

- System views (Inbox, Closed, Snoozed, Unassigned, All, Trash, Spam) are
  built-in on every Gorgias account and identified by their canonical name.
- Channel views are auto-created per inbound channel and identified by a
  name pattern.
- User views are hand-built saved filters; exposed via `list_views()` but
  not alias-resolved.
"""

from typing import Any, Callable, Dict, List, Optional, Tuple

# Alias → exact Gorgias "system" view name (stable across all accounts)
SYSTEM_ALIASES: Dict[str, str] = {
    "open": "Inbox",
    "closed": "Closed",
    "snoozed": "Snoozed",
    "unassigned": "Unassigned",
    "all": "All",
    "trash": "Trash",
    "spam": "Spam",
}

# Alias → (matcher) for channel views. Matchers run against the view name
# (lowercased). First match wins. Patterns are intentionally loose to
# survive varying account-specific names (e.g. Chat widget subtitles,
# support inbox addresses, help-center branding).
_CHANNEL_MATCHERS: List[Tuple[str, Callable[[str], bool]]] = [
    ("email", lambda n: "@" in n and "impulse" in n),
    ("contact_form", lambda n: "contact form" in n),
    ("chat", lambda n: n.startswith("chat")),
    ("help_center", lambda n: "help center" in n),
]


def build_maps(raw_views: List[Dict[str, Any]]) -> Dict[str, Dict[str, int]]:
    """Split a raw /api/views response into system / channel / user maps.

    Args:
        raw_views: the `data` array from `GET /api/views`.

    Returns:
        `{"system": {alias: id}, "channel": {alias: id}, "user": {name: id}}`.
    """
    system: Dict[str, int] = {}
    channel: Dict[str, int] = {}
    user: Dict[str, int] = {}

    system_by_name = {
        v.get("name"): v.get("id")
        for v in raw_views
        if v.get("category") == "system" and v.get("id") is not None
    }
    for alias, canonical in SYSTEM_ALIASES.items():
        if canonical in system_by_name:
            system[alias] = system_by_name[canonical]

    for v in raw_views:
        category = v.get("category")
        name = (v.get("name") or "").strip()
        vid = v.get("id")
        if vid is None:
            continue
        if category == "system":
            continue
        if category == "user":
            user[name] = vid
            continue
        # Channel or uncategorized views → match by pattern
        lower = name.lower()
        for alias, matcher in _CHANNEL_MATCHERS:
            if alias in channel:
                continue
            if matcher(lower):
                channel[alias] = vid
                break

    return {"system": system, "channel": channel, "user": user}


def resolve_view_id(
    maps: Dict[str, Dict[str, int]],
    status: Optional[str] = None,
    channel: Optional[str] = None,
    view_id: Optional[int] = None,
) -> Optional[int]:
    """Resolve the effective view_id from user intent + the live views map.

    Precedence: explicit `view_id` > `channel` > `status`.
    Returns None when no filter is requested (caller should hit /tickets).
    Raises ValueError on unknown status/channel alias.
    """
    if view_id is not None:
        return int(view_id)
    if channel:
        key = channel.lower()
        channel_map = maps.get("channel", {})
        if key not in channel_map:
            raise ValueError(
                f"Unknown channel '{channel}'. Known: {sorted(channel_map)}"
            )
        return channel_map[key]
    if status:
        key = status.lower()
        system_map = maps.get("system", {})
        if key not in system_map:
            raise ValueError(
                f"Unknown status '{status}'. Known: {sorted(system_map)}"
            )
        return system_map[key]
    return None
