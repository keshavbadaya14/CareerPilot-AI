import hashlib
import html
import json
import re

import httpx

from bs4 import BeautifulSoup

from app.schemas.job import NormalizedJob


BASE_URL = "https://boards-api.greenhouse.io/v1/boards"


class RetryableSourceError(Exception):
    pass


def clean_html(raw_html: str) -> str:

    decoded_html = html.unescape(raw_html)

    soup = BeautifulSoup(
        decoded_html,
        "html.parser"
    )

    for tag in soup(["script", "style"]):
        tag.decompose()

    text = soup.get_text(
        separator=" ",
        strip=True
    )

    return " ".join(text.split())


def generate_content_hash(
    title: str,
    company: str,
    description: str
) -> str:

    content = json.dumps(
        [title, company, description],
        ensure_ascii=False
    )

    return hashlib.sha256(
        content.encode("utf-8")
    ).hexdigest()


def normalize_job(
    raw_job: dict,
    board: str,
    company: str
) -> NormalizedJob:

    title = raw_job["title"].strip()

    description = clean_html(
        raw_job["content"]
    )

    location = (
        raw_job.get("location") or {}
    ).get("name")

    job_type = None
    work_mode = None

    if re.search(
        r"\b(intern|internship)\b",
        title,
        re.IGNORECASE
    ):
        job_type = "internship"

    if location:

        location = location.strip()

        if location.lower() == "remote":
            work_mode = "remote"

    content_hash = generate_content_hash(
        title,
        company,
        description
    )

    return NormalizedJob(
        source=f"greenhouse:{board}",
        external_id=str(raw_job["id"]),
        title=title,
        company=company,
        description=description,
        location=location[:255] if location else None,
        job_type=job_type,
        work_mode=work_mode,
        job_url=raw_job["absolute_url"],
        content_hash=content_hash
    )


def fetch_jobs(
    board: str,
    company: str
) -> list[NormalizedJob]:

    if not re.fullmatch(r"[a-zA-Z0-9_-]+", board):
        raise ValueError("Invalid Greenhouse board token")

    url = f"{BASE_URL}/{board}/jobs"

    with httpx.Client(
        timeout=30.0
    ) as client:

        response = client.get(
            url,
            params={"content": "true"}
        )

        if (
            response.status_code == 429
            or response.status_code >= 500
        ):
            raise RetryableSourceError(
                f"Greenhouse returned HTTP "
                f"{response.status_code}"
            )

        response.raise_for_status()

        payload = response.json()

    raw_jobs = payload["jobs"]

    expected_total = payload["meta"]["total"]

    if not isinstance(raw_jobs, list):
        raise ValueError("Invalid jobs response")

    if len(raw_jobs) != expected_total:
        raise ValueError("Incomplete jobs snapshot")

    if not raw_jobs:
        raise ValueError(
            "Empty snapshot: deactivation skipped"
        )

    normalized_jobs = {}

    for raw_job in raw_jobs:

        job = normalize_job(
            raw_job,
            board,
            company
        )

        normalized_jobs[job.external_id] = job

    return list(normalized_jobs.values())