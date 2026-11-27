import httpx

from sqlalchemy.exc import OperationalError

from app.core.config import settings

from app.workers.celery_app import celery_app

from app.services.ingestion import ingest_board

from app.providers.greenhouse import (
    RetryableSourceError
)


@celery_app.task(
    name="careerpilot.ingest_board",

    autoretry_for=(
        httpx.TransportError,
        RetryableSourceError,
        OperationalError
    ),

    retry_backoff=60,

    retry_backoff_max=900,

    retry_jitter=True,

    retry_kwargs={
        "max_retries": 3
    }
)
def ingest_board_task(
    board: str,
    company: str
):

    return ingest_board(
        board,
        company
    )


@celery_app.task(
    name="careerpilot.ingest_all"
)
def ingest_all_jobs():

    queued = 0

    for board, company in (
        settings.GREENHOUSE_BOARDS.items()
    ):

        ingest_board_task.delay(
            board,
            company
        )

        queued += 1

    return {
        "boards_queued": queued
    }