from enum import Enum


class OutboxEventType(str, Enum):
    REQUEST_CREATED = "ApprovalRequestCreated"

    REQUEST_APPROVED = "ApprovalRequestApproved"

    REQUEST_REJECTED = "ApprovalRequestRejected"

    REQUEST_CANCELLED = "ApprovalRequestCancelled"