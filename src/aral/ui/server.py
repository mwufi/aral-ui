import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

class UIServer:
    def __init__(self, agent, api_only=False):
        self.agent = agent
        self.api_only = api_only
        self.app = FastAPI()
        
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
    
    def setup_routes(self):
        @self.app.post("/api/message")
        async def handle_message(request: Request):
            data = await request.json()
            conversation_id = data.get("conversation_id")
            message = data.get("message")
            
            response = self.agent.on_message(conversation_id, message)
            return JSONResponse(content={"response": response})
        
        @self.app.get("/api/conversations")
        async def get_conversations():
            # This would need to be implemented in your agent
            if hasattr(self.agent, "get_conversations"):
                conversations = self.agent.get_conversations()
                return JSONResponse(content={"conversations": conversations})
            return JSONResponse(content={"conversations": []})
        
        # Only add the catch-all route if not in API-only mode
        if not self.api_only:
            @self.app.get("/{full_path:path}")
            async def serve_frontend(full_path: str):
                # Only reached if the static files mount doesn't handle the request
                static_export_dir = Path(__file__).parent / "frontend" / "out"
                if not static_export_dir.exists():
                    return HTMLResponse(content="UI not built. Run 'cd src/aral/ui/frontend && bun run build' to build the UI.")
                
                # If we get here, the path wasn't found in the static export
                return HTMLResponse(content="Page not found", status_code=404)
    
    def run(self, host="0.0.0.0", port=3000):
        import uvicorn
        uvicorn.run(self.app, host=host, port=port) 