"""Reporting contracts for PDF generation and evidence manifest.

No external URL fetch or ML training occurs in this module.
"""
from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ReportFormat(StrEnum):
    PDF = "pdf"
    JSON = "json"
    CSV = "csv"


class ReportStatus(StrEnum):
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


class EvidenceCategory(StrEnum):
    LEXICAL = "lexical"
    ENRICHMENT = "enrichment"
    INFRASTRUCTURE = "infrastructure"
    VISUAL = "visual"
    ANALYST = "analyst"


class EvidenceItem(BaseModel):
    """A single piece of evidence referenced in a report manifest."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    id: UUID = Field(default_factory=uuid4)
    category: EvidenceCategory
    source: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=1000)
    collected_at: datetime
    sha256_checksum: str | None = Field(default=None, min_length=64, max_length=64)
    file_path: str | None = Field(default=None, max_length=500)
    metadata: dict[str, str | int | float | bool] = Field(default_factory=dict)

    @field_validator("sha256_checksum")
    @classmethod
    def validate_hex(cls, value: str | None) -> str | None:
        if value is None:
            return value
        if not all(c in "0123456789abcdef" for c in value.lower()):
            raise ValueError("sha256_checksum must be a valid hex string")
        return value.lower()


class EvidenceManifest(BaseModel):
    """Immutable manifest of evidence items attached to a report."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    manifest_id: UUID = Field(default_factory=uuid4)
    scan_id: UUID
    created_at: datetime = Field(default_factory=datetime.utcnow)
    items: list[EvidenceItem] = Field(default_factory=list, max_length=100)

    def by_category(self, category: EvidenceCategory) -> list[EvidenceItem]:
        return [item for item in self.items if item.category == category]

    def checksums_present(self) -> bool:
        return all(item.sha256_checksum is not None for item in self.items)


class ReportSection(BaseModel):
    """A section within a generated report."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    title: str = Field(min_length=1, max_length=120)
    body: str = Field(min_length=1, max_length=50000)
    order: int = Field(ge=0, le=100)


class ReportRequest(BaseModel):
    """Request to generate a report for a scan."""

    model_config = ConfigDict(extra="forbid")
    scan_id: UUID
    format: ReportFormat = ReportFormat.PDF
    include_evidence: bool = True
    analyst_note: str | None = Field(default=None, max_length=2000)


class ReportMetadata(BaseModel):
    """Metadata for a generated report."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    report_id: UUID = Field(default_factory=uuid4)
    scan_id: UUID
    format: ReportFormat
    status: ReportStatus = ReportStatus.PENDING
    model_version: str = Field(min_length=1, max_length=80)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None
    file_path: str | None = Field(default=None, max_length=500)
    error_message: str | None = Field(default=None, max_length=2000)

    def mark_completed(self, file_path: str) -> "ReportMetadata":
        return self.model_copy(update={"status": ReportStatus.COMPLETED, "completed_at": datetime.utcnow(), "file_path": file_path})

    def mark_failed(self, error_message: str) -> "ReportMetadata":
        return self.model_copy(update={"status": ReportStatus.FAILED, "error_message": error_message})


class GeneratedReport(BaseModel):
    """A completed report with metadata, sections, and manifest."""

    model_config = ConfigDict(extra="forbid")
    metadata: ReportMetadata
    sections: list[ReportSection] = Field(default_factory=list)
    manifest: EvidenceManifest | None = None
