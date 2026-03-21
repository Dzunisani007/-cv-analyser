"""Quick diagnostic - what's hanging?"""
import os
import sys
import time

print("Quick diagnostic - checking what's hanging...")

# Set minimal environment
os.environ["HF_API_TOKEN"] = ""
os.environ["SKIP_MODEL_LOAD"] = "true"  # Skip models to test basic loading

try:
    print("1. Testing basic import...")
    from app.main import app
    print("   ✅ Basic import works")
    
    print("\n2. Testing database connection...")
    from app.db import init_session_factory
    init_session_factory()
    print("   ✅ Database connection works")
    
    print("\n3. Testing config...")
    from app.config import settings
    print(f"   ✅ Config loaded, NER_MODE: {settings.ner_mode}")
    
    print("\n✅ Basic components work!")
    print("The issue is likely model loading taking too long.")
    
except Exception as e:
    print(f"\n❌ Error in basic components: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
print("DIAGNOSIS:")
print("- If basic import works but models hang, it's a memory/loading issue")
print("- Render free tier (512MB) may not be enough for transformer models")
print("- Solution: Use Hugging Face Spaces (16GB free) or set SKIP_MODEL_LOAD=true")
