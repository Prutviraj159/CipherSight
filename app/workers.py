"""Contracts for asynchronous ingestion and isolated crawling.

This module intentionally does not fetch URLs. The deployment worker must run in
an egress-controlled container and implement `collect_evidence` without sharing
the API process or its network privileges.
"""
from __future__ import annotations

import logging
from collections.abc import Callable
from time import sleep
from typing import TypeVar

from app.domain import normalize_url
from app.schemas import EnrichmentEvidence

logger = logging.getLogger(__name__)
Result = TypeVar("Result")


class RetryExhausted(RuntimeError):
    pass


def run_with_retry(operation: Callable[[], Result], attempts: int = 3, base_delay_seconds: float = 0.25) -> Result:
    """Retry transient worker failures with bounded exponential backoff."""
    for attempt in range(1, attempts + 1):
        try:
            return operation()
        except (TimeoutError, ConnectionError) as error:
            logger.warning("worker_attempt_failed", extra={"attempt": attempt, "error": str(error)})
            if attempt == attempts:
                raise RetryExhausted("Enrichment exhausted its retry budget") from error
            sleep(base_delay_seconds * 2 ** (attempt - 1))
    raise AssertionError("unreachable")


def validate_crawl_job(url: str) -> str:
    """Validate before queueing; network policy enforcement belongs in the worker."""
    return normalize_url(url).host


def evidence_contract() -> EnrichmentEvidence:
    """Schema marker for worker integrations and replay-mode fixtures."""
    return EnrichmentEvidence()
