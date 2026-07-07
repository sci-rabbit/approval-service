import enum


class ApprovalEventType(str, enum.Enum):
    created = "created"
    approved = "approved"
    rejected = "rejected"
    cancelled = "cancelled"