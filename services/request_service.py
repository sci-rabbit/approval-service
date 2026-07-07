import uuid
from dataclasses import asdict

from dto.approval_request_dto import CreateApprovalRequestDto

from enums.approval_event_type_enum import ApprovalEventType
from enums.outbox_event_enum import OutboxEventType

from exceptions.request_exc import RequestNotFound
from models.approval_request import ApprovalRequest

from repositories.approval_event_repository import ApprovalEventRepository
from repositories.approval_request_repository import ApprovalRequestRepository
from repositories.approval_reviewer_repository import ApprovalReviewerRepository
from repositories.idempotency_repository import IdempotencyKeyRepository
from repositories.outbox_event_repository import OutboxEventRepository


class RequestService:
    def __init__(self, session):
        self.session = session
        self.request_repo = ApprovalRequestRepository(session=session)
        self.event_repo = ApprovalEventRepository(session=session)
        self.outbox_event_repo = OutboxEventRepository(session=session)
        self.idempotency_repo = IdempotencyKeyRepository(session=session)
        self.reviewer_repo = ApprovalReviewerRepository(session=session)

    async def create(
        self,
        dto: CreateApprovalRequestDto,
        idempotency_key: str,
    ) -> ApprovalRequest:
        existing = await self.idempotency_repo.get_one_by(key=idempotency_key)

        if existing:
            return await self.request_repo.get_details(
                request_id=existing.request_id,
                workspace_id=dto.workspace_id,
            )

        data = asdict(dto)

        reviewer_user_ids = data.pop("reviewer_user_ids")
        data.pop("actor_user_id")

        request = await self.request_repo.create(
            **data,
            created_by=dto.actor_user_id,
        )

        await self.reviewer_repo.create_many(
            request=request,
            reviewer_user_ids=reviewer_user_ids,
        )

        await self.idempotency_repo.create(
            key=idempotency_key,
            workspace_id=request.workspace_id,
            request_id=request.id,
        )

        await self.event_repo.create(
            request=request,
            actor_user_id=dto.actor_user_id,
            event_type=ApprovalEventType.created,
        )

        await self.outbox_event_repo.create(
            aggregate_id=request.id,
            event_type=OutboxEventType.REQUEST_CREATED,
            payload={
                "requestId": str(request.id),
                "workspaceId": request.workspace_id,
            },
        )

        return await self.request_repo.get_details(
            request_id=request.id,
            workspace_id=request.workspace_id,
        )

    async def get_requests_by_workspace_id(
        self,
        workspace_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> list[ApprovalRequest]:
        return await self.request_repo.list_by_workspace(
            workspace_id=workspace_id,
            limit=limit,
            offset=offset,
        )

    async def get_request_by_id(
        self,
        request_id: uuid.UUID,
        workspace_id: str,
    ) -> ApprovalRequest:
        request = await self.request_repo.get_details(
            request_id=request_id,
            workspace_id=workspace_id,
        )

        if request is None:
            raise RequestNotFound()

        return request


