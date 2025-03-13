import asyncio
import os
import json
from queue import Queue
from pathlib import Path
from fastapi import FastAPI, Request, Body
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.websockets import WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import List, Dict, Any, Optional, Set


class MessageRequest(BaseModel):
    conversation_id: str
    message: str


class MessageResponse(BaseModel):
    response: str


class ConversationMessage(BaseModel):
    id: str
    content: str
    role: str
    created_at: str


class Conversation(BaseModel):
    id: str
    title: str
    messages: List[ConversationMessage]


class ConversationsResponse(BaseModel):
    conversations: List[Conversation]


class UIServer:
    def __init__(self, agent, api_only=False):
        self.agent = agent
        self.agent.ui_server = self
        self.api_only = api_only
        self.app = FastAPI()
        
        # Initialize websocket connections and queues
        self.active_connections: Dict[str, Set[WebSocket]] = {
            'default': set()  # Default set for all connections
        }
        self.update_queues: Dict[str, Queue] = {
            'default': Queue()  # Default queue for broadcasts
        }
        
        # Setup CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # In production, restrict this
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Mount the Next.js static files - using static export
        # Only if not in API-only mode
        if not api_only:
            static_export_dir = Path(__file__).parent / "frontend" / "out"
            if static_export_dir.exists():
                # Mount the static export at root
                self.app.mount("/", StaticFiles(directory=str(static_export_dir), html=True), name="static-export")
        
        # API routes
        self.setup_routes()
    
    async def connect_websocket(self, websocket: WebSocket, conversation_id: Optional[str] = None):
        """Connect a websocket client and associate it with a conversation if provided"""
        # Note: Do not accept the websocket here, it should be accepted before calling this function
        
        # Add to default connections for broadcast messages
        if 'default' not in self.active_connections:
            self.active_connections['default'] = set()
        self.active_connections['default'].add(websocket)
        
        # If a conversation ID is provided, add to that conversation's connections
        if conversation_id:
            if conversation_id not in self.active_connections:
                self.active_connections[conversation_id] = set()
            self.active_connections[conversation_id].add(websocket)
            
            # Create a queue for this conversation if it doesn't exist
            if conversation_id not in self.update_queues:
                self.update_queues[conversation_id] = Queue()
    
    def disconnect_websocket(self, websocket: WebSocket, conversation_id: Optional[str] = None):
        """Disconnect a websocket client"""
        # Remove from default connections
        if 'default' in self.active_connections:
            self.active_connections['default'].discard(websocket)
        
        # If a conversation ID is provided, remove from that conversation's connections
        if conversation_id and conversation_id in self.active_connections:
            self.active_connections[conversation_id].discard(websocket)
    
    def send_update(self, conversation_id: str, update_data: Dict[str, Any]):
        """Send an update to clients connected to a specific conversation"""
        if not update_data:
            print("Warning: Empty update data provided to send_update")
            return
            
        # Ensure the update has a conversation_id field
        message = {**update_data, 'conversation_id': conversation_id}
        
        print(f"Sending update for conversation {conversation_id}: {update_data.get('type', 'unknown_type')}")
        
        # Add to the conversation queue if it exists
        if conversation_id in self.update_queues:
            self.update_queues[conversation_id].put(message)
        else:
            print(f"No queue for conversation {conversation_id}, creating one")
            self.update_queues[conversation_id] = Queue()
            self.update_queues[conversation_id].put(message)
        
        # Also add to default queue for clients not subscribed to a specific conversation
        self.update_queues['default'].put(message)

    def setup_routes(self):
        @self.app.post("/api/message")
        async def handle_message(request: Request):
            data = await request.json()
            conversation_id = data.get("conversation_id")
            message = data.get("message")
            
            if not conversation_id or not message:
                return JSONResponse(
                    status_code=400,
                    content={"error": "conversation_id and message are required"}
                )
            try:
                response = self.agent.on_message(conversation_id, message)
                return JSONResponse(content={"response": response})
            except Exception as e:
                # Log the error
                print(f"Error handling message: {str(e)}")
                return JSONResponse(
                    status_code=500,
                    content={
                        "error": "Failed to process message",
                        "detail": str(e)
                    }
                )
        
        @self.app.get("/api/conversations")
        async def get_conversations():
            # This would need to be implemented in your agent
            if hasattr(self.agent, "get_conversations"):
                conversations = self.agent.get_conversations()
                return JSONResponse(content={"conversations": conversations})
            return JSONResponse(content={"conversations": []})
        
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            
            # Register with default connection pool
            await self.connect_websocket(websocket)
            
            # Store conversation ID for later cleanup
            conversation_id = None
            
            # Create a cancellation event to handle clean shutdown
            cancel_event = asyncio.Event()
            
            # Task for processing queue messages
            async def process_queue():
                try:
                    while not cancel_event.is_set():
                        # First check conversation-specific queue
                        if conversation_id and conversation_id in self.update_queues:
                            queue = self.update_queues[conversation_id]
                            if not queue.empty():
                                message = queue.get_nowait()
                                await websocket.send_json(message)
                                continue
                        
                        # Then check default queue
                        queue = self.update_queues['default']
                        if not queue.empty():
                            message = queue.get_nowait()
                            # Only send the message if it's either a broadcast or for this conversation
                            if not conversation_id or message.get('conversation_id') == conversation_id:
                                await websocket.send_json(message)
                                continue
                        
                        # No messages to send, wait a bit
                        try:
                            # Use wait_for with a short timeout so we can check the cancel flag frequently
                            await asyncio.wait_for(asyncio.shield(cancel_event.wait()), timeout=0.1)
                        except asyncio.TimeoutError:
                            # This is expected, just continue the loop
                            pass
                        
                except WebSocketDisconnect:
                    print(f"WebSocket disconnected for conversation {conversation_id}")
                except Exception as e:
                    print(f"Error in queue processing task: {str(e)}")
                finally:
                    self.disconnect_websocket(websocket, conversation_id)
            
            # Initialize queue_task variable so it's always accessible
            queue_task = None
            
            try:
                # First, read a message from the client for subscription info
                try:
                    # Set a timeout for receiving the initial message
                    subscription_msg = await asyncio.wait_for(websocket.receive_text(), timeout=5.0)
                    try:
                        data = json.loads(subscription_msg)
                        conversation_id = data.get('conversation_id')
                        
                        # If conversation_id is provided, register for that conversation
                        if conversation_id:
                            await self.connect_websocket(websocket, conversation_id)
                            
                            # Send ack to client
                            await websocket.send_json({
                                'type': 'subscription_ack',
                                'conversation_id': conversation_id
                            })
                    except json.JSONDecodeError:
                        # Invalid subscription message, just use default queue
                        pass
                except asyncio.TimeoutError:
                    print("No subscription message received within timeout")
                
                # Start queue processing task
                queue_task = asyncio.create_task(process_queue())
                
                # Wait for disconnection by continuously receiving
                while True:
                    # This will raise WebSocketDisconnect when the client disconnects
                    await websocket.receive_text()
                
            except WebSocketDisconnect:
                print(f"WebSocket disconnected for conversation {conversation_id}")
            except Exception as e:
                print(f"WebSocket error: {str(e)}")
            finally:
                # Signal the queue task to stop
                cancel_event.set()
                
                # Wait for queue task to finish (with timeout) if it exists
                if queue_task is not None:
                    try:
                        await asyncio.wait_for(queue_task, timeout=1.0)
                    except (asyncio.TimeoutError, asyncio.CancelledError):
                        # Force cancel if it doesn't finish in time
                        queue_task.cancel()
                
                # Clean up connections
                self.disconnect_websocket(websocket, conversation_id)

        # Only add the catch-all route if not in API-only mode
        if not self.api_only:
            @self.app.get("/{full_path:path}")
            async def serve_frontend(full_path: str, request: Request):
                # Only reached if the static files mount doesn't handle the request
                static_export_dir = Path(__file__).parent / "frontend" / "out"
                if not static_export_dir.exists():
                    return HTMLResponse(content="UI not built. Run 'cd src/aral/ui/frontend && bun run build' to build the UI.")
                
                # Check if this is a Next.js dynamic route
                if full_path.startswith("conversation/"):
                    # Serve the index.html for the conversation route
                    index_path = static_export_dir / "index.html"
                    if index_path.exists():
                        with open(index_path, "r") as f:
                            content = f.read()
                        return HTMLResponse(content=content)
                
                # If we get here, the path wasn't found in the static export
                return HTMLResponse(content="Page not found", status_code=404)
    
    def run(self, host="0.0.0.0", port=3000):
        import uvicorn
        import signal
        import sys
        
        # Create server
        config = uvicorn.Config(self.app, host=host, port=port)
        server = uvicorn.Server(config)
        
        # Add signal handlers for graceful shutdown
        def handle_exit(signum, frame):
            print("\nShutting down server gracefully...")
            # Stop the server
            server.should_exit = True
            # Clear all background tasks
            for conn_set in self.active_connections.values():
                conn_set.clear()
            # Clear all queues
            for queue in self.update_queues.values():
                while not queue.empty():
                    try:
                        queue.get_nowait()
                    except:
                        pass
        
        # Register signals
        signal.signal(signal.SIGINT, handle_exit)
        signal.signal(signal.SIGTERM, handle_exit)
        
        # Run the server
        try:
            server.run()
        except KeyboardInterrupt:
            print("Received keyboard interrupt - shutting down")
        finally:
            print("Server stopped") 