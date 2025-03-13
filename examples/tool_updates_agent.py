from aral.agent import BaseAgent
from openai import OpenAI
import time
import random
import json
import dotenv
import requests
from typing import Dict, Any

dotenv.load_dotenv()

client = OpenAI()

class ToolUpdatesAgent(BaseAgent):
    def init(self):
        """Initialize any tools or services needed by the agent."""
        self.tools = {
            "weather": self.get_weather,
            "search": self.search_web,
            "calculator": self.calculate,
            "wait": self.wait_tool  # A simple tool that just waits (for demo purposes)
        }
    
    def _handle_message(self, convo_id, message):
        """Handles the incoming message and demonstrates tool updates."""
        # Start by sending a thinking update
        self.send_update(convo_id, {
            "type": "thinking",
            "message": "Thinking about how to respond..."
        })
        
        # Parse the message to see if it's requesting a specific tool
        message_lower = message.lower()
        
        response_parts = []
        
        # Check if message asks for weather
        if "weather" in message_lower:
            tool_result = self.use_tool(convo_id, "weather", {"location": "San Francisco"})
            response_parts.append(f"The current weather in San Francisco is {tool_result['temperature']}°F and {tool_result['conditions']}.")
        
        # Check if message asks for search
        if "search" in message_lower:
            query = "latest AI research"
            tool_result = self.use_tool(convo_id, "search", {"query": query})
            response_parts.append(f"Here are some search results for '{query}':\n" + "\n".join([f"- {result}" for result in tool_result["results"]]))
        
        # Check if message asks for calculation
        if "calculate" in message_lower or "math" in message_lower:
            expression = "256 * 14 + 42"
            tool_result = self.use_tool(convo_id, "calculator", {"expression": expression})
            response_parts.append(f"The result of {expression} is {tool_result['result']}.")
        
        # Demonstrate the waiting tool regardless of input
        # self.use_tool(convo_id, "wait", {"seconds": 5})
        
        # If no specific tools were triggered, use OpenAI
        if not response_parts:
            # Send update that we're calling OpenAI
            self.send_update(convo_id, {
                "type": "tool_start",
                "tool": "openai",
                "args": {"model": "gpt-4o", "prompt": message[:50] + "..." if len(message) > 50 else message}
            })
            
            # Get previous conversation messages
            openai_messages = [
                {'role': m.role, 'content': m.content}
                for m in self.message_store.get_conversation(convo_id).messages
            ]
            
            # Call OpenAI
            try:
                start_time = time.time()
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=openai_messages
                )
                elapsed_time = time.time() - start_time
                
                # Extract the response text
                response_text = response.choices[0].message.content
                
                # Send the tool result update
                self.send_update(convo_id, {
                    "type": "tool_result",
                    "tool": "openai",
                    "result": {
                        "time_taken": f"{elapsed_time:.2f}s",
                        "tokens": response.usage.total_tokens
                    }
                })
                
                return response_text
            except Exception as e:
                self.send_update(convo_id, {
                    "type": "tool_result",
                    "tool": "openai",
                    "result": {"error": str(e)}
                })
                return f"Sorry, I encountered an error: {str(e)}"
        
        # Join all the response parts together
        return "\n\n".join(response_parts)
    
    def use_tool(self, convo_id, tool_name, args):
        """Run a tool and send WebSocket updates about its progress."""
        if tool_name not in self.tools:
            raise ValueError(f"Tool {tool_name} not found")
        
        # Send the starting update
        tool_id = f"{tool_name}-{time.time()}"
        self.send_update(convo_id, {
            "id": tool_id,
            "type": "tool_start",
            "tool": tool_name,
            "args": args
        })
        
        # Actually run the tool
        try:
            # Add convo_id to args if the tool accepts it
            if tool_name == "wait":
                args['convo_id'] = convo_id
                
            result = self.tools[tool_name](**args)
            
            # Send the result update
            self.send_update(convo_id, {
                "id": tool_id,
                "type": "tool_result",
                "tool": tool_name,
                "result": result
            })
            
            return result
        except Exception as e:
            # Send error update
            self.send_update(convo_id, {
                "id": tool_id,
                "type": "tool_result",
                "tool": tool_name,
                "error": str(e)
            })
            raise
    
    def get_weather(self, location):
        """Simulated weather tool."""
        # Simulate API call delay
        time.sleep(1.5)
        
        # Return mock weather data
        return {
            "location": location,
            "temperature": random.randint(65, 85),
            "conditions": random.choice(["Sunny", "Cloudy", "Partly Cloudy", "Rainy"]),
            "humidity": random.randint(30, 90),
            "wind": f"{random.randint(0, 20)} mph"
        }
    
    def search_web(self, query):
        """Simulated web search tool."""
        # Simulate API call delay
        time.sleep(2)
        
        # Generate a fixed set of fake results based on the query
        return {
            "query": query,
            "results": [
                f"Result 1 for {query}: Lorem ipsum dolor sit amet",
                f"Result 2 for {query}: consectetur adipiscing elit",
                f"Result 3 for {query}: sed do eiusmod tempor incididunt",
                f"Result 4 for {query}: ut labore et dolore magna aliqua"
            ]
        }
    
    def calculate(self, expression):
        """Simple calculator tool."""
        # Simulate a slight delay
        time.sleep(0.5)
        
        try:
            # WARNING: eval is used here for demonstration purposes only
            # In a real application, use a safer evaluation method
            result = eval(expression)
            return {
                "expression": expression,
                "result": result
            }
        except Exception as e:
            return {
                "expression": expression,
                "error": str(e)
            }
    
    def wait_tool(self, seconds, convo_id=None):
        """A tool that simply waits for the specified number of seconds."""
        # Cap at 5 seconds max for safety
        seconds = min(seconds, 5)
        
        # Create a unique ID for this waiting operation
        wait_id = f"wait-{time.time()}"
        
        # Sleep in small increments to show progress updates
        increment = 0.5
        for i in range(int(seconds / increment)):
            progress = (i + 1) * increment / seconds
            if convo_id:
                self.send_update(convo_id, {
                    "id": wait_id,
                    "type": "progress_update",
                    "progress": progress,
                    "message": f"Waiting... {int(progress * 100)}% complete"
                })
            time.sleep(increment)
        
        return {
            "seconds_waited": seconds,
            "message": "Finished waiting"
        }


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run the ToolUpdatesAgent")
    parser.add_argument("--dev", action="store_true", help="Run in development mode with hot reloading")
    parser.add_argument("--port", type=int, default=3000, help="Port for the main server")
    parser.add_argument("--api-port", type=int, default=4000, help="Port for the API server (only used in dev mode)")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()
    
    agent = ToolUpdatesAgent(verbose=args.verbose)
    
    if args.dev:
        # Run in development mode with separate API and UI servers
        print(f"Running in development mode with UI on port {args.port} and API on port {args.api_port}")
        agent.run(port=args.port, api_port=args.api_port, dev_mode=True)
    else:
        # Run in production mode with a single server
        print(f"Running in production mode on port {args.port}")
        agent.run(port=args.port)