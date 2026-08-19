from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class FeedSource(StrEnum):
    CERTIFICATE_TRANSPARENCY = "certificate_transparency"
    REGISTERED_DOMAIN_FEED = "registered_domain_feed"
    MANUAL_SUBMISSION = "manual_submission"
    REPLAY_FIXTURE = "replay_fixture"


class JobStatus(StrEnum):
    QUEUED = "queued"
    PROCESSING = "processing"
    ENRICHED = "enriched"
    FAILED = "failed"
    EXPIRED = "expired"


class EnrichmentState(StrEnum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    FAILED = "failed"
    EXPIRED = "expired"


class EvidenceKind(StrEnum):
    RDAP = "rdap"
    DNS = "dns"
    TLS = "tls"


class DomainFeedItem(BaseModel):
    """A normalized candidate supplied by an approved feed adapter."""

    model_config = ConfigDict(from_attributes=True, extra="forbid")
    domain: str = Field(min_length=1, max_length=253)
    source: FeedSource
    source_record_id: str = Field(min_length=1, max_length=256)
    observed_at: datetime


class IngestionJob(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")
    id: UUID = Field(default_factory=uuid4)
    domain: str
    source: FeedSource
    status: JobStatus = JobStatus.QUEUED
    attempts: int = Field(default=0, ge=0, le=10)
    created_at: datetime
    updated_at: datetime
    failure_reason: str | None = Field(default=None, max_length=500)


class CachedEvidence(BaseModel):
    """Provider-neutral cached result; payloads must contain no credentials."""

    model_config = ConfigDict(from_attributes=True, extra="forbid")
    id: UUID = Field(default_factory=uuid4)
    domain: str
    kind: EvidenceKind
    provenance: str = Field(min_length=1, max_length=200)
    collected_at: datetime
    expires_at: datetime
    ttl_seconds: int = Field(default=86400, ge=1, le=604800)
    state: EnrichmentState
    payload: dict[str, Any] = Field(default_factory=dict)
    failure_count: int = Field(default=0, ge=0, le=100)
    failure_reason: str | None = Field(default=None, max_length=500)


class RdapSnapshot(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")
    registrar: str | None = None
    registered_at: datetime | None = None
    expires_at: datetime | None = None
    nameservers: list[str] = Field(default_factory=list)


class DnsSnapshot(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")
    a_records: list[str] = Field(default_factory=list)
    mx_records: list[str] = Field(default_factory=list)
    nameservers: list[str] = Field(default_factory=list)


class TlsSnapshot(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")
    issuer: str | None = None
    not_before: datetime | None = None
    not_after: datetime | None = None
    serial_number: str | None = None
