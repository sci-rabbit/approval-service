from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from enums.approval_status_enum import ApprovalStatus
from enums.source_type_enum import SourceType
from schemas.approval_event_schemas import ApprovalEventResponse
from schemas.approval_reviewer_schemas import ReviewerResponse


class CreateApprovalRequestSchema(BaseModel):
    source_type: SourceType
    source_id: str
    title: str
    description: str | None = None
    reviewer_user_ids: list[str]


class ApprovalRequestResponse(BaseModel):
    id: UUID

    workspace_id: str

    source_type: SourceType
    source_id: str

    title: str
    description: str | None

    status: ApprovalStatus

    created_by: str
    decision_by: str | None
    decision_comment: str | None

    created_at: datetime
    decided_at: datetime | None

    reviewers: list[ReviewerResponse]
    events: list[ApprovalEventResponse]

    model_config = ConfigDict(from_attributes=True)


class ApprovalRequestListResponse(BaseModel):
    id: UUID

    workspace_id: str

    source_type: SourceType
    source_id: str

    title: str
    description: str | None

    status: ApprovalStatus

    created_by: str
    created_at: datetime

    reviewers: list[ReviewerResponse]

    model_config = ConfigDict(from_attributes=True)




class ApproveRequestSchema(BaseModel):
    comment: str | None = None


class RejectRequestSchema(BaseModel):
    reason: str


class CancelRequestSchema(BaseModel):
    reason: str
