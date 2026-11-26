from datetime import datetime

from sqlalchemy import (
    ForeignKey,
    String,
    Text,
    DateTime,
    func
)

from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class UserMemory(Base):

    __tablename__ = "user_memory"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True
    )

    memory_type: Mapped[str] = mapped_column(
        String(50)
    )

    content: Mapped[str] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )