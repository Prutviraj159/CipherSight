import httpx
import json

BASE_URL = 'http://localhost:8000'

# 1. Login
auth_res = httpx.post(f'{BASE_URL}/auth/token', params={'username': 'admin', 'password': 'change-me'})
token = auth_res.json().get('access_token')
headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

# 2. Real SBI
real_payload = {
    "url": "https://sbi.bank.in",
    "enrichment": {
        "registration_age_days": 5840,
        "registrar": "MarkMonitor Inc.",
        "registrant_country": "IN",
        "ssl_issuer": "DigiCert Inc",
        "ssl_cn_matches_domain": True,
        "visual_similarity": 1.0,
        "credential_form_detected": False,
        "external_form_action": False,
        "suspicious_form_actions": []
    }
}

print("=== SCORING REAL DOMAIN (sbi.bank.in) ===")
res_real = httpx.post(f'{BASE_URL}/scans', json=real_payload, headers=headers)
data_real = res_real.json()
print(f"Risk Score: {data_real.get('risk_score')} ({data_real.get('risk_level')})")
print("Explanations:")
for exp in data_real.get('explanation', []):
    print(f" - [{exp['contribution']}] {exp['signal']}: {exp['detail']}")
print("\n")


# 3. Fake SBI
fake_payload = {
    "url": "https://sbi-secure-verify.com",
    "enrichment": {
        "registration_age_days": 12,
        "registrar": "PrivacyGuard Services",
        "registrant_country": "PA",
        "ssl_issuer": "Let's Encrypt",
        "ssl_cn_matches_domain": False,
        "visual_similarity": 0.92,
        "credential_form_detected": True,
        "external_form_action": False,
        "suspicious_form_actions": ["login.php"]
    }
}

print("=== SCORING FAKE DOMAIN (sbi-secure-verify.com) ===")
res_fake = httpx.post(f'{BASE_URL}/scans', json=fake_payload, headers=headers)
data_fake = res_fake.json()
print(f"Risk Score: {data_fake.get('risk_score')} ({data_fake.get('risk_level')})")
print("Explanations:")
for exp in data_fake.get('explanation', []):
    print(f" - [{exp['contribution']}] {exp['signal']}: {exp['detail']}")

