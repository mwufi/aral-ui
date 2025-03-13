#!/usr/bin/env python3
"""
Example script demonstrating the use of the MessageStore persistence layer.
"""

import os
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.aral.storage import JsonFileStorage, PersistentMessageStore


def main():
    """Run the example."""
    # Create a data directory
    data_dir = Path("./data")
    data_dir.mkdir(exist_ok=True)
    
    # Create a storage provider
    storage = JsonFileStorage(storage_dir=str(data_dir))
    
    # Create a persistent message store
    store = PersistentMessageStore(storage_provider=storage)
    
    # Initialize the store (loads existing data if available)
    store.initialize()
    
    # Print existing conversations
    print("Existing conversations:")
    for conv_id, conv in store.conversations.items():
        print(f"  - {conv.title} ({conv_id})")
    
    # Create a new conversation if none exist
    if not store.conversations:
        print("\nCreating a new conversation...")
        conversation = store.create_conversation(title="Example Conversation")
        print(f"Created conversation: {conversation.title} ({conversation.id})")
        
        # Add some messages
        print("Adding messages...")
        store.add_message(conversation.id, "Hello, this is a user message", role="user")
        store.add_message(conversation.id, "Hi there! I'm an assistant.", role="assistant")
        
        # Add an action
        print("Adding an action...")
        store.add_action(conversation.id, "button_click", {"button_id": "submit"})
    else:
        # Get the first conversation
        conv_id = next(iter(store.conversations.keys()))
        conversation = store.get_conversation(conv_id)
        
        print(f"\nUsing existing conversation: {conversation.title} ({conversation.id})")
        
        # Add a new message
        print("Adding a new message...")
        store.add_message(conversation.id, f"Hello again! Message #{len(conversation.messages) + 1}", role="user")
    
    # Print the conversation details
    print("\nConversation details:")
    print(f"ID: {conversation.id}")
    print(f"Title: {conversation.title}")
    print(f"Created at: {conversation.created_at}")
    print(f"Messages: {len(conversation.messages)}")
    print(f"Actions: {len(conversation.actions)}")
    
    print("\nMessages:")
    for i, message in enumerate(conversation.messages):
        print(f"  {i+1}. [{message.role}]: {message.content}")
    
    print("\nActions:")
    for i, action in enumerate(conversation.actions):
        print(f"  {i+1}. [{action.action_type}]: {action.data}")
    
    print("\nData is automatically persisted to:", data_dir.absolute())
    print("Run this script again to see persistence in action!")


if __name__ == "__main__":
    main() 