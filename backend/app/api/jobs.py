from fastapi import (
    APIRouter,
    Depends,
    Query,
    HTTPException
)

from sqlalchemy import select, func

from sqlalchemy.orm import Session

from app.db.session import get_db

from app.models.job import Job

from app.schemas.job import (
    JobResponse,
    JobListResponse
)

from app.repositories.job_repository import (
    get_active_jobs
)


router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"]
)


@router.get(
    "",
    response_model=JobListResponse
)
def list_jobs(

    limit: int = Query(
        default=20,
        ge=1,
        le=100
    ),

    offset: int = Query(
        default=0,
        ge=0
    ),

    db: Session = Depends(get_db)
):

    jobs = get_active_jobs(
        db,
        limit,
        offset
    )

    total = db.scalar(
        select(func.count(Job.id))
        .where(Job.is_active.is_(True))
    )

    return JobListResponse(
        total=total,
        limit=limit,
        offset=offset,
        jobs=jobs
    )


@router.get("/stats")
def job_stats(
    db: Session = Depends(get_db)
):

    total = db.scalar(
        select(func.count(Job.id))
    )

    active = db.scalar(
        select(func.count(Job.id))
        .where(Job.is_active.is_(True))
    )

    embedded = db.scalar(
        select(func.count(Job.id))
        .where(
            Job.is_active.is_(True),
            Job.embedding.is_not(None)
        )
    )

    source_rows = db.execute(

        select(
            Job.source,
            func.count(Job.id)
        )
        .where(Job.is_active.is_(True))
        .group_by(Job.source)

    ).all()

    return {
        "total_jobs": total,
        "active_jobs": active,
        "inactive_jobs": total - active,
        "embedded_jobs": embedded,
        "pending_embeddings": active - embedded,

        "sources": {
            source: count
            for source, count in source_rows
        }
    }


@router.get(
    "/{job_id}",
    response_model=JobResponse
)
def get_job(

    job_id: int,

    db: Session = Depends(get_db)
):

    job = db.get(
        Job,
        job_id
    )

    if job is None or not job.is_active:

        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    return job