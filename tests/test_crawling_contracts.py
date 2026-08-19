import json
from pathlib import Path
from uuid import UUID

import pytest
from pydantic import ValidationError

from app.crawling.contracts import CrawlJob, CrawlOptions, CrawlStatus
from app.crawling.safety import UnsafeCrawlTarget, validate_crawl_domain, validate_resolved_addresses
from app.crawling.service import CrawlSubmissionService


@pytest.fixture
def crawl_fixtures() -> list[dict]:
    path = Path(__file__).parent / "fixtures" / "crawl_jobs.json"
    return json.loads(path.read_text(encoding="utf-8"))


class FixtureQueue:
    def __init__(self) -> None:
        self.jobs: list[CrawlJob] = []

    async def enqueue(self, job: CrawlJob) -> None:
        self.jobs.append(job)


class FixtureAuditSink:
    def __init__(self) -> None:
        self.events = []

    async def append(self, event) -> None:
        self.events.append(event)


@pytest.mark.asyncio
async def test_safe_fixture_is_validated_queued_and_audited(crawl_fixtures: list[dict]) -> None:
    queue = FixtureQueue()
    audit = FixtureAuditSink()
    job = await CrawlSubmissionService(queue, audit).submit(crawl_fixtures[0]["domain"], UUID(crawl_fixtures[0]["scan_id"]))
    assert job.domain == "secure-sbi-login.example"
    assert queue.jobs == [job]
    assert audit.events[0].scan_id == job.scan_id


def test_private_ip_fixture_is_rejected_before_queueing(crawl_fixtures: list[dict]) -> None:
    with pytest.raises((UnsafeCrawlTarget, ValidationError)):
        CrawlJob.model_validate(crawl_fixtures[1])


@pytest.mark.parametrize("unsafe", ["http://192.168.1.1", "localhost", "service.internal", "file:///etc/passwd"])
def test_unsafe_targets_are_rejected(unsafe: str) -> None:
    with pytest.raises(UnsafeCrawlTarget):
        validate_crawl_domain(unsafe)


def test_resolved_private_addresses_are_rejected() -> None:
    with pytest.raises(UnsafeCrawlTarget):
        validate_resolved_addresses(["93.184.216.34", "10.0.0.8"])


def test_limits_are_bounded() -> None:
    with pytest.raises(ValidationError):
        CrawlOptions(timeout_seconds=31)
    with pytest.raises(ValidationError):
        CrawlOptions(max_redirects=6)
