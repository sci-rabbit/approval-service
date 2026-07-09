from dataclasses import dataclass

from enums.source_type_enum import SourceType
from schemas.approval_request_schemas import CreateApprovalRequestSchema


@dataclass(frozen=True, slots=True)
class CreateApprovalRequestDto:
    workspace_id: str
    actor_user_id: str

    source_type: SourceType
    source_id: str

    title: str
    description: str | None

    reviewer_user_ids: list[str]

    @classmethod
    def from_schema(
        cls,
        schema: CreateApprovalRequestSchema,
        workspace_id: str,
        actor_user_id: str,
    ) -> "CreateApprovalRequestDto":
        return cls(
            workspace_id=workspace_id,
            actor_user_id=actor_user_id,
            source_type=schema.source_type,
            source_id=schema.source_id,
            title=schema.title,
            description=schema.description,
            reviewer_user_ids=schema.reviewer_user_ids,
        )
    
    def to_request_fields(self) -> dict:
        return {
            "workspace_id": self.workspace_id,
            "source_type": self.source_type,
            "source_id": self.source_id,
            "title": self.title,
            "description": self.description,
            "created_by": self.actor_user_id,
        }
