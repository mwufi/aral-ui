import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

class UIServer:
    def __init__(self, agent):
        self.agent = agent
        self.app = FastAPI()
        
        # Setup CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # In production, restrict this
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Mount the Next.js static files
        frontend_dir = Path(__file__).parent / "frontend" / ".next"
        if frontend_dir.exists():
            self.app.mount("/_next", StaticFiles(directory=str(frontend_dir / "static")), name="next-static")
            self.app.mount("/public", StaticFiles(directory=str(Path(__file__).parent / "frontend" / "public")), name="public")
        
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
        
        @self.app.get("/{full_path:path}")
        async def serve_frontend(full_path: str):
            # Serve the Next.js index.html for all non-API routes
            index_path = Path(__file__).parent / "frontend" / ".next" / "server" / "pages" / "index.html"
            if index_path.exists():
                with open(index_path) as f:
                    return HTMLResponse(content=f.read())
            return HTMLResponse(content="UI not built. Run 'cd aral/ui/frontend && bun run build' to build the UI.")
    
    def run(self, host="0.0.0.0", port=3000):
        import uvicorn
        uvicorn.run(self.app, host=host, port=port) 