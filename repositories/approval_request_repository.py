from sqlalchemy import select
from sqlalchemy.orm import selectinload

from models.approval_request import ApprovalRequest
from repositories.base_repository import AsyncRepository


class ApprovalRequestRepository(AsyncRepository):
    model = ApprovalRequest

    async def list_by_workspace(
        self,
        workspace_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> list[ApprovalRequest]:
        stmt = (
            select(ApprovalRequest)
            .where(ApprovalRequest.workspace_id == workspace_id)
            .options(selectinload(ApprovalRequest.reviewers))
            .order_by(ApprovalRequest.created_at.desc())
            .limit(min(limit, 50))
            .offset(offset)
        )

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_details(
        self,
        request_id,
        workspace_id,
    ) -> ApprovalRequest:
        stmt = (
            select(ApprovalRequest)
            .where(
                ApprovalRequest.id == request_id,
                ApprovalRequest.workspace_id == workspace_id,
            )
            .options(
                selectinload(ApprovalRequest.reviewers),
                selectinload(ApprovalRequest.events),
            )
        )

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
