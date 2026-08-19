# Phase completion

## Phase 5 - detection and analyst workflow contracts

Implemented contracts only: deterministic explainable risk fusion, configurable signal weights and thresholds, brand ranking/confidence, typed scan alert and analyst-verdict workflows, audit-event contracts, JSON/CSV export interfaces, structured logging, and fixture-only tests. Verdict submission now transitions the alert lifecycle and requires a composition-provided trusted analyst identity dependency rather than a client-selected analyst ID.

No trained model, model-performance metric, production API route registration, persistence adapter, queue adapter, or external evidence retrieval is implemented. The visual signal is an optional future-worker input and is explicitly reported as unavailable when absent.

### External dependencies still required for Phase 5

- A persistent alert/verdict/audit repository with transactional writes and authorized analyst identity.
- A durable scan queue adapter connected to the Phase 3 ingestion and Phase 4 isolated worker flows.
- A configured API router with JWT/RBAC dependencies, pagination, and RFC 7807 error handlers.
- Approved reference text/logo/screenshot data and a measured evaluation process before any ML/visual accuracy statement or model deployment.
- Streaming-export storage/access controls for production JSON and CSV downloads.

## Phase 4 - safe crawling worker contracts

Implemented contracts only: a separate crawler queue interface, typed crawl job/options/result/audit schemas, domain-only validation, private/internal-host checks, post-resolution address validation, redirect/timeout/page-size/retry bounds, and fixture-only safety tests.

No browser, Playwright runtime, network resolver, downloader, external URL request, or credential submission is implemented. The API-facing submission service can only enqueue a validated domain contract.

### External dependencies still required for Phase 4

- A separately deployed non-root Playwright worker image with browser sandboxing, filesystem isolation, egress allow-listing, and resource limits.
- Queue and audit-sink adapters (for example Celery/Redis and PostgreSQL) with dead-letter handling.
- A DNS resolution layer that invokes `validate_resolved_addresses` immediately before every navigation and redirect.
- Sanitized artifact storage for screenshots, HTML, text, and form summaries; no raw credentials, cookies, or downloads may be stored.
- A browser route interceptor that blocks non-HTTP(S) schemes, downloads, private IP destinations, redirect overflow, and oversized responses.

## Phase 3 - domain ingestion and enrichment contracts

Implemented contracts only: validated feed items, local IDNA/punycode normalization, lexical feature extraction, queue/job states, provider protocols, cache-evidence schemas, retry policy, structured logging, and fixture-only tests.

No HTTP, DNS, RDAP, TLS, browser, or third-party API call is implemented in the API process. The ingestion service only validates a candidate and submits a provider-neutral job to an injected queue.

## External dependencies still required

- An approved new-domain or certificate-transparency feed adapter.
- Authorized RDAP, DNS, and TLS enrichment providers with rate limits, licensing, credentials, and cache policy.
- A durable queue implementation such as Celery/Redis, RabbitMQ, or a managed queue.
- A separately deployed worker with network policy, secret management, retries, dead-letter handling, and metrics.
- A Redis-compatible `EvidenceCache` implementation for the `enrichment:{domain}:{provider}` namespace and 24-hour TTL enforcement.
- Concrete `EnrichmentProvider` implementations for RDAP, DNS, and TLS, including circuit breaking and failure provenance.
- Public Suffix List support for production-grade registrable-domain analysis.

## Not implemented in this phase

Live provider clients, persistence for ingestion jobs/evidence cache, safe browser crawling, provider secrets, and execution verification are intentionally deferred to later phases. The Phase 3 API/queue boundary never fetches arbitrary URLs or directly accesses untrusted websites.


**Status: Phase 5 COMPLETE**
*(Interfaces requiring external provider implementations are explicitly tracked in the section above).*


## Phase 6 - Reporting, ML readiness, and deployment

Implemented contracts and workflows:
- Evidence Manifest builder and generator.
- PDF generation core utilizing immutable manifests with SHA-256 checksums.
- docker-compose.yml defining the pi, db, worker, and 	est isolated environments.
- API endpoints for /brands, /scans, /exports/scans.json, and /exports/scans.csv.
- Offline robust testing suite using pytest-asyncio successfully isolated to internal network fixtures.

### External dependencies still required for Phase 6
- Concrete implementation for generating physical PDFs bound to the pp/main.py routing layer.
- Fully wired Playwright/Crawling worker replacing the mock sleep process in docker-compose.yml.
- Certified production ML Model to replace the lexical-fusion-v1 deterministic offline rule-set, gated by Evaluation dataset/results schemas approval.
- An approved backup, migration, rollback, and production secrets manager integration before cloud deployment.
