from aral.agent import BaseAgent
from openai import OpenAI

import dotenv
dotenv.load_dotenv()

client = OpenAI()

class SimpleAgent(BaseAgent):
    def init(self):
        # Any additional initialization can go here
        pass
    
    def on_message(self, convo_id, message):
        # Add the user message to the store
        self.message_store.add_message(convo_id, message, role="user")
        
        # Generate a response using OpenAI if available, otherwise use a simple echo
        openai_messages = [
            {'role': m.role, 'content': m.content}
            for m in self.message_store.get_conversation(convo_id).messages
        ]
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=openai_messages
        )
        # Extract the actual message content from the ChatCompletion response
        response_text = response.choices[0].message.content

        # Add the assistant response to the store and return it
        self.message_store.add_message(convo_id, response_text, role="assistant")

        print(self.message_store.get_conversation(convo_id))
        # Return just the response text instead of the entire ChatCompletion object
        return response_text

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