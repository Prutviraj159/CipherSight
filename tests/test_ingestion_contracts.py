import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from app.ingestion.contracts import CachedEvidence, DomainFeedItem, EnrichmentState, EvidenceKind, FeedSource, JobStatus
from app.ingestion.normalization import extract_lexical_features, normalize_domain
from app.ingestion.providers import cache_key
from app.ingestion.retry import RetryPolicy
from app.ingestion.service import DomainIngestionService


@pytest.fixture
def feed_item() -> DomainFeedItem:
    fixture = Path(__file__).parent / "fixtures" / "domain_feed.json"
    return DomainFeedItem.model_validate(json.loads(fixture.read_text(encoding="utf-8"))[0])


class FixtureQueue:
    def __init__(self):
        self.jobs = []

    async def enqueue(self, job):
        self.jobs.append(job)


@pytest.mark.asyncio
async def test_fixture_feed_item_is_normalized_and_queued(feed_item):
    queue = FixtureQueue()
    job = await DomainIngestionService(queue).submit(feed_item)
    assert job.status is JobStatus.QUEUED
    assert job.domain == "secure-sbi-login.example"
    assert queue.jobs == [job]


def test_punycode_and_lexical_features_are_local_only():
    domain = normalize_domain("https://xn--pple-43d.example/login")
    features = extract_lexical_features(domain)
    assert domain.is_punycode is True
    assert features.hyphen_count >= 1
    assert "xn" in features.tokens


def test_retry_policy_is_bounded():
    policy = RetryPolicy(max_attempts=3, initial_delay_seconds=1, multiplier=2)
    assert policy.next_delay(1) == 1
    assert policy.next_delay(2) == 2
    assert policy.next_delay(3) is None


def test_cached_evidence_preserves_provenance_and_expiration():
    evidence = CachedEvidence.model_validate({
        "domain": "secure-sbi-login.example",
        "kind": EvidenceKind.RDAP,
        "provenance": "fixture-rdap-provider",
        "collected_at": "2026-08-18T00:00:00Z",
        "expires_at": "2026-08-19T00:00:00Z",
        "state": EnrichmentState.AVAILABLE,
        "failure_count": 0,
        "payload": {"registered_at": "2026-08-16T00:00:00Z"},
    })
    assert evidence.ttl_seconds == 86400
    assert cache_key(evidence.domain, "rdap") == "enrichment:secure-sbi-login.example:rdap"


def test_invalid_domain_is_rejected_without_provider_call():
    with pytest.raises(ValueError):
        normalize_domain("https://user:password@example.test")
