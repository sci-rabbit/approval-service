import uuid
from datetime import datetime, timezone

from sqlalchemy import ForeignKey, Enum, String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from enums.approval_event_type_enum import ApprovalEventType
from models.base import Base


class ApprovalEvent(Base):
    __tablename__ = "approval_events"

    id: Mapped[int] = mapped_column(primary_key=True)

    request_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("approval_requests.id", ondelete="CASCADE")
    )

    event_type: Mapped[ApprovalEventType] = mapped_column(Enum(ApprovalEventType))

    actor_user_id: Mapped[str] = mapped_column(String(64))

    message: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    request = relationship(
        "ApprovalRequest",
        back_populates="events",
    )
