import os
from pathlib import Path

# Load environment variables
for line in Path('.env').read_text().splitlines():
    if '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1)
        os.environ[k.strip()] = v.strip()

# Test the storage functions
from app.utils.storage import save_file, load_file_bytes

print("=== Testing Cloudinary Storage Fix ===")

# Test save and load
test_content = b"This is a test PDF content for CV analysis"
filename = "test_cv.pdf"

try:
    # Save file
    print("Saving file to Cloudinary...")
    save_result = save_file(test_content, filename, "application/pdf")
    print(f"✅ Saved successfully: {save_result}")
    
    storage_key = save_result.get("storage_key")
    print(f"Storage key: {storage_key}")
    
    # Load file
    print("Loading file from Cloudinary...")
    loaded_content = load_file_bytes(storage_key)
    
    if loaded_content == test_content:
        print("✅ File loaded successfully - content matches!")
    else:
        print(f"❌ Content mismatch. Original: {len(test_content)} bytes, Loaded: {len(loaded_content)} bytes")
    
    # Clean up
    from app.utils.storage import delete_file
    delete_file(storage_key)
    print("✅ Test file cleaned up")
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()

print("\n=== Test Complete ===")
