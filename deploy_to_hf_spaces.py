"""Deploy CV Analyser to Hugging Face Spaces"""
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
        return False
    print(result.stdout)
    return True

def main():
    """Deploy the CV Analyser to HF Spaces."""
    print("=== CV Analyser HF Spaces Deployment ===\n")
    
    # Check if we're in the right directory
    if not Path("app").exists():
        print("Error: Not in the service directory. Please run from the service folder.")
        return False
    
    # Create deployment directory
    deploy_dir = Path("hf_deploy")
    if deploy_dir.exists():
        import shutil
        shutil.rmtree(deploy_dir)
    
    deploy_dir.mkdir()
    print(f"Created deployment directory: {deploy_dir}")
    
    # Copy necessary files
    print("\n1. Copying application files...")
    files_to_copy = [
        "app/",
        "alembic.ini",
        "migrations/",
        "requirements.hf.txt",
        "Dockerfile.simple",
        ".gitignore.hf",
        "README.md"
    ]
    
    import shutil
    for item in files_to_copy:
        src = Path(item)
        if src.exists():
            if src.is_dir():
                shutil.copytree(src, deploy_dir / src.name)
            else:
                shutil.copy2(src, deploy_dir / src.name)
            print(f"   ✅ Copied {item}")
        else:
            print(f"   ❌ Not found: {item}")
    
    # Rename files for deployment
    print("\n2. Preparing deployment files...")
    (deploy_dir / "requirements.hf.txt").rename(deploy_dir / "requirements.txt")
    (deploy_dir / "Dockerfile.simple").rename(deploy_dir / "Dockerfile")
    (deploy_dir / ".gitignore.hf").rename(deploy_dir / ".gitignore")
    
    # Create .env file for HF Spaces
    env_content = """# HF Spaces Environment Variables
ENVIRONMENT=production
SERVICE_HOST=0.0.0.0
SERVICE_PORT=7860
SKIP_MODEL_LOAD=false
INLINE_JOBS=true
LAZY_MODEL_LOAD=true
"""
    (deploy_dir / ".env").write_text(env_content)
    print("   ✅ Created .env")
    
    # Instructions
    print("\n3. Deployment ready!")
    print("\nNext steps:")
    print(f"1. cd {deploy_dir}")
    print("2. git init")
    print("3. git add .")
    print('4. git commit -m "Deploy CV Analyser to HF Spaces"')
    print("5. git remote add hf https://huggingface.co/spaces/Dzunisani007/cv-analyser")
    print("6. git push hf main")
    print("\n4. After deployment:")
    print("   - Add secrets in Space Settings:")
    print("     DATABASE_URL=postgresql://recruiter:zhubXkTYjieGoYevXB7jtHj5EdhNYmV7@dpg-d6v72fchg0os73ddre00-a.oregon-postgres.render.com/analyser_w2n9?sslmode=require")
    print("     HF_TOKEN=your_token_here (optional)")
    print("     SKIP_MODEL_LOAD=false")
    print("     INLINE_JOBS=true")
    print("\n   - Test at: https://dzunisani007-cv-analyser.hf.space/health")
    
    # Option to initialize git
    response = input("\nInitialize git repository and push? (y/n): ")
    if response.lower() == 'y':
        os.chdir(deploy_dir)
        
        if not run_command("git init"):
            return False
        if not run_command('git add .'):
            return False
        if not run_command('git commit -m "Deploy CV Analyser to HF Spaces"'):
            return False
        
        # Check if remote already exists
        result = subprocess.run("git remote", shell=True, capture_output=True, text=True)
        if "hf" not in result.stdout:
            if not run_command("git remote add hf https://huggingface.co/spaces/Dzunisani007/cv-analyser"):
                return False
        
        print("\nPushing to Hugging Face Spaces...")
        if not run_command("git push hf main"):
            print("\nIf push failed, you may need to:")
            print("1. Install HF CLI: huggingface-cli login")
            print("2. Use access token as password")
            print("3. Try again: git push hf main")
            return False
        
        print("\n✅ Deployment pushed successfully!")
        print("Monitor build at: https://huggingface.co/spaces/Dzunisani007/cv-analyser")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
