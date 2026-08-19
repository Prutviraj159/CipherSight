window.scanMapper = {
    mapVerdict: function(raw) {
        if (!raw) return "DATA_UNAVAILABLE";
        
        if (raw.status === "failed") return "ERROR";
        if (raw.status === "pending" || raw.status === "processing") return "PROCESSING";

        // 1. Explicit analyst verdict
        if (raw.verdict && typeof raw.verdict === 'string') {
            const v = raw.verdict.toLowerCase();
            if (v === 'phishing') return 'PHISHING';
            if (v === 'legitimate') return 'LEGITIMATE';
            if (v === 'needs_review') return 'NEEDS_REVIEW';
        }
        
        // Use status if verdict not explicitly 'verdict' field but status is used for analyst verdict
        if (raw.status && typeof raw.status === 'string') {
            const s = raw.status.toLowerCase();
            if (s === 'phishing') return 'PHISHING';
            if (s === 'legitimate') return 'LEGITIMATE';
        }

        // 2. Map backend risk_level
        if (raw.risk_level) {
            switch (raw.risk_level.toLowerCase()) {
                case "low": return "SAFE";
                case "suspicious": return "NEEDS_REVIEW";
                case "high": return "HIGH_RISK";
                case "critical": return "HIGH_RISK";
            }
        }
        
        return "DATA_UNAVAILABLE";
    },

    normalizeRiskLevel: function(raw) {
        if (!raw || !raw.risk_level) return "DATA_UNAVAILABLE";
        return raw.risk_level.toLowerCase();
    },

    safeNumeric: function(value) {
        if (value === null || value === undefined) return "N/A";
        return value;
    },

    mapScanResponse: function(raw) {
        if (!raw) return null;
        return {
            scanId: raw.id || raw.scan_id || "DATA_UNAVAILABLE",
            domain: raw.normalized_domain || raw.domain || "DATA_UNAVAILABLE",
            status: raw.status || "DATA_UNAVAILABLE",
            riskScore: this.safeNumeric(raw.risk_score),
            riskLevel: this.normalizeRiskLevel(raw),
            verdict: this.mapVerdict(raw),
            domainAge: this.safeNumeric(raw.domain_age_days !== undefined ? raw.domain_age_days : raw.domain_age),
            visualMatch: this.safeNumeric(raw.visual_match_score !== undefined ? raw.visual_match_score : raw.visual_match),
            sslMatch: raw.ssl_certificate_match !== undefined ? raw.ssl_certificate_match : null,
            suspiciousKeywords: raw.suspicious_keywords || [],
            createdAt: raw.created_at || "DATA_UNAVAILABLE",
            targetBrand: raw.target_brand || null,
            explanation: raw.explanation || []
        };
    }
};
