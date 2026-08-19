from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Query, Response, status
from fastapi.middleware.cors import CORSMiddleware

from app.auth import issue_access_token, require_role
from app.config import MODEL_VERSION, settings
from app.domain import UnsafeTarget, normalize_url
from app.schemas import Brand, BrandCreate, ScanRequest, ScanResult, VerdictUpdate
from app.scoring import score
from app.storage import Repository
from prometheus_client import CONTENT_TYPE_LATEST, Counter, generate_latest


repository = Repository()


@asynccontextmanager
async def lifespan(_: FastAPI):
    repository.initialize()
    yield


app = FastAPI(title="Lookalike Radar API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

REQUESTS = Counter("lookalike_api_requests_total", "API requests by method and path", ["method", "path"])


def serialize_brand(brand) -> dict:
    return {"id": brand.id, "name": brand.name, "official_domain": brand.official_domain, "aliases": brand.aliases, "sector": brand.sector, "created_at": brand.created_at}


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "model_version": MODEL_VERSION, "mode": "offline_analysis"}


@app.get("/metrics", include_in_schema=False)
def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/auth/token")
def login(username: str, password: str) -> dict:
    if username != settings.admin_username or password != settings.admin_password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": issue_access_token(username, "admin"), "token_type": "bearer"}


@app.get("/brands", response_model=list[Brand])
def list_brands():
    return [serialize_brand(brand) for brand in repository.list_brands()]


@app.post("/brands", response_model=Brand, status_code=status.HTTP_201_CREATED)
def create_brand(brand: BrandCreate, _: dict = Depends(require_role("admin"))):
    try:
        return serialize_brand(repository.create_brand(brand))
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error


@app.post("/scans", response_model=ScanResult, status_code=status.HTTP_201_CREATED)
def create_scan(request: ScanRequest, _: dict = Depends(require_role("analyst", "admin"))):
    REQUESTS.labels("POST", "/scans").inc()
    try:
        normalized = normalize_url(request.url)
    except (ValueError, UnsafeTarget) as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    detection = score(normalized, repository.list_brands(), request.enrichment)
    return repository.create_scan(request.url, normalized.host, detection, request.enrichment, MODEL_VERSION)


@app.get("/scans", response_model=list[ScanResult])
def list_scans(limit: int = Query(default=100, ge=1, le=500)):
    return repository.list_scans(limit)


@app.get("/scans/{scan_id}", response_model=ScanResult)
def get_scan(scan_id: int):
    try:
        return repository.get_scan(scan_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail="Scan not found") from error


@app.put("/scans/{scan_id}/verdict", response_model=ScanResult)
def update_verdict(scan_id: int, update: VerdictUpdate, _: dict = Depends(require_role("analyst", "admin"))):
    try:
        return repository.record_verdict(scan_id, update.verdict, update.note)
    except KeyError as error:
        raise HTTPException(status_code=404, detail="Scan not found") from error


@app.get("/exports/scans.json")
def export_json():
    return repository.list_scans(limit=500)


@app.get("/exports/scans.csv")
def export_csv():
    return Response(repository.export_csv(), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=scans.csv"})
