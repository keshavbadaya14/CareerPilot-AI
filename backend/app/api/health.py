import logging

from fastapi import APIRouter, Depends, Response
from sqlalchemy import text
from sqlalchemy.orm import Session

from redis import Redis

from app.core.config import settings
from app.db.session import get_db
from app.schemas.health import HealthResponse


router = APIRouter(tags=["Health"])

logger = logging.getLogger(__name__)


@router.get(
    "/health",
    response_model=HealthResponse
)
def health_check(
    response: Response,
    db: Session = Depends(get_db)
):

    database_status = "connected"
    redis_status = "connected"

    try:
        db.execute(text("SELECT 1"))

    except Exception:
        logger.exception("Database health check failed")
        database_status = "unavailable"

    try:
        with Redis.from_url(
            settings.REDIS_URL,
            socket_connect_timeout=2,
            socket_timeout=2
        ) as redis_client:

            redis_client.ping()

    except Exception:
        logger.exception("Redis health check failed")
        redis_status = "unavailable"

    is_healthy = (
        database_status == "connected"
        and redis_status == "connected"
    )

    if not is_healthy:
        response.status_code = 503

    return HealthResponse(
        status="healthy" if is_healthy else "unhealthy",
        database=database_status,
        redis=redis_status
    )