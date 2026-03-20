"""Check what's happening with job processing"""
import requests
import json

BASE_URL = "https://cv-analyser-kt1u.onrender.com"

print("Testing job processing...")

# Submit a new analysis to see what happens
payload = {
    "cv_text": "John Doe\nSoftware Engineer\nPython, Django, PostgreSQL\n5 years experience",
    "job_description": "Senior Python Developer"
}

print("\n1. Submitting new analysis...")
response = requests.post(
    f"{BASE_URL}/api/v1/analyze",
    json=payload,
    headers={"Content-Type": "application/json"}
)

if response.status_code == 202:
    data = response.json()
    analysis_id = data.get("analysis_id")
    print(f"   Analysis ID: {analysis_id}")
    
    # Check status immediately
    print("\n2. Checking initial status...")
    status_response = requests.get(f"{BASE_URL}/api/v1/analyze/{analysis_id}/status")
    print(f"   Status: {status_response.json()}")
    
    # Wait a moment and check again
    import time
    time.sleep(2)
    
    print("\n3. Checking status after 2 seconds...")
    status_response = requests.get(f"{BASE_URL}/api/v1/analyze/{analysis_id}/status")
    status_data = status_response.json()
    print(f"   Status: {status_data}")
    
    if status_data.get("status") == "failed":
        print("\n   ❌ Job failed immediately")
        print("   The issue is likely in the job worker:")
        print("   - Models not loading (HF API token issue)")
        print("   - Missing dependencies")
        print("   - Error in the processing pipeline")
        
        # Check if we can see any error details
        print("\n4. Checking for error logs...")
        # Try to access the admin endpoint to see if there are any error details
        try:
            admin_response = requests.get(f"{BASE_URL}/admin/analyses")
            if admin_response.status_code == 200:
                analyses = admin_response.json()
                for analysis in analyses:
                    if analysis.get("id") == analysis_id:
                        print(f"   Admin view: {analysis}")
                        break
        except:
            print("   Could not access admin endpoint")
            
else:
    print(f"   Error submitting: {response.text[:500]}")

# Check health again to see if models are actually loading
print("\n5. Checking model status in health...")
health = requests.get(f"{BASE_URL}/health")
health_data = health.json()
print(f"   Models mode: {health_data.get('models', {}).get('mode')}")
print(f"   Models OK: {health_data.get('models', {}).get('ok')}")

print("\n" + "=" * 80)
print("DIAGNOSIS COMPLETE")
print("=" * 80)
print("\nLikely issues:")
print("1. HF_API_TOKEN is not set or invalid")
print("2. Models are failing to load in the worker")
print("3. The worker is encountering an error during processing")
print("\nTo fix:")
print("1. Check Render logs for detailed error messages")
print("2. Ensure HF_API_TOKEN is set in Render environment")
print("3. Consider using local models instead of HF API")
