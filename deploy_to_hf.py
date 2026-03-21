"""Deploy to Hugging Face Spaces"""
import os
import subprocess
import sys
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a command and return the result."""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        sys.exit(1)
    return result.stdout

def main():
    """Deploy the CV Analyser to Hugging Face Spaces."""
    print("=== CV Analyser HF Spaces Deployment ===\n")
    
    # Check if we're in the right directory
    if not Path("app").exists():
        print("Error: Not in the service directory. Please run from the service folder.")
        sys.exit(1)
    
    # Check if Dockerfile.hf exists
    if not Path("Dockerfile.hf").exists():
        print("Error: Dockerfile.hf not found.")
        sys.exit(1)
    
    # Copy Dockerfile.hf to Dockerfile
    print("\n1. Preparing Dockerfile...")
    run_command("cp Dockerfile.hf Dockerfile")
    
    # Copy requirements.hf.txt to requirements.txt
    print("\n2. Preparing requirements...")
    run_command("cp requirements.hf.txt requirements.txt")
    
    # Create .env file with HF settings
    print("\n3. Preparing environment...")
    env_content = """# Hugging Face Spaces Environment
ENVIRONMENT=production
SERVICE_HOST=0.0.0.0
SERVICE_PORT=7860
LAZY_MODEL_LOAD=true
INLINE_JOBS=true
SKIP_MODEL_LOAD=false
"""
    with open(".env", "w") as f:
        f.write(env_content)
    
    print("\n4. Files prepared for HF Spaces deployment!")
    print("\nNext steps:")
    print("1. Create a new Hugging Face Space with Docker template")
    print("2. Initialize git in this directory:")
    print("   git init")
    print("   git add .")
    print("   git commit -m 'Initial HF Spaces deployment'")
    print("3. Add HF Space as remote:")
    print("   git remote add hf https://huggingface.co/spaces/your-username/cv-analyser")
    print("4. Push to HF Spaces:")
    print("   git push hf main")
    print("\n5. Set DATABASE_URL as a secret in your HF Space settings")
    print("\n6. After deployment, call POST /warmup to pre-load models")
    
    # Optionally initialize git
    if Path(".git").exists():
        print("\n⚠️  Git repository already exists. Proceed with caution.")
    else:
        response = input("\nInitialize git repository? (y/n): ")
        if response.lower() == 'y':
            run_command("git init")
            run_command("git add .")
            run_command('git commit -m "Initial HF Spaces deployment"')
            print("\n✅ Git repository initialized!")

if __name__ == "__main__":
    main()
