from models.idempotency_key import IdempotencyKey
from repositories.base_repository import AsyncRepository


class IdempotencyKeyRepository(AsyncRepository):
    model = IdempotencyKey
