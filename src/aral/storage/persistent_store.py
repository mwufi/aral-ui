from typing import Optional

from .message_store import MessageStore, Conversation, Message, ConversationAction
from .persistence import StorageProvider


class PersistentMessageStore(MessageStore):
    """MessageStore with persistence capabilities."""
    
    def __init__(self, storage_provider: Optional[StorageProvider] = None):
        super().__init__()
        self.storage_provider = storage_provider
        self._initialized = False
    
    def initialize(self) -> None:
        """Initialize the persistent message store."""
        if self.storage_provider and not self._initialized:
            self.storage_provider.initialize()
            loaded_store = self.storage_provider.load_store()
            if loaded_store:
                self.conversations = loaded_store.conversations
            self._initialized = True
    
    def save(self) -> None:
        """Save the message store."""
        if self.storage_provider:
            self.storage_provider.save_store(self)
    
    def create_conversation(self, *args, **kwargs) -> Conversation:
        """Create a conversation and save it."""
        conversation = super().create_conversation(*args, **kwargs)
        if self.storage_provider:
            self.storage_provider.save_conversation(conversation)
        return conversation
    
    def add_message(self, *args, **kwargs) -> Message:
        """Add a message and save the conversation."""
        message = super().add_message(*args, **kwargs)
        if self.storage_provider:
            conversation_id = args[0]
            conversation = self.get_conversation(conversation_id)
            if conversation:
                self.storage_provider.save_conversation(conversation)
        return message
    
    def add_action(self, *args, **kwargs) -> ConversationAction:
        """Add an action and save the conversation."""
        action = super().add_action(*args, **kwargs)
        if self.storage_provider:
            conversation_id = args[0]
            conversation = self.get_conversation(conversation_id)
            if conversation:
                self.storage_provider.save_conversation(conversation)
        return action 