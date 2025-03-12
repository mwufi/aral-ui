from .ui.server import UIServer

class BaseAgent:
    # ... other agent code ...
    
    def run(self, host="0.0.0.0", port=3000):
        """Run the agent with a web UI"""
        server = UIServer(self)
        server.run(host=host, port=port) 