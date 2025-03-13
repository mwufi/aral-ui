import os
import subprocess
from pathlib import Path

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
        
        try:
            # Try with bun first
            print("Building UI with Bun...")
            subprocess.run(["bun", "install"], check=True, env=env)
            subprocess.run(["bun", "run", "build"], check=True, env=env)
            print(f"✅ UI built successfully at {os.path.abspath(frontend_dir / 'out')}")
        except (subprocess.SubprocessError, FileNotFoundError):
            # Fall back to npm
            try:
                print("Bun not found, trying with npm...")
                subprocess.run(["npm", "install"], check=True, env=env)
                subprocess.run(["npm", "run", "build"], check=True, env=env)
                print(f"✅ UI built successfully at {os.path.abspath(frontend_dir / 'out')}")
            except (subprocess.SubprocessError, FileNotFoundError):
                print("❌ Error: Could not build the UI. Please install bun or npm.")
        finally:
            os.chdir(current_dir)  # Restore original directory
    else:
        print(f"❌ Error: Frontend directory not found at {frontend_dir}")

def main():
    build_frontend()

if __name__ == "__main__":
    main() 