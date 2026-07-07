from tests.utils import auth_headers, create_payload

BASE = "/api/v1/workspaces/ws_1/approval-requests"


async def _create(client, *, reviewers=None, idempotency_key="k1"):
    resp = await client.post(
        BASE,
        json=create_payload(reviewer_user_ids=reviewers or ["usr_1", "usr_2"]),
        headers=auth_headers(idempotency_key=idempotency_key),
    )
    return resp.json()


async def test_approve_sets_status_and_decision(client):
    req = await _create(client)
    resp = await client.post(
        f"{BASE}/{req['id']}/approve",
        json={"comment": "Approved"},
        headers=auth_headers(user_id="usr_1"),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "approved"
    assert body["decision_by"] == "usr_1"
    assert body["decision_comment"] == "Approved"
    assert body["decided_at"] is not None


async def test_reject_uses_reason(client):
    req = await _create(client)
    resp = await client.post(
        f"{BASE}/{req['id']}/reject",
        json={"reason": "Brand tone is wrong"},
        headers=auth_headers(user_id="usr_2"),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "rejected"
    assert body["decision_comment"] == "Brand tone is wrong"


async def test_cancel_uses_reason(client):
    req = await _create(client)
    resp = await client.post(
        f"{BASE}/{req['id']}/cancel",
        json={"reason": "Draft was removed"},
        headers=auth_headers(user_id="usr_1"),
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "cancelled"


async def test_decision_appends_event(client):
    req = await _create(client)
    body = (
        await client.post(
            f"{BASE}/{req['id']}/approve",
            json={"comment": "ok"},
            headers=auth_headers(user_id="usr_1"),
        )
    ).json()
    event_types = [e["event_type"] for e in body["events"]]
    assert event_types == ["created", "approved"]


async def test_non_reviewer_cannot_decide(client):
    req = await _create(client, reviewers=["usr_1", "usr_2"])
    
    resp = await client.post(
        f"{BASE}/{req['id']}/approve",
        json={"comment": "sneaky"},
        headers=auth_headers(user_id="usr_9"),
    )
    assert resp.status_code == 403


async def test_decide_requires_decide_action(client):
    req = await _create(client)
    resp = await client.post(
        f"{BASE}/{req['id']}/approve",
        json={"comment": "ok"},
        headers=auth_headers(user_id="usr_1", actions=("approval:read",)),
    )
    assert resp.status_code == 403


async def test_cannot_transition_after_final_decision(client):
    req = await _create(client)
    approve = await client.post(
        f"{BASE}/{req['id']}/approve",
        json={"comment": "ok"},
        headers=auth_headers(user_id="usr_1"),
    )
    assert approve.status_code == 200

    resp = await client.post(
        f"{BASE}/{req['id']}/reject",
        json={"reason": "changed my mind"},
        headers=auth_headers(user_id="usr_1"),
    )
    assert resp.status_code == 409


async def test_decide_missing_request_is_404(client):
    resp = await client.post(
        f"{BASE}/00000000-0000-0000-0000-000000000000/approve",
        json={"comment": "ok"},
        headers=auth_headers(user_id="usr_1"),
    )
    assert resp.status_code == 404
