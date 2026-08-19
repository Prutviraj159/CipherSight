"""PDF report generator using ReportLab.

No external URL fetch or ML training occurs in this module.
All report content is derived from validated internal scan records.
"""
from __future__ import annotations

import hashlib
import logging
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Final

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.reporting.contracts import (
    EvidenceItem,
    EvidenceManifest,
    GeneratedReport,
    ReportFormat,
    ReportMetadata,
    ReportSection,
    ReportStatus,
)

logger = logging.getLogger(__name__)

# Page layout constants
PAGE_WIDTH: Final[float] = letter[0]
PAGE_HEIGHT: Final[float] = letter[1]
MARGIN: Final[float] = 0.75 * inch


def _build_styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "ReportTitle",
            parent=base["Heading1"],
            fontSize=18,
            textColor=colors.HexColor("#1a1a2e"),
            spaceAfter=16,
        ),
        "heading": ParagraphStyle(
            "ReportHeading",
            parent=base["Heading2"],
            fontSize=14,
            textColor=colors.HexColor("#16213e"),
            spaceAfter=10,
        ),
        "body": ParagraphStyle(
            "ReportBody",
            parent=base["BodyText"],
            fontSize=10,
            leading=14,
        ),
        "mono": ParagraphStyle(
            "ReportMono",
            parent=base["Code"],
            fontSize=9,
            fontName="Courier",
        ),
        "footer": ParagraphStyle(
            "ReportFooter",
            parent=base["Normal"],
            fontSize=8,
            textColor=colors.grey,
        ),
    }


class ReportGenerator:
    """Generate PDF reports from scan results and evidence manifests.

    Thread-safe for concurrent generation of different reports.
    Not safe for concurrent writes to the same output path.
    """

    def __init__(self, output_dir: Path | None = None) -> None:
        self.output_dir = output_dir or Path("data/reports")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._styles = _build_styles()
        logger.info("report_generator_initialized", extra={"output_dir": str(self.output_dir)})

    def generate(
        self,
        metadata: ReportMetadata,
        sections: list[ReportSection],
        manifest: EvidenceManifest | None = None,
    ) -> GeneratedReport:
        """Generate a PDF report and persist it to the output directory.

        Returns a GeneratedReport with the file path populated.
        Raises RuntimeError on generation failure.
        """
        if metadata.format != ReportFormat.PDF:
            raise ValueError(f"Unsupported format: {metadata.format}")

        logger.info(
            "report_generation_started",
            extra={"report_id": str(metadata.report_id), "scan_id": str(metadata.scan_id)},
        )

        try:
            pdf_bytes = self._render_pdf(metadata, sections, manifest)
            file_path = self._write_file(metadata, pdf_bytes)
            updated_metadata = metadata.mark_completed(str(file_path))
            logger.info(
                "report_generation_completed",
                extra={"report_id": str(updated_metadata.report_id), "file_path": str(file_path)},
            )
            return GeneratedReport(
                metadata=updated_metadata,
                sections=sections,
                manifest=manifest,
            )
        except Exception as error:
            logger.error(
                "report_generation_failed",
                extra={"report_id": str(metadata.report_id), "error": str(error)},
            )
            updated_metadata = metadata.mark_failed(str(error))
            return GeneratedReport(
                metadata=updated_metadata,
                sections=sections,
                manifest=manifest,
            )

    def _render_pdf(
        self,
        metadata: ReportMetadata,
        sections: list[ReportSection],
        manifest: EvidenceManifest | None,
    ) -> bytes:
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=MARGIN,
            leftMargin=MARGIN,
            topMargin=MARGIN,
            bottomMargin=MARGIN,
        )
        story: list = []
        styles = self._styles

        # Header / Title
        story.append(Paragraph("Lookalike Radar — Detection Report", styles["title"]))
        story.append(Paragraph(f"Report ID: {metadata.report_id}", styles["mono"]))
        story.append(Paragraph(f"Scan ID: {metadata.scan_id}", styles["mono"]))
        story.append(Paragraph(f"Model Version: {metadata.model_version}", styles["mono"]))
        story.append(Paragraph(f"Generated: {metadata.created_at.isoformat()}", styles["mono"]))
        story.append(Spacer(1, 12))

        # Sections
        for section in sorted(sections, key=lambda s: s.order):
            story.append(Paragraph(section.title, styles["heading"]))
            story.append(Paragraph(section.body.replace("\n", "<br/>"), styles["body"]))
            story.append(Spacer(1, 8))

        # Evidence Manifest
        if manifest and manifest.items:
            story.append(Paragraph("Evidence Manifest", styles["heading"]))
            story.append(Paragraph(f"Manifest ID: {manifest.manifest_id}", styles["mono"]))
            story.append(Spacer(1, 6))

            table_data = [["Category", "Source", "Description", "Collected At", "SHA-256"]]
            for item in manifest.items:
                table_data.append([
                    item.category.value,
                    item.source,
                    item.description[:80] + "..." if len(item.description) > 80 else item.description,
                    item.collected_at.isoformat(),
                    item.sha256_checksum[:16] + "..." if item.sha256_checksum else "N/A",
                ])

            table = Table(table_data, colWidths=[1.0 * inch, 1.2 * inch, 2.4 * inch, 1.3 * inch, 1.1 * inch])
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#16213e")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 9),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f5f5f5")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTSIZE", (0, 1), (-1, -1), 8),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]))
            story.append(table)
            story.append(Spacer(1, 12))

        # Footer
        story.append(Spacer(1, 24))
        story.append(Paragraph(
            "This report was generated by Lookalike Radar. "
            "It does not constitute legal advice. "
            "All timestamps are in UTC.",
            styles["footer"],
        ))

        doc.build(story)
        return buffer.getvalue()

    def _write_file(self, metadata: ReportMetadata, pdf_bytes: bytes) -> Path:
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"report_{metadata.scan_id}_{timestamp}.pdf"
        file_path = self.output_dir / filename
        file_path.write_bytes(pdf_bytes)

        # Verify checksum for integrity
        checksum = hashlib.sha256(pdf_bytes).hexdigest()
        logger.info(
            "report_file_written",
            extra={
                "file_path": str(file_path),
                "size_bytes": len(pdf_bytes),
                "sha256": checksum,
            },
        )
        return file_path

    def build_manifest(
        self,
        scan_id: str,
        evidence_items: list[EvidenceItem],
    ) -> EvidenceManifest:
        """Build a validated evidence manifest from collected items."""
        manifest = EvidenceManifest(
            scan_id=scan_id,
            items=evidence_items,
        )
        if not manifest.checksums_present():
            logger.warning(
                "manifest_incomplete_checksums",
                extra={"scan_id": str(scan_id), "item_count": len(evidence_items)},
            )
        logger.info(
            "manifest_built",
            extra={"scan_id": str(scan_id), "item_count": len(evidence_items)},
        )
        return manifest
