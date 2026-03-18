import requests
import json

secret = 'a262029a40fd49e85f1d56178af894d9'
BASE = 'https://cv-analyser-kt1u.onrender.com'
headers = {'Authorization': f'Bearer {secret}'}

print('Testing upload with debug info...')

# Test upload with a simple PDF
test_pdf = b'%PDF-1.4\n%EOF\n'

try:
    r = requests.post(f'{BASE}/upload', 
                     headers=headers, 
                     files={'file': ('debug.pdf', test_pdf, 'application/pdf')},
                     timeout=30)
    
    print('Upload Status:', r.status_code)
    if r.status_code == 202:
        data = r.json()
        print('Upload Response:', json.dumps(data, indent=2))
        
        # Now check the status immediately
        analysis_id = data.get('analysis_id')
        if analysis_id:
            print(f'\nChecking status for {analysis_id}...')
            status_r = requests.get(f'{BASE}/analyses/{analysis_id}/status', headers=headers, timeout=30)
            print('Status Response:', json.dumps(status_r.json(), indent=2))
    else:
        print('Upload Response:', r.text)
        
except Exception as e:
    print('Error:', e)
