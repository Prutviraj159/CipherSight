# Lookalike Radar backend delivery

## Research references

The supplied 50-page `Research.pdf` is a resource repository rather than a product specification. It prioritizes VisualPhishNet (visual zero-day comparison), BadDomains (registration-stage detection), newly registered-domain studies, RDAP and certificate-transparency data, PhishTank/OpenPhish/URLhaus feeds, Unicode TR39, WHATWG URL/HTML, OWASP SSRF/input-validation guidance, NIST AI RMF, FastAPI and Docker documentation.

The companion SIH report turns those references into the required workflow: ingest newly registered domains; compare them with protected brands; enrich registration/DNS/TLS data; safely analyze page artefacts; fuse lexical, content, visual and infrastructure evidence; identify the target brand; retain explanations; support analyst verdicts; export evidence. It also explicitly prohibits credential submission, unverified automatic takedowns, and uncontrolled scanning.

## Technical tasks derived from the research

1. Maintain a verified protected-brand catalogue with official domains, aliases and reference assets.
2. Normalize input safely, including IDNA/punycode handling and URL validation.
3. Use an explainable initial score before any trained model is deployed.
4. Persist score inputs, outputs, model version, analyst feedback and audit events.
5. Separate the public API from isolated enrichment/crawl workers; do not let API input trigger unrestricted server-side fetches.
6. Expose analyst and reporting workflows through stable JSON/CSV APIs.
7. Evaluate future models with temporal, brand-held-out, campaign-held-out and adversarial visual splits; report measured metrics only.

## Production implementation plan

1. Run `docker compose up --build` to provision PostgreSQL, execute Alembic `0001_initial`, and start the API. Change every sample secret before use.
2. Assign the `admin` role only to catalogue administrators; use the `analyst` role for scanning and verdict workflows. Add an identity-provider integration before public deployment.
3. Schedule feed/RDAP/DNS/TLS ingestion as separate retrying workers. Persist raw provenance and expiry metadata, and cache each external response.
4. Implement the crawler behind `app/workers.py` in an isolated container with network egress policy, private-address blocking after DNS resolution, download blocking, credential prohibition, redirect/page/time limits, and artifact sanitization.
5. Feed sanitized text, DOM, form and visual similarities to `POST /scans`; calibrate score weights only against held-out data.
6. Add Playwright, Redis/Celery, PDF reporting, object storage, and PostgreSQL backup/restore drills before claiming the complete research architecture.

## Code snippets

- `app/domain.py`: validation, IDNA normalization and lexical primitives.
- `app/scoring.py`: deterministic multimodal risk fusion with per-signal explanations.
- `app/db.py` and `migrations/`: SQLAlchemy PostgreSQL records, connection pooling and versioned Alembic schema.
- `app/auth.py`: signed, expiring JWTs with admin/analyst authorization checks.
- `app/storage.py`: transactional persistence, seeded brand catalogue and audit trail.
- `app/workers.py`: retry budget and an explicit safe-crawl integration boundary.
- `app/main.py`: typed FastAPI routes, consistent errors, exports and Prometheus metrics.
- `tests/test_api.py`: risk-analysis/verdict flow and SSRF-relevant IP rejection.

## Execution results

Executed locally in the available environment (an Antigravity runtime was not available in this task). The declared FastAPI runtime was installed into `.venv`; after the PostgreSQL/JWT migration, the isolated test suite completed with `2 passed` in 0.66 seconds. The only output was a non-failing upstream Starlette TestClient deprecation warning.

A loopback Uvicorn run accepted `POST /scans` for the controlled fixture `https://sbi-secure-login.zip/verify` and returned `201 Created`. It identified `State Bank of India` at brand confidence `0.90`, produced a `critical` risk score of `1.00`, recorded eight ranked explanations, and retained `needs_review` pending an analyst decision. The server log is captured locally in `logs/uvicorn.log`; startup diagnostics are in `logs/uvicorn-error.log`. No external or suspicious target was contacted.

Docker Engine `29.7.2` is available. The `docker compose up --build -d` request that would have started the PostgreSQL/API stack was not approved, so PostgreSQL migration and container-level execution remain unverified in this workspace. This is a deployment-verification gap, not a successful Antigravity run.

## Verification notes

Implemented: domain ingestion, protected brands, IDNA/punycode signal, lexical similarity, explainable fusion, enrichment contract, analyst verdicts, audit logging, JSON/CSV exports and model tracking.

Deferred deliberately: RDAP/DNS/TLS clients, queue workers, browser capture, visual/HTML extractors, PostgreSQL, authentication, reports in PDF and trained ML. These need provider credentials, isolated execution infrastructure, approved datasets and measured calibration. The MVP supports those components through its enrichment contract without weakening the API security boundary. In production, replace the MVP registered-label heuristic with a Public Suffix List implementation and calibrate the current deterministic weights using the prescribed held-out datasets.
