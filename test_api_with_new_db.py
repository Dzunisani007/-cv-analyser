"""Test API with new database"""
import os
import requests
import json
import time

# Set environment
os.environ["DATABASE_URL"] = "postgresql://recruiter:zhubXkTYjieGoYevXB7jtHj5EdhNYmV7@dpg-d6v72fchg0os73ddre00-a.oregon-postgres.render.com/analyser_w2n9?sslmode=require"
os.environ["HF_API_TOKEN"] = ""  # Use local models
os.environ["SKIP_MODEL_LOAD"] = "false"
os.environ["INLINE_JOBS"] = "true"

print("Testing API with new database...")

# Start the server
import subprocess
import sys
import threading

def start_server():
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    return process

print("\n1. Starting server...")
server_process = start_server()
time.sleep(10)  # Wait for startup

try:
    # Test health
    print("\n2. Testing health endpoint...")
    response = requests.get("http://127.0.0.1:8000/health", timeout=5)
    if response.status_code == 200:
        print(f"   ✅ Health OK: {response.json()}")
    else:
        print(f"   ❌ Health failed: {response.status_code}")
    
    # Test analyze
    print("\n3. Testing analyze endpoint...")
    payload = {
        "cv_text": """John Doe
Software Engineer

Experience:
- Senior Python Developer at Tech Corp (2020-Present)
- Developed web applications using Django, Flask
- Worked with PostgreSQL, MongoDB, Redis
- Led team of 5 developers

Skills:
- Python, Django, Flask
- PostgreSQL, MongoDB
- Docker, Kubernetes
- Git, CI/CD

Education:
- BSc Computer Science, University of Technology (2016-2020)""",
        "job_description": "Senior Python Developer with Django experience and database skills"
    }
    
    response = requests.post(
        "http://127.0.0.1:8000/api/v1/analyze",
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=30
    )
    
    if response.status_code == 202:
        analysis_id = response.json().get("analysis_id")
        print(f"   ✅ Analysis submitted: {analysis_id}")
        
        # Poll for results
        print("\n4. Polling for results...")
        for i in range(60):  # Wait up to 60 seconds
            time.sleep(1)
            status_response = requests.get(f"http://127.0.0.1:8000/api/v1/analyze/{analysis_id}/status")
            if status_response.status_code == 200:
                status_data = status_response.json()
                status = status_data.get("status")
                print(f"   Check {i+1}: {status}")
                
                if status == "completed":
                    print("\n   ✅ Analysis completed!")
                    # Get result
                    result_response = requests.get(f"http://127.0.0.1:8000/api/v1/analyze/{analysis_id}/result")
                    if result_response.status_code == 200:
                        result = result_response.json()
                        print(f"   Overall Score: {result.get('match_analysis', {}).get('overall_score', 'N/A')}")
                        
                        # Show some extracted data
                        structured = result.get('structured_data', {})
                        if 'personal_details' in structured:
                            print(f"   Name: {structured['personal_details'].get('full_name', 'N/A')}")
                        if 'professional_details' in structured:
                            skills = structured['professional_details'].get('skills', [])
                            print(f"   Skills found: {skills[:5]}...")  # Show first 5 skills
                    break
                elif status == "failed":
                    print("\n   ❌ Analysis failed!")
                    warnings = status_data.get("warnings", {})
                    if warnings:
                        print(f"   Error: {warnings}")
                    break
        else:
            print("\n   ⏰ Analysis timed out")
    else:
        print(f"   ❌ Submit failed: {response.status_code} - {response.text}")
        
except Exception as e:
    print(f"\n❌ Error during testing: {e}")
    import traceback
    traceback.print_exc()

finally:
    # Stop the server
    print("\n5. Stopping server...")
    if server_process:
        server_process.terminate()
        server_process.wait()
        print("   ✅ Server stopped")

print("\n" + "=" * 60)
print("Test complete!")
print("=" * 60)
