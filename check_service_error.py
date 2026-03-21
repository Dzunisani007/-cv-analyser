"""Check the actual error in the deployed service logs"""
import requests

BASE_URL = "https://cv-analyser-kt1u.onrender.com"

print("Checking deployed service for actual errors...")

# Submit a simple analysis to capture the error
payload = {
    "cv_text": "Test CV text",
    "job_description": "Test job"
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
    
    # Check status
    status_response = requests.get(f"{BASE_URL}/api/v1/analyze/{analysis_id}/status")
    status_data = status_response.json()
    
    print(f"   Status: {status_data.get('status')}")
    
    if status_data.get('status') == 'failed':
        print("\n   ⚠️  Analysis failed immediately")
        print("\n   The issue is likely:")
        print("   1. Token not passed to container environment")
        print("   2. Token has a typo or extra characters")
        print("   3. Service needs to be redeployed after token update")
        
        print("\n   Please check:")
        print("   - In Render dashboard, verify HF_API_TOKEN is exactly:")
        print("     hf_YMOefnqmd1JnCnacvKXCRpCkYsMPzFomsT")
        print("   - Click 'Save Changes' even if it looks correct")
        print("   - Trigger 'Manual Deploy'")
        print("   - Check service logs after deployment for HF API errors")

print("\n" + "=" * 60)
print("RECOMMENDATION:")
print("The token might not be loaded into the container.")
print("Please redeploy the service after saving the environment variable.")
print("=" * 60)
