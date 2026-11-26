from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.health import router as health_router


app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "An agentic AI-powered job search "
        "and recommendation platform."
    ),
    version="0.1.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


app.include_router(
    health_router,
    prefix="/api/v1"
)


@app.get("/", tags=["Root"])
def root():

    return {
        "message": "Welcome to CareerPilot AI",
        "version": "0.1.0",
        "docs": "/docs"
    }