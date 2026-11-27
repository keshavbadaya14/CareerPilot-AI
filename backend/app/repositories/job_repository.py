from datetime import datetime

from sqlalchemy import case, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.models.job import Job
from app.schemas.job import NormalizedJob


def upsert_jobs(
    db: Session,
    jobs: list[NormalizedJob],
    seen_at: datetime
) -> int:

    if not jobs:
        return 0

    batch_size = 100

    for start in range(0, len(jobs), batch_size):

        batch = jobs[start:start + batch_size]

        records = []

        for job in batch:

            record = job.model_dump()

            record["job_url"] = str(job.job_url)
            record["last_seen_at"] = seen_at
            record["is_active"] = True

            records.append(record)

        stmt = insert(Job).values(records)

        content_changed = Job.content_hash.is_distinct_from(
            stmt.excluded.content_hash
        )

        stmt = stmt.on_conflict_do_update(

            constraint="uq_jobs_source_external_id",

            set_={
                "title": stmt.excluded.title,
                "company": stmt.excluded.company,
                "description": stmt.excluded.description,
                "location": stmt.excluded.location,
                "job_type": stmt.excluded.job_type,
                "work_mode": stmt.excluded.work_mode,
                "job_url": stmt.excluded.job_url,
                "content_hash": stmt.excluded.content_hash,
                "last_seen_at": seen_at,
                "updated_at": seen_at,
                "is_active": True,

                "embedding": case(
                    (content_changed, None),
                    else_=Job.embedding
                )
            }
        )

        db.execute(stmt)

    return len(jobs)


def deactivate_missing_jobs(
    db: Session,
    source: str,
    seen_at: datetime
) -> int:

    stmt = (
        update(Job)
        .where(
            Job.source == source,
            Job.is_active.is_(True),
            Job.last_seen_at < seen_at
        )
        .values(
            is_active=False,
            updated_at=seen_at
        )
    )

    result = db.execute(stmt)

    return result.rowcount


def get_active_jobs(
    db: Session,
    limit: int = 20,
    offset: int = 0
):

    stmt = (
        select(Job)
        .where(Job.is_active.is_(True))
        .order_by(
            Job.created_at.desc(),
            Job.id.desc()
        )
        .offset(offset)
        .limit(limit)
    )

    return db.scalars(stmt).all()