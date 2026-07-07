from typing import Annotated, List
from uuid import UUID

from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth import require
from core.database import get_rw_session, get_ro_session
from dto.approval_request_dto import CreateApprovalRequestDto
from dto.auth_context_dto import AuthContextDto
from dto.decision_dto import ApproveDto, RejectDto, CancelDto
from enums.auth_action_enum import AuthAction
from schemas.approval_request_schemas import (
    CreateApprovalRequestSchema,
    ApprovalRequestResponse,
    ApprovalRequestListResponse,
    ApproveRequestSchema,
    RejectRequestSchema,
    CancelRequestSchema,
)
from services.request_decision_service import RequestDecisionService
from services.request_service import RequestService

router = APIRouter(prefix="/workspaces", tags=["Workspaces"])


@router.post("/{workspace_id}/approval-requests")
async def create_approval_request(
    workspace_id: str,
    body: CreateApprovalRequestSchema,
    session: Annotated[AsyncSession, Depends(get_rw_session)],
    auth: Annotated[AuthContextDto, Depends(require(AuthAction.create))],
    idempotency_key: Annotated[str, Header(alias="Idempotency-Key")],
) -> ApprovalRequestResponse:
    service = RequestService(session=session)
    approval_request = await service.create(
        dto=CreateApprovalRequestDto.from_schema(
            schema=body,
            workspace_id=workspace_id,
            actor_user_id=auth.user_id,
        ),
        idempotency_key=idempotency_key,
    )
    return ApprovalRequestResponse.model_validate(approval_request)


@router.get("/{workspace_id}/approval-requests")
async def get_approval_requests(
    workspace_id: str,
    session: Annotated[AsyncSession, Depends(get_ro_session)],
    auth: Annotated[AuthContextDto, Depends(require(AuthAction.read))],
) -> List[ApprovalRequestListResponse]:
    service = RequestService(session=session)
    approval_request_list = await service.get_requests_by_workspace_id(
        workspace_id=workspace_id
    )
    return [
        ApprovalRequestListResponse.model_validate(approval_request)
        for approval_request in approval_request_list
    ]


@router.get("/{workspace_id}/approval-requests/{request_id}")
async def get_approval_request(
    workspace_id: str,
    request_id: UUID,
    session: Annotated[AsyncSession, Depends(get_ro_session)],
    auth: Annotated[AuthContextDto, Depends(require(AuthAction.read))],
) -> ApprovalRequestResponse:
    service = RequestService(session=session)
    approval_request = await service.get_request_by_id(
        request_id=request_id,
        workspace_id=workspace_id,
    )
    return ApprovalRequestResponse.model_validate(approval_request)


@router.post("/{workspace_id}/approval-requests/{request_id}/approve")
async def approve_request(
    workspace_id: str,
    request_id: UUID,
    body: ApproveRequestSchema,
    session: Annotated[AsyncSession, Depends(get_rw_session)],
    auth: Annotated[AuthContextDto, Depends(require(AuthAction.decide))],
) -> ApprovalRequestResponse:
    service = RequestDecisionService(session=session)
    approval_request = await service.approve(
        ApproveDto(
            workspace_id=workspace_id,
            request_id=request_id,
            actor_user_id=auth.user_id,
            message=body.comment,
        )
    )
    return ApprovalRequestResponse.model_validate(approval_request)


@router.post("/{workspace_id}/approval-requests/{request_id}/reject")
async def reject_request(
    workspace_id: str,
    request_id: UUID,
    body: RejectRequestSchema,
    session: Annotated[AsyncSession, Depends(get_rw_session)],
    auth: Annotated[AuthContextDto, Depends(require(AuthAction.decide))],
) -> ApprovalRequestResponse:
    service = RequestDecisionService(session=session)
    approval_request = await service.reject(
        RejectDto(
            workspace_id=workspace_id,
            request_id=request_id,
            actor_user_id=auth.user_id,
            message=body.reason,
        )
    )
    return ApprovalRequestResponse.model_validate(approval_request)


@router.post("/{workspace_id}/approval-requests/{request_id}/cancel")
async def cancel_request(
    workspace_id: str,
    request_id: UUID,
    body: CancelRequestSchema,
    session: Annotated[AsyncSession, Depends(get_rw_session)],
    auth: Annotated[AuthContextDto, Depends(require(AuthAction.cancel))],
) -> ApprovalRequestResponse:
    service = RequestDecisionService(session=session)
    approval_request = await service.cancel(
        CancelDto(
            workspace_id=workspace_id,
            request_id=request_id,
            actor_user_id=auth.user_id,
            message=body.reason,
        )
    )
    return ApprovalRequestResponse.model_validate(approval_request)
