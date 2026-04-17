import time

import pytest
import responses

from gorgias_mcp import client as client_module
from gorgias_mcp import tools
from gorgias_mcp.cache import ttl_cache


BASE = "https://impulse-nutrition-vitavea.gorgias.com/api"

STUB_VIEWS = [
    {"id": 33360, "name": "Inbox", "category": "system"},
    {"id": 33364, "name": "Closed", "category": "system"},
    {"id": 33363, "name": "Snoozed", "category": "system"},
    {"id": 33361, "name": "Unassigned", "category": "system"},
    {"id": 33362, "name": "All", "category": "system"},
    {"id": 44348, "name": "contact@impulse-nutrition.fr", "category": None},
    {"id": 45597, "name": "Chat - Comment pouvons-nous vous aider ?", "category": None},
]


def _register_views():
    """Register the /views stub, callable any number of times."""
    responses.add(
        responses.GET,
        f"{BASE}/views",
        json={"data": STUB_VIEWS},
        status=200,
    )


@pytest.fixture(autouse=True)
def _reset_client(monkeypatch):
    """Reset client + caches before each test so stubs apply cleanly."""
    monkeypatch.setenv("GORGIAS_DOMAIN", "impulse-nutrition-vitavea")
    monkeypatch.setenv("GORGIAS_EMAIL", "test@example.com")
    monkeypatch.setenv("GORGIAS_API_KEY", "test_key")
    client_module.GORGIAS_DOMAIN = "impulse-nutrition-vitavea"
    client_module.GORGIAS_EMAIL = "test@example.com"
    client_module.GORGIAS_API_KEY = "test_key"
    client_module.BASE_URL = BASE
    client_module.reset_client()
    tools._cached_users.invalidate()  # type: ignore[attr-defined]
    tools._views_maps.invalidate()  # type: ignore[attr-defined]
    yield


@responses.activate
def test_list_tickets_with_status_uses_view_endpoint():
    _register_views()
    responses.add(
        responses.GET,
        f"{BASE}/views/33360/items",
        json={"data": [{"id": 1, "subject": "S", "customer": {}, "tags": []}], "meta": {}},
        status=200,
    )
    out = tools.list_tickets(status="open", limit=5)
    assert out["view_id"] == 33360
    assert len(out["tickets"]) == 1


@responses.activate
def test_list_tickets_no_filter_uses_tickets_endpoint():
    # No views fetch needed when no filter is requested
    responses.add(
        responses.GET,
        f"{BASE}/tickets",
        json={"data": [{"id": 2, "customer": {}, "tags": []}], "meta": {"total_resources": 99}},
        status=200,
    )
    out = tools.list_tickets(limit=5)
    assert out["view_id"] is None
    assert out["total"] == 99


@responses.activate
def test_list_tickets_channel_resolves_to_view():
    _register_views()
    responses.add(
        responses.GET,
        f"{BASE}/views/44348/items",
        json={"data": [], "meta": {}},
        status=200,
    )
    out = tools.list_tickets(channel="email", limit=5)
    assert out["view_id"] == 44348


@responses.activate
def test_list_views_reflects_live_api():
    _register_views()
    out = tools.list_views()
    assert out["system"]["open"] == 33360
    assert out["system"]["closed"] == 33364
    assert out["channel"]["email"] == 44348
    assert out["channel"]["chat"] == 45597


@responses.activate
def test_get_ticket_stats_caps_pages():
    _register_views()
    next_url = "/api/views/X/items/?direction=next&cursor=eyJjIjoibmV4dCJ9"
    full_page = {
        "data": [{"id": i, "customer": {}, "tags": []} for i in range(100)],
        "meta": {"next_items": next_url},
    }
    for status_view in [33360, 33364, 33363, 33361]:
        for _ in range(tools.STATS_MAX_PAGES):
            responses.add(
                responses.GET,
                f"{BASE}/views/{status_view}/items",
                json=full_page,
                status=200,
            )
    out = tools.get_ticket_stats()
    assert out["open"] == {"count": 500, "capped": True}
    assert out["closed"]["capped"] is True


@responses.activate
def test_get_ticket_stats_under_one_page_not_capped():
    _register_views()
    page = {
        "data": [{"id": 1, "customer": {}, "tags": []}],
        "meta": {"next_items": None},
    }
    for status_view in [33360, 33364, 33363, 33361]:
        responses.add(
            responses.GET,
            f"{BASE}/views/{status_view}/items",
            json=page,
            status=200,
        )
    out = tools.get_ticket_stats()
    assert out["open"] == {"count": 1, "capped": False}


@responses.activate
def test_list_tags_returns_dict_wrapped():
    responses.add(
        responses.GET,
        f"{BASE}/tags",
        json={"data": [{"id": 1, "name": "urgent"}, {"id": 2, "name": "WAX"}]},
        status=200,
    )
    out = tools.list_tags()
    assert out == {"tags": [{"id": 1, "name": "urgent"}, {"id": 2, "name": "WAX"}]}


@responses.activate
def test_reply_contact_form_uses_email_channel():
    """Reply to a contact_form ticket must switch channel to email in payload."""
    responses.add(
        responses.GET,
        f"{BASE}/tickets/7777",
        json={
            "id": 7777,
            "channel": "contact_form",
            "subject": "Question",
            "customer": {"id": 42, "name": "Jane", "email": "jane@example.com"},
        },
        status=200,
    )
    captured = {}

    def _capture(request):
        import json as _json
        captured["body"] = _json.loads(request.body)
        return (200, {}, _json.dumps({"id": 999}))

    responses.add_callback(
        responses.POST,
        f"{BASE}/tickets/7777/messages",
        callback=_capture,
    )

    out = tools.reply_to_ticket(ticket_id=7777, body_text="Hello")
    assert out["message_id"] == 999
    assert captured["body"]["channel"] == "email"  # mapped from contact_form
    assert captured["body"]["receiver"]["email"] == "jane@example.com"


@responses.activate
def test_reply_email_keeps_email_channel():
    responses.add(
        responses.GET,
        f"{BASE}/tickets/8888",
        json={
            "id": 8888,
            "channel": "email",
            "subject": "RE: order",
            "customer": {"id": 42, "email": "jane@example.com"},
        },
        status=200,
    )
    captured = {}

    def _capture(request):
        import json as _json
        captured["body"] = _json.loads(request.body)
        return (200, {}, _json.dumps({"id": 1000}))

    responses.add_callback(responses.POST, f"{BASE}/tickets/8888/messages", callback=_capture)
    tools.reply_to_ticket(ticket_id=8888, body_text="Hi")
    assert captured["body"]["channel"] == "email"


@responses.activate
def test_assign_ticket_caches_users():
    responses.add(
        responses.GET,
        f"{BASE}/users",
        json={"data": [{"id": 7, "email": "achabrat@havea.com"}]},
        status=200,
    )
    responses.add(responses.PUT, f"{BASE}/tickets/100", json={}, status=200)
    responses.add(responses.PUT, f"{BASE}/tickets/101", json={}, status=200)

    out1 = tools.assign_ticket(ticket_id=100)
    out2 = tools.assign_ticket(ticket_id=101)
    assert out1["assigned_to"]["id"] == 7
    assert out2["assigned_to"]["id"] == 7
    user_calls = [c for c in responses.calls if c.request.url.startswith(f"{BASE}/users")]
    assert len(user_calls) == 1


@responses.activate
def test_views_maps_cached():
    _register_views()
    # First call populates cache
    tools._views_maps()
    # Second call should hit cache — no extra /views request
    tools._views_maps()
    views_calls = [c for c in responses.calls if c.request.url.startswith(f"{BASE}/views")]
    assert len(views_calls) == 1


def test_ttl_cache_invalidation_works():
    counter = {"n": 0}

    @ttl_cache(seconds=60)
    def f(x):
        counter["n"] += 1
        return x * 2

    assert f(2) == 4
    assert f(2) == 4
    assert counter["n"] == 1
    f.invalidate()
    assert f(2) == 4
    assert counter["n"] == 2


def test_ttl_cache_expires():
    counter = {"n": 0}

    @ttl_cache(seconds=0.05)
    def f():
        counter["n"] += 1
        return counter["n"]

    f()
    f()
    time.sleep(0.1)
    f()
    assert counter["n"] == 2
