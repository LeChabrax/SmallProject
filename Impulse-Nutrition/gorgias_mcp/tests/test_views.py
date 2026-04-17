import pytest

from gorgias_mcp.views import SYSTEM_ALIASES, build_maps, resolve_view_id


RAW_VIEWS = [
    {"id": 10, "name": "Inbox", "category": "system"},
    {"id": 11, "name": "Closed", "category": "system"},
    {"id": 12, "name": "Snoozed", "category": "system"},
    {"id": 13, "name": "Unassigned", "category": "system"},
    {"id": 14, "name": "All", "category": "system"},
    {"id": 20, "name": "contact@impulse-nutrition.fr", "category": None},
    {"id": 21, "name": "Contact Form - Nous contacter", "category": None},
    {"id": 22, "name": "Chat - Comment pouvons-nous vous aider ?", "category": None},
    {"id": 23, "name": "Help Center - impulse-nutrition", "category": None},
    {"id": 30, "name": "Critical", "category": "user"},
    {"id": 31, "name": "To review", "category": "user"},
]


def test_build_maps_system():
    m = build_maps(RAW_VIEWS)
    assert m["system"]["open"] == 10
    assert m["system"]["closed"] == 11
    assert m["system"]["snoozed"] == 12
    assert m["system"]["unassigned"] == 13
    assert m["system"]["all"] == 14


def test_build_maps_channel():
    m = build_maps(RAW_VIEWS)
    assert m["channel"]["email"] == 20
    assert m["channel"]["contact_form"] == 21
    assert m["channel"]["chat"] == 22
    assert m["channel"]["help_center"] == 23


def test_build_maps_user():
    m = build_maps(RAW_VIEWS)
    assert m["user"]["Critical"] == 30
    assert m["user"]["To review"] == 31


def test_build_maps_missing_system_gracefully():
    sparse = [{"id": 1, "name": "Inbox", "category": "system"}]
    m = build_maps(sparse)
    assert m["system"] == {"open": 1}
    assert m["channel"] == {}


def test_build_maps_empty():
    m = build_maps([])
    assert m == {"system": {}, "channel": {}, "user": {}}


def test_resolve_no_filter_returns_none():
    m = build_maps(RAW_VIEWS)
    assert resolve_view_id(m) is None


def test_resolve_status_open():
    m = build_maps(RAW_VIEWS)
    assert resolve_view_id(m, status="open") == 10


def test_resolve_channel_email():
    m = build_maps(RAW_VIEWS)
    assert resolve_view_id(m, channel="email") == 20


def test_resolve_view_id_overrides_other_filters():
    m = build_maps(RAW_VIEWS)
    assert resolve_view_id(m, status="open", channel="email", view_id=999) == 999


def test_resolve_channel_overrides_status():
    m = build_maps(RAW_VIEWS)
    assert resolve_view_id(m, status="open", channel="chat") == 22


def test_resolve_unknown_status_raises():
    m = build_maps(RAW_VIEWS)
    with pytest.raises(ValueError):
        resolve_view_id(m, status="bogus")


def test_resolve_unknown_channel_raises():
    m = build_maps(RAW_VIEWS)
    with pytest.raises(ValueError):
        resolve_view_id(m, channel="bogus")


def test_system_aliases_stable():
    assert SYSTEM_ALIASES["open"] == "Inbox"
    assert SYSTEM_ALIASES["closed"] == "Closed"
