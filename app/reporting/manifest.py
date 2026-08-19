"""Evidence manifest builder and validator.

Provides utilities to construct, validate, and serialize evidence manifests
for inclusion in reports and audit trails.
"""
from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Final

from app.reporting.contracts import EvidenceCategory, EvidenceItem, EvidenceManifest

logger = logging.getLogger(__name__)

MAX_MANIFEST_ITEMS: Final[int] = 100
MAX_DESCRIPTION_LENGTH: Final[int] = 1000


class ManifestBuilder:
    """Fluent builder for constructing evidence manifests.

    Usage:
        builder = ManifestBuilder(scan_id)
        builder.add_lexical(source="domain_normalizer", description="...")
        builder.add_enrichment(source="rdap_provider", description="...")
        manifest = builder.build()
    """

    def __init__(self, scan_id: str) -> None:
        self._scan_id = scan_id
        self._items: list[EvidenceItem] = []

    def add(
        self,
        category: EvidenceCategory,
        source: str,
        description: str,
        collected_at: datetime | None = None,
        sha256_checksum: str | None = None,
        file_path: str | None = None,
        metadata: dict[str, str | int | float | bool] | None = None,
    ) -> "ManifestBuilder":
        """Add an evidence item to the manifest."""
        if len(self._items) >= MAX_MANIFEST_ITEMS:
            logger.warning(
                "manifest_item_limit_reached",
                extra={"scan_id": self._scan_id, "limit": MAX_MANIFEST_ITEMS},
            )
            return self

        item = EvidenceItem(
            category=category,
            source=source,
            description=description[:MAX_DESCRIPTION_LENGTH],
            collected_at=collected_at or datetime.utcnow(),
            sha256_checksum=sha256_checksum,
            file_path=file_path,
            metadata=metadata or {},
        )
        self._items.append(item)
        return self

    def add_lexical(
        self,
        source: str,
        description: str,
        **kwargs,
    ) -> "ManifestBuilder":
        return self.add(EvidenceCategory.LEXICAL, source, description, **kwargs)

    def add_enrichment(
        self,
        source: str,
        description: str,
        **kwargs,
    ) -> "ManifestBuilder":
        return self.add(EvidenceCategory.ENRICHMENT, source, description, **kwargs)

    def add_infrastructure(
        self,
        source: str,
        description: str,
        **kwargs,
    ) -> "ManifestBuilder":
        return self.add(EvidenceCategory.INFRASTRUCTURE, source, description, **kwargs)

    def add_visual(
        self,
        source: str,
        description: str,
        **kwargs,
    ) -> "ManifestBuilder":
        return self.add(EvidenceCategory.VISUAL, source, description, **kwargs)

    def add_analyst(
        self,
        source: str,
        description: str,
        **kwargs,
    ) -> "ManifestBuilder":
        return self.add(EvidenceCategory.ANALYST, source, description, **kwargs)

    def build(self) -> EvidenceManifest:
        """Build and return the evidence manifest."""
        manifest = EvidenceManifest(
            scan_id=self._scan_id,
            items=self._items,
        )
        logger.info(
            "manifest_built",
            extra={
                "scan_id": str(self._scan_id),
                "item_count": len(self._items),
                "categories": list({item.category.value for item in self._items}),
            },
        )
        return manifest


def validate_manifest_files(manifest: EvidenceManifest, base_dir: Path) -> list[str]:
    """Validate that all file_path entries in the manifest exist on disk.

    Returns a list of missing file paths (empty if all present).
    """
    missing: list[str] = []
    for item in manifest.items:
        if item.file_path:
            resolved = base_dir / item.file_path
            if not resolved.exists():
                missing.append(str(resolved))
                logger.warning(
                    "manifest_file_missing",
                    extra={"scan_id": str(manifest.scan_id), "file_path": str(resolved)},
                )
    return missing
