import os, requests
from pathlib import Path

# Load env from recruitment backend
secret = None
env_path = Path('../server/.env')
if not env_path.exists():
    env_path = Path('.env')
    
for line in env_path.read_text().splitlines():
    if '=' in line and not line.startswith('#'):
        k,v = line.split('=',1)
        if k.strip() == 'CV_ANALYSER_SIGNING_SECRET':
            secret = v.strip()
            break

print('Testing with secret:', secret)
print('Secret length:', len(secret) if secret else 0)

BASE = 'https://cv-analyser-kt1u.onrender.com'
headers = {'Authorization': f'Bearer {secret}'}

try:
    r = requests.post(f'{BASE}/upload', headers=headers, files={'file': ('test.pdf', b'%PDF-1.4\n%EOF\n', 'application/pdf')}, timeout=30)
    print('Status:', r.status_code)
    print('Response:', r.text)
except Exception as e:
    print('Error:', e)
