import logging

from datetime import datetime, timezone

from sqlalchemy import text

from app.db.session import SessionLocal
from app.models.ingestion import IngestionRun

from app.providers.greenhouse import fetch_jobs

from app.repositories.job_repository import (
    upsert_jobs,
    deactivate_missing_jobs
)


logger = logging.getLogger(__name__)


def ingest_board(
    board: str,
    company: str
) -> dict:

    source = f"greenhouse:{board}"

    # Create a monitoring record.
    with SessionLocal.begin() as db:

        run = IngestionRun(
            source=source,
            status="running"
        )

        db.add(run)
        db.flush()

        run_id = run.id

    fetched = 0

    try:

        with SessionLocal.begin() as db:

            # Prevent simultaneous ingestion
            # of the same company board.
            locked = db.execute(
                text(
                    "SELECT pg_try_advisory_xact_lock"
                    "(hashtext(:source)::bigint)"
                ),
                {"source": source}
            ).scalar_one()

            run = db.get(IngestionRun, run_id)

            if not locked:

                run.status = "skipped"

                run.completed_at = datetime.now(
                    timezone.utc
                )

                return {
                    "source": source,
                    "status": "skipped"
                }

            jobs = fetch_jobs(board, company)

            fetched = len(jobs)

            seen_at = datetime.now(timezone.utc)

            upserted = upsert_jobs(
                db,
                jobs,
                seen_at
            )

            deactivated = deactivate_missing_jobs(
                db,
                source,
                seen_at
            )

            run.status = "completed"
            run.jobs_fetched = fetched
            run.jobs_upserted = upserted

            run.completed_at = datetime.now(
                timezone.utc
            )

        result = {
            "source": source,
            "status": "completed",
            "jobs_fetched": fetched,
            "jobs_upserted": upserted,
            "jobs_deactivated": deactivated
        }

        logger.info(
            "Ingestion completed: %s",
            result
        )

        return result

    except Exception as exc:

        logger.exception(
            "Ingestion failed for %s",
            source
        )

        # Record failure using a separate transaction.
        try:

            with SessionLocal.begin() as db:

                run = db.get(IngestionRun, run_id)

                run.status = "failed"

                run.jobs_fetched = fetched
                run.jobs_upserted = 0

                run.error_message = (
                    f"{type(exc).__name__}: "
                    f"{str(exc)[:500]}"
                )

                run.completed_at = datetime.now(
                    timezone.utc
                )

        except Exception:

            logger.exception(
                "Could not record ingestion failure"
            )

        raise