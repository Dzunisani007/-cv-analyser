"""Test if the token is being read correctly in the service"""
import requests

BASE_URL = "https://cv-analyser-kt1u.onrender.com"

print("Testing if HF token is configured in the service...")

# Check health to see model status
health = requests.get(f"{BASE_URL}/health")
health_data = health.json()
print(f"Models mode: {health_data.get('models', {}).get('mode')}")
print(f"Models OK: {health_data.get('models', {}).get('ok')}")

# The issue might be that the token is not being passed to the environment
# Let's check if there's a way to verify the token is set

print("\n" + "=" * 60)
print("POSSIBLE ISSUES:")
print("1. Token might not be passed to the container environment")
print("2. Token might have expired or been revoked")
print("3. Service might be using a cached token")
print("\nRECOMMENDATIONS:")
print("1. In Render dashboard, verify the HF_API_TOKEN is exactly:")
print("   hf_YMOefnqmd1JnCnacvKXCRpCkYsMPzFomsT")
print("2. Click 'Save Changes' after updating")
print("3. Trigger a 'Manual Deploy' to ensure the token is loaded")
print("4. Check the service logs after deployment for any token errors")
print("=" * 60)
