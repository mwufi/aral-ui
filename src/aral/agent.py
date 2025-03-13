import os
from pathlib import Path
from .ui.server import UIServer
from .ui.build import build_frontend
from .storage import MessageStore
import subprocess
import threading

class BaseAgent:
    def __init__(self):
        """Initialize the agent with a MessageStore."""
        self.message_store = MessageStore()
    
    def on_message(self, convo_id, message):
        """
        Handle an incoming message.
        
        Args:
            convo_id: The conversation ID
            message: The message content
            
        Returns:
            The response message content
        """
        # Add the user message to the store
        self.message_store.add_message(convo_id, message, role="user")
        
        # Default implementation just echoes the message
        response = f"Echo: {message}"
        
        # Add the assistant response to the store
        self.message_store.add_message(convo_id, response, role="assistant")
        
        return response
    
    def get_conversations(self):
        """
        Get all conversations.
        
        Returns:
            A list of conversations in a format suitable for the UI
        """
        conversations = self.message_store.get_all_conversations()
        return [
            {
                "id": conv.id,
                "title": conv.title,
                "messages": [
                    {
                        "id": msg.id,
                        "content": msg.content,
                        "role": msg.role,
                        "created_at": msg.created_at.isoformat(),
                    }
                    for msg in conv.messages
                ]
            }
            for conv in conversations
        ]
    
    def run(self, host="0.0.0.0", port=3000, api_port=None, dev_mode=False, auto_build=True):
        """
        Run the agent with a web UI
        
        Args:
            host: Host to bind the server to
            port: Port to bind the server to
            api_port: If provided, run the API on this port and the UI on the main port
            dev_mode: If True, run the Next.js frontend in dev mode with hot reloading
            auto_build: Whether to automatically build the UI if not already built
        """
        frontend_dir = Path(__file__).parent / "ui" / "frontend"
        ui_dir = frontend_dir / "out"
        
        # If dev_mode is True, we need to run the Next.js dev server
        if dev_mode:
            if api_port is None:
                raise ValueError("api_port must be provided when dev_mode is True")
            
            # Start the API server
            server = UIServer(self, api_only=True)
            api_url = f"http://{host if host != '0.0.0.0' else 'localhost'}:{api_port}"
            print(f"🚀 API server running at {api_url}")
            
            # Start the Next.js dev server in a separate thread
            def run_frontend_dev():
                current_dir = os.getcwd()
                try:
                    os.chdir(frontend_dir)
                    # Set environment variable for the API URL
                    env = os.environ.copy()
                    env["NEXT_PUBLIC_API_URL"] = api_url
                    # Run the Next.js dev server
                    subprocess.run(["bun", "run", "dev", "--port", str(port)], env=env)
                except Exception as e:
                    print(f"Error running frontend dev server: {e}")
                finally:
                    os.chdir(current_dir)
            
            # Start the frontend in a separate thread
            frontend_thread = threading.Thread(target=run_frontend_dev)
            frontend_thread.daemon = True
            frontend_thread.start()
            
            # Run the API server (this will block)
            server.run(host=host, port=api_port)
        else:
            # Regular mode - check if UI is built
            if auto_build and not ui_dir.exists():
                print("🔨 First run detected! Building UI...")
                print("⏳ This may take a minute, but only happens once...")
                # In regular mode, we don't need to set the API URL since it will use relative paths
                build_frontend()
                print("🚀 UI built successfully! Starting server...")
            
            # Start the server
            server = UIServer(self)
            print(f"🌐 Server running at http://{host if host != '0.0.0.0' else 'localhost'}:{port}")
            server.run(host=host, port=port) 