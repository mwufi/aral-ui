import os
import subprocess
from pathlib import Path

def ensure_deps(frontend_dir=None):
    """
    Ensure that dependencies are installed by checking if node_modules exists.
    If node_modules doesn't exist, attempt to install dependencies using bun or npm.
    
    Args:
        frontend_dir: Path to the frontend directory. If None, it will be determined automatically.
        
    Returns:
        bool: True if dependencies are installed or were successfully installed, False otherwise.
    """
    if frontend_dir is None:
        frontend_dir = Path(__file__).parent / "frontend"
    
    if not frontend_dir.exists():
        print(f"❌ Error: Frontend directory not found at {frontend_dir}")
        return False
    
    node_modules = frontend_dir / "node_modules"
    
    # If node_modules already exists, we're good
    if node_modules.exists() and node_modules.is_dir():
        print("✅ Dependencies already installed.")
        return True
    
    # Otherwise, we need to install dependencies
    print("📦 Installing dependencies...")
    current_dir = os.getcwd()  # Save current directory
    
    try:
        os.chdir(frontend_dir)
        env = os.environ.copy()
        
        # Try with bun first
        try:
            print("Installing dependencies with Bun...")
            subprocess.run(["bun", "install"], check=True, env=env)
            print("✅ Dependencies installed successfully with Bun.")
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            # Fall back to npm
            try:
                print("Bun not found, trying with npm...")
                subprocess.run(["npm", "install"], check=True, env=env)
                print("✅ Dependencies installed successfully with npm.")
                return True
            except (subprocess.SubprocessError, FileNotFoundError):
                print("❌ Error: Could not install dependencies. Please install bun or npm.")
                return False
    finally:
        os.chdir(current_dir)  # Restore original directory

def build_frontend(api_url=None):
    frontend_dir = Path(__file__).parent / "frontend"
    if frontend_dir.exists():
        current_dir = os.getcwd()  # Save current directory
        os.chdir(frontend_dir)
        
        # Set up environment variables for the build
        env = os.environ.copy()
        if api_url:
            env["NEXT_PUBLIC_API_URL"] = api_url
            print(f"Setting API URL for build: {api_url}")
        
        # Ensure dependencies are installed first
        if not ensure_deps(frontend_dir):
            print("❌ Cannot build frontend without dependencies.")
            os.chdir(current_dir)
            return False
        
        try:
            # Try with bun first
            print("Building UI with Bun...")
            subprocess.run(["bun", "run", "build"], check=True, env=env)
            print(f"✅ UI built successfully at {os.path.abspath(frontend_dir / 'out')}")
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            # Fall back to npm
            try:
                print("Bun not found, trying with npm...")
                subprocess.run(["npm", "run", "build"], check=True, env=env)
                print(f"✅ UI built successfully at {os.path.abspath(frontend_dir / 'out')}")
                return True
            except (subprocess.SubprocessError, FileNotFoundError):
                print("❌ Error: Could not build the UI. Please install bun or npm.")
                return False
        finally:
            os.chdir(current_dir)  # Restore original directory
    else:
        print(f"❌ Error: Frontend directory not found at {frontend_dir}")
        return False

def main():
    build_frontend()

if __name__ == "__main__":
    main() 