import os
import requests
from pathlib import Path

# Load environment variables
for line in Path('.env').read_text().splitlines():
    if '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1)
        os.environ[k.strip()] = v.strip()

# Test configuration
print("=== CV Analyser Configuration Test ===")
print(f"Storage Backend: {os.getenv('STORAGE_BACKEND')}")
print(f"Cloudinary Cloud Name: {os.getenv('CLOUDINARY_CLOUD_NAME')}")
print(f"Cloudinary API Key: {os.getenv('CLOUDINARY_API_KEY')[:10]}..." if os.getenv('CLOUDINARY_API_KEY') else "Not set")
print(f"Cloudinary API Secret: {'*' * 10 if os.getenv('CLOUDINARY_API_SECRET') else 'Not set'}")

# Check for SendGrid
sendgrid_key = os.getenv('SENDGRID_API_KEY')
sendgrid_from = os.getenv('SENDGRID_FROM_EMAIL')
print(f"SendGrid API Key: {'Set' if sendgrid_key else 'Not set'}")
print(f"SendGrid From Email: {sendgrid_key or 'Not set'}")

# Test Cloudinary connection
print("\n=== Cloudinary Connection Test ===")
try:
    import cloudinary
    import cloudinary.api
    
    cloudinary.config(
        cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
        api_key=os.getenv('CLOUDINARY_API_KEY'),
        api_secret=os.getenv('CLOUDINARY_API_SECRET'),
    )
    
    # Test API connection
    result = cloudinary.api.ping()
    print(f"Cloudinary Ping: {result}")
    
    # Test upload
    print("Testing Cloudinary upload...")
    test_result = cloudinary.uploader.upload(
        b"Test file content",
        public_id="cv_analyser/test_connection",
        resource_type="raw"
    )
    print(f"Upload successful: {test_result.get('public_id')}")
    
    # Clean up
    cloudinary.uploader.destroy("cv_analyser/test_connection", resource_type="raw")
    print("Test file cleaned up")
    
except Exception as e:
    print(f"Cloudinary test failed: {e}")

# Test SendGrid if configured
if sendgrid_key:
    print("\n=== SendGrid Connection Test ===")
    try:
        import sendgrid
        from sendgrid.helpers.mail import Mail
        
        sg = sendgrid.SendGridAPIClient(api_key=sendgrid_key)
        
        # Test API connection (get account info)
        response = sg.client.api_keys.get()
        print(f"SendGrid API connection: {response.status_code}")
        
    except Exception as e:
        print(f"SendGrid test failed: {e}")
else:
    print("\n=== SendGrid Not Configured ===")
    print("Add SENDGRID_API_KEY and SENDGRID_FROM_EMAIL to .env to test")

# Test CV Analyser API
print("\n=== CV Analyser API Test ===")
BASE = "https://cv-analyser-kt1u.onrender.com"
SECRET = os.getenv('AUTH_SECRET')

try:
    # Health check
    health_resp = requests.get(f"{BASE}/health", timeout=30)
    print(f"Health Check: {health_resp.status_code}")
    if health_resp.status_code == 200:
        health_data = health_resp.json()
        print(f"Storage Mode: {health_data.get('storage', {}).get('mode')}")
    
    # Test upload
    print("Testing CV upload...")
    with open('Dzunisani-Mabundas-Resume-Cv-Qualifications.pdf', 'rb') as f:
        upload_resp = requests.post(
            f"{BASE}/upload",
            headers={"Authorization": f"Bearer {SECRET}"},
            files={"file": ("test.pdf", f, "application/pdf")},
            timeout=60
        )
    
    print(f"Upload Status: {upload_resp.status_code}")
    if upload_resp.status_code == 202:
        upload_data = upload_resp.json()
        print(f"Analysis ID: {upload_data.get('analysis_id')}")
        
        # Check status
        analysis_id = upload_data.get('analysis_id')
        status_resp = requests.get(
            f"{BASE}/analyses/{analysis_id}/status",
            headers={"Authorization": f"Bearer {SECRET}"},
            timeout=30
        )
        print(f"Status: {status_resp.json().get('status')}")
    else:
        print(f"Upload Error: {upload_resp.text}")
        
except Exception as e:
    print(f"API test failed: {e}")

print("\n=== Test Complete ===")
