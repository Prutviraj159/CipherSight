# Phase 6 Execution Results

## Commands Executed
```bash
# Build and Start Services
docker-compose build
docker-compose --profile worker --profile test --profile api up -d --force-recreate

# Run Migrations
docker compose exec api alembic upgrade head

# Run Pytest (Fixed PYTHONPATH)
docker compose logs test

# Execute API Workflows (via httpx)
docker compose exec api python test_api.py
```

## Container Status
- **lookalike-radar-api-1**: RUNNING (Port 8000)
- **lookalike-radar-worker-1**: RUNNING (Mocked sleep)
- **lookalike-radar-db-1**: RUNNING (Port 5432)
- **lookalike-radar-test-1**: STOPPED (Completed test execution)

## Migration Output
Alembic successfully ran inside the `api` container on startup and via manual `upgrade head`. Schema includes all relevant tracking tables. 

## Test Output
```text
19 passed, 1 warning in 0.76s
```
*(1 SQLite operational error was fixed by removing the hardcoded `sqlite:///:memory:` override and allowing the tests to cleanly target the Postgres container).*

## HTTP Request/Response Summaries

**4. API Health Check**
- Request: `GET /health`
- Status: `200 OK`
- Response: `{"status":"ok","model_version":"lexical-fusion-v1","mode":"offline_analysis"}`

**5. Authentication Workflow**
- Request: `POST /auth/token`
- Status: `200 OK`
- Response: Token successfully issued (`eyJhbG...`).

**6. Brand Catalogue Workflow**
- Request: `POST /brands`
- Status: `201 Created`
- Response: `{"name":"Docker Brand","official_domain":"docker.com", ... "id":4}`
- Request: `GET /brands`
- Status: `200 OK`
- Response: Array of 4 brands retrieved.

**7. Mocked Ingestion Workflow**
- Request: `POST /scans` (Payload: `http://evil-test.com`)
- Status: `201 Created`
- Response: `{"id":1,"submitted_url":"http://evil-test.com","normalized_domain":"evil-test.com", ... "risk_score":0.08,"status":"needs_review"}`

**8. Detection & Verdict Workflow**
- Request: `PUT /scans/1/verdict` (Payload: `{"verdict": "phishing"}`)
- Status: `200 OK`
- Response: `{"status":"phishing", ...}`

**9. Reporting Workflow (Exports)**
- Request: `GET /exports/scans.json`
- Status: `200 OK`
- Request: `GET /exports/scans.csv`
- Status: `200 OK`
- Note: The PDF generator contract (`app/reporting/generator.py` and `manifest.py`) has been verified and built by Claude, but is not exposed to a direct API route in `app/main.py`. As per instructions to strictly retain the provided implementation, no new API routes were forcefully injected.

## Errors and Root Cause
1. **ModuleNotFoundError ('app') in Pytest**: The `test` docker container could not resolve local packages. **Root Cause**: The `PYTHONPATH` was not mapped to `/service`. **Fix**: Added `PYTHONPATH=/service` to the `docker-compose.yml` test command.
2. **SQLite OperationalError**: `test_api.py` was hardcoded to hit `./data/test_lookalike.db`, causing schema drops to fail. **Fix**: Stripped the SQLite override so tests correctly utilize the robust PostgreSQL container provided in the `test` profile.

## Services Left Running
- **API**, **Worker**, and **PostgreSQL Database** remain safely running in the background. 

