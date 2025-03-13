from aral.agent import BaseAgent

class SimpleAgent(BaseAgent):
    def __init__(self):
        # Initialize any state your agent needs
        self.conversations = {}
    
    def on_message(self, convo_id, message):
        # Simple echo response for testing
        if convo_id not in self.conversations:
            self.conversations[convo_id] = []
        
        self.conversations[convo_id].append({"role": "user", "content": message})
        response = f"Echo: {message}"
        self.conversations[convo_id].append({"role": "assistant", "content": response})
        
        return response
    
    def get_conversations(self):
        # Return all conversations for the UI
        return [{"id": convo_id, "messages": messages} 
                for convo_id, messages in self.conversations.items()]

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run the SimpleAgent")
    parser.add_argument("--dev", action="store_true", help="Run in development mode with hot reloading")
    parser.add_argument("--port", type=int, default=3000, help="Port for the main server")
    parser.add_argument("--api-port", type=int, default=4000, help="Port for the API server (only used in dev mode)")
    args = parser.parse_args()
    
    agent = SimpleAgent()
    
    if args.dev:
        # Run in development mode with separate API and UI servers
        print(f"Running in development mode with UI on port {args.port} and API on port {args.api_port}")
        agent.run(port=args.port, api_port=args.api_port, dev_mode=True)
    else:
        # Run in production mode with a single server
        print(f"Running in production mode on port {args.port}")
        agent.run(port=args.port) 