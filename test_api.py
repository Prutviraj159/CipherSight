import httpx

BASE_URL = 'http://localhost:8000'
headers = {}

print('=== 4. API Health Check ===')
resp = httpx.get(f'{BASE_URL}/health')
print(resp.status_code, resp.text)

print('\n=== 5. Authentication Workflow ===')
resp = httpx.post(f'{BASE_URL}/auth/token', params={'username':'admin', 'password':'change-me'})
print(resp.status_code, resp.text)
if resp.status_code == 200:
    token = resp.json().get('access_token')
    headers['Authorization'] = f'Bearer {token}'

print('\n=== 6. Brand Catalogue Workflow ===')
resp = httpx.post(f'{BASE_URL}/brands', json={'name': 'Docker Brand', 'official_domain': 'docker.com', 'aliases': [], 'sector': 'tech'}, headers=headers)
print('Create:', resp.status_code, resp.text)
resp = httpx.get(f'{BASE_URL}/brands', headers=headers)
print('List:', resp.status_code, resp.text[:100] + '...')

print('\n=== 7. Mocked Ingestion Workflow ===')
resp = httpx.post(f'{BASE_URL}/scans', json={'url': 'http://evil-test.com', 'enrichment': {}}, headers=headers)
print('Scan:', resp.status_code, resp.text)

print('\n=== 8. Detection & Verdict Workflow ===')
resp = httpx.put(f'{BASE_URL}/scans/1/verdict', json={'verdict': 'phishing', 'note': 'Confirmed malicious'}, headers=headers)
print('Verdict:', resp.status_code, resp.text)

print('\n=== 9. Reporting Workflow (Exports) ===')
resp = httpx.get(f'{BASE_URL}/exports/scans.json', headers=headers)
print('JSON Export:', resp.status_code, resp.text[:100] + '...')
resp = httpx.get(f'{BASE_URL}/exports/scans.csv', headers=headers)
print('CSV Export:', resp.status_code, resp.text[:100] + '...')
