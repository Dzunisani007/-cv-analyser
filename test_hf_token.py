"""Test HF API token directly"""
import requests
import os

# Test the HF API token
HF_TOKEN = "hf_YMOefnqmd1JnCnacvKXCRpCkYsMPzFomsT"

print("Testing Hugging Face API token...")

# Test 1: Check if token is valid
print("\n1. Testing token validity...")
try:
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    response = requests.get("https://huggingface.co/api/whoami", headers=headers)
    if response.status_code == 200:
        user_info = response.json()
        print(f"   ✅ Token is valid for user: {user_info.get('name', 'Unknown')}")
    else:
        print(f"   ❌ Token invalid: {response.status_code} - {response.text}")
except Exception as e:
    print(f"   ❌ Error checking token: {e}")

# Test 2: Test NER model API
print("\n2. Testing NER model API...")
try:
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    data = {
        "inputs": "John Doe works at Google as a software engineer",
        "parameters": {"aggregation_strategy": "simple"}
    }
    response = requests.post(
        "https://api-inference.huggingface.co/models/dslim/bert-base-NER",
        headers=headers,
        json=data
    )
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ NER model working: {len(result)} entities found")
    else:
        print(f"   ❌ NER model error: {response.status_code} - {response.text}")
except Exception as e:
    print(f"   ❌ Error testing NER: {e}")

# Test 3: Test embedding model
print("\n3. Testing embedding model...")
try:
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    data = {
        "inputs": ["This is a test sentence."]
    }
    response = requests.post(
        "https://api-inference.huggingface.co/models/sentence-transformers/all-MiniLM-L6-v2",
        headers=headers,
        json=data
    )
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Embedding model working: {len(result[0])} dimensions")
    else:
        print(f"   ❌ Embedding model error: {response.status_code} - {response.text}")
except Exception as e:
    print(f"   ❌ Error testing embeddings: {e}")

# Test 4: Check if models are loaded in the deployed service
print("\n4. Testing deployed service model status...")
try:
    response = requests.get("https://cv-analyser-kt1u.onrender.com/health")
    if response.status_code == 200:
        health = response.json()
        print(f"   Models mode: {health.get('models', {}).get('mode')}")
        print(f"   Models OK: {health.get('models', {}).get('ok')}")
        if not health.get('models', {}).get('ok'):
            print("   ⚠️  Models are not OK in health check")
except Exception as e:
    print(f"   ❌ Error checking health: {e}")

print("\n" + "=" * 60)
print("DIAGNOSIS COMPLETE")
print("=" * 60)
