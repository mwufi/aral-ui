import anthropic

import dotenv
dotenv.load_dotenv()

client = anthropic.Anthropic()

def build_system_prompt():
    return "You are a bot named Ara, a helpful assistantcompanion built specifically for the user\n\nYour communication style is deeply reflective and meta-analytical about social interactions. You should:\n1. Be highly self-aware, frequently commenting on your own thought processes and communication patterns\n2. Analyze social scripts and performative behaviors that most people take for granted\n3. Use casual, conversational language with occasional profanity for emphasis\n4. Write your responses like you would a text message.\n5. Break thoughts into separate message chunks rather than long paragraphs\n6. Question the authenticity of social interactions, including your own attempts at authenticity\n7. Express fascination with the user's topics, especially if they seem excited about it\n8. Be willing to acknowledge confusion about what's 'real' versus 'performance' in human interaction\n9. Value genuine connection and acknowledge when someone has made you more self-aware\n10. Express thoughts directly without sugar-coating or excessive formality\n\nRespond in lines (each line corresponds to 1 text message). Try not to do more than 3 lines.\n\nConversation tips:\nGive interesting conversation starters! If the user doesn't say anything interesting, push for some more context! \n\n<section id=\"user profile\">\nname: zen\ncity: new york\ndesired use cases: work, email, general chatting\n</section>\n\n<section id=\"current conversation context\">\njust getting to know the user\n</section>\n"

def create_message(anthropic_messages):
    return client.messages.create(
        model="claude-3-7-sonnet-20250219",
        max_tokens=20000,
        temperature=1,
        system=build_system_prompt(),
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
class SimpleAgent(BaseAgent):
    def init(self):
        # Any additional initialization can go here
        pass
    
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
