"""Simple test of API with new database"""
import os
import requests
import time

# Set environment
os.environ["DATABASE_URL"] = "postgresql://recruiter:zhubXkTYjieGoYevXB7jtHj5EdhNYmV7@dpg-d6v72fchg0os73ddre00-a.oregon-postgres.render.com/analyser_w2n9?sslmode=require"
os.environ["HF_API_TOKEN"] = ""
os.environ["SKIP_MODEL_LOAD"] = "false"
os.environ["INLINE_JOBS"] = "true"

print("Simple API test...")

# Start server in background
import subprocess
import sys
server_proc = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)

time.sleep(20)  # Wait for startup

try:
    # Test health
    print("Testing health...")
    r = requests.get("http://127.0.0.1:8000/health", timeout=5)
    if r.status_code == 200:
        print("✅ Health OK")
    else:
        print(f"❌ Health failed: {r.status_code}")
    
    # Test analyze
    print("Testing analyze...")
    payload = {
        "cv_text": "John Doe\nPython Developer\n5 years experience",
        "job_description": "Python developer role"
    }
    
    r = requests.post("http://127.0.0.1:8000/api/v1/analyze", json=payload, timeout=30)
    if r.status_code == 202:
        analysis_id = r.json()["analysis_id"]
        print(f"✅ Submitted: {analysis_id}")
        
        # Check status after delay
        time.sleep(10)
        s = requests.get(f"http://127.0.0.1:8000/api/v1/analyze/{analysis_id}/status")
        if s.status_code == 200:
            data = s.json()
            print(f"Status: {data['status']}")
            if data.get("warnings"):
                print(f"Warnings: {data['warnings']}")
    else:
        print(f"❌ Submit failed: {r.status_code}")
        
except Exception as e:
    print(f"Error: {e}")
finally:
    server_proc.terminate()
    server_proc.wait()
