from gorgias_mcp.slim import (
    extract_customer_email,
    slim_customer,
    slim_message,
    slim_ticket,
)


def _ticket_fixture():
    return {
        "id": 12345,
        "subject": "Hello",
        "status": "open",
        "channel": "email",
        "customer": {"id": 99, "name": "Alice", "email": "a@example.com"},
        "assignee_user": {"id": 7, "name": "Bob"},
        "created_datetime": "2026-04-01T00:00:00Z",
        "updated_datetime": "2026-04-15T00:00:00Z",
        "tags": [{"id": 1, "name": "urgent"}, {"id": 2, "name": "WAX"}],
        "messages_count": 3,
        "extra_field": "should_be_dropped",
    }


def test_slim_ticket_keeps_essentials():
    s = slim_ticket(_ticket_fixture())
    assert s["id"] == 12345
    assert s["customer"] == {"id": 99, "name": "Alice", "email": "a@example.com"}
    assert s["assignee"] == {"id": 7, "name": "Bob"}
    assert s["tags"] == ["urgent", "WAX"]
    assert s["messages_count"] == 3
    assert "extra_field" not in s


def test_slim_ticket_no_assignee():
    t = _ticket_fixture()
    t["assignee_user"] = None
    assert slim_ticket(t)["assignee"] is None


def test_slim_message_truncates_by_default():
    m = {"body_text": "x" * 1000, "source": {"from": {"name": "C"}}}
    assert slim_message(m)["body_text"].endswith("...")
    assert len(slim_message(m)["body_text"]) == 603


def test_slim_message_full_body():
    m = {"body_text": "x" * 1000, "source": {"from": {"name": "C"}}}
    assert slim_message(m, full_body=True)["body_text"] == "x" * 1000


def test_slim_customer_includes_nb_tickets_when_present():
    c = {"id": 1, "name": "n", "email": "e", "nb_tickets": 5}
    assert slim_customer(c)["nb_tickets"] == 5


def test_extract_customer_email_prefers_top_level():
    t = {"customer": {"email": "top@example.com", "channels": [{"type": "email", "address": "ch@example.com"}]}}
    assert extract_customer_email(t) == "top@example.com"


def test_extract_customer_email_falls_back_to_channels():
    t = {"customer": {"channels": [{"type": "phone", "address": "+33"}, {"type": "email", "address": "ch@example.com"}]}}
    assert extract_customer_email(t) == "ch@example.com"


def test_extract_customer_email_returns_empty_when_missing():
    t = {"customer": {}}
    assert extract_customer_email(t) == ""
