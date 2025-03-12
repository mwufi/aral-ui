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
    agent = SimpleAgent()
    agent.run(port=3000)  # This will start the FastAPI server with the Next.js UI 