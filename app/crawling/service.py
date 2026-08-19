from __future__ import annotations

from datetime import datetime, timezone
from typing import Protocol
from uuid import UUID

import structlog

from app.crawling.contracts import AuditEventType, CrawlAuditEvent, CrawlJob, CrawlOptions, CrawlStatus

logger = structlog.get_logger(__name__)


class CrawlerQueue(Protocol):
    """A worker queue adapter. Implementations must not be created in the API layer."""

    async def enqueue(self, job: CrawlJob) -> None: ...


class CrawlAuditSink(Protocol):
    async def append(self, event: CrawlAuditEvent) -> None: ...


class CrawlSubmissionService:
    """Creates validated jobs; it never launches Playwright or calls a domain."""

    def __init__(self, queue: CrawlerQueue, audit_sink: CrawlAuditSink, worker_id: str = "api"):
        self._queue = queue
        self._audit_sink = audit_sink
        self._worker_id = worker_id

    async def submit(self, domain: str, scan_id: UUID, options: CrawlOptions | None = None) -> CrawlJob:
        now = datetime.now(timezone.utc)
        job = CrawlJob(domain=domain, scan_id=scan_id, options=options or CrawlOptions(), created_at=now)
        await self._queue.enqueue(job)
        event = CrawlAuditEvent(event_type=AuditEventType.CRAWL_STARTED, scan_id=scan_id, domain=job.domain, worker_id=self._worker_id, timestamp=now)
        await self._audit_sink.append(event)
        logger.info("crawl_job_queued", scan_id=str(scan_id), job_id=str(job.id), domain=job.domain, timeout_seconds=job.options.timeout_seconds)
        return job


def blocked_audit_event(scan_id: UUID, domain: str, worker_id: str, reason: str) -> CrawlAuditEvent:
    return CrawlAuditEvent(event_type=AuditEventType.CRAWL_BLOCKED, scan_id=scan_id, domain=domain, worker_id=worker_id, timestamp=datetime.now(timezone.utc), reason=reason)
