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
import time
import random
import json

class SimpleAgent(BaseAgent):
    def __init__(self):
        # Initialize with a persistent store in the convos directory
        # Simple and clean!
        super().__init__(save_dir='./convos', verbose=True)
    
    def _handle_message(self, convo_id, message):
        """Process the message and generate a response using Anthropic."""
        # Check if the message is asking for weather
        if "weather" in message.lower():
            return self.handle_weather_request(convo_id, message)
            
        # Get conversation history
        anthropic_messages = format_anthropic_messages(self.message_store.get_conversation(convo_id).messages)
        
        # Send tool usage update
        tool_id = f"claude-{time.time()}"
        self.send_update(convo_id, {
            "id": tool_id,
            "type": "tool_start",
            "tool": "anthropic",
            "args": {
                "model": "claude-3-7-sonnet",
                "messages": len(anthropic_messages)
            }
        })
        
        start_time = time.time()
        
        # Send to Anthropic
        response = create_message(anthropic_messages)
        
        # Send completion update
        elapsed_time = time.time() - start_time
        self.send_update(convo_id, {
            "id": tool_id,
            "type": "tool_result",
            "tool": "anthropic",
            "result": {
                "time_taken": f"{elapsed_time:.2f}s",
                "tokens": response.usage.output_tokens + response.usage.input_tokens
            }
        })
        
        # Check if there's a tool call
        if response.tool_calls and len(response.tool_calls) > 0:
            # Handle tool calls from Claude
            for tool_call in response.tool_calls:
                if tool_call.name == "get_weather":
                    location = tool_call.input.get("location", "Unknown location")
                    weather_data = self.get_weather(convo_id, location)
                    # You would normally send this back to Claude, but for this example
                    # we'll just include it in the response
                    weather_text = f"\n\nI checked the weather for you: {weather_data['temperature']}°F and {weather_data['conditions']} in {location}."
                    return response.content[0].text + weather_text
        
        # Extract just the text content
        return response.content[0].text
    
    def handle_weather_request(self, convo_id, message):
        """Handle direct weather requests from the user."""
        # Extract location from message or default to New York
        import re
        location_match = re.search(r"weather\s+(?:in|at|for)?\s+([a-zA-Z\s,]+)", message, re.IGNORECASE)
        location = location_match.group(1).strip() if location_match else "New York"
        
        # Get weather data
        weather_data = self.get_weather(convo_id, location)
        
        # Return formatted response
        return f"The weather in {location} is currently {weather_data['temperature']}°F and {weather_data['conditions']} with {weather_data['humidity']}% humidity and wind at {weather_data['wind']}."
    
    def get_weather(self, convo_id, location):
        """Simulated weather tool that sends UI updates."""
        # Send weather tool start update
        tool_id = f"weather-{time.time()}"
        self.send_update(convo_id, {
            "id": tool_id,
            "type": "tool_start",
            "tool": "weather",
            "args": {"location": location}
        })
        
        # Simulate API call delay
        time.sleep(1.5)
        
        # Generate mock weather data
        weather_data = {
            "location": location,
            "temperature": random.randint(65, 85),
            "conditions": random.choice(["Sunny", "Cloudy", "Partly Cloudy", "Rainy"]),
            "humidity": random.randint(30, 90),
            "wind": f"{random.randint(0, 20)} mph"
        }
        
        # Send weather tool result update
        self.send_update(convo_id, {
            "id": tool_id,
            "type": "tool_result",
            "tool": "weather",
            "result": weather_data
        })
        
        return weather_data

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run the Claude Agent")
    parser.add_argument("--dev", action="store_true", help="Run in development mode with hot reloading")
    parser.add_argument("--port", type=int, default=3000, help="Port for the main server")
    parser.add_argument("--api-port", type=int, default=4000, help="Port for the API server (only used in dev mode)")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()
    
    # This fixes the issue with running from a different directory
    import os
    # Ensure we're in the right directory for loading files
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    agent = SimpleAgent()
    
    if args.dev:
        # Run in development mode with separate API and UI servers
        print(f"Running in development mode with UI on port {args.port} and API on port {args.api_port}")
        agent.run(port=args.port, api_port=args.api_port, dev_mode=True)
    else:
        # Run in production mode with a single server
        print(f"Running in production mode on port {args.port}")
        agent.run(port=args.port)
