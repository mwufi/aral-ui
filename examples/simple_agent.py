from aral.agent import BaseAgent

class SimpleAgent(BaseAgent):
    def init(self):
        # Any additional initialization can go here
        pass
    
    def on_message(self, convo_id, message):
        # Add the user message to the store
        self.message_store.add_message(convo_id, message, role="user")
        
        # Generate a response - in a real agent, this would use an LLM
        response = f"You said: {message}"
        
        # Add the assistant response to the store and return it
        self.message_store.add_message(convo_id, response, role="assistant")
        return response

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