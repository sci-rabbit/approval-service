from models.outbox_event import OutboxEvent
from repositories.base_repository import AsyncRepository


class OutboxEventRepository(AsyncRepository):
    model = OutboxEvent
