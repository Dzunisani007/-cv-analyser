"""Test optimized HF Spaces setup with token support and lazy loading"""
import os
import sys
import time

# Test with HF_TOKEN (HF Spaces default)
print("=== Test 1: Using HF_TOKEN ===")
os.environ["DATABASE_URL"] = "postgresql://recruiter:zhubXkTYjieGoYevXB7jtHj5EdhNYmV7@dpg-d6v72fchg0os73ddre00-a.oregon-postgres.render.com/analyser_w2n9?sslmode=require"
os.environ["SERVICE_PORT"] = "7860"
os.environ["LAZY_MODEL_LOAD"] = "true"
os.environ["INLINE_JOBS"] = "true"
os.environ["SKIP_MODEL_LOAD"] = "false"
os.environ["HF_TOKEN"] = ""  # Empty token to use local models
# Don't remove HF_API_TOKEN, let it be None to use local models

def test_config():
    """Test configuration with different token names."""
    from app.config import settings
    
    print(f"\nConfiguration:")
    print(f"  Service Port: {settings.service_port}")
    print(f"  Lazy Model Load: {settings.lazy_model_load}")
    print(f"  Inline Jobs: {settings.inline_jobs}")
    print(f"  HF API Token: {'SET' if settings.hf_api_token else 'NOT SET'}")
    print(f"  Token source: {'HF_TOKEN' if os.getenv('HF_TOKEN') else 'HF_API_TOKEN' if os.getenv('HF_API_TOKEN') else 'NONE'}")
    
    return settings

def test_imports():
    """Test that all imports work."""
    print("\n=== Testing Imports ===")
    try:
        from app.main import app
        print("✅ App imported successfully")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_health_endpoint():
    """Test health endpoint."""
    print("\n=== Testing Health Endpoint ===")
    try:
        from fastapi.testclient import TestClient
        from app.main import app
        
        client = TestClient(app)
        response = client.get("/health")
        
        if response.status_code == 200:
            health = response.json()
            print("✅ Health OK")
            print(f"  Database: {health.get('db', {}).get('ok', 'unknown')}")
            print(f"  Models: {health.get('models', {}).get('mode', 'unknown')}")
            return True
        else:
            print(f"❌ Health failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health test failed: {e}")
        return False

def test_lazy_loading():
    """Test that models are not loaded on startup."""
    print("\n=== Testing Lazy Loading ===")
    try:
        from app.services.embedding_matcher import load_embed
        from app.services.ner_and_canon import load_ner
        
        # With lazy loading, these should return None
        embed_model = load_embed()
        ner_model = load_ner()
        
        print(f"  Embeddings model: {type(embed_model)} (None = lazy)")
        print(f"  NER model: {type(ner_model)} (None = lazy)")
        
        if embed_model is None and ner_model is None:
            print("✅ Lazy loading working - models not loaded on startup")
            return True
        else:
            print("❌ Lazy loading not working - models preloaded")
            return False
    except Exception as e:
        print(f"❌ Lazy loading test failed: {e}")
        return False

def test_warmup_endpoint():
    """Test model warmup endpoint."""
    print("\n=== Testing Warmup Endpoint ===")
    try:
        from fastapi.testclient import TestClient
        from app.main import app
        
        client = TestClient(app)
        response = client.post("/warmup")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Warmup successful: {result.get('status')}")
            models = result.get('models', {})
            print(f"  NER: {models.get('ner', 'unknown')}")
            print(f"  Embeddings: {models.get('embeddings', 'unknown')}")
            return True
        else:
            print(f"❌ Warmup failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Warmup test failed: {e}")
        return False

def test_analyze_endpoint():
    """Test analyze endpoint after warmup."""
    print("\n=== Testing Analyze Endpoint ===")
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
            print(f"✅ Analysis submitted: {analysis_id}")
            
            # Check status after delay
            time.sleep(5)
            status_response = client.get(f"/api/v1/analyze/{analysis_id}/status")
            if status_response.status_code == 200:
                status = status_response.json()
                print(f"  Status: {status.get('status')}")
                if status.get("warnings"):
                    print(f"  Warnings: {status.get('warnings')}")
            return True
        else:
            print(f"❌ Analyze failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Analyze test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("HF Spaces Optimization Test")
    print("=" * 60)
    
    # Test configuration
    config = test_config()
    
    # Run tests
    tests = [
        test_imports,
        test_health_endpoint,
        test_lazy_loading,
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
        print("\nDeployment checklist:")
        print("1. Create HF Space with Docker template")
        print("2. Push code to HF Space")
        print("3. Set DATABASE_URL as secret")
        print("4. Set HF_TOKEN as secret (optional)")
        print("5. Call POST /warmup after deployment")
    else:
        print("❌ Some tests failed. Fix issues before deploying.")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
