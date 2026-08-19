"""Pure validation helpers for the crawler worker boundary."""
from __future__ import annotations

import ipaddress
from collections.abc import Iterable

from app.ingestion.normalization import normalize_domain


BLOCKED_HOSTS = {"localhost", "localhost.localdomain", "metadata.google.internal"}
BLOCKED_SUFFIXES = (".local", ".internal", ".localhost")


class UnsafeCrawlTarget(ValueError):
    """The candidate would allow internal-network or non-domain crawling."""


def validate_crawl_domain(value: str) -> str:
    """Accept a public DNS name only; never resolve or fetch it here."""
    if "://" in value or "/" in value or "@" in value:
        raise UnsafeCrawlTarget("Crawl jobs accept a domain only, not a URL")
    try:
        address = ipaddress.ip_address(value.strip().strip("[]"))
    except ValueError:
        address = None
    if address is not None:
        raise UnsafeCrawlTarget("IP-address crawl targets are prohibited")
    normalized = normalize_domain(value)
    if normalized.ascii_domain in BLOCKED_HOSTS or normalized.ascii_domain.endswith(BLOCKED_SUFFIXES):
        raise UnsafeCrawlTarget("Internal hostnames are prohibited")
    return normalized.ascii_domain


def is_private_or_internal_address(value: str) -> bool:
    """Use after DNS resolution in the isolated worker to prevent SSRF rebinding."""
    address = ipaddress.ip_address(value)
    return not address.is_global


def validate_resolved_addresses(addresses: Iterable[str]) -> None:
    blocked = [address for address in addresses if is_private_or_internal_address(address)]
    if blocked:
        raise UnsafeCrawlTarget("Private or internal resolved address blocked")
