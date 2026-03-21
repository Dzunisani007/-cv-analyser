"""Complete API test with new database"""
import os
import requests
import time
import subprocess
import sys

# Set environment
os.environ["DATABASE_URL"] = "postgresql://recruiter:zhubXkTYjieGoYevXB7jtHj5EdhNYmV7@dpg-d6v72fchg0os73ddre00-a.oregon-postgres.render.com/analyser_w2n9?sslmode=require"
os.environ["HF_API_TOKEN"] = ""
os.environ["SKIP_MODEL_LOAD"] = "false"
os.environ["INLINE_JOBS"] = "true"

print("Complete API test with new database...")

def start_server():
    return subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

print("\n1. Starting server...")
server_process = start_server()
time.sleep(15)

try:
    # Test health
    print("\n2. Testing health endpoint...")
    response = requests.get("http://127.0.0.1:8000/health", timeout=10)
    if response.status_code == 200:
        print("   ✅ Health OK")
        health = response.json()
        print(f"   Models mode: {health.get('models', {}).get('mode', 'unknown')}")
    else:
        print(f"   ❌ Health failed: {response.status_code}")
        return
    
    # Test analyze
    print("\n3. Testing analyze endpoint...")
    payload = {
        "cv_text": "John Doe\nSoftware Engineer\n\nExperience:\n- Senior Python Developer at Tech Corp\n- Developed web applications using Django, Flask\n- Worked with PostgreSQL, MongoDB, Redis\n- Led team of 5 developers\n\nSkills:\n- Python, Django, Flask\n- PostgreSQL, MongoDB\n- Docker, Kubernetes\n- Git, CI/CD\n\nEducation:\n- BSc Computer Science, University of Technology",
        "job_description": "Senior Python Developer with Django experience and database skills"
    }
    
    response = requests.post(
        "http://127.0.0.1:8000/api/v1/analyze",
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=60
    )
    
    if response.status_code == 202:
        analysis_id = response.json().get("analysis_id")
        print(f"   ✅ Analysis submitted: {analysis_id}")
        
        # Poll for results
        print("\n4. Polling for results...")
        for i in range(120):
            time.sleep(1)
            status_response = requests.get(f"http://127.0.0.1:8000/api/v1/analyze/{analysis_id}/status")
            if status_response.status_code == 200:
                status_data = status_response.json()
                status = status_data.get("status")
                print(f"   Check {i+1}: {status}", end="")
                
                if status == "completed":
                    print("\n   ✅ Analysis completed successfully!")
                    result_response = requests.get(f"http://127.0.0.1:8000/api/v1/analyze/{analysis_id}/result")
                    if result_response.status_code == 200:
                        result = result_response.json()
                        print(f"\n   Overall Score: {result.get('match_analysis', {}).get('overall_score', 'N/A')}")
                        
                        structured = result.get('structured_data', {})
                        if 'personal_details' in structured:
                            print(f"   Name: {structured['personal_details'].get('full_name', 'N/A')}")
                        if 'professional_details' in structured:
                            skills = structured['professional_details'].get('skills', [])
                            print(f"   Skills found: {len(skills)}")
                    break
                elif status == "failed":
                    print("\n   ❌ Analysis failed!")
                    warnings = status_data.get("warnings", {})
                    if warnings and isinstance(warnings, dict):
                        error = warnings.get("error", "Unknown error")
                        print(f"   Error details: {error}")
                    else:
                        print(f"   Warnings: {warnings}")
                    break
        else:
            print("\n   ⏰ Analysis timed out after 2 minutes")
    else:
        print(f"   ❌ Submit failed: {response.status_code}")
        
except Exception as e:
    print(f"\n❌ Error during testing: {e}")
    import traceback
    traceback.print_exc()

finally:
    # Stop server
    print("\n5. Stopping server...")
    if server_process:
        server_process.terminate()
        server_process.wait()
        print("   ✅ Server stopped")

print("\n" + "=" * 60)
print("Test complete!")
print("=" * 60)
