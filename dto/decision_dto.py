from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class DecisionDto:
    workspace_id: str
    actor_user_id: str
    request_id: UUID
    message: str | None


@dataclass(frozen=True)
class ApproveDto(DecisionDto):
    pass

@dataclass(frozen=True)
class RejectDto(DecisionDto):
    pass


@dataclass(frozen=True)
class CancelDto(DecisionDto):
    pass