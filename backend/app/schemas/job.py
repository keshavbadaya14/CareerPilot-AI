from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class NormalizedJob(BaseModel):

    source: str = Field(min_length=1, max_length=100)

    external_id: str = Field(min_length=1, max_length=255)

    title: str = Field(min_length=1, max_length=255)

    company: str = Field(min_length=1, max_length=255)

    description: str = Field(min_length=1)

    location: str | None = Field(
        default=None,
        max_length=255
    )

    job_type: str | None = None

    work_mode: str | None = None

    job_url: HttpUrl

    content_hash: str = Field(
        min_length=64,
        max_length=64
    )


class JobResponse(BaseModel):

    id: int
    source: str
    title: str
    company: str
    description: str

    location: str | None
    job_type: str | None
    work_mode: str | None

    skills: list[str]

    job_url: str
    is_active: bool

    posted_at: datetime | None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class JobListResponse(BaseModel):

    total: int
    limit: int
    offset: int

    jobs: list[JobResponse]