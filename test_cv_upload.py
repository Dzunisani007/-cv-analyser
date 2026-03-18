import os
import requests
from pathlib import Path

# Load environment variables
for line in Path('.env').read_text().splitlines():
    if '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1)
        os.environ[k.strip()] = v.strip()

print("=== CV Upload Test with Cloudinary ===")
BASE = "https://cv-analyser-kt1u.onrender.com"
SECRET = os.getenv('AUTH_SECRET')

try:
    # Test upload with the actual CV file
    print("Uploading Dzunisani CV...")
    with open('Dzunisani-Mabundas-Resume-Cv-Qualifications.pdf', 'rb') as f:
        upload_resp = requests.post(
            f"{BASE}/upload",
            headers={"Authorization": f"Bearer {SECRET}"},
            files={"file": ("dzunisani.pdf", f, "application/pdf")},
            timeout=60
        )
    
    print(f"Upload Status: {upload_resp.status_code}")
    if upload_resp.status_code == 202:
        upload_data = upload_resp.json()
        print(f"✅ Analysis ID: {upload_data.get('analysis_id')}")
        print(f"✅ Resume ID: {upload_data.get('resume_id')}")
        
        # Poll for completion
        analysis_id = upload_data.get('analysis_id')
        print("\nPolling for analysis completion...")
        
        import time
        max_wait = 300  # 5 minutes
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            status_resp = requests.get(
                f"{BASE}/analyses/{analysis_id}/status",
                headers={"Authorization": f"Bearer {SECRET}"},
                timeout=30
            )
            
            if status_resp.status_code == 200:
                status_data = status_resp.json()
                status = status_data.get('status')
                print(f"Status: {status}")
                
                if status == 'completed':
                    print(f"✅ Analysis completed!")
                    print(f"Match Score: {status_data.get('match_score', 0)}")
                    
                    # Get full results
                    result_resp = requests.get(
                        f"{BASE}/analyses/{analysis_id}/result",
                        headers={"Authorization": f"Bearer {SECRET}"},
                        timeout=30
                    )
                    
                    if result_resp.status_code == 200:
                        result_data = result_resp.json()
                        print(f"Overall Score: {result_data.get('overall_score', 0)}")
                        
                        component_scores = result_data.get('component_scores', {})
                        print("Component Scores:")
                        for key, value in component_scores.items():
                            print(f"  {key}: {value}")
                        
                        evidence = result_data.get('evidence', {})
                        missing_skills = evidence.get('missing_skills', [])
                        print(f"Missing Skills ({len(missing_skills)}): {missing_skills[:5]}")
                        
                        suggestions = result_data.get('suggestions', [])
                        print(f"Suggestions ({len(suggestions)}):")
                        for suggestion in suggestions[:3]:
                            print(f"  - {suggestion.get('text', 'N/A')}")
                    
                    break
                elif status == 'failed':
                    print(f"❌ Analysis failed")
                    warnings = status_data.get('warnings', {})
                    if warnings:
                        print(f"Error: {warnings.get('error', 'Unknown error')}")
                    break
                
                time.sleep(5)  # Wait 5 seconds before next check
            else:
                print(f"Status check failed: {status_resp.text}")
                break
        else:
            print("⏰ Analysis timed out")
    else:
        print(f"❌ Upload failed: {upload_resp.text}")
        
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()

print("\n=== SendGrid Setup ===")
print("To configure SendGrid for email notifications:")
print("1. Get API Key from https://app.sendgrid.com/settings/api_keys")
print("2. Add to .env:")
print("   SENDGRID_API_KEY=SG.xxxxx...")
print("   SENDGRID_FROM_EMAIL=your_email@example.com")
print("3. The system will then send analysis completion emails")
