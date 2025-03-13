import os
from pathlib import Path
from .ui.server import UIServer
from .ui.build import build_frontend
from .storage import MessageStore
import subprocess
import threading
import uuid
from typing import Dict, Any, Optional

class BaseAgent:
    def __init__(self, message_store=None, save_dir=None, verbose=False):
        """Initialize the agent with a MessageStore.
        
        Args:
            message_store: Optional custom MessageStore instance
            save_dir: Directory where conversations should be saved
            verbose: Whether to print diagnostic information
        """
        self.verbose = verbose
        self.initial_cwd = os.getcwd()  # Store the initial working directory

        # Will be set by the UI server
        self.ui_server = None
        
        # Initialize message store
        if message_store:
            self.message_store = message_store
        elif save_dir:
            self.message_store = MessageStore(save_dir=save_dir)
        else:
            self.message_store = MessageStore()
            
        if self.verbose:
            print(f"Initializing agent with MessageStore {'with persistence' if save_dir else 'in memory only'}")
            print(f"Initial working directory: {self.initial_cwd}")
            
            if hasattr(self.message_store, 'backend') and hasattr(self.message_store.backend, 'list_conversation_ids'):
                conversation_ids = self.message_store.backend.list_conversation_ids()
                print(f"Found existing conversations: {conversation_ids}")
                
        # Call the init method for any additional initialization
        self.init()
    
    def init(self):
        """Override this method to initialize your agent."""
        pass
    
    def send_update(self, conversation_id: str, update_data: Dict[str, Any]):
        """
        Send an update to the frontend via WebSocket.
        Used to notify the UI of tool usage, processing steps, or other updates.
        
        Args:
            conversation_id: The conversation ID this update relates to
            update_data: A dictionary with update information. Should have a 'type' field
                         to indicate the kind of update (e.g., 'tool_start', 'tool_result').
        
        Example:
            self.send_update(convo_id, {
                'type': 'tool_start',
                'tool': 'weather_api',
                'args': {'location': 'San Francisco'}
            })
            
            # Later, after tool completes:
            self.send_update(convo_id, {
                'type': 'tool_result',
                'tool': 'weather_api',
                'result': {'temperature': 72, 'conditions': 'Sunny'}
            })
        """
        if self.ui_server:
            # Make sure update_data has an ID field for tracking
            if 'id' not in update_data:
                update_data['id'] = str(uuid.uuid4())
                
            # Send the update to the UI server
            self.ui_server.send_update(conversation_id, update_data)
        elif self.verbose:
            print(f"No UI server available to send update: {update_data}")
    
    def _handle_message(self, convo_id, message):
        """
        Internal method that handles the actual message processing.
        Override this in your subclass instead of on_message.
        
        Args:
            convo_id: The conversation ID
            message: The message content
            
        Returns:
            The response message content
        """
        # Default implementation just echoes the message
        return f"Echo: {message}"
    
    def on_message(self, convo_id, message):
        """
        Handle an incoming message. This method:
        1. Logs the incoming message if verbose mode is on
        2. Adds the user message to the store
        3. Calls the _handle_message method for custom processing
        4. Adds the response to the store
        5. Returns the response
        
        Do NOT override this method in your subclass.
        Override _handle_message instead.
        
        Args:
            convo_id: The conversation ID
            message: The message content
            
        Returns:
            The response message content
        """
        if self.verbose:
            print(f"\n==== Received message in conversation {convo_id} ====")
            print(f"Message: {message}")
            print(f"Current working directory: {os.getcwd()}")
        
        # Add the user message to the store
        self.message_store.add_message(convo_id, message, role="user")
        
        # Call the handler method for custom processing
        response = self._handle_message(convo_id, message)
        
        # Add the assistant response to the store
        self.message_store.add_message(convo_id, response, role="assistant")
        
        if self.verbose:
            print(f"Response: {response[:50]}{'...' if len(response) > 50 else ''}")
            if hasattr(self.message_store, 'backend') and hasattr(self.message_store.backend, 'list_conversation_ids'):
                conversation_ids = self.message_store.backend.list_conversation_ids()
                print(f"Active conversations: {conversation_ids}")
        
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