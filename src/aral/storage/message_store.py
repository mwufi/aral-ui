from typing import Dict, List, Optional, Any, Union, Literal
from datetime import datetime
import uuid
import os
import json
import shutil
from pathlib import Path
from pydantic import BaseModel, Field


class Message(BaseModel):
    """A message in a conversation."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content: str
    role: str = "user"
    created_at: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        arbitrary_types_allowed = True


class ConversationAction(BaseModel):
    """An action performed in a conversation, such as a tool call or event."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    action_type: str
    data: Dict[str, Any]
    created_at: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        arbitrary_types_allowed = True


class Conversation(BaseModel):
    """A conversation between a user and an agent."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    created_at: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    messages: List[Message] = Field(default_factory=list)
    actions: List[ConversationAction] = Field(default_factory=list)
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, **data):
        if "title" not in data or not data["title"]:
            # Generate a title based on ID if not provided
            id_value = data.get("id", str(uuid.uuid4()))
            data["title"] = f"Conversation {id_value[:8]}"
        super().__init__(**data)
    
    def add_message(self, message: Union[Message, Dict[str, Any]]) -> Message:
        """Add a message to the conversation."""
        if isinstance(message, dict):
            message = Message(**message)
        
        self.messages.append(message)
        return message
    
    def add_action(self, action: Union[ConversationAction, Dict[str, Any]]) -> ConversationAction:
        """Add an action to the conversation."""
        if isinstance(action, dict):
            action = ConversationAction(**action)
        
        self.actions.append(action)
        return action


class DateTimeEncoder(json.JSONEncoder):
    """JSON encoder that handles datetime objects."""
    
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


class StorageBackend:
    """Base class for storage backends."""
    
    def initialize(self) -> None:
        """Initialize the storage backend."""
        pass
    
    def save_store(self, store_data: Dict[str, Any]) -> None:
        """Save the message store data."""
        pass
    
    def load_store(self) -> Optional[Dict[str, Any]]:
        """Load the message store data."""
        pass
    
    def save_conversation(self, conversation_id: str, conversation_data: Dict[str, Any]) -> None:
        """Save a single conversation."""
        pass
    
    def load_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Load a single conversation."""
        pass
    
    def list_conversation_ids(self) -> List[str]:
        """List all available conversation IDs."""
        return []


class MemoryStorageBackend(StorageBackend):
    """In-memory storage backend."""
    
    def __init__(self):
        self.data: Dict[str, Any] = {"conversations": {}}
    
    def save_store(self, store_data: Dict[str, Any]) -> None:
        """Save the message store data."""
        self.data = store_data
    
    def load_store(self) -> Optional[Dict[str, Any]]:
        """Load the message store data."""
        return self.data
    
    def save_conversation(self, conversation_id: str, conversation_data: Dict[str, Any]) -> None:
        """Save a single conversation."""
        self.data["conversations"][conversation_id] = conversation_data
    
    def load_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Load a single conversation."""
        return self.data["conversations"].get(conversation_id)
    
    def list_conversation_ids(self) -> List[str]:
        """List all available conversation IDs."""
        return list(self.data["conversations"].keys())


class FileStorageBackend(StorageBackend):
    """File-based storage backend."""
    
    def __init__(self, save_dir: str):
        self.save_dir = Path(save_dir)
        self.store_file = self.save_dir / "message_store.json"
        self.conversations_dir = self.save_dir / "conversations"
    
    def initialize(self) -> None:
        """Create necessary directories."""
        self.save_dir.mkdir(exist_ok=True, parents=True)
        self.conversations_dir.mkdir(exist_ok=True, parents=True)
        
        # Create store file if it doesn't exist
        if not self.store_file.exists():
            with open(self.store_file, 'w') as f:
                json.dump({"conversation_ids": []}, f, indent=2)
    
    def save_store(self, store_data: Dict[str, Any]) -> None:
        """Save the message store index."""
        # Create a temporary file first to avoid corruption
        temp_file = self.store_file.with_suffix('.tmp')
        
        # Extract conversation IDs
        conversation_ids = list(store_data.get("conversations", {}).keys())
        
        # Save basic store info (without full conversations)
        store_index = {
            "conversation_ids": conversation_ids
        }
        
        with open(temp_file, 'w') as f:
            json.dump(store_index, f, indent=2, cls=DateTimeEncoder)
        
        # Atomic replace
        shutil.move(temp_file, self.store_file)
        
        # Save each conversation individually
        for conv_id, conv_data in store_data.get("conversations", {}).items():
            self.save_conversation(conv_id, conv_data)
    
    def load_store(self) -> Optional[Dict[str, Any]]:
        """Load the message store."""
        if not self.store_file.exists():
            return {"conversations": {}}
        
        store_data = {"conversations": {}}
        
        # Load the store index
        try:
            with open(self.store_file, 'r') as f:
                store_index = json.load(f)
            
            # Load each conversation
            for conv_id in store_index.get("conversation_ids", []):
                conversation = self.load_conversation(conv_id)
                if conversation:
                    store_data["conversations"][conv_id] = conversation
            
            # If no conversations were loaded from the index, try loading from files
            if not store_data["conversations"]:
                conv_ids = self.list_conversation_ids()
                for conv_id in conv_ids:
                    conversation = self.load_conversation(conv_id)
                    if conversation:
                        store_data["conversations"][conv_id] = conversation
            
            return store_data
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading message store: {e}")
            return {"conversations": {}}
    
    def save_conversation(self, conversation_id: str, conversation_data: Dict[str, Any]) -> None:
        """Save a single conversation to its own file."""
        conv_file = self.conversations_dir / f"{conversation_id}.json"
        temp_file = conv_file.with_suffix('.tmp')
        
        # Write to temp file first
        with open(temp_file, 'w') as f:
            json.dump(conversation_data, f, indent=2, cls=DateTimeEncoder)
        
        # Atomic replace
        shutil.move(temp_file, conv_file)
        
        # Update the store file to include this conversation
        self._update_store_index(conversation_id)
    
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
    
    def load_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
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
            
            return conv_data
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


class MessageStore:
    """A store for conversations and messages.
    
    If save_dir is provided, conversations will be persisted to disk.
    """
    
    def __init__(self, save_dir: Optional[str] = None, backend_type: Literal["memory", "file"] = "memory"):
        self.conversations: Dict[str, Conversation] = {}
        
        # Set up the storage backend
        if save_dir:
            self.backend = FileStorageBackend(save_dir)
            backend_type = "file"  # Override backend_type if save_dir is provided
        elif backend_type == "file":
            raise ValueError("save_dir must be provided when using file backend")
        else:
            self.backend = MemoryStorageBackend()
        
        # Initialize the backend and load any existing data
        self.backend.initialize()
        self._load_from_backend()
    
    def _load_from_backend(self) -> None:
        """Load data from the backend."""
        store_data = self.backend.load_store()
        if store_data:
            for conv_id, conv_data in store_data.get("conversations", {}).items():
                conversation = Conversation(**conv_data)
                self.conversations[conv_id] = conversation
    
    def _save_to_backend(self) -> None:
        """Save data to the backend."""
        store_data = self.to_dict()
        self.backend.save_store(store_data)
    
    def _save_conversation(self, conversation: Conversation) -> None:
        """Save a single conversation."""
        conv_data = conversation.model_dump()
        self.backend.save_conversation(conversation.id, conv_data)
    
    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Get a conversation by ID."""
        return self.conversations.get(conversation_id)
    
    def create_conversation(
        self, 
        title: Optional[str] = None, 
        id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Conversation:
        """Create a new conversation."""
        conversation = Conversation(
            id=id or str(uuid.uuid4()),
            title=title,
            metadata=metadata or {}
        )
        self.conversations[conversation.id] = conversation
        
        # Save to backend
        self._save_conversation(conversation)
        
        return conversation
    
    def add_message(
        self, 
        conversation_id: str, 
        content: str, 
        role: str = "user",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Message:
        """Add a message to a conversation."""
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            conversation = self.create_conversation(id=conversation_id)
        
        message = Message(content=content, role=role, metadata=metadata or {})
        conversation.add_message(message)
        
        # Save the updated conversation
        self._save_conversation(conversation)
        
        return message
    
    def add_action(
        self,
        conversation_id: str,
        action_type: str,
        data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> ConversationAction:
        """Add an action to a conversation."""
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            conversation = self.create_conversation(id=conversation_id)
        
        action = ConversationAction(
            action_type=action_type, 
            data=data, 
            metadata=metadata or {}
        )
        conversation.add_action(action)
        
        # Save the updated conversation
        self._save_conversation(conversation)
        
        return action
    
    def get_all_conversations(self) -> List[Conversation]:
        """Get all conversations."""
        return list(self.conversations.values())
    
    def get_conversation_messages(self, conversation_id: str) -> List[Message]:
        """Get all messages in a conversation."""
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return []
        
        return conversation.messages
    
    def get_conversation_actions(self, conversation_id: str) -> List[ConversationAction]:
        """Get all actions in a conversation."""
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return []
        
        return conversation.actions
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the message store to a dictionary."""
        return {
            "conversations": {
                conv_id: conv.model_dump() 
                for conv_id, conv in self.conversations.items()
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MessageStore":
        """Create a message store from a dictionary."""
        store = cls()
        
        for conv_id, conv_data in data.get("conversations", {}).items():
            conversation = Conversation(**conv_data)
            store.conversations[conv_id] = conversation
        
        return store 