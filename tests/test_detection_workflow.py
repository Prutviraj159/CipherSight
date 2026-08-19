import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.detection.contracts import AnalystVerdictRequest, BrandCandidate, CreateScanRequest, DetectionSignals, VerdictType
from app.detection.scoring import RiskScorer
from app.detection.workflow import DetectionWorkflow


@pytest.fixture
def signal_fixture() -> dict:
    return json.loads((Path(__file__).parent / "fixtures" / "detection_signals.json").read_text(encoding="utf-8"))


@pytest.fixture
def brands() -> list[BrandCandidate]:
    return [BrandCandidate(name="State Bank of India", domains=["sbi.co.in"])]


def test_high_risk_fixture_is_explainable(signal_fixture: dict, brands: list[BrandCandidate]) -> None:
    assessment = RiskScorer().assess("sbi-secure-login.example", DetectionSignals.model_validate(signal_fixture["high_risk"]), brands)
    assert assessment.score > 0.8
    assert assessment.contributions
    assert assessment.limitations


def test_low_risk_fixture_scores_below_threshold(signal_fixture: dict, brands: list[BrandCandidate]) -> None:
    assessment = RiskScorer().assess("legitimate.example", DetectionSignals.model_validate(signal_fixture["low_risk"]), brands)
    assert assessment.score < 0.2


def test_invalid_scan_input_is_rejected() -> None:
    with pytest.raises(ValidationError):
        CreateScanRequest(domain="not-a-fqdn")


class FixtureQueue:
    async def enqueue(self, scan_id, domain) -> None:
        self.item = (scan_id, domain)


class FixtureStore:
    def __init__(self) -> None:
        self.alerts = {}
        self.saved = []

    async def create(self, alert) -> None:
        self.alerts[alert.scan_id] = alert

    async def get(self, scan_id):
        return self.alerts.get(scan_id)

    async def save_verdict(self, alert, verdict, audit) -> None:
        self.alerts[alert.scan_id] = alert
        self.saved.append((verdict, audit))

    async def list(self):
        return list(self.alerts.values())


@pytest.mark.asyncio
async def test_verdict_lifecycle_creates_audit_entry() -> None:
    workflow = DetectionWorkflow(FixtureQueue(), FixtureStore())
    alert = await workflow.create_scan(CreateScanRequest(domain="safe-example.test"))
    verdict, audit = await workflow.submit_verdict(alert.scan_id, uuid4(), AnalystVerdictRequest(verdict=VerdictType.NEEDS_REVIEW, note="Fixture review"))
    assert verdict.scan_id == alert.scan_id
    assert audit.action == "analyst_verdict_submitted"
    assert (await workflow.get_scan(alert.scan_id)).status == "verdict_submitted"
