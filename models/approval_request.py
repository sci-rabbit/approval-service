import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import UUID, String, Enum, Text, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from enums.approval_status_enum import ApprovalStatus
from enums.source_type_enum import SourceType
from models.base import Base

if TYPE_CHECKING:
    from models.approval_reviewer import ApprovalReviewer
    from models.approval_event import ApprovalEvent


class ApprovalRequest(Base):
    __tablename__ = "approval_requests"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    workspace_id: Mapped[str] = mapped_column(String(64), index=True)

    source_type: Mapped[SourceType] = mapped_column(Enum(SourceType))

    source_id: Mapped[str] = mapped_column(String(128))

    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)

    status: Mapped[ApprovalStatus] = mapped_column(
        Enum(ApprovalStatus),
        default=ApprovalStatus.pending,
    )

    created_by: Mapped[str] = mapped_column(String(64))

    decision_by: Mapped[str | None] = mapped_column(String(64))
    decision_comment: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    reviewers: Mapped[list["ApprovalReviewer"]] = relationship(
        "ApprovalReviewer",
        back_populates="request",
        cascade="all, delete-orphan",
    )

    events: Mapped[list["ApprovalEvent"]] = relationship(
        "ApprovalEvent",
        back_populates="request",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index(
            "ix_workspace_status",
            "workspace_id",
            "status",
        ),
    )
