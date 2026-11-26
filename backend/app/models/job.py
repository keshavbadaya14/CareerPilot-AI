from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    String,
    Text,
    Float,
    Numeric,
    Boolean,
    DateTime,
    Index,
    UniqueConstraint,
    func,
    text
)

from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector

from app.db.base import Base


class Job(Base):

    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    source: Mapped[str] = mapped_column(
        String(100)
    )

    external_id: Mapped[str] = mapped_column(
        String(255)
    )

    title: Mapped[str] = mapped_column(
        String(255),
        index=True
    )

    company: Mapped[str] = mapped_column(
        String(255),
        index=True
    )

    description: Mapped[str] = mapped_column(Text)

    location: Mapped[str | None] = mapped_column(
        String(255)
    )

    job_type: Mapped[str | None] = mapped_column(
        String(50)
    )

    work_mode: Mapped[str | None] = mapped_column(
        String(50)
    )

    skills: Mapped[list[str]] = mapped_column(
        ARRAY(String),
        default=list,
        server_default=text("'{}'")
    )

    experience_required: Mapped[float | None] = mapped_column(
        Float
    )

    salary_min: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2)
    )

    salary_max: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2)
    )

    currency: Mapped[str | None] = mapped_column(
        String(3)
    )

    salary_period: Mapped[str | None] = mapped_column(
        String(20)
    )

    job_url: Mapped[str] = mapped_column(Text)

    content_hash: Mapped[str | None] = mapped_column(
        String(64)
    )

    embedding: Mapped[list[float] | None] = mapped_column(
        Vector(384)
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default=text("true")
    )

    posted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )

    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )

    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    __table_args__ = (

        UniqueConstraint(
            "source",
            "external_id",
            name="uq_jobs_source_external_id"
        ),

        Index(
            "ix_jobs_embedding_hnsw",
            "embedding",
            postgresql_using="hnsw",
            postgresql_ops={
                "embedding": "vector_cosine_ops"
            }
        ),

        Index(
            "ix_jobs_active_type",
            "is_active",
            "job_type"
        ),

    )