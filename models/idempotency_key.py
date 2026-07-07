import uuid
from datetime import datetime, timezone

from sqlalchemy import String, ForeignKey, DateTime
from sqlalchemy.orm import mapped_column, Mapped

from models.base import Base


class IdempotencyKey(Base):
    __tablename__ = "idempotency_keys"

    key: Mapped[str] = mapped_column(
        String(128),
        primary_key=True,
    )

    workspace_id: Mapped[str] = mapped_column(String(64))

    request_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("approval_requests.id"))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
