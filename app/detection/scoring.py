from __future__ import annotations

import structlog
from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.domain import normalized_levenshtein, registered_label
from app.detection.contracts import BrandCandidate, BrandRank, DetectionSignals, RiskAssessment, RiskLevel, SignalContribution

logger = structlog.get_logger(__name__)


class RiskWeights(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    lexical: float = Field(default=0.20, ge=0, le=1)
    registration: float = Field(default=0.15, ge=0, le=1)
    infrastructure: float = Field(default=0.20, ge=0, le=1)
    text: float = Field(default=0.15, ge=0, le=1)
    visual: float = Field(default=0.10, ge=0, le=1)
    forms: float = Field(default=0.20, ge=0, le=1)

    @model_validator(mode="after")
    def require_unit_sum(self) -> "RiskWeights":
        if abs(sum(self.model_dump().values()) - 1.0) > 0.00001:
            raise ValueError("risk weights must sum to 1.0")
        return self


class RiskThresholds(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    suspicious: float = 0.30
    high: float = 0.60
    critical: float = 0.85

    @model_validator(mode="after")
    def require_ordered_thresholds(self) -> "RiskThresholds":
        if not 0 < self.suspicious < self.high < self.critical < 1:
            raise ValueError("thresholds must satisfy 0 < suspicious < high < critical < 1")
        return self


class RiskScorer:
    """Deterministic, explainable scorer; not a trained ML classifier."""

    def __init__(self, weights: RiskWeights | None = None, thresholds: RiskThresholds | None = None, model_version: str = "rules-fusion-v1"):
        self.weights = weights or RiskWeights()
        self.thresholds = thresholds or RiskThresholds()
        self.model_version = model_version

    def calculate_lexical_score(self, domain: str, brands: list[BrandCandidate]) -> float:
        return max((rank.confidence for rank in self.rank_brands(domain, brands)), default=0.0)

    def calculate_registration_score(self, score: float) -> float:
        return self._bounded(score)

    def calculate_content_score(self, score: float) -> float:
        return self._bounded(score)

    def calculate_visual_score(self, score: float, available: bool) -> float:
        return self._bounded(score) if available else 0.0

    def calculate_form_score(self, score: float) -> float:
        return self._bounded(score)

    def rank_brands(self, domain: str, brands: list[BrandCandidate]) -> list[BrandRank]:
        observed = registered_label(domain).replace("-", "")
        ranks = []
        for brand in brands:
            similarity = max((normalized_levenshtein(observed, registered_label(candidate).replace("-", "")) for candidate in brand.domains), default=0.0)
            ranks.append(BrandRank(brand_id=brand.id, name=brand.name, confidence=round(similarity, 4)))
        return sorted(ranks, key=lambda item: item.confidence, reverse=True)

    def assess(self, domain: str, signals: DetectionSignals, brands: list[BrandCandidate]) -> RiskAssessment:
        visual = self.calculate_visual_score(signals.visual, signals.visual_source_available)
        raw = {"lexical": self._bounded(signals.lexical), "registration": self.calculate_registration_score(signals.registration), "infrastructure": self._bounded(signals.infrastructure), "text": self.calculate_content_score(signals.text), "visual": visual, "forms": self.calculate_form_score(signals.forms)}
        descriptions = {"lexical": "Domain structure and protected-brand similarity.", "registration": "Registration-age and registrar evidence.", "infrastructure": "DNS, TLS, and reputation evidence.", "text": "Sanitized text similarity evidence.", "visual": "Visual similarity input from an evaluated future worker.", "forms": "Credential-form and suspicious-action evidence."}
        contributions = [SignalContribution(signal=name, raw_score=value, weight=getattr(self.weights, name), contribution=round(value * getattr(self.weights, name), 6), explanation=descriptions[name]) for name, value in raw.items()]
        score = round(sum(item.contribution for item in contributions), 6)
        limitations = [] if signals.visual_source_available else ["Visual contribution unavailable; no ML or visual-similarity accuracy is claimed."]
        assessment = RiskAssessment(score=score, level=self._level(score), model_version=self.model_version, contributions=contributions, ranked_brands=self.rank_brands(domain, brands), limitations=limitations)
        logger.info("risk_assessed", domain=domain, risk_score=score, risk_level=assessment.level, model_version=self.model_version)
        return assessment

    def _level(self, score: float) -> RiskLevel:
        if score > self.thresholds.critical:
            return RiskLevel.CRITICAL
        if score >= self.thresholds.high:
            return RiskLevel.HIGH
        if score >= self.thresholds.suspicious:
            return RiskLevel.SUSPICIOUS
        return RiskLevel.LOW

    @staticmethod
    def _bounded(value: float) -> float:
        if not 0 <= value <= 1:
            raise ValueError("signal score must be between 0 and 1")
        return value
