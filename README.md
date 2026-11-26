# CareerPilot AI

An agentic AI-powered job discovery and personalised
recommendation platform.

## Technology Stack

- Python and FastAPI
- PostgreSQL and pgvector
- SQLAlchemy and Alembic
- LangGraph and Gemini
- Sentence Transformers
- Celery and Redis
- React and Tailwind CSS
- Docker
- Pytest and RAGAS

## Local Development

1. Create a virtual environment.
2. Install backend/requirements.txt.
3. Copy .env.example to .env and configure credentials.
4. Start infrastructure using Docker Compose.
5. Apply database migrations.
6. Start FastAPI.

```bash
docker compose up -d
cd backend
alembic upgrade head
python -m uvicorn app.main:app --reload
```

API documentation:
http://localhost:8000/docs

## Development Progress

- [x] Project infrastructure
- [x] PostgreSQL and Redis setup
- [x] SQLAlchemy models
- [x] Alembic migrations
- [x] FastAPI health endpoints
- [ ] Job ingestion pipeline
- [ ] Hybrid search
- [ ] Recommendation engine
- [ ] LangGraph agent
- [ ] Persistent memory
- [ ] Evaluation
- [ ] React frontend
- [ ] Deployment