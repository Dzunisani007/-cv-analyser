"""Test direct database insertion to bypass worker"""
import os
import psycopg2
import uuid
from datetime import datetime
import json

# Database connection
db_url = os.getenv("DATABASE_URL", "postgresql://recruitement_deploy_user:tHkpCaJ8nxQpN1tCItF7BEXNvzLrkgiQ@dpg-d62tb67pm1nc738h8jv0-a.oregon-postgres.render.com/recruitement_deploy?sslmode=require")

print("=" * 80)
print("TESTING DIRECT DATABASE INSERTION")
print("=" * 80)

try:
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor()
    
    # Create a test CV record
    print("\n1. Creating CV record...")
    cv_text = "John Doe\nSoftware Engineer\nPython, Django, PostgreSQL\n5 years experience"
    record_id = str(uuid.uuid4())
    cursor.execute("""
        INSERT INTO cv_records (id, cv_text, status, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
    """, (record_id, cv_text, "completed", datetime.now(), datetime.now()))
    
    print(f"   ✅ CV Record created: {record_id}")
    
    # Create a test analysis
    print("\n2. Creating analysis...")
    job_description = "Senior Python Developer with Django experience"
    
    # Create a mock result
    result = {
        "schema_version": "v1",
        "extraction_metadata": {"method": "direct", "confidence": 0.9},
        "structured_data": {
            "personal_details": {"full_name": "John Doe"},
            "professional_details": {"skills": ["Python", "Django", "PostgreSQL"]}
        },
        "match_analysis": {
            "overall_score": 85,
            "component_scores": {"skills": 90, "experience": 80},
            "evidence": {"matched_skills": ["Python", "Django"]}
        }
    }
    
    analysis_id = str(uuid.uuid4())
    cursor.execute("""
        INSERT INTO cv_analyses 
        (id, record_id, job_description, status, result, overall_score, component_scores, started_at, finished_at, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    """, (
        analysis_id,
        record_id,
        job_description,
        "completed",
        json.dumps(result),
        85,
        json.dumps({"skills": 90, "experience": 80}),
        datetime.now(),
        datetime.now(),
        datetime.now(),
        datetime.now()
    ))
    
    print(f"   ✅ Analysis created: {analysis_id}")
    
    conn.commit()
    
    # Test retrieving via API
    print("\n3. Testing API retrieval...")
    import requests
    
    # Get status
    status_response = requests.get(f"https://cv-analyser-kt1u.onrender.com/api/v1/analyze/{analysis_id}/status")
    print(f"   Status endpoint: {status_response.status_code}")
    if status_response.status_code == 200:
        print(f"   Status: {status_response.json()}")
    
    # Get result
    result_response = requests.get(f"https://cv-analyser-kt1u.onrender.com/api/v1/analyze/{analysis_id}/result")
    print(f"   Result endpoint: {result_response.status_code}")
    if result_response.status_code == 200:
        print(f"   Result: {result_response.json()}")
    else:
        print(f"   Error: {result_response.text[:200]}")
    
    conn.close()
    
    print("\n✅ Direct insertion test completed!")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    if 'conn' in locals():
        conn.rollback()

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
