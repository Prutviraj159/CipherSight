"""Unregistered FastAPI router factory for Phase 5 adapters.

The composition root must attach JWT/RBAC dependencies and concrete queue/store
adapters before exposing these routes in a deployed API.
"""
from __future__ import annotations

from collections.abc import Callable
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response, StreamingResponse

from app.detection.contracts import AnalystVerdictRequest, CreateScanRequest, ScanAlert
from app.detection.workflow import DetectionWorkflow


def create_detection_router(workflow: DetectionWorkflow, current_analyst: Callable[..., UUID]) -> APIRouter:
    """Create routes using a trusted JWT/RBAC identity dependency.

    The caller must provide a dependency that returns the authenticated analyst
    UUID; API clients must never choose an analyst identity through query input.
    """
    router = APIRouter(tags=["detection"])

    @router.post("/scans", response_model=ScanAlert, status_code=status.HTTP_202_ACCEPTED)
    async def create_scan(request: CreateScanRequest) -> ScanAlert:
        return await workflow.create_scan(request)

    @router.get("/scans/{scan_id}", response_model=ScanAlert)
    async def get_scan(scan_id: UUID) -> ScanAlert:
        try:
            return await workflow.get_scan(scan_id)
        except KeyError as error:
            raise HTTPException(status_code=404, detail="Scan not found") from error

    @router.post("/scans/{scan_id}/verdict")
    async def submit_verdict(scan_id: UUID, request: AnalystVerdictRequest, analyst_id: UUID = Depends(current_analyst)) -> dict:
        try:
            verdict, audit = await workflow.submit_verdict(scan_id, analyst_id, request)
        except KeyError as error:
            raise HTTPException(status_code=404, detail="Scan not found") from error
        return {"verdict_id": verdict.id, "audit_log_id": audit.id}

    @router.get("/scans/export")
    async def export_scans(format: str = Query(pattern="^(json|csv)$")) -> Response:
        if format == "csv":
            return StreamingResponse(iter([await workflow.export_csv()]), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=scans.csv"})
        return Response(await workflow.export_json(), media_type="application/json")

    return router
