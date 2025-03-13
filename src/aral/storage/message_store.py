from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import uuid
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


class MessageStore:
    """A store for conversations and messages."""
    
    def __init__(self):
        self.conversations: Dict[str, Conversation] = {}
    
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