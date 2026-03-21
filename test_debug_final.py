"""Test with debug endpoint to see the actual error"""
import requests

BASE_URL = "https://cv-analyser-kt1u.onrender.com"

print("Testing with debug endpoint to see the actual error...")

payload = {
    "cv_text": "John Doe\nSoftware Engineer\nPython, Django, PostgreSQL\n5 years experience",
    "job_description": "Senior Python Developer"
}

# Test debug endpoint
response = requests.post(
    f"{BASE_URL}/api/v1/analyze-debug",
    json=payload,
    headers={"Content-Type": "application/json"}
)

print(f"Debug endpoint status: {response.status_code}")
if response.status_code == 202:
    analysis_id = response.json().get("analysis_id")
    print(f"Analysis ID: {analysis_id}")
    
    # Check status
    status_response = requests.get(f"{BASE_URL}/api/v1/analyze/{analysis_id}/status")
    status_data = status_response.json()
    print(f"Status: {status_data}")
else:
    print(f"Debug error: {response.text}")

print("\n" + "=" * 60)
print("The issue is likely that the HF_API_TOKEN is still not")
print("being passed to the container environment.")
print("\nTo fix this:")
print("1. Go to Render dashboard > Environment")
print("2. Delete the existing HF_API_TOKEN")
print("3. Add it again with the exact value:")
print("   hf_YMOefnqmd1JnCnacvKXCRpCkYsMPzFomsT")
print("4. Click 'Save Changes'")
print("5. Trigger 'Manual Deploy'")
print("=" * 60)
