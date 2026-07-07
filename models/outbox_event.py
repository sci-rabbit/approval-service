import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import UUID, String, JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class OutboxEvent(Base):
    __tablename__ = "outbox_events"

    id: Mapped[int] = mapped_column(primary_key=True)

    aggregate_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))

    event_type: Mapped[str] = mapped_column(String(64))

    payload: Mapped[dict[str, Any]] = mapped_column(JSON)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
