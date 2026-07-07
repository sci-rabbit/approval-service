from tests.utils import auth_headers, create_payload

BASE = "/api/v1/workspaces/ws_1/approval-requests"

ALLOWED_RESPONSE_KEYS = {
    "id",
    "workspace_id",
    "source_type",
    "source_id",
    "title",
    "description",
    "status",
    "created_by",
    "decision_by",
    "decision_comment",
    "created_at",
    "decided_at",
    "reviewers",
    "events",
}


async def _create(client, *, idempotency_key: str = "k1", **kwargs):
    return await client.post(
        BASE,
        json=create_payload(**kwargs),
        headers=auth_headers(idempotency_key=idempotency_key),
    )


async def test_create_returns_pending_request(client):
    resp = await _create(client)
    assert resp.status_code == 200
    body = resp.json()

    assert body["status"] == "pending"
    assert body["workspace_id"] == "ws_1"
    assert body["created_by"] == "usr_1"
    assert body["source_type"] == "publication"
    assert body["decision_by"] is None
    assert {r["reviewer_user_id"] for r in body["reviewers"]} == {"usr_1", "usr_2"}


async def test_create_records_created_event(client):
    body = (await _create(client)).json()
    event_types = [e["event_type"] for e in body["events"]]
    assert event_types == ["created"]


async def test_create_response_has_no_unexpected_fields(client):
    body = (await _create(client)).json()
    assert set(body) <= ALLOWED_RESPONSE_KEYS


async def test_list_returns_created_request(client):
    await _create(client)
    resp = await client.get(BASE, headers=auth_headers())
    assert resp.status_code == 200
    assert len(resp.json()) == 1


async def test_get_one_by_id(client):
    created = (await _create(client)).json()
    resp = await client.get(f"{BASE}/{created['id']}", headers=auth_headers())
    assert resp.status_code == 200
    assert resp.json()["id"] == created["id"]


async def test_get_missing_request_is_404(client):
    resp = await client.get(
        f"{BASE}/00000000-0000-0000-0000-000000000000",
        headers=auth_headers(),
    )
    assert resp.status_code == 404


async def test_idempotent_create_does_not_duplicate(client):
    first = (await _create(client, idempotency_key="same-key")).json()
    second = (await _create(client, idempotency_key="same-key")).json()

    assert first["id"] == second["id"]

    listed = (await client.get(BASE, headers=auth_headers())).json()
    assert len(listed) == 1


async def test_different_idempotency_keys_create_two(client):
    await _create(client, idempotency_key="k1")
    await _create(client, idempotency_key="k2")

    listed = (await client.get(BASE, headers=auth_headers())).json()
    assert len(listed) == 2


async def test_workspace_isolation_on_list(client):
    await _create(client)

    resp = await client.get(
        "/api/v1/workspaces/ws_2/approval-requests",
        headers=auth_headers(workspace_id="ws_2", user_id="usr_9"),
    )
    assert resp.status_code == 200
    assert resp.json() == []


async def test_workspace_isolation_on_get_one(client):
    created = (await _create(client)).json()

    resp = await client.get(
        f"/api/v1/workspaces/ws_2/approval-requests/{created['id']}",
        headers=auth_headers(workspace_id="ws_2", user_id="usr_9"),
    )
    assert resp.status_code == 404
