import os
import requests
from pathlib import Path

# Load environment variables
for line in Path('.env').read_text().splitlines():
    if '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1)
        os.environ[k.strip()] = v.strip()

print("=== Cloudinary Detailed Test ===")

try:
    import cloudinary
    import cloudinary.api
    import cloudinary.uploader
    import io
    
    cloudinary.config(
        cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
        api_key=os.getenv('CLOUDINARY_API_KEY'),
        api_secret=os.getenv('CLOUDINARY_API_SECRET'),
    )
    
    # Test upload with proper parameters
    print("Testing Cloudinary upload...")
    test_result = cloudinary.uploader.upload(
        io.BytesIO(b"Test file content for CV analyser"),
        public_id="cv_analyser/test_connection",
        resource_type="raw",
        folder="cv_analyser"
    )
    print(f"✅ Upload successful: {test_result.get('public_id')}")
    print(f"   Secure URL: {test_result.get('secure_url')}")
    
    # Test download
    print("Testing Cloudinary download...")
    resource = cloudinary.api.resource("cv_analyser/test_connection", resource_type="raw")
    print(f"✅ Resource found: {resource.get('secure_url')}")
    
    # Clean up
    cloudinary.uploader.destroy("cv_analyser/test_connection", resource_type="raw")
    print("✅ Test file cleaned up")
    
except Exception as e:
    print(f"❌ Cloudinary test failed: {e}")
    import traceback
    traceback.print_exc()

print("\n=== CV Analyser Service Status ===")
BASE = "https://cv-analyser-kt1u.onrender.com"

try:
    # Health check
    health_resp = requests.get(f"{BASE}/health", timeout=60)
    print(f"Health Check: {health_resp.status_code}")
    if health_resp.status_code == 200:
        health_data = health_resp.json()
        print(f"Storage Mode: {health_data.get('storage', {}).get('mode')}")
        print(f"Database: {health_data.get('db', {}).get('ok')}")
        print(f"Models: {health_data.get('models', {}).get('ok')}")
    else:
        print(f"Health check failed: {health_resp.text}")
        
except Exception as e:
    print(f"❌ Service check failed: {e}")

print("\n=== SendGrid Configuration ===")
sendgrid_key = os.getenv('SENDGRID_API_KEY')
sendgrid_from = os.getenv('SENDGRID_FROM_EMAIL')

if not sendgrid_key:
    print("❌ SendGrid not configured")
    print("To configure SendGrid, add to .env:")
    print("SENDGRID_API_KEY=your_sendgrid_api_key")
    print("SENDGRID_FROM_EMAIL=your_email@example.com")
else:
    print(f"✅ SendGrid API Key configured: {sendgrid_key[:10]}...")
    print(f"✅ SendGrid From: {sendgrid_from}")
