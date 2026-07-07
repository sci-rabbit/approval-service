import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base

if TYPE_CHECKING:
    from models.approval_request import ApprovalRequest


class ApprovalReviewer(Base):
    __tablename__ = "approval_reviewers"

    id: Mapped[int] = mapped_column(primary_key=True)

    request_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("approval_requests.id", ondelete="CASCADE")
    )

    reviewer_user_id: Mapped[str] = mapped_column(String(64))

    request: Mapped[list["ApprovalRequest"]] = relationship(
        "ApprovalRequest",
        back_populates="reviewers",
    )
