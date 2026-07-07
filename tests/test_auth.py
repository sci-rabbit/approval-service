from tests.utils import auth_headers, create_payload

BASE = "/api/v1/workspaces/ws_1/approval-requests"


async def test_missing_auth_headers_is_401(client):
    resp = await client.get(BASE)
    assert resp.status_code == 401


async def test_unknown_action_value_is_401(client):
    resp = await client.get(
        BASE, headers=auth_headers(actions=("approval:bogus",))
    )
    assert resp.status_code == 401


async def test_action_not_granted_is_403(client):
    resp = await client.post(
        BASE,
        json=create_payload(),
        headers=auth_headers(
            actions=("approval:read",), idempotency_key="k1"
        ),
    )
    assert resp.status_code == 403


async def test_workspace_mismatch_is_403(client):
    resp = await client.get(
        "/api/v1/workspaces/ws_2/approval-requests",
        headers=auth_headers(workspace_id="ws_1"),
    )
    assert resp.status_code == 403
