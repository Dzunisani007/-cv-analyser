import os
from pathlib import Path

# Load environment variables
for line in Path('.env').read_text().splitlines():
    if '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1)
        os.environ[k.strip()] = v.strip()

import cloudinary
import cloudinary.api

cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET'),
)

print("=== Checking Cloudinary Resources ===")

# List all resources in the cv_analyser/resumes folder
try:
    resources = cloudinary.api.resources(
        type="upload",
        resource_type="raw",
        prefix="cv_analyser/resumes",
        max_results=50
    )
    
    print(f"Found {len(resources.get('resources', []))} resources:")
    for resource in resources.get('resources', []):
        print(f"  - Public ID: {resource.get('public_id')}")
        print(f"    URL: {resource.get('secure_url')}")
        print(f"    Format: {resource.get('format')}")
        print()
        
except Exception as e:
    print(f"Error listing resources: {e}")

# Test accessing a specific resource
print("=== Testing Resource Access ===")
test_public_id = "cv_analyser/resumes/5552f778-3963-440d-b930-43698a379058"

try:
    resource = cloudinary.api.resource(test_public_id, resource_type="raw")
    print(f"✅ Found resource: {resource.get('public_id')}")
    print(f"   URL: {resource.get('secure_url')}")
except Exception as e:
    print(f"❌ Resource not found: {e}")
    
    # Try without .pdf
    try:
        resource = cloudinary.api.resource(f"{test_public_id}.pdf", resource_type="raw")
        print(f"✅ Found resource with .pdf: {resource.get('public_id')}")
        print(f"   URL: {resource.get('secure_url')}")
    except Exception as e2:
        print(f"❌ Also not found with .pdf: {e2}")
