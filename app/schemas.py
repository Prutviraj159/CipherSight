from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl, field_validator


Verdict = Literal["phishing", "legitimate", "needs_review"]


class BrandCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    official_domain: str = Field(min_length=3, max_length=253)
    aliases: list[str] = Field(default_factory=list, max_length=20)
    sector: str | None = Field(default=None, max_length=80)


class Brand(BrandCreate):
    id: int
    created_at: datetime


class EnrichmentEvidence(BaseModel):
    """Evidence supplied by a trusted, isolated enrichment worker.

    The API intentionally accepts summaries instead of crawling arbitrary URLs.
    This preserves a security boundary between the public API and a future crawler.
    """

    registration_age_days: int | None = Field(default=None, ge=0, le=36500)
    registrar: str | None = Field(default=None, max_length=255)
    registrant_country: str | None = Field(default=None, max_length=10)
    suspicious_tld: bool = False
    known_malicious_infrastructure: bool = False
    ssl_issuer: str | None = Field(default=None, max_length=255)
    ssl_cn_matches_domain: bool | None = Field(default=None)
    text_similarity: float | None = Field(default=None, ge=0, le=1)
    visual_similarity: float | None = Field(default=None, ge=0, le=1)
    credential_form_detected: bool = False
    external_form_action: bool = False
    suspicious_form_actions: list[str] = Field(default_factory=list)


class ScanRequest(BaseModel):
    url: str = Field(min_length=3, max_length=2048)
    enrichment: EnrichmentEvidence = Field(default_factory=EnrichmentEvidence)

    @field_validator("url")
    @classmethod
    def reject_controls(cls, value: str) -> str:
        if any(ord(character) < 32 for character in value):
            raise ValueError("URL must not contain control characters")
        return value.strip()


class Explanation(BaseModel):
    signal: str
    contribution: float
    detail: str


class ScanResult(BaseModel):
    id: int
    submitted_url: str
    normalized_domain: str
    target_brand: Brand | None
    brand_confidence: float
    risk_score: float
    risk_level: Literal["low", "suspicious", "high", "critical"]
    status: Verdict
    model_version: str
    explanation: list[Explanation]
    domain_age_days: int | None = None
    visual_match_score: float | None = None
    ssl_certificate_match: bool | None = None
    suspicious_keywords: list[str] = Field(default_factory=list)
    created_at: datetime


class VerdictUpdate(BaseModel):
    verdict: Verdict
    note: str | None = Field(default=None, max_length=1000)

