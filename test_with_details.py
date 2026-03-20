"""Test with detailed error logging"""
import requests
import json

BASE_URL = "https://cv-analyser-kt1u.onrender.com"

print("Testing analyze endpoint with detailed logging...")

# Test with minimal valid payload
payload = {
    "cv_text": "John Doe\nSoftware Engineer\n5 years of experience in Python development",
    "job_description": "Looking for a Python developer",
    "industry": "technology"
}

print(f"Payload: {json.dumps(payload, indent=2)}")

try:
    response = requests.post(
        f"{BASE_URL}/api/v1/analyze",
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=30
    )
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    
    if response.status_code != 200:
        print(f"Error Response: {response.text}")
        
        # Try to get more details
        if response.headers.get('content-type', '').startswith('application/json'):
            try:
                error_json = response.json()
                print(f"Error JSON: {json.dumps(error_json, indent=2)}")
            except:
                pass
    else:
        print(f"Success Response: {response.text}")
        
except requests.exceptions.Timeout:
    print("Request timed out")
except requests.exceptions.ConnectionError:
    print("Connection error")
except Exception as e:
    print(f"Unexpected error: {e}")
