from models.approval_event import ApprovalEvent
from repositories.base_repository import AsyncRepository


class ApprovalEventRepository(AsyncRepository):
    model = ApprovalEvent
