from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.ingestion.normalization import normalize_domain


class RiskLevel(StrEnum):
    LOW = "low"
    SUSPICIOUS = "suspicious"
    HIGH = "high"
    CRITICAL = "critical"


class ScanLifecycle(StrEnum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    VERDICT_SUBMITTED = "verdict_submitted"


class VerdictType(StrEnum):
    PHISHING = "phishing"
    LEGITIMATE = "legitimate"
    NEEDS_REVIEW = "needs_review"


class BrandCandidate(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")
    id: UUID = Field(default_factory=uuid4)
    name: str = Field(min_length=3, max_length=100)
    domains: list[str] = Field(min_length=1, max_length=20)


class DetectionSignals(BaseModel):
    """Normalized worker evidence. Visual input is not an ML-performance claim."""

    model_config = ConfigDict(extra="forbid")
    lexical: float = Field(ge=0, le=1)
    registration: float = Field(ge=0, le=1)
    infrastructure: float = Field(ge=0, le=1)
    text: float = Field(ge=0, le=1)
    visual: float = Field(default=0, ge=0, le=1)
    forms: float = Field(ge=0, le=1)
    visual_source_available: bool = False


class SignalContribution(BaseModel):
    model_config = ConfigDict(extra="forbid")
    signal: str
    raw_score: float = Field(ge=0, le=1)
    weight: float = Field(ge=0, le=1)
    contribution: float = Field(ge=0, le=1)
    explanation: str


class RiskAssessment(BaseModel):
    model_config = ConfigDict(extra="forbid")
    score: float = Field(ge=0, le=1)
    level: RiskLevel
    model_version: str
    contributions: list[SignalContribution]
    ranked_brands: list["BrandRank"]
    limitations: list[str] = Field(default_factory=list)


class BrandRank(BaseModel):
    model_config = ConfigDict(extra="forbid")
    brand_id: UUID
    name: str
    confidence: float = Field(ge=0, le=1)


class CreateScanRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    domain: str = Field(min_length=3, max_length=253)

    @field_validator("domain")
    @classmethod
    def require_fqdn(cls, value: str) -> str:
        if "://" in value or "/" in value or len(value.split(".")) < 2:
            raise ValueError("domain must be a fully qualified domain name")
        return normalize_domain(value).ascii_domain


class ScanAlert(BaseModel):
    model_config = ConfigDict(extra="forbid")
    scan_id: UUID = Field(default_factory=uuid4)
    domain: str
    status: ScanLifecycle = ScanLifecycle.QUEUED
    assessment: RiskAssessment | None = None
    evidence_summary: dict[str, int | float | str | bool] = Field(default_factory=dict)
    created_at: datetime


class AnalystVerdictRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    verdict: VerdictType
    note: str | None = Field(default=None, max_length=1000)


class AnalystVerdict(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: UUID = Field(default_factory=uuid4)
    scan_id: UUID
    verdict: VerdictType
    analyst_id: UUID
    note: str | None = None
    created_at: datetime


class WorkflowAuditEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: UUID = Field(default_factory=uuid4)
    scan_id: UUID
    actor_id: UUID
    action: str
    timestamp: datetime
    old_values: dict[str, str] = Field(default_factory=dict)
    new_values: dict[str, str] = Field(default_factory=dict)
