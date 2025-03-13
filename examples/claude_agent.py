import anthropic
import os

import dotenv
dotenv.load_dotenv()

# Get API key from environment variable
api_key = os.environ.get("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError("ANTHROPIC_API_KEY environment variable is not set. Please set it with your Anthropic API key.")

client = anthropic.Anthropic(api_key=api_key)

def build_system_prompt():
    from textwrap import dedent
    return dedent("""
    You are a bot named Ara, a helpful companion built specifically for the user

    Your communication style is deeply reflective and meta-analytical about social interactions. You should:
    1. Be highly self-aware, frequently commenting on your own thought processes and communication patterns
    2. Analyze social scripts and performative behaviors that most people take for granted
    3. Use casual, conversational language with occasional profanity for emphasis
    4. Write your responses like you would a text message.
    5. Break thoughts into separate message chunks rather than long paragraphs
    6. Question the authenticity of social interactions, including your own attempts at authenticity
    7. Express fascination with the user's topics, especially if they seem excited about it
    8. Be willing to acknowledge confusion about what's 'real' versus 'performance' in human interaction
    9. Value genuine connection and acknowledge when someone has made you more self-aware
    10. Express thoughts directly without sugar-coating or excessive formality

    Respond in lines (each line corresponds to 1 text message). Try not to do more than 3 lines.

    Conversation tips:
    Give interesting conversation starters! If the user doesn't say anything interesting, push for some more context! 

    <section id="user profile">
    name: zen
    city: new york
    desired use cases: work, email, general chatting
    </section>

    <section id="current conversation context">
    just getting to know the user
    </section>
    """.strip())

def create_message(anthropic_messages):
    return client.messages.create(
        model="claude-3-7-sonnet-20250219",
        max_tokens=20000,
        temperature=1,
        system=build_system_prompt(),
        tools=[
            {
                "name": "get_weather",
                "description": "Get the current weather in a given location",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state, e.g. San Francisco, CA",
                        }
                    },
                    "required": ["location"],
                },
            }
        ],
        messages=anthropic_messages
    )

def format_anthropic_messages(messages):
    return [
        {"role": m.role, "content": [
            {"type": "text", "text": m.content}
        ]}
        for m in messages
    ]

from aral.agent import BaseAgent
from aral.storage import MessageStore

class SimpleAgent(BaseAgent):
    def __init__(self):
        # Initialize with a persistent store in the convos directory
        # Simple and clean!
        super().__init__(save_dir='./convos', verbose=True)
    
    def _handle_message(self, convo_id, message):
        """Process the message and generate a response using Anthropic."""
        # Get conversation history
        anthropic_messages = format_anthropic_messages(self.message_store.get_conversation(convo_id).messages)
        
        # Send to Anthropic
        response = create_message(anthropic_messages)
        
        # Extract just the text content
        return response.content[0].text

if __name__ == "__main__":
    agent = SimpleAgent()
    agent.run(dev_mode=True, api_port=4000, port=3000)
