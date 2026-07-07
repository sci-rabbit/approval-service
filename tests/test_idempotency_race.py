from repositories.idempotency_repository import IdempotencyKeyRepository
from tests.utils import auth_headers, create_payload

BASE = "/api/v1/workspaces/ws_1/approval-requests"


async def test_idempotency_race_returns_409(client, monkeypatch):
    first = await client.post(
        BASE, json=create_payload(), headers=auth_headers(idempotency_key="dup")
    )
    assert first.status_code == 200

    async def fake_get_one_by(self, **filters):
        return None

    monkeypatch.setattr(IdempotencyKeyRepository, "get_one_by", fake_get_one_by)

    second = await client.post(
        BASE, json=create_payload(), headers=auth_headers(idempotency_key="dup")
    )
    assert second.status_code == 409
