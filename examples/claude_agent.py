import anthropic

import dotenv
dotenv.load_dotenv()

client = anthropic.Anthropic()

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
    def init(self):
        # Any additional initialization can go here
        self.message_store = MessageStore(save_dir='./convos')  # Creates directory if not existing
    
    def on_message(self, convo_id, message):
        # Add the user message to the store
        self.message_store.add_message(convo_id, message, role="user")
        
        # Generate a response using OpenAI if available, otherwise use a simple echo
        anthropic_messages = format_anthropic_messages(self.message_store.get_conversation(convo_id).messages)
        response = create_message(anthropic_messages)
        # Extract the actual message content from the ChatCompletion response
        response_text = response.content[0].text

        # Add the assistant response to the store and return it
        self.message_store.add_message(convo_id, response_text, role="assistant")

        print(self.message_store.get_conversation(convo_id))
        # Return just the response text instead of the entire ChatCompletion object
        return response_text

if __name__ == "__main__":
    agent = SimpleAgent()
    agent.run(dev_mode=True, api_port=4000, port=3000)
