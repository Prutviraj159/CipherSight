from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Protocol

from app.ingestion.contracts import DnsSnapshot, RdapSnapshot, TlsSnapshot


class EnrichmentProvider(ABC):
    """Worker-only boundary for authorized enrichment integrations.

    Implementations may call only their configured RDAP, DNS, or TLS provider.
    They must not navigate to the submitted domain or fetch its webpage.
    """

    @abstractmethod
    async def fetch_rdap(self, domain: str) -> RdapSnapshot: ...

    @abstractmethod
    async def fetch_dns(self, domain: str) -> DnsSnapshot: ...

    @abstractmethod
    async def fetch_tls(self, domain: str) -> TlsSnapshot: ...


class EvidenceCache(Protocol):
    """Cache adapter contract; Redis is a deployment implementation, not an API dependency."""

    async def get(self, key: str) -> str | None: ...

    async def set(self, key: str, value: str, ttl_seconds: int) -> None: ...


def cache_key(domain: str, provider: str) -> str:
    """Return the Phase 3 cache namespace for provider-neutral evidence."""
    return f"enrichment:{domain}:{provider}"


class RdapProvider(Protocol):
    async def lookup(self, domain: str) -> RdapSnapshot: ...


class DnsProvider(Protocol):
    async def lookup(self, domain: str) -> DnsSnapshot: ...


class TlsProvider(Protocol):
    async def lookup(self, domain: str) -> TlsSnapshot: ...


class ProviderNotConfigured(RuntimeError):
    """Raised by a deployment worker when an authorized provider is absent."""
