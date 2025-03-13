import os
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from src.aral.storage import MessageStore, Message, Conversation, ConversationAction


class TestFileMessageStore(unittest.TestCase):
    """Test the MessageStore class with file persistence."""
    
    def setUp(self):
        """Set up a temporary directory for testing."""
        self.temp_dir = tempfile.mkdtemp()
        print(f"\nTest temp dir: {self.temp_dir}")
        self.store = MessageStore(save_dir=self.temp_dir)
    
    def tearDown(self):
        """Clean up the temporary directory."""
        shutil.rmtree(self.temp_dir)
    
    def test_directory_creation(self):
        """Test that directories are created."""
        self.assertTrue(os.path.exists(self.temp_dir))
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir, "conversations")))
    
    def test_create_conversation_persists(self):
        """Test that creating a conversation persists it."""
        # Create a conversation
        conversation = self.store.create_conversation(
            id="test-conv-1",
            title="Test Conversation"
        )
        
        # Check that the file exists
        conv_file = Path(self.temp_dir) / "conversations" / "test-conv-1.json"
        self.assertTrue(conv_file.exists())
        print(f"Conversation file exists: {conv_file}")
        
        # Check file contents
        with open(conv_file, 'r') as f:
            conv_data = json.load(f)
            print(f"Conversation file contents: {json.dumps(conv_data, indent=2)}")
        
        # Create a new store and load from the same directory
        new_store = MessageStore(save_dir=self.temp_dir)
        
        # Check that the conversation was loaded
        loaded_conv = new_store.get_conversation("test-conv-1")
        print(f"Loaded conversation: {loaded_conv}")
        if loaded_conv:
            print(f"Loaded conversation ID: {loaded_conv.id}")
            print(f"Loaded conversation title: {loaded_conv.title}")
        
        # Check store contents
        print(f"New store conversations: {list(new_store.conversations.keys())}")
        
        self.assertIsNotNone(loaded_conv)
        self.assertEqual(loaded_conv.id, "test-conv-1")
        self.assertEqual(loaded_conv.title, "Test Conversation")
    
    def test_add_message_persists(self):
        """Test that adding a message persists it."""
        # Create a conversation
        conversation = self.store.create_conversation(
            id="test-conv-1",
            title="Test Conversation"
        )
        
        # Add a message
        self.store.add_message(
            conversation.id,
            "Hello, world!",
            role="user"
        )
        
        # Check file contents
        conv_file = Path(self.temp_dir) / "conversations" / "test-conv-1.json"
        with open(conv_file, 'r') as f:
            conv_data = json.load(f)
            print(f"Conversation file contents: {json.dumps(conv_data, indent=2)}")
        
        # Create a new store and load from the same directory
        new_store = MessageStore(save_dir=self.temp_dir)
        
        # Check that the message was loaded
        loaded_conv = new_store.get_conversation("test-conv-1")
        print(f"Loaded conversation: {loaded_conv}")
        if loaded_conv:
            print(f"Loaded conversation messages: {loaded_conv.messages}")
        
        # Check store contents
        print(f"New store conversations: {list(new_store.conversations.keys())}")
        
        self.assertIsNotNone(loaded_conv)
        self.assertEqual(len(loaded_conv.messages), 1)
        self.assertEqual(loaded_conv.messages[0].content, "Hello, world!")
        self.assertEqual(loaded_conv.messages[0].role, "user")
    
    def test_add_action_persists(self):
        """Test that adding an action persists it."""
        # Create a conversation
        conversation = self.store.create_conversation(
            id="test-conv-1",
            title="Test Conversation"
        )
        
        # Add an action
        self.store.add_action(
            conversation.id,
            "button_click",
            {"button_id": "submit"}
        )
        
        # Check file contents
        conv_file = Path(self.temp_dir) / "conversations" / "test-conv-1.json"
        with open(conv_file, 'r') as f:
            conv_data = json.load(f)
            print(f"Conversation file contents: {json.dumps(conv_data, indent=2)}")
        
        # Create a new store and load from the same directory
        new_store = MessageStore(save_dir=self.temp_dir)
        
        # Check that the action was loaded
        loaded_conv = new_store.get_conversation("test-conv-1")
        print(f"Loaded conversation: {loaded_conv}")
        if loaded_conv:
            print(f"Loaded conversation actions: {loaded_conv.actions}")
        
        # Check store contents
        print(f"New store conversations: {list(new_store.conversations.keys())}")
        
        self.assertIsNotNone(loaded_conv)
        self.assertEqual(len(loaded_conv.actions), 1)
        self.assertEqual(loaded_conv.actions[0].action_type, "button_click")
        self.assertEqual(loaded_conv.actions[0].data, {"button_id": "submit"})
    
    def test_direct_modification(self):
        """Test modifying a conversation directly."""
        # Create a conversation
        conversation = self.store.create_conversation(
            id="test-conv-1",
            title="Test Conversation"
        )
        
        # Modify the conversation title directly
        conversation.title = "Modified Title"
        
        # We need to save the conversation explicitly since we modified it directly
        self.store._save_conversation(conversation)
        
        # Check file contents
        conv_file = Path(self.temp_dir) / "conversations" / "test-conv-1.json"
        with open(conv_file, 'r') as f:
            conv_data = json.load(f)
            print(f"Conversation file contents: {json.dumps(conv_data, indent=2)}")
        
        # Create a new store and load from the same directory
        new_store = MessageStore(save_dir=self.temp_dir)
        
        # Check that the modified title was saved
        loaded_conv = new_store.get_conversation("test-conv-1")
        print(f"Loaded conversation: {loaded_conv}")
        if loaded_conv:
            print(f"Loaded conversation title: {loaded_conv.title}")
        
        # Check store contents
        print(f"New store conversations: {list(new_store.conversations.keys())}")
        
        self.assertIsNotNone(loaded_conv)
        self.assertEqual(loaded_conv.title, "Modified Title")


class TestMemoryMessageStore(unittest.TestCase):
    """Test the MessageStore class with in-memory storage."""
    
    def setUp(self):
        """Set up a store with in-memory persistence."""
        self.store = MessageStore()  # Default is in-memory
    
    def test_create_conversation(self):
        """Test creating a conversation."""
        conversation = self.store.create_conversation(
            id="test-conv-1",
            title="Test Conversation"
        )
        
        self.assertEqual(conversation.id, "test-conv-1")
        self.assertEqual(conversation.title, "Test Conversation")
        self.assertEqual(len(conversation.messages), 0)
        self.assertEqual(len(conversation.actions), 0)
    
    def test_add_message(self):
        """Test adding a message."""
        # Create a conversation
        conversation = self.store.create_conversation(
            id="test-conv-1",
            title="Test Conversation"
        )
        
        # Add a message
        message = self.store.add_message(
            conversation.id,
            "Hello, world!",
            role="user"
        )
        
        # Check that the message was added
        self.assertEqual(len(conversation.messages), 1)
        self.assertEqual(conversation.messages[0].content, "Hello, world!")
        self.assertEqual(conversation.messages[0].role, "user")
        self.assertEqual(message.content, "Hello, world!")
        self.assertEqual(message.role, "user")
    
    def test_add_action(self):
        """Test adding an action."""
        # Create a conversation
        conversation = self.store.create_conversation(
            id="test-conv-1",
            title="Test Conversation"
        )
        
        # Add an action
        action = self.store.add_action(
            conversation.id,
            "button_click",
            {"button_id": "submit"}
        )
        
        # Check that the action was added
        self.assertEqual(len(conversation.actions), 1)
        self.assertEqual(conversation.actions[0].action_type, "button_click")
        self.assertEqual(conversation.actions[0].data, {"button_id": "submit"})
        self.assertEqual(action.action_type, "button_click")
        self.assertEqual(action.data, {"button_id": "submit"})
    
    def test_get_conversation(self):
        """Test getting a conversation."""
        # Create a conversation
        self.store.create_conversation(
            id="test-conv-1",
            title="Test Conversation"
        )
        
        # Get the conversation
        conversation = self.store.get_conversation("test-conv-1")
        
        # Check that it was retrieved correctly
        self.assertIsNotNone(conversation)
        self.assertEqual(conversation.id, "test-conv-1")
        self.assertEqual(conversation.title, "Test Conversation")
    
    def test_get_all_conversations(self):
        """Test getting all conversations."""
        # Create multiple conversations
        self.store.create_conversation(id="test-conv-1", title="Conversation 1")
        self.store.create_conversation(id="test-conv-2", title="Conversation 2")
        
        # Get all conversations
        conversations = self.store.get_all_conversations()
        
        # Check that they were retrieved correctly
        self.assertEqual(len(conversations), 2)
        conversation_ids = [conv.id for conv in conversations]
        self.assertIn("test-conv-1", conversation_ids)
        self.assertIn("test-conv-2", conversation_ids)
    
    def test_serialization(self):
        """Test serializing and deserializing a message store."""
        # Create some conversations with messages and actions
        conv1 = self.store.create_conversation(id="test-conv-1", title="Conversation 1")
        self.store.add_message(conv1.id, "Hello from conv1", role="user")
        
        conv2 = self.store.create_conversation(id="test-conv-2", title="Conversation 2")
        self.store.add_message(conv2.id, "Hello from conv2", role="user")
        self.store.add_action(conv2.id, "button_click", {"button_id": "submit"})
        
        # Serialize the store
        store_dict = self.store.to_dict()
        
        # Create a new store from the serialized data
        new_store = MessageStore.from_dict(store_dict)
        
        # Check that it was deserialized correctly
        self.assertEqual(len(new_store.conversations), 2)
        self.assertIn("test-conv-1", new_store.conversations)
        self.assertIn("test-conv-2", new_store.conversations)
        
        # Check conversation 1
        loaded_conv1 = new_store.get_conversation("test-conv-1")
        self.assertEqual(loaded_conv1.title, "Conversation 1")
        self.assertEqual(len(loaded_conv1.messages), 1)
        self.assertEqual(loaded_conv1.messages[0].content, "Hello from conv1")
        
        # Check conversation 2
        loaded_conv2 = new_store.get_conversation("test-conv-2")
        self.assertEqual(loaded_conv2.title, "Conversation 2")
        self.assertEqual(len(loaded_conv2.messages), 1)
        self.assertEqual(loaded_conv2.messages[0].content, "Hello from conv2")
        self.assertEqual(len(loaded_conv2.actions), 1)
        self.assertEqual(loaded_conv2.actions[0].action_type, "button_click")


if __name__ == "__main__":
    unittest.main() 