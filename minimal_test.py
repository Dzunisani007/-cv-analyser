"""Minimal test to isolate the issue"""
import requests
import json

BASE_URL = "https://cv-analyser-kt1u.onrender.com"

# Test 1: Health check
print("1. Testing health endpoint...")
health = requests.get(f"{BASE_URL}/health")
print(f"   Status: {health.status_code}")
print(f"   Response: {health.json()}")

# Test 2: Check OpenAPI docs
print("\n2. Testing OpenAPI docs...")
docs = requests.get(f"{BASE_URL}/docs")
print(f"   Status: {docs.status_code}")

# Test 3: Check if API routes exist
print("\n3. Testing API routes...")
try:
    # Try to access the analyze endpoint with OPTIONS
    options = requests.options(f"{BASE_URL}/api/v1/analyze")
    print(f"   OPTIONS /api/v1/analyze: {options.status_code}")
except:
    print("   OPTIONS request failed")

# Test 4: Try with minimal payload
print("\n4. Testing analyze endpoint with minimal payload...")
payload = {
    "cv_text": "Test CV text - this is a minimal test"
}

try:
    response = requests.post(
        f"{BASE_URL}/api/v1/analyze",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    print(f"   Status: {response.status_code}")
    if response.status_code != 200:
        print(f"   Error: {response.text[:500]}")
except Exception as e:
    print(f"   Exception: {e}")

# Test 5: Check if there's a missing module issue
print("\n5. Checking for common issues...")
try:
    # Try to access root
    root = requests.get(f"{BASE_URL}/")
    print(f"   Root /: {root.status_code}")
except:
    print("   Root request failed")
