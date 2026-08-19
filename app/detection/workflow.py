from __future__ import annotations

import csv
import io
import json
from datetime import datetime, timezone
from typing import Protocol
from uuid import UUID

import structlog

from app.detection.contracts import AnalystVerdict, AnalystVerdictRequest, CreateScanRequest, ScanAlert, ScanLifecycle, WorkflowAuditEvent

logger = structlog.get_logger(__name__)


class ScanQueue(Protocol):
    async def enqueue(self, scan_id: UUID, domain: str) -> None: ...


class AlertStore(Protocol):
    async def create(self, alert: ScanAlert) -> None: ...
    async def get(self, scan_id: UUID) -> ScanAlert | None: ...
    async def save_verdict(self, alert: ScanAlert, verdict: AnalystVerdict, audit: WorkflowAuditEvent) -> None: ...
    async def list(self) -> list[ScanAlert]: ...


class DetectionWorkflow:
    """API-neutral workflow; injected adapters provide persistence and queueing."""

    def __init__(self, queue: ScanQueue, store: AlertStore):
        self._queue = queue
        self._store = store

    async def create_scan(self, request: CreateScanRequest) -> ScanAlert:
        alert = ScanAlert(domain=request.domain, created_at=datetime.now(timezone.utc))
        await self._store.create(alert)
        await self._queue.enqueue(alert.scan_id, alert.domain)
        logger.info("scan_queued", scan_id=str(alert.scan_id), domain=alert.domain)
        return alert

    async def submit_verdict(self, scan_id: UUID, analyst_id: UUID, request: AnalystVerdictRequest) -> tuple[AnalystVerdict, WorkflowAuditEvent]:
        alert = await self._store.get(scan_id)
        if alert is None:
            raise KeyError(scan_id)
        now = datetime.now(timezone.utc)
        verdict = AnalystVerdict(scan_id=scan_id, analyst_id=analyst_id, verdict=request.verdict, note=request.note, created_at=now)
        updated_alert = alert.model_copy(update={"status": ScanLifecycle.VERDICT_SUBMITTED})
        audit = WorkflowAuditEvent(scan_id=scan_id, actor_id=analyst_id, action="analyst_verdict_submitted", timestamp=now, old_values={"status": alert.status.value}, new_values={"status": updated_alert.status.value, "verdict": request.verdict.value, "note": request.note or ""})
        await self._store.save_verdict(updated_alert, verdict, audit)
        logger.info("analyst_verdict_submitted", scan_id=str(scan_id), verdict=request.verdict, analyst_id=str(analyst_id))
        return verdict, audit

    async def get_scan(self, scan_id: UUID) -> ScanAlert:
        alert = await self._store.get(scan_id)
        if alert is None:
            raise KeyError(scan_id)
        return alert

    async def export_json(self) -> str:
        return json.dumps([alert.model_dump(mode="json") for alert in await self._store.list()])

    async def export_csv(self) -> str:
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=["scan_id", "domain", "status", "risk_score", "risk_level"])
        writer.writeheader()
        for alert in await self._store.list():
            writer.writerow({"scan_id": alert.scan_id, "domain": alert.domain, "status": alert.status, "risk_score": alert.assessment.score if alert.assessment else "", "risk_level": alert.assessment.level if alert.assessment else ""})
        return output.getvalue()
