import os
import subprocess
from pathlib import Path

def build_frontend():
    frontend_dir = Path(__file__).parent / "frontend"
    if frontend_dir.exists():
        current_dir = os.getcwd()  # Save current directory
        os.chdir(frontend_dir)
        try:
            # Try with bun first
            print("Building UI with Bun...")
            subprocess.run(["bun", "install"], check=True)
            subprocess.run(["bun", "run", "build"], check=True)
            print(f"✅ UI built successfully at {os.path.abspath(frontend_dir / 'out')}")
        except (subprocess.SubprocessError, FileNotFoundError):
            # Fall back to npm
            try:
                print("Bun not found, trying with npm...")
                subprocess.run(["npm", "install"], check=True)
                subprocess.run(["npm", "run", "build"], check=True)
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