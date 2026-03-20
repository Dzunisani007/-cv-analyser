"""Debug script to test API endpoint"""
import requests
import json

BASE_URL = "https://cv-analyser-kt1u.onrender.com"

# Test without auth first
print("Testing without authentication...")
payload = {
    "cv_text": "John Doe\nSoftware Engineer\n5 years experience",
    "job_description": "Looking for software engineer"
}

response = requests.post(
    f"{BASE_URL}/api/v1/analyze",
    json=payload
)

print(f"Status: {response.status_code}")
print(f"Response: {response.text[:500]}")

# Test with auth
print("\nTesting with Bearer token...")
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer test"
}

response = requests.post(
    f"{BASE_URL}/api/v1/analyze",
    json=payload,
    headers=headers
)

print(f"Status: {response.status_code}")
print(f"Response: {response.text[:500]}")

# Check if service needs specific auth
print("\nChecking service configuration...")
health_response = requests.get(f"{BASE_URL}/health")
print(f"Health: {health_response.json()}")
