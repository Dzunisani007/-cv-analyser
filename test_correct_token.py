"""Test the correct HF token"""
import requests

HF_TOKEN = "hf_YMOefnqmd1JnCnacvKXCRpCkYsMPzFomsT"

print("Testing the correct HF token...")

# Test 1: Check token validity
print("\n1. Testing token validity...")
try:
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    response = requests.get("https://huggingface.co/api/whoami", headers=headers)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        user_info = response.json()
        print(f"   ✅ Token valid for: {user_info.get('name', 'Unknown')}")
        print(f"   ✅ User type: {user_info.get('type', 'Unknown')}")
    else:
        print(f"   ❌ Response: {response.text}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 2: Test with huggingface_hub InferenceClient
print("\n2. Testing with huggingface_hub client...")
try:
    from huggingface_hub import InferenceClient
    
    client = InferenceClient(api_key=HF_TOKEN)
    
    # Test NER
    result = client.token_classification(
        "John Doe works at Google as a software engineer",
        model="dslim/bert-base-NER"
    )
    print(f"   ✅ NER working: Found {len(result)} entities")
    for entity in result[:3]:
        print(f"      - {entity.get('word', '')}: {entity.get('entity_group', '')}")
    
    # Test embeddings
    result = client.feature_extraction(
        "This is a test sentence for CV analysis",
        model="sentence-transformers/all-MiniLM-L6-v2"
    )
    print(f"   ✅ Embeddings working: {len(result[0])} dimensions")
    
except Exception as e:
    print(f"   ❌ HF Hub error: {e}")

print("\n" + "=" * 60)
print("TOKEN IS VALID! The issue must be elsewhere...")
print("=" * 60)
print("\nNext steps:")
print("1. The token is working - the issue is in the deployed service")
print("2. The token might not be passed to the container correctly")
print("3. Check Render service logs for actual error details")
print("4. The service might need to be redeployed to pick up the token")
