"""Check if the issue is with database or job queue"""
import requests
import json

BASE_URL = "https://cv-analyser-kt1u.onrender.com"

# First, let's check if there are any existing analyses
print("1. Checking existing analyses...")
try:
    # Try to get a non-existent analysis to see the error format
    response = requests.get(f"{BASE_URL}/api/v1/analyze/00000000-0000-0000-0000-000000000000/status")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text[:200]}")
except:
    print("   Failed to check status endpoint")

# Test with a simpler payload
print("\n2. Testing with absolute minimum payload...")
payload = {"cv_text": "Test CV text"}

try:
    response = requests.post(
        f"{BASE_URL}/api/v1/analyze",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text[:500]}")
except Exception as e:
    print(f"   Error: {e}")

# Check if the issue is related to authentication
print("\n3. Testing with different headers...")
headers = [
    {"Content-Type": "application/json"},
    {"Content-Type": "application/json", "Authorization": ""},
    {"Content-Type": "application/json", "Authorization": "Bearer test"},
]

for i, header in enumerate(headers, 1):
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/analyze",
            json={"cv_text": "Test"},
            headers=header
        )
        print(f"   Header set {i}: Status {response.status_code}")
    except:
        print(f"   Header set {i}: Failed")
