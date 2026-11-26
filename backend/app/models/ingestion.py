from datetime import datetime

from sqlalchemy import (
    String,
    Integer,
    Text,
    DateTime,
    func
)

from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class IngestionRun(Base):

    __tablename__ = "ingestion_runs"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    source: Mapped[str] = mapped_column(
        String(100)
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="running",
        server_default="running"
    )

    jobs_fetched: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default="0"
    )

    jobs_upserted: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default="0"
    )

    error_message: Mapped[str | None] = mapped_column(
        Text
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )