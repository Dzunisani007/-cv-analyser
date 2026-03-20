"""Test with inline jobs to bypass worker queue"""
import requests
import json

BASE_URL = "https://cv-analyser-kt1u.onrender.com"

print("Testing with inline jobs (if supported)...")

# First, let's check if we can set INLINE_JOBS
print("\n1. Checking current health...")
health = requests.get(f"{BASE_URL}/health")
print(f"   Health: {health.json()}")

# Test with minimal payload
payload = {
    "cv_text": "John Doe\nSoftware Engineer\nPython, Django, PostgreSQL\n5 years experience",
    "job_description": "Senior Python Developer"
}

print("\n2. Submitting analysis...")
response = requests.post(
    f"{BASE_URL}/api/v1/analyze",
    json=payload,
    headers={"Content-Type": "application/json"}
)

print(f"   Status: {response.status_code}")
if response.status_code == 202:
    data = response.json()
    analysis_id = data.get("analysis_id")
    print(f"   Analysis ID: {analysis_id}")
    
    # Poll for status
    print("\n3. Polling status...")
    for i in range(10):
        import time
        time.sleep(1)
        status_response = requests.get(f"{BASE_URL}/api/v1/analyze/{analysis_id}/status")
        if status_response.status_code == 200:
            status_data = status_response.json()
            status = status_data.get("status")
            print(f"   Attempt {i+1}: {status}")
            
            if status == "completed":
                print("   ✅ Analysis completed!")
                break
            elif status == "failed":
                print("   ❌ Analysis failed")
                break
    else:
        print("   ⏰ Polling timed out")
        
        # Try to get the analysis record directly from DB
        print("\n4. Checking if record was created...")
        # We can't access DB directly, but we can check if the analysis exists
        result_response = requests.get(f"{BASE_URL}/api/v1/analyze/{analysis_id}/result")
        print(f"   Result endpoint: {result_response.status_code}")
        if result_response.status_code != 200:
            print(f"   Error: {result_response.text[:200]}")
else:
    print(f"   Error: {response.text[:500]}")
