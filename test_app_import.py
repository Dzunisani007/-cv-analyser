"""Test app import"""
import os

# Set environment
os.environ["DATABASE_URL"] = "postgresql://recruiter:zhubXkTYjieGoYevXB7jtHj5EdhNYmV7@dpg-d6v72fchg0os73ddre00-a.oregon-postgres.render.com/analyser_w2n9?sslmode=require"
os.environ["HF_API_TOKEN"] = ""
os.environ["SKIP_MODEL_LOAD"] = "false"
os.environ["INLINE_JOBS"] = "true"

print("Testing app import...")

try:
    from app.main import app
    print("✅ App imported successfully")
    
    # Test creating a test client
    from fastapi.testclient import TestClient
    client = TestClient(app)
    
    # Test root endpoint
    response = client.get("/")
    print(f"Root endpoint: {response.status_code}")
    
    # Test health endpoint
    response = client.get("/health")
    print(f"Health endpoint: {response.status_code}")
    if response.status_code == 200:
        print(f"  Health data: {response.json()}")
    
    # Test analyze endpoint
    payload = {"cv_text": "Test CV", "job_description": "Test job"}
    response = client.post("/api/v1/analyze", json=payload)
    print(f"Analyze endpoint: {response.status_code}")
    if response.status_code == 202:
        print(f"  Analysis ID: {response.json()}")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
