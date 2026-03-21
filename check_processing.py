"""Check if the analysis is actually processing now"""
import requests
import time

BASE_URL = "https://cv-analyser-kt1u.onrender.com"
analysis_id = "81389e6f-b43e-47f6-8b00-afbd78873d9f"

print(f"Checking analysis {analysis_id}...")

for i in range(10):
    time.sleep(3)
    response = requests.get(f"{BASE_URL}/api/v1/analyze/{analysis_id}/status")
    if response.status_code == 200:
        status = response.json()
        print(f"   Check {i+1}: {status.get('status')}")
        
        if status.get('status') == 'completed':
            print("\n   ✅ Analysis completed!")
            # Get result
            result_response = requests.get(f"{BASE_URL}/api/v1/analyze/{analysis_id}/result")
            if result_response.status_code == 200:
                result = result_response.json()
                print(f"   Overall Score: {result.get('overall_score', 'N/A')}")
            break
        elif status.get('status') == 'failed':
            print("\n   ❌ Analysis failed")
            break
else:
    print("\n   ⏰ Still processing or timed out")

print("\n" + "=" * 60)
print("If it's still 'processing', the service might be working")
print("but taking time to load models or process the request.")
print("=" * 60)
