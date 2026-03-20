"""Test the debug endpoint locally first"""
import requests
import json

BASE_URL = "https://cv-analyser-kt1u.onrender.com"

print("Testing debug endpoint (may not be deployed yet)...")

payload = {
    "cv_text": "John Doe\nSoftware Engineer\n5 years of experience",
    "job_description": "Looking for a software engineer"
}

try:
    response = requests.post(
        f"{BASE_URL}/api/v1/analyze-debug",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:1000]}")
except Exception as e:
    print(f"Error: {e}")
    
    # If debug endpoint doesn't exist, let's check what endpoints are available
    print("\nChecking available endpoints...")
    try:
        docs = requests.get(f"{BASE_URL}/docs")
        if docs.status_code == 200:
            print("OpenAPI docs are available at: https://cv-analyser-kt1u.onrender.com/docs")
            print("You can check the available endpoints there.")
    except:
        print("Could not access docs")
