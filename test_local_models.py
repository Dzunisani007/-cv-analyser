"""Test local models with empty HF token"""
import os

# Clear HF token to force local models
os.environ["HF_API_TOKEN"] = ""

print("Testing local model loading...")

try:
    from app.services.embedding_matcher import load_embed, embed_text
    
    print("\n1. Loading embedding model...")
    model = load_embed()
    print(f"   Model type: {type(model)}")
    print(f"   Model loaded: {model}")
    
    if model != "__skipped__":
        print("\n2. Testing embedding...")
        embeddings = embed_text(["This is a test sentence."])
        print(f"   Embeddings shape: {embeddings.shape}")
        print("   ✅ Local embeddings working!")
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("Testing NER with local models...")
try:
    from app.services.ner_and_canon import load_ner
    
    print("\n3. Loading NER model...")
    ner_pipe = load_ner()
    print(f"   NER pipe type: {type(ner_pipe)}")
    
    # Test NER
    text = "John Doe works at Google as a software engineer"
    entities = ner_pipe(text)
    print(f"   Found {len(entities)} entities")
    for entity in entities[:3]:
        print(f"      - {entity.get('word', '')}: {entity.get('entity_group', '')}")
    print("   ✅ Local NER working!")
    
except Exception as e:
    print(f"   ❌ NER Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("Local model test complete!")
print("=" * 60)
