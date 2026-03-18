import requests

secret = 'a262029a40fd49e85f1d56178af894d9'
BASE = 'https://cv-analyser-kt1u.onrender.com'
headers = {'Authorization': f'Bearer {secret}'}

print('Testing with secret:', secret)
print('Secret length:', len(secret))

try:
    r = requests.post(f'{BASE}/upload', headers=headers, files={'file': ('test.pdf', b'%PDF-1.4\n%EOF\n', 'application/pdf')}, timeout=30)
    print('Status:', r.status_code)
    print('Response:', r.text)
except Exception as e:
    print('Error:', e)
