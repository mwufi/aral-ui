from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from pathlib import Path
import json
import shutil
import os
from datetime import datetime

from .message_store import MessageStore, Conversation


class DateTimeEncoder(json.JSONEncoder):
    """JSON encoder that handles datetime objects."""
    
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


class StorageProvider(ABC):
    """Simple interface for MessageStore persistence."""
    
    @abstractmethod
    def initialize(self) -> None:
        """Set up the storage provider."""
        pass
    
    @abstractmethod
    def save_store(self, store: MessageStore) -> None:
        """Save the entire message store."""
        pass
    
    @abstractmethod
    def load_store(self) -> Optional[MessageStore]:
        """Load the message store."""
        pass
    
    @abstractmethod
    def save_conversation(self, conversation: Conversation) -> None:
        """Save a single conversation."""
        pass
    
    @abstractmethod
    def load_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Load a single conversation."""
        pass
    
    @abstractmethod
    def list_conversation_ids(self) -> List[str]:
        """List all available conversation IDs."""
        pass


class JsonFileStorage(StorageProvider):
    """Store MessageStore data in JSON files."""
    
    def __init__(self, storage_dir: str = "./data"):
        self.storage_dir = Path(storage_dir)
        self.store_file = self.storage_dir / "message_store.json"
        self.conversations_dir = self.storage_dir / "conversations"
    
    def initialize(self) -> None:
        """Create necessary directories."""
        self.storage_dir.mkdir(exist_ok=True, parents=True)
        self.conversations_dir.mkdir(exist_ok=True, parents=True)
        
        # Create store file if it doesn't exist
        if not self.store_file.exists():
            with open(self.store_file, 'w') as f:
                json.dump({"conversation_ids": []}, f, indent=2)
    
    def save_store(self, store: MessageStore) -> None:
        """Save the message store index."""
        # Create a temporary file first to avoid corruption
        temp_file = self.store_file.with_suffix('.tmp')
        
        # Save basic store info (without full conversations)
        store_data = {
            "conversation_ids": list(store.conversations.keys())
        }
        
        with open(temp_file, 'w') as f:
            json.dump(store_data, f, indent=2, cls=DateTimeEncoder)
        
        # Atomic replace
        shutil.move(temp_file, self.store_file)
        
        # Save each conversation individually
        for conv_id, conversation in store.conversations.items():
            self.save_conversation(conversation)
    
    def load_store(self) -> Optional[MessageStore]:
        """Load the message store."""
        if not self.store_file.exists():
            return None
        
        store = MessageStore()
        
        # Load the store index
        try:
            with open(self.store_file, 'r') as f:
                store_data = json.load(f)
            
            # Load each conversation
            for conv_id in store_data.get("conversation_ids", []):
                conversation = self.load_conversation(conv_id)
                if conversation:
                    store.conversations[conv_id] = conversation
            
            # If no conversations were loaded from the index, try loading from files
            if not store.conversations:
                conv_ids = self.list_conversation_ids()
                for conv_id in conv_ids:
                    conversation = self.load_conversation(conv_id)
                    if conversation:
                        store.conversations[conv_id] = conversation
                
                # Update the store file with the found conversations
                if store.conversations:
                    self.save_store(store)
            
            return store
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading message store: {e}")
            return None
    
    def save_conversation(self, conversation: Conversation) -> None:
        """Save a single conversation to its own file."""
        conv_file = self.conversations_dir / f"{conversation.id}.json"
        temp_file = conv_file.with_suffix('.tmp')
        
        # Convert to dict
        conv_data = conversation.model_dump()
        
        # Write to temp file first
        with open(temp_file, 'w') as f:
            json.dump(conv_data, f, indent=2, cls=DateTimeEncoder)
        
        # Atomic replace
        shutil.move(temp_file, conv_file)
        
        # Update the store file to include this conversation
        self._update_store_index(conversation.id)
    
    def _update_store_index(self, conversation_id: str) -> None:
        """Update the store index to include a conversation ID."""
        if not self.store_file.exists():
            with open(self.store_file, 'w') as f:
                json.dump({"conversation_ids": [conversation_id]}, f, indent=2)
            return
        
        try:
            # Load existing data
            with open(self.store_file, 'r') as f:
                store_data = json.load(f)
            
            # Add the conversation ID if not already present
            if conversation_id not in store_data.get("conversation_ids", []):
                store_data.setdefault("conversation_ids", []).append(conversation_id)
                
                # Write back to the file
                temp_file = self.store_file.with_suffix('.tmp')
                with open(temp_file, 'w') as f:
                    json.dump(store_data, f, indent=2)
                
                # Atomic replace
                shutil.move(temp_file, self.store_file)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error updating store index: {e}")
    
    def load_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Load a single conversation from its file."""
        conv_file = self.conversations_dir / f"{conversation_id}.json"
        
        if not conv_file.exists():
            return None
        
        try:
            with open(conv_file, 'r') as f:
                conv_data = json.load(f)
            
            # Convert ISO datetime strings back to datetime objects
            if "created_at" in conv_data and isinstance(conv_data["created_at"], str):
                conv_data["created_at"] = datetime.fromisoformat(conv_data["created_at"])
            
            # Convert message datetimes
            for msg in conv_data.get("messages", []):
                if "created_at" in msg and isinstance(msg["created_at"], str):
                    msg["created_at"] = datetime.fromisoformat(msg["created_at"])
            
            # Convert action datetimes
            for action in conv_data.get("actions", []):
                if "created_at" in action and isinstance(action["created_at"], str):
                    action["created_at"] = datetime.fromisoformat(action["created_at"])
            
            return Conversation(**conv_data)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading conversation {conversation_id}: {e}")
            return None
    
    def list_conversation_ids(self) -> List[str]:
        """List all conversation IDs from the file system."""
        if not self.conversations_dir.exists():
            return []
        
        # Get all JSON files in the conversations directory
        conv_files = list(self.conversations_dir.glob("*.json"))
        
        # Extract conversation IDs from filenames
        return [f.stem for f in conv_files] 