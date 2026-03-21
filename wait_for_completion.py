"""Wait for debug analysis to complete"""
import requests
import time

BASE_URL = "https://cv-analyser-kt1u.onrender.com"
analysis_id = "9ecbfc33-9139-491f-9b61-9cb2574891d8"

print(f"Waiting for analysis {analysis_id} to complete...")

for i in range(20):
    time.sleep(3)
    response = requests.get(f"{BASE_URL}/api/v1/analyze/{analysis_id}/status")
    if response.status_code == 200:
        status = response.json()
        print(f"   Check {i+1}: {status.get('status')}")
        
        if status.get('status') == 'completed':
            print("\n   ✅ SUCCESS! Analysis completed!")
            # Get result
            result_response = requests.get(f"{BASE_URL}/api/v1/analyze/{analysis_id}/result")
            if result_response.status_code == 200:
                result = result_response.json()
                print(f"   Overall Score: {result.get('overall_score', 'N/A')}")
                print(f"   Matched Skills: {result.get('match_analysis', {}).get('evidence', {}).get('matched_skills', [])}")
            break
        elif status.get('status') == 'failed':
            print("\n   ❌ Analysis failed")
            break
else:
    print("\n   ⏰ Still processing or timed out")

print("\n" + "=" * 60)
print("If it shows 'completed', the service is working!")
print("If it shows 'failed', the HF token issue persists.")
print("=" * 60)
