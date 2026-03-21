"""Test simple startup"""
import os
import sys

# Set environment
os.environ["DATABASE_URL"] = "postgresql://recruiter:zhubXkTYjieGoYevXB7jtHj5EdhNYmV7@dpg-d6v72fchg0os73ddre00-a.oregon-postgres.render.com/analyser_w2n9?sslmode=require"
os.environ["HF_API_TOKEN"] = ""
os.environ["SKIP_MODEL_LOAD"] = "false"
os.environ["INLINE_JOBS"] = "true"

print("Testing simple startup...")

try:
    # Test database connection
    from app.db import check_db
    db_status = check_db()
    print(f"Database: {db_status}")
    
    # Test model loading
    from app.services.embedding_matcher import load_embed
    from app.services.ner_and_canon import load_ner
    
    print("\nLoading models...")
    embed_model = load_embed()
    print(f"Embeddings: {type(embed_model)}")
    
    ner_model = load_ner()
    print(f"NER: {type(ner_model)}")
    
    # Test creating a record
    from app.db import session_scope
    from app.models import CVRecord, CVAnalysis
    import uuid
    
    with session_scope() as db:
        record = CVRecord(cv_text="Test CV", status="pending")
        db.add(record)
        db.flush()
        print(f"\n✅ Created CV record: {record.id}")
    
    print("\n✅ All tests passed!")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
