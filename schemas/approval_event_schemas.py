from datetime import datetime

from pydantic import BaseModel, ConfigDict

from enums.approval_event_type_enum import ApprovalEventType


class ApprovalEventResponse(BaseModel):
    event_type: ApprovalEventType
    actor_user_id: str
    message: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
