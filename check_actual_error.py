"""Check the actual error in the deployed service"""
import requests
import json

BASE_URL = "https://cv-analyser-kt1u.onrender.com"

print("Checking actual error in deployed service...")

# Submit an analysis to see the error
payload = {
    "cv_text": "John Doe\nSoftware Engineer\nPython, Django\n5 years",
    "job_description": "Senior Python Developer"
}

print("\n1. Submitting analysis...")
response = requests.post(
    f"{BASE_URL}/api/v1/analyze",
    json=payload,
    headers={"Content-Type": "application/json"}
)

if response.status_code == 202:
    analysis_id = response.json().get("analysis_id")
    print(f"   Analysis ID: {analysis_id}")
    
    # Check status immediately
    status_response = requests.get(f"{BASE_URL}/api/v1/analyze/{analysis_id}/status")
    status_data = status_response.json()
    
    if status_data.get("status") == "failed":
        print("   ❌ Analysis failed")
        
        # Try to get more details from the debug endpoint
        print("\n2. Testing with debug endpoint...")
        debug_response = requests.post(
            f"{BASE_URL}/api/v1/analyze-debug",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   Debug status: {debug_response.status_code}")
        if debug_response.status_code != 202:
            print(f"   Debug error: {debug_response.text}")
        else:
            debug_analysis_id = debug_response.json().get("analysis_id")
            # Check debug status
            debug_status = requests.get(f"{BASE_URL}/api/v1/analyze/{debug_analysis_id}/status")
            print(f"   Debug status: {debug_status.json()}")

print("\n" + "=" * 60)
print("ISSUES IDENTIFIED:")
print("1. HF Token is invalid (401 error)")
print("2. Service is using deprecated HF API endpoint")
print("\nSOLUTIONS:")
print("1. Get a valid HF token from https://huggingface.co/settings/tokens")
print("2. Update the service to use the new HF API router")
print("=" * 60)
