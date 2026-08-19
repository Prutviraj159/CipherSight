from __future__ import annotations
import math
from dataclasses import dataclass
from app.domain import RISKY_TLDS, SUSPICIOUS_WORDS, NormalizedUrl, normalized_levenshtein, registered_label
from app.schemas import EnrichmentEvidence, Explanation

@dataclass(frozen=True)
class CandidateBrand:
    id: int
    name: str
    official_domain: str
    aliases: list[str]
    sector: str | None
    created_at: str

@dataclass(frozen=True)
class ScoredDetection:
    brand: CandidateBrand | None
    brand_confidence: float
    risk_score: float
    risk_level: str
    explanation: list[Explanation]

def _brand_similarity(url: NormalizedUrl, brand: CandidateBrand) -> float:
    label = registered_label(url.host)
    candidates = [registered_label(brand.official_domain), *brand.aliases]
    scores = []
    for candidate in candidates:
        compact = candidate.lower().replace(" ", "").replace("-", "")
        observed = label.replace("-", "")
        similarity = normalized_levenshtein(observed, compact)
        if compact in observed or observed in compact:
            similarity = max(similarity, 0.9)
        scores.append(similarity)
    return max(scores, default=0.0)

def _shannon_entropy(text: str) -> float:
    if not text:
        return 0.0
    counts = {}
    for char in text:
        counts[char] = counts.get(char, 0) + 1
    n = len(text)
    return -sum((c / n) * math.log2(c / n) for c in counts.values())

def score(url: NormalizedUrl, brands: list[CandidateBrand], evidence: EnrichmentEvidence) -> ScoredDetection:
    chosen = max(brands, key=lambda brand: _brand_similarity(url, brand), default=None)
    confidence = _brand_similarity(url, chosen) if chosen else 0.0
    
    signal_rows: list[Explanation] = []
    domain = url.host.lower()
    
    # Analyze Keywords for all layers
    keywords = {"login": 0.20, "secure": 0.15, "verify": 0.20, "account": 0.10, "password": 0.20, "credential": 0.20, "sbi": 0.05}
    found_keywords = [kw for kw in keywords if kw in domain or any(kw in token for token in url.path_tokens)]
    
    # ==========================================
    # LAYER 1: KILL SWITCH
    # ==========================================
    age = evidence.registration_age_days if evidence.registration_age_days is not None else 9999
    
    if age < 30 and confidence > 0.80:
        signal_rows.append(Explanation(signal="kill_switch", contribution=0.95, detail=f"Newly registered domain ({age} days) with high brand match ({confidence:.2f})"))
        return ScoredDetection(chosen, round(confidence, 3), 0.95, "critical", signal_rows)
        
    if age < 7 and found_keywords:
        signal_rows.append(Explanation(signal="kill_switch", contribution=0.95, detail=f"Domain < 7 days ({age}) with brand keywords: {found_keywords}"))
        return ScoredDetection(chosen, round(confidence, 3), 0.95, "critical", signal_rows)
        
    # ==========================================
    # LAYER 2: HARD SIGNALS
    # ==========================================
    hard_score = 0.0
    
    # Registration
    if age < 30:
        hard_score += 0.30
        signal_rows.append(Explanation(signal="domain_age", contribution=0.30, detail=f"Domain age: {age} days (< 30)"))
    
    if evidence.registrar:
        reg = evidence.registrar.lower()
        if "privacy" in reg or "whois guard" in reg:
            hard_score += 0.20
            signal_rows.append(Explanation(signal="registrar_privacy", contribution=0.20, detail=f"Privacy-protected registrar: {evidence.registrar}"))
            
    if evidence.registrant_country and evidence.registrant_country.upper() not in ["IN", "US", "GB"]:
        hard_score += 0.10
        signal_rows.append(Explanation(signal="registrant_country", contribution=0.10, detail=f"High-risk registration country: {evidence.registrant_country}"))

    # URL Entropy
    if len(found_keywords) >= 2:
        hard_score += 0.25
        signal_rows.append(Explanation(signal="suspicious_keywords", contribution=0.25, detail=f"Multiple suspicious keywords: {', '.join(found_keywords)}"))
    elif len(found_keywords) == 1:
        hard_score += 0.15
        signal_rows.append(Explanation(signal="suspicious_keywords", contribution=0.15, detail=f"Suspicious keyword: {found_keywords[0]}"))
        
    hyphens = domain.count("-")
    if hyphens >= 2:
        hard_score += 0.15
        signal_rows.append(Explanation(signal="url_hyphens", contribution=0.15, detail=f"Multiple hyphens: {hyphens}"))
        
    # SSL
    if evidence.ssl_cn_matches_domain is False:
        hard_score += 0.30
        signal_rows.append(Explanation(signal="ssl_mismatch", contribution=0.30, detail="SSL CN mismatch detected"))
        
    if evidence.ssl_issuer:
        trusted_issuers = {"digicert", "globalsign", "entrust", "sectigo", "let's encrypt"}
        if not any(t in evidence.ssl_issuer.lower() for t in trusted_issuers):
            hard_score += 0.15
            signal_rows.append(Explanation(signal="ssl_untrusted", contribution=0.15, detail=f"Untrusted SSL issuer: {evidence.ssl_issuer}"))
            
    # Form Endpoints
    if evidence.credential_form_detected or evidence.suspicious_form_actions:
        hard_score += 0.20
        signal_rows.append(Explanation(signal="form_endpoints", contribution=0.20, detail="Suspicious credential collection forms detected"))
            
    hard_score = min(hard_score, 1.0)
    
    if hard_score >= 0.60:
        base_score = min(hard_score + 0.10, 0.85)
        return ScoredDetection(chosen, round(confidence, 3), round(base_score, 3), "high", signal_rows)
        
    # ==========================================
    # LAYER 3: SOFT SIGNALS
    # ==========================================
    soft_score = 0.0
    if evidence.visual_similarity:
        visual_contrib = evidence.visual_similarity * 0.05
        soft_score += visual_contrib
        signal_rows.append(Explanation(signal="visual_similarity", contribution=round(visual_contrib, 3), detail=f"Visual similarity: {evidence.visual_similarity*100}%"))
        
    if evidence.text_similarity:
        text_contrib = evidence.text_similarity * 0.05
        soft_score += text_contrib
        signal_rows.append(Explanation(signal="content_similarity", contribution=round(text_contrib, 3), detail="Content similarity detected"))
        
    final_score = (hard_score * 0.90) + soft_score
    
    risk_level = "low"
    if final_score >= 0.70:
        risk_level = "critical"
    elif final_score >= 0.45:
        risk_level = "high"
    elif final_score >= 0.20:
        risk_level = "suspicious"
        
    if not signal_rows:
        signal_rows.append(Explanation(signal="no_high_risk_signal", contribution=0.0, detail="Domain passed kill switch and hard signal checks."))
        
    return ScoredDetection(chosen if confidence >= 0.45 else None, round(confidence, 3), round(final_score, 3), risk_level, signal_rows)
