from __future__ import annotations

import csv
import io

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.config import settings
from app.db import AuditRecord, Base, BrandRecord, ScanRecord, SessionLocal
from app.schemas import BrandCreate, EnrichmentEvidence
from app.scoring import CandidateBrand, ScoredDetection


class Repository:
    """Transactional PostgreSQL persistence facade."""

    def initialize(self) -> None:
        if settings.auto_create_schema:  # test-only; production runs Alembic.
            from app.db import engine
            Base.metadata.create_all(engine)
        with SessionLocal.begin() as session:
            if session.scalar(select(BrandRecord.id).limit(1)) is None:
                session.add_all([
                    BrandRecord(name="State Bank of India", official_domain="sbi.co.in", aliases=["sbi", "statebank"], sector="banking"),
                    BrandRecord(name="Government of India", official_domain="india.gov.in", aliases=["india", "govindia"], sector="government"),
                    BrandRecord(name="Example Payments", official_domain="example-payments.in", aliases=["examplepayments", "expay"], sector="payments"),
                ])

    @staticmethod
    def _brand(record: BrandRecord) -> CandidateBrand:
        return CandidateBrand(record.id, record.name, record.official_domain, record.aliases, record.sector, record.created_at.isoformat())

    def create_brand(self, brand: BrandCreate) -> CandidateBrand:
        try:
            with SessionLocal.begin() as session:
                record = BrandRecord(name=brand.name, official_domain=brand.official_domain.lower(), aliases=brand.aliases, sector=brand.sector)
                session.add(record)
                session.flush()
                return self._brand(record)
        except IntegrityError as error:
            raise ValueError("Brand name or official domain already exists") from error

    def list_brands(self) -> list[CandidateBrand]:
        with SessionLocal() as session:
            return [self._brand(row) for row in session.scalars(select(BrandRecord).order_by(BrandRecord.name)).all()]

    def create_scan(self, submitted_url: str, normalized_domain: str, result: ScoredDetection, evidence: EnrichmentEvidence, model_version: str) -> dict:
        with SessionLocal.begin() as session:
            record = ScanRecord(submitted_url=submitted_url, normalized_domain=normalized_domain, brand_id=result.brand.id if result.brand else None, brand_confidence=result.brand_confidence, risk_score=result.risk_score, risk_level=result.risk_level, model_version=model_version, evidence=evidence.model_dump(mode="json"), explanation=[item.model_dump() for item in result.explanation])
            session.add(record)
            session.flush()
            session.add(AuditRecord(event_type="scan_created", scan_id=record.id, payload={"model_version": model_version}))
            scan_id = record.id
        return self.get_scan(scan_id)

    @staticmethod
    def _scan(record: ScanRecord, brand: BrandRecord | None) -> dict:
        target = None if brand is None else {"id": brand.id, "name": brand.name, "official_domain": brand.official_domain, "aliases": brand.aliases, "sector": brand.sector, "created_at": brand.created_at.isoformat()}
        return {
            "id": record.id, "submitted_url": record.submitted_url, "normalized_domain": record.normalized_domain,
            "target_brand": target, "brand_confidence": record.brand_confidence, "risk_score": record.risk_score,
            "risk_level": record.risk_level, "status": record.status, "model_version": record.model_version,
            "explanation": record.explanation, "created_at": record.created_at.isoformat(),
            "domain_age_days": record.evidence.get("registration_age_days"),
            "visual_match_score": record.evidence.get("visual_similarity"),
            "ssl_certificate_match": record.evidence.get("ssl_cn_matches_domain"),
            "suspicious_keywords": record.evidence.get("suspicious_form_actions", [])
        }

    def get_scan(self, scan_id: int) -> dict:
        with SessionLocal() as session:
            record = session.get(ScanRecord, scan_id)
            if record is None:
                raise KeyError(scan_id)
            return self._scan(record, session.get(BrandRecord, record.brand_id) if record.brand_id else None)

    def list_scans(self, limit: int = 100) -> list[dict]:
        with SessionLocal() as session:
            rows = session.scalars(select(ScanRecord).order_by(ScanRecord.created_at.desc()).limit(limit)).all()
            return [self._scan(row, session.get(BrandRecord, row.brand_id) if row.brand_id else None) for row in rows]

    def record_verdict(self, scan_id: int, verdict: str, note: str | None) -> dict:
        with SessionLocal.begin() as session:
            record = session.get(ScanRecord, scan_id)
            if record is None:
                raise KeyError(scan_id)
            record.status = verdict
            session.add(AuditRecord(event_type="analyst_verdict", scan_id=scan_id, payload={"verdict": verdict, "note": note}))
        return self.get_scan(scan_id)

    def export_csv(self) -> str:
        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, fieldnames=["id", "submitted_url", "normalized_domain", "brand", "risk_score", "risk_level", "status", "model_version", "created_at"])
        writer.writeheader()
        for scan in self.list_scans(500):
            writer.writerow({"id": scan["id"], "submitted_url": scan["submitted_url"], "normalized_domain": scan["normalized_domain"], "brand": scan["target_brand"]["name"] if scan["target_brand"] else "", "risk_score": scan["risk_score"], "risk_level": scan["risk_level"], "status": scan["status"], "model_version": scan["model_version"], "created_at": scan["created_at"]})
        return buffer.getvalue()
