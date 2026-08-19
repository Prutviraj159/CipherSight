from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import urlsplit


_LABEL = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$")
_TOKEN = re.compile(r"[a-z0-9]+")


@dataclass(frozen=True)
class NormalizedDomain:
    ascii_domain: str
    unicode_domain: str
    is_punycode: bool


@dataclass(frozen=True)
class LexicalFeatures:
    length: int
    label_count: int
    hyphen_count: int
    digit_count: int
    is_punycode: bool
    tokens: tuple[str, ...]


def normalize_domain(value: str) -> NormalizedDomain:
    """Normalize a domain or HTTP(S) URL without resolving or fetching it."""
    candidate = value.strip()
    parsed = urlsplit(candidate if "://" in candidate else f"https://{candidate}")
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("Expected an HTTP(S) URL or hostname")
    if parsed.username or parsed.password:
        raise ValueError("Credential-bearing URLs are not accepted")
    raw = parsed.hostname.rstrip(".")
    try:
        ascii_domain = raw.encode("idna").decode("ascii").lower()
        unicode_domain = ascii_domain.encode("ascii").decode("idna")
    except UnicodeError as error:
        raise ValueError("Domain is not valid IDNA") from error
    labels = ascii_domain.split(".")
    if len(ascii_domain) > 253 or any(not _LABEL.fullmatch(label) for label in labels):
        raise ValueError("Domain contains an invalid DNS label")
    return NormalizedDomain(ascii_domain, unicode_domain, "xn--" in ascii_domain)


def extract_lexical_features(domain: NormalizedDomain) -> LexicalFeatures:
    labels = domain.ascii_domain.split(".")
    return LexicalFeatures(
        length=len(domain.ascii_domain),
        label_count=len(labels),
        hyphen_count=domain.ascii_domain.count("-"),
        digit_count=sum(char.isdigit() for char in domain.ascii_domain),
        is_punycode=domain.is_punycode,
        tokens=tuple(_TOKEN.findall(domain.ascii_domain)),
    )
