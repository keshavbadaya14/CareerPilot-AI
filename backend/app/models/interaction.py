from datetime import datetime

from sqlalchemy import (
    ForeignKey,
    String,
    DateTime,
    CheckConstraint,
    Index,
    func
)

from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Interaction(Base):

    __tablename__ = "interactions"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )

    job_id: Mapped[int] = mapped_column(
        ForeignKey("jobs.id", ondelete="CASCADE")
    )

    action: Mapped[str] = mapped_column(
        String(20)
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    __table_args__ = (

        CheckConstraint(
            "action IN ('view', 'save', 'reject', 'apply')",
            name="ck_interaction_action"
        ),

        Index(
            "ix_interactions_user_job",
            "user_id",
            "job_id"
        ),

    )