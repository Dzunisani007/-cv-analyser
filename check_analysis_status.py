"""Check analysis status and error details"""
import requests
import json

BASE_URL = "https://cv-analyser-kt1u.onrender.com"

# Use the analysis ID from the test
analysis_id = "038bf675-200c-4fa3-bc7d-08fd49ffcc5d"

print(f"Checking analysis status for: {analysis_id}")

# Get status
response = requests.get(f"{BASE_URL}/api/v1/analyze/{analysis_id}/status")
print(f"\nStatus endpoint: {response.status_code}")
if response.status_code == 200:
    status_data = response.json()
    print(f"Status: {status_data}")
    
    # If failed, try to get more details
    if status_data.get("status") == "failed":
        print("\nAnalysis failed. Checking for error details...")
        
        # Try to get the result (might contain error info)
        result_response = requests.get(f"{BASE_URL}/api/v1/analyze/{analysis_id}/result")
        print(f"Result endpoint: {result_response.status_code}")
        if result_response.status_code == 200:
            result = result_response.json()
            print(f"Result: {json.dumps(result, indent=2)}")
        else:
            print(f"Error: {result_response.text}")
else:
    print(f"Error: {response.text}")

# Also check if there are any recent analyses
print("\n\nChecking for any existing analyses...")
try:
    # Try to list analyses (might not exist)
    response = requests.get(f"{BASE_URL}/api/v1/analyses")
    print(f"Analyses list: {response.status_code}")
    if response.status_code == 200:
        analyses = response.json()
        print(f"Found {len(analyses)} analyses")
        for analysis in analyses[:3]:  # Show first 3
            print(f"  - ID: {analysis.get('id')}, Status: {analysis.get('status')}")
except:
    print("Could not list analyses")
