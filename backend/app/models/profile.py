from datetime import datetime

from sqlalchemy import (
    ForeignKey,
    String,
    Text,
    Float,
    DateTime,
    func,
    text
)

from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class UserProfile(Base):

    __tablename__ = "user_profiles"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    )

    skills: Mapped[list[str]] = mapped_column(
        ARRAY(String),
        default=list,
        server_default=text("'{}'")
    )

    experience_years: Mapped[float] = mapped_column(
        Float,
        default=0,
        server_default="0"
    )

    education: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    resume_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    preferences: Mapped[dict] = mapped_column(
        JSONB,
        default=dict,
        server_default=text("'{}'::jsonb")
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )