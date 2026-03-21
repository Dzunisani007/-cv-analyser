"""Test HF Spaces setup locally"""
import os
import subprocess
import sys
import time
import requests

# Set HF Spaces environment
os.environ["DATABASE_URL"] = "postgresql://recruiter:zhubXkTYjieGoYevXB7jtHj5EdhNYmV7@dpg-d6v72fchg0os73ddre00-a.oregon-postgres.render.com/analyser_w2n9?sslmode=require"
os.environ["SERVICE_PORT"] = "7860"
os.environ["LAZY_MODEL_LOAD"] = "true"
os.environ["INLINE_JOBS"] = "true"
os.environ["SKIP_MODEL_LOAD"] = "false"

print("Testing HF Spaces setup locally...")

def test_imports():
    """Test that all imports work with HF settings."""
    print("\n1. Testing imports...")
    try:
        from app.main import app
        print("   ✅ App imported successfully")
        return True
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        return False

def test_health_endpoint():
    """Test health endpoint with lazy loading."""
    print("\n2. Testing health endpoint...")
    try:
        from fastapi.testclient import TestClient
        from app.main import app
        
        client = TestClient(app)
        response = client.get("/health")
        
        if response.status_code == 200:
            health = response.json()
            print(f"   ✅ Health OK")
            print(f"   Database: {health.get('db', {}).get('ok', 'unknown')}")
            print(f"   Models: {health.get('models', {}).get('mode', 'unknown')}")
            return True
        else:
            print(f"   ❌ Health failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Health test failed: {e}")
        return False

def test_warmup_endpoint():
    """Test model warmup endpoint."""
    print("\n3. Testing warmup endpoint...")
    try:
        from fastapi.testclient import TestClient
        from app.main import app
        
        client = TestClient(app)
        response = client.post("/warmup")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Warmup successful: {result.get('status')}")
            models = result.get('models', {})
            print(f"   NER: {models.get('ner', 'unknown')}")
            print(f"   Embeddings: {models.get('embeddings', 'unknown')}")
            return True
        else:
            print(f"   ❌ Warmup failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Warmup test failed: {e}")
        return False

def test_analyze_endpoint():
    """Test analyze endpoint with lazy loading."""
    print("\n4. Testing analyze endpoint...")
    try:
        from fastapi.testclient import TestClient
        from app.main import app
        
        client = TestClient(app)
        payload = {
            "cv_text": "John Doe\nSoftware Engineer\n5 years experience with Python and Django",
            "job_description": "Senior Python Developer"
        }
        
        response = client.post("/api/v1/analyze", json=payload)
        
        if response.status_code == 202:
            analysis_id = response.json().get("analysis_id")
            print(f"   ✅ Analysis submitted: {analysis_id}")
            
            # Check status
            time.sleep(5)  # Wait for processing
            status_response = client.get(f"/api/v1/analyze/{analysis_id}/status")
            if status_response.status_code == 200:
                status = status_response.json()
                print(f"   Status: {status.get('status')}")
                if status.get("warnings"):
                    print(f"   Warnings: {status.get('warnings')}")
            return True
        else:
            print(f"   ❌ Analyze failed: {response.status_code}")
            if response.text:
                print(f"   Response: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"   ❌ Analyze test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    
    tests = [
        test_imports,
        test_health_endpoint,
        test_warmup_endpoint,
        test_analyze_endpoint
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 60)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All tests passed! Ready for HF Spaces deployment.")
    else:
        print("❌ Some tests failed. Fix issues before deploying.")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
