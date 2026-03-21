"""Test analyze endpoint validation"""
import os

# Set environment
os.environ["DATABASE_URL"] = "postgresql://recruiter:zhubXkTYjieGoYevXB7jtHj5EdhNYmV7@dpg-d6v72fchg0os73ddre00-a.oregon-postgres.render.com/analyser_w2n9?sslmode=require"
os.environ["HF_API_TOKEN"] = ""
os.environ["SKIP_MODEL_LOAD"] = "false"
os.environ["INLINE_JOBS"] = "true"

print("Testing analyze endpoint validation...")

try:
    from fastapi.testclient import TestClient
    from app.main import app
    
    client = TestClient(app)
    
    # Test with minimal valid payload
    print("\n1. Testing minimal valid payload...")
    payload = {
        "cv_text": "John Doe\nSoftware Engineer",
        "job_description": "Software engineer role"
    }
    
    response = client.post("/api/v1/analyze", json=payload)
    print(f"   Status: {response.status_code}")
    if response.status_code != 202:
        print(f"   Response: {response.json()}")
    
    # Test with empty cv_text
    print("\n2. Testing with empty cv_text...")
    payload = {
        "cv_text": "",
        "job_description": "Test"
    }
    
    response = client.post("/api/v1/analyze", json=payload)
    print(f"   Status: {response.status_code}")
    if response.status_code != 422:
        print(f"   Response: {response.json()}")
    
    # Test with cv_text too short
    print("\n3. Testing with cv_text too short...")
    payload = {
        "cv_text": "ABC",
        "job_description": "Test"
    }
    
    response = client.post("/api/v1/analyze", json=payload)
    print(f"   Status: {response.status_code}")
    if response.status_code != 422:
        print(f"   Response: {response.json()}")
    
    # Test with only cv_text (job_description optional)
    print("\n4. Testing with only cv_text...")
    payload = {
        "cv_text": "Valid CV text with enough characters to pass validation"
    }
    
    response = client.post("/api/v1/analyze", json=payload)
    print(f"   Status: {response.status_code}")
    if response.status_code != 202:
        print(f"   Response: {response.json()}")
    
    print("\n✅ Validation tests completed!")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
