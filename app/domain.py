from __future__ import annotations

import ipaddress
import re
from dataclasses import dataclass
from urllib.parse import urlsplit


SUSPICIOUS_WORDS = {"login", "verify", "secure", "update", "signin", "account", "support"}
RISKY_TLDS = {"zip", "mov", "top", "xyz", "click", "rest", "country"}
HOST_LABEL = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$")


class UnsafeTarget(ValueError):
    """Raised when input would target an IP address instead of a public hostname."""


@dataclass(frozen=True)
class NormalizedUrl:
    submitted_url: str
    host: str
    unicode_host: str
    is_punycode: bool
    path_tokens: set[str]
    has_ip_host: bool


def normalize_url(value: str) -> NormalizedUrl:
    candidate = value if "://" in value else f"https://{value}"
    parsed = urlsplit(candidate)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("URL must be an absolute HTTP or HTTPS URL with a hostname")
    if parsed.username or parsed.password:
        raise ValueError("URLs containing credentials are not accepted")

    raw_host = parsed.hostname.rstrip(".")
    try:
        address = ipaddress.ip_address(raw_host)
    except ValueError:
        address = None
    if address is not None:
        raise UnsafeTarget("IP-address targets are rejected; submit a public domain name")

    try:
        ascii_host = raw_host.encode("idna").decode("ascii").lower()
        unicode_host = ascii_host.encode("ascii").decode("idna")
    except UnicodeError as error:
        raise ValueError("Hostname is not valid IDNA") from error
    if len(ascii_host) > 253 or any(not HOST_LABEL.fullmatch(label) for label in ascii_host.split(".")):
        raise ValueError("Hostname contains an invalid DNS label")

    tokens = set(re.findall(r"[a-z0-9]+", f"{ascii_host}{parsed.path}".lower()))
    return NormalizedUrl(
        submitted_url=value,
        host=ascii_host,
        unicode_host=unicode_host,
        is_punycode="xn--" in ascii_host,
        path_tokens=tokens,
        has_ip_host=False,
    )


def registered_label(host: str) -> str:
    """A conservative label used for MVP lexical comparison.

    Production should use a Public Suffix List implementation to derive eTLD+1.
    """
    labels = host.split(".")
    return labels[-2] if len(labels) >= 2 else labels[0]


def normalized_levenshtein(left: str, right: str) -> float:
    if left == right:
        return 1.0
    if not left or not right:
        return 0.0
    previous = list(range(len(right) + 1))
    for i, source in enumerate(left, start=1):
        current = [i]
        for j, target in enumerate(right, start=1):
            current.append(min(current[-1] + 1, previous[j] + 1, previous[j - 1] + (source != target)))
        previous = current
    return 1.0 - previous[-1] / max(len(left), len(right))

