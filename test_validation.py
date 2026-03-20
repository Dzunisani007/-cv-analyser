"""Check if the issue is with database models"""
import requests
import json

BASE_URL = "https://cv-analyser-kt1u.onrender.com"

# Test validation error to see proper error format
print("Testing validation error...")
payload = {"cv_text": ""}  # Empty cv_text should trigger validation

try:
    response = requests.post(
        f"{BASE_URL}/api/v1/analyze",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")

# Test with valid cv_text but minimal
print("\nTesting with valid cv_text...")
payload = {"cv_text": "x" * 10}  # Minimum 10 chars

try:
    response = requests.post(
        f"{BASE_URL}/api/v1/analyze",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    print(f"Status: {response.status_code}")
    if response.status_code != 200:
        print(f"Response: {response.text}")
    else:
        print(f"Success: {response.json()}")
except Exception as e:
    print(f"Error: {e}")
