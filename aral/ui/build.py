import os
import subprocess
from pathlib import Path

def build_frontend():
    frontend_dir = Path(__file__).parent / "frontend"
    if frontend_dir.exists():
        os.chdir(frontend_dir)
        try:
            # Try with bun first
            subprocess.run(["bun", "install"], check=True)
            subprocess.run(["bun", "run", "build"], check=True)
        except (subprocess.SubprocessError, FileNotFoundError):
            # Fall back to npm
            try:
                subprocess.run(["npm", "install"], check=True)
                subprocess.run(["npm", "run", "build"], check=True)
            except (subprocess.SubprocessError, FileNotFoundError):
                print("Warning: Could not build the UI. Please install bun or npm.")

def main():
    build_frontend()

if __name__ == "__main__":
    main() 