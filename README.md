# Lookalike Radar backend MVP

An offline-safe, explainable FastAPI vertical slice for early detection of phishing lookalike domains. It was derived from the supplied research repository and its companion SIH research report.

## What it provides

- Protected brand catalogue with seeded demonstration brands.
- Strict HTTP(S), IDNA and hostname validation; IP-address targets and credential-bearing URLs are rejected.
- Explainable hybrid baseline: lexical brand similarity, punycode, domain structure, sensitive terms, TLD, registration, infrastructure, text, visual, and form signals.
- Persistent scans, analyst verdicts and audit records using SQLite for the local MVP.
- JSON and CSV exports; model-version tracking on every scan.
- A defined security boundary: this public API never crawls a submitted target. A future isolated worker supplies normalized enrichment summaries.

## Run

Production-like local deployment (PostgreSQL plus Alembic migration):

```powershell
docker compose up --build
```

For the SQLite-backed test harness only:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python -m pytest -q
```

Set `DATABASE_URL`, a 32-byte-or-longer `JWT_SECRET`, `ADMIN_USERNAME`, and `ADMIN_PASSWORD` before starting the API outside Docker. Obtain a bearer token from `POST /auth/token`, then send it in `Authorization: Bearer <token>` for scan creation and analyst verdicts.

```powershell
docker compose logs api
```

## Example scan

```powershell
$token = (Invoke-RestMethod -Method Post -Uri 'http://127.0.0.1:8000/auth/token?username=admin&password=change-me').access_token
$headers = @{ Authorization = "Bearer $token" }
$body = @{ url = 'https://sbi-secure-login.zip/verify'; enrichment = @{ registration_age_days = 2; visual_similarity = 0.90; credential_form_detected = $true; external_form_action = $true } } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/scans -Headers $headers -ContentType 'application/json' -Body $body
```

## Production hardening path

Replace SQLite with PostgreSQL, use the Public Suffix List for eTLD+1 extraction, authenticate and rate-limit every write endpoint, move enrichment to Celery/Redis workers, and run Playwright in a disposable sandbox with egress controls, SSRF protection, download blocking, redirect/time/page limits, and no credential submission. Tune score weights on held-out, time-split evaluation data instead of treating this baseline as a production classifier.

## Phase 6 Deployment Runbook

### Secrets Management
- Do NOT hardcode JWT_SECRET, ADMIN_PASSWORD, or Database credentials in source control or docker-compose.yml for production.
- Production secrets should be injected via a secure Vault and passed into the environment strictly at runtime.

### Backup Strategy
- PostgreSQL Data: Execute daily pg_dump snapshots. Configure WAL archiving to an isolated S3 bucket for point-in-time recovery.
- Evidence Storage: Ensure PDF reports and raw HTML/screenshot artifacts are stored in a WORM compliant object storage bucket.

### Migrations & Rollbacks
- Apply migrations using alembic upgrade head exclusively through an automated CI/CD pipeline after passing test gates.
- Never drop columns; deprecate them first, then drop them in a subsequent major release to avoid breaking running API containers.

### Execution Profiles
The repository now natively supports Docker compose profiles.
- API & DB Only: docker-compose up -d
- Include Worker: docker-compose --profile worker up -d
- Run Tests Offline: docker-compose --profile test run test
