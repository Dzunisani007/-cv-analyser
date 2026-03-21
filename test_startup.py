"""Quick test to verify the service starts correctly"""
import os
import sys
import time

# Set environment like Render
os.environ["PORT"] = "8000"
os.environ["HF_API_TOKEN"] = ""  # Use local models
os.environ["SKIP_MODEL_LOAD"] = "false"  # Load models to test

print("Testing CV Analyser startup...")

try:
    # Import and check if app loads
    from app.main import app
    print("✅ App imported successfully")
    
    # Test if models can load (this is where it might hang)
    print("\nTesting model loading (this may take 30-60 seconds)...")
    start = time.time()
    
    from app.services.embedding_matcher import load_embed
    model = load_embed()
    print(f"✅ Embeddings loaded in {time.time()-start:.1f}s: {type(model)}")
    
    from app.services.ner_and_canon import load_ner
    ner = load_ner()
    print(f"✅ NER loaded: {type(ner)}")
    
    print("\n✅ All components loaded successfully!")
    print("The service should work on Render with the fixes.")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    
    if "Killed" in str(e) or "Memory" in str(e):
        print("\n⚠️  This looks like a memory issue.")
        print("Render's free tier (512MB RAM) may not be enough.")
        print("Consider Hugging Face Spaces (16GB RAM free) or upgrade Render.")
