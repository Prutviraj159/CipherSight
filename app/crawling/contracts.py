from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.crawling.safety import validate_crawl_domain


class CrawlStatus(StrEnum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


class AuditEventType(StrEnum):
    CRAWL_STARTED = "crawl_started"
    CRAWL_COMPLETED = "crawl_completed"
    CRAWL_BLOCKED = "crawl_blocked"
    CRAWL_FAILED = "crawl_failed"


class CrawlOptions(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    timeout_seconds: int = Field(default=30, ge=1, le=30)
    overall_timeout_seconds: int = Field(default=35, ge=1, le=35)
    max_redirects: int = Field(default=5, ge=0, le=5)
    max_page_bytes: int = Field(default=5_000_000, ge=1_024, le=10_000_000)
    max_attempts: int = Field(default=3, ge=1, le=3)
    block_downloads: bool = True
    block_private_ips: bool = True


class CrawlJob(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    id: UUID = Field(default_factory=uuid4)
    domain: str = Field(min_length=1, max_length=253)
    scan_id: UUID
    options: CrawlOptions = Field(default_factory=CrawlOptions)
    created_at: datetime

    @field_validator("domain")
    @classmethod
    def validate_domain(cls, value: str) -> str:
        return validate_crawl_domain(value)


class FormFinding(BaseModel):
    model_config = ConfigDict(extra="forbid")
    password_input_detected: bool = False
    suspicious_action_detected: bool = False
    action_host: str | None = Field(default=None, max_length=253)
    input_count: int = Field(default=0, ge=0, le=100)


class CrawlResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    scan_id: UUID
    status: CrawlStatus
    screenshot_paths: list[str] = Field(default_factory=list, max_length=10)
    html_path: str | None = None
    text_path: str | None = None
    forms_detected: list[FormFinding] = Field(default_factory=list, max_length=50)
    redirects_observed: int = Field(default=0, ge=0, le=5)
    page_bytes: int = Field(default=0, ge=0, le=10_000_000)
    error: str | None = Field(default=None, max_length=500)


class CrawlAuditEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")
    event_type: AuditEventType
    scan_id: UUID
    domain: str
    worker_id: str = Field(min_length=1, max_length=128)
    timestamp: datetime
    reason: str | None = Field(default=None, max_length=500)
    artifacts_count: int = Field(default=0, ge=0, le=12)
