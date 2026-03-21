"""Test HF token with the correct API endpoint"""
import requests
import json

HF_TOKEN = "hf_YMOefnqmd1JnCnacvKXCRpCkYsMPzFomsT"

print("Testing HF token with the correct API...")

# Test 1: Check whoami with the new API
print("\n1. Testing token validity...")
try:
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    response = requests.get("https://huggingface.co/api/whoami", headers=headers)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        user_info = response.json()
        print(f"   ✅ Token valid for: {user_info}")
    else:
        print(f"   ❌ Response: {response.text}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 2: Test with the new router API
print("\n2. Testing with router.huggingface.co...")
try:
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    data = {"inputs": "John Doe works at Google as a software engineer"}
    
    # Try NER model
    response = requests.post(
        "https://router.huggingface.co/huggingface-course/dslim/bert-base-NER",
        headers=headers,
        json=data
    )
    print(f"   NER Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ NER working: {len(result)} entities")
    else:
        print(f"   ❌ NER error: {response.text}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 3: Test feature extraction
print("\n3. Testing feature extraction...")
try:
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    data = {"inputs": ["This is a test sentence."]}
    
    response = requests.post(
        "https://router.huggingface.co/huggingface-course/sentence-transformers/all-MiniLM-L6-v2",
        headers=headers,
        json=data
    )
    print(f"   Embedding Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Embeddings working: {type(result)}")
    else:
        print(f"   ❌ Embedding error: {response.text}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 4: Try the huggingface_hub InferenceClient directly
print("\n4. Testing with huggingface_hub client...")
try:
    from huggingface_hub import InferenceClient
    
    client = InferenceClient(api_key=HF_TOKEN)
    
    # Test NER
    result = client.token_classification(
        "John Doe works at Google",
        model="dslim/bert-base-NER"
    )
    print(f"   ✅ HF Hub NER: {len(result)} entities")
    
    # Test embeddings
    result = client.feature_extraction(
        "This is a test",
        model="sentence-transformers/all-MiniLM-L6-v2"
    )
    print(f"   ✅ HF Hub embeddings: {len(result[0])} dimensions")
    
except Exception as e:
    print(f"   ❌ HF Hub error: {e}")

print("\n" + "=" * 60)
print("TOKEN TEST COMPLETE")
print("=" * 60)
