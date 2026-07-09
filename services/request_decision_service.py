from datetime import datetime, timezone

from dto.decision_dto import ApproveDto, DecisionDto, RejectDto, CancelDto
from enums.approval_event_type_enum import ApprovalEventType
from enums.approval_status_enum import ApprovalStatus
from exceptions.request_exc import (
    RequestNotFound,
    RequestAlreadyFinalized,
    PermissionDenied,
)
from models.approval_request import ApprovalRequest
from repositories.approval_event_repository import ApprovalEventRepository
from repositories.approval_request_repository import ApprovalRequestRepository
from repositories.idempotency_repository import IdempotencyKeyRepository
from repositories.outbox_event_repository import OutboxEventRepository


class RequestDecisionService:
    def __init__(self, session):
        self.request_repo = ApprovalRequestRepository(session=session)
        self.event_repo = ApprovalEventRepository(session=session)
        self.outbox_event_repo = OutboxEventRepository(session=session)
        self.idempotency_repo = IdempotencyKeyRepository(session=session)

    async def _decide(
        self,
        dto: DecisionDto,
        *,
        status: ApprovalStatus,
        event_type: ApprovalEventType,
    ) -> ApprovalRequest:
        request = await self.request_repo.get_details(
            request_id=dto.request_id,
            workspace_id=dto.workspace_id,
        )

        if request is None:
            raise RequestNotFound()

        if request.status != ApprovalStatus.pending:
            raise RequestAlreadyFinalized()

        if dto.actor_user_id not in {
            reviewer.reviewer_user_id for reviewer in request.reviewers
        }:
            raise PermissionDenied()

        await self.request_repo.update(
            request,
            {
                "status": status,
                "decision_by": dto.actor_user_id,
                "decision_comment": dto.message,
                "decided_at": datetime.now(timezone.utc),
            },
        )

        await self.event_repo.create(
            request=request,
            actor_user_id=dto.actor_user_id,
            event_type=event_type,
            message=dto.message,
        )

        await self.outbox_event_repo.create(
            aggregate_id=request.id,
            event_type=f"ApprovalRequest{event_type.value.title()}",
            payload={
                "requestId": str(request.id),
                "workspaceId": request.workspace_id,
                "status": status.value,
                "actorUserId": dto.actor_user_id,
            },
        )

        return request

    async def approve(self, dto: ApproveDto) -> ApprovalRequest:
        return await self._decide(
            dto=dto,
            status=ApprovalStatus.approved,
            event_type=ApprovalEventType.approved,
        )

    async def reject(self, dto: RejectDto) -> ApprovalRequest:
        return await self._decide(
            dto=dto,
            status=ApprovalStatus.rejected,
            event_type=ApprovalEventType.rejected,
        )

    async def cancel(self, dto: CancelDto) -> ApprovalRequest:
        return await self._decide(
            dto=dto,
            status=ApprovalStatus.cancelled,
            event_type=ApprovalEventType.cancelled,
        )
