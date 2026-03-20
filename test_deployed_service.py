"""Test script for deployed CV Analyser service"""
import requests
import json
import time
from datetime import datetime

BASE_URL = "https://cv-analyser-kt1u.onrender.com"

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Health check passed")
        print(f"   Database: {'OK' if data['db']['ok'] else 'ERROR'}")
        print(f"   Storage: {data['storage']['mode']} ({'OK' if data['storage']['ok'] else 'ERROR'})")
        print(f"   Models: {data['models']['mode']} ({'OK' if data['models']['ok'] else 'ERROR'})")
        return True
    else:
        print(f"❌ Health check failed: {response.status_code}")
        return False

def test_analyze_endpoint():
    """Test the new analyze endpoint"""
    print("\nTesting analyze endpoint...")
    
    # Sample CV text
    cv_text = """
    John Doe
    Software Engineer
    
    Experience:
    - Senior Software Engineer at Tech Corp (2020-2023)
    - Developed REST APIs using Python and FastAPI
    - Worked with PostgreSQL databases
    - Implemented CI/CD pipelines
    
    Skills:
    - Python, JavaScript, SQL
    - Docker, Kubernetes
    - AWS, Git
    """
    
    # Test data
    payload = {
        "cv_text": cv_text,
        "job_description": "Looking for a Senior Software Engineer with Python and PostgreSQL experience",
        "industry": "technology"
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer test-secret"  # You may need to update this
    }
    
    # Submit analysis
    response = requests.post(
        f"{BASE_URL}/api/v1/analyze",
        json=payload,
        headers=headers
    )
    
    if response.status_code == 202:
        data = response.json()
        analysis_id = data.get("analysis_id")
        print(f"✅ Analysis submitted successfully")
        print(f"   Analysis ID: {analysis_id}")
        
        # Poll for results
        print("\nPolling for results...")
        for i in range(30):  # Poll for up to 30 seconds
            time.sleep(1)
            status_response = requests.get(
                f"{BASE_URL}/api/v1/analyze/{analysis_id}/status",
                headers=headers
            )
            
            if status_response.status_code == 200:
                status_data = status_response.json()
                status = status_data.get("status")
                print(f"   Status: {status}")
                
                if status == "completed":
                    # Get results
                    result_response = requests.get(
                        f"{BASE_URL}/api/v1/analyze/{analysis_id}/result",
                        headers=headers
                    )
                    
                    if result_response.status_code == 200:
                        result = result_response.json()
                        print(f"✅ Analysis completed!")
                        print(f"   Overall Score: {result.get('overall_score', 'N/A')}")
                        print(f"   Component Scores: {result.get('component_scores', {})}")
                        return True
                    else:
                        print(f"❌ Failed to get results: {result_response.status_code}")
                        return False
                        
                elif status == "failed":
                    print(f"❌ Analysis failed")
                    return False
        else:
            print("⏰ Analysis timed out")
            return False
    else:
        print(f"❌ Failed to submit analysis: {response.status_code}")
        print(f"   Error: {response.text}")
        return False

def main():
    print("=" * 60)
    print("CV Analyser Deployment Test")
    print("=" * 60)
    print(f"Testing service at: {BASE_URL}")
    print(f"Time: {datetime.now().isoformat()}")
    print("=" * 60)
    
    # Run tests
    health_ok = test_health()
    
    if health_ok:
        analyze_ok = test_analyze_endpoint()
        
        if analyze_ok:
            print("\n" + "=" * 60)
            print("✅ ALL TESTS PASSED!")
            print("The refactored CV Analyser is working correctly!")
            print("=" * 60)
        else:
            print("\n" + "=" * 60)
            print("⚠️  Some tests failed. Check the logs.")
            print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ Health check failed. Service may not be ready.")
        print("=" * 60)

if __name__ == "__main__":
    main()
