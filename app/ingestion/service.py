from __future__ import annotations

from datetime import datetime, timezone
from typing import Protocol

import structlog

from app.ingestion.contracts import DomainFeedItem, IngestionJob, JobStatus
from app.ingestion.normalization import extract_lexical_features, normalize_domain

logger = structlog.get_logger(__name__)


class JobQueue(Protocol):
    async def enqueue(self, job: IngestionJob) -> None: ...


class DomainIngestionService:
    """Validates feed records and queues contracts; it never invokes providers."""

    def __init__(self, queue: JobQueue):
        self._queue = queue

    async def submit(self, item: DomainFeedItem) -> IngestionJob:
        normalized = normalize_domain(item.domain)
        features = extract_lexical_features(normalized)
        now = datetime.now(timezone.utc)
        job = IngestionJob(domain=normalized.ascii_domain, source=item.source, created_at=now, updated_at=now)
        await self._queue.enqueue(job)
        logger.info("domain_ingestion_queued", job_id=str(job.id), domain=job.domain, source=job.source, is_punycode=features.is_punycode)
        return job

    @staticmethod
    def mark_failed(job: IngestionJob, reason: str, now: datetime) -> IngestionJob:
        return job.model_copy(update={"status": JobStatus.FAILED, "updated_at": now, "failure_reason": reason, "attempts": job.attempts + 1})
