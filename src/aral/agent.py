import os
from pathlib import Path
from .ui.server import UIServer
from .ui.build import build_frontend

class BaseAgent:
    # ... other agent code ...
    
    def run(self, host="0.0.0.0", port=3000, auto_build=True):
        """
        Run the agent with a web UI
        
        Args:
            host: Host to bind the server to
            port: Port to bind the server to
            auto_build: Whether to automatically build the UI if not already built
        """
        # Check if UI is built
        ui_dir = Path(__file__).parent / "ui" / "frontend" / "out"
        if auto_build and not ui_dir.exists():
            print("🔨 First run detected! Building UI...")
            print("⏳ This may take a minute, but only happens once...")
            build_frontend()
            print("🚀 UI built successfully! Starting server...")
        
        # Start the server
        server = UIServer(self)
        print(f"🌐 Server running at http://{host if host != '0.0.0.0' else 'localhost'}:{port}")
        server.run(host=host, port=port) 