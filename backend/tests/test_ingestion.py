from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import select, func

from app.db.session import SessionLocal

from app.models.job import Job

from app.providers.greenhouse import (
    clean_html,
    normalize_job,
    generate_content_hash
)

from app.repositories.job_repository import (
    upsert_jobs,
    deactivate_missing_jobs
)


def sample_job():

    return {
        "id": 101,

        "title": "Python Developer Intern",

        "content": (
            "<p>Experience with Python "
            "and FastAPI</p>"
        ),

        "location": {
            "name": "Remote"
        },

        "absolute_url": (
            "https://example.com/jobs/101"
        )
    }


def test_clean_html():

    raw = "<h1>Python</h1><p>FastAPI</p>"

    result = clean_html(raw)

    assert result == "Python FastAPI"


def test_content_hash_consistency():

    hash1 = generate_content_hash(
        "Developer",
        "Company",
        "Python"
    )

    hash2 = generate_content_hash(
        "Developer",
        "Company",
        "Python"
    )

    assert hash1 == hash2


def test_content_hash_changes():

    hash1 = generate_content_hash(
        "Developer",
        "Company",
        "Python"
    )

    hash2 = generate_content_hash(
        "Developer",
        "Company",
        "Python and Docker"
    )

    assert hash1 != hash2


def test_normalize_job():

    job = normalize_job(
        sample_job(),
        "test-company",
        "Test Company"
    )

    assert job.external_id == "101"

    assert job.source == (
        "greenhouse:test-company"
    )

    assert job.job_type == "internship"

    assert job.work_mode == "remote"

    assert "<p>" not in job.description


def test_upsert_and_embedding_invalidation():

    board = f"test-{uuid4().hex}"

    raw_job = sample_job()

    job = normalize_job(
        raw_job,
        board,
        "Test Company"
    )

    now = datetime.now(timezone.utc)

    with SessionLocal() as db:

        try:

            upsert_jobs(db, [job], now)

            stored = db.scalar(
                select(Job)
                .where(Job.source == job.source)
            )

            stored.embedding = [0.1] * 384

            db.flush()

            # Same job: preserve embedding.
            upsert_jobs(db, [job], now)

            db.expire_all()

            assert stored.embedding is not None

            count = db.scalar(
                select(func.count(Job.id))
                .where(Job.source == job.source)
            )

            assert count == 1

            # Changed job: invalidate embedding.
            raw_job["content"] = (
                "<p>Python, FastAPI and Docker</p>"
            )

            changed_job = normalize_job(
                raw_job,
                board,
                "Test Company"
            )

            upsert_jobs(
                db,
                [changed_job],
                now
            )

            db.expire_all()

            assert stored.embedding is None

            assert "Docker" in stored.description

        finally:

            db.rollback()


def test_deactivate_missing_job():

    board = f"test-{uuid4().hex}"

    job = normalize_job(
        sample_job(),
        board,
        "Test Company"
    )

    with SessionLocal() as db:

        try:

            from datetime import timedelta

            old_time = (
                datetime.now(timezone.utc)
                - timedelta(hours=6)
            )

            upsert_jobs(
                db,
                [job],
                old_time
            )

            count = deactivate_missing_jobs(
                db,
                job.source,
                datetime.now(timezone.utc)
            )

            assert count == 1

            stored = db.scalar(
                select(Job)
                .where(Job.source == job.source)
            )

            assert stored.is_active is False

        finally:

            db.rollback()