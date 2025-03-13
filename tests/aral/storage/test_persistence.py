import os
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from src.aral.storage import (
    MessageStore, Message, Conversation, ConversationAction,
    JsonFileStorage, PersistentMessageStore
)


class TestJsonFileStorage(unittest.TestCase):
    """Test the JsonFileStorage class."""
    
    def setUp(self):
        """Set up a temporary directory for testing."""
        self.temp_dir = tempfile.mkdtemp()
        self.storage = JsonFileStorage(storage_dir=self.temp_dir)
        self.storage.initialize()
    
    def tearDown(self):
        """Clean up the temporary directory."""
        shutil.rmtree(self.temp_dir)
    
    def test_initialize(self):
        """Test that initialize creates the necessary directories."""
        self.assertTrue(os.path.exists(self.temp_dir))
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir, "conversations")))
    
    def test_save_and_load_conversation(self):
        """Test saving and loading a single conversation."""
        # Create a conversation
        conversation = Conversation(
            id="test-conv-1",
            title="Test Conversation"
        )
        conversation.add_message(Message(content="Hello", role="user"))
        conversation.add_message(Message(content="Hi there", role="assistant"))
        conversation.add_action(ConversationAction(action_type="button_click", data={"button_id": "submit"}))
        
        # Save the conversation
        self.storage.save_conversation(conversation)
        
        # Check that the file exists
        conv_file = Path(self.temp_dir) / "conversations" / "test-conv-1.json"
        self.assertTrue(conv_file.exists())
        
        # Load the conversation
        loaded_conv = self.storage.load_conversation("test-conv-1")
        
        # Check that it loaded correctly
        self.assertIsNotNone(loaded_conv)
        self.assertEqual(loaded_conv.id, "test-conv-1")
        self.assertEqual(loaded_conv.title, "Test Conversation")
        self.assertEqual(len(loaded_conv.messages), 2)
        self.assertEqual(loaded_conv.messages[0].content, "Hello")
        self.assertEqual(loaded_conv.messages[1].content, "Hi there")
        self.assertEqual(len(loaded_conv.actions), 1)
        self.assertEqual(loaded_conv.actions[0].action_type, "button_click")
    
    def test_save_and_load_store(self):
        """Test saving and loading an entire message store."""
        # Create a message store with multiple conversations
        store = MessageStore()
        
        conv1 = store.create_conversation(id="test-conv-1", title="Conversation 1")
        store.add_message(conv1.id, "Hello from conv1", role="user")
        
        conv2 = store.create_conversation(id="test-conv-2", title="Conversation 2")
        store.add_message(conv2.id, "Hello from conv2", role="user")
        store.add_action(conv2.id, "button_click", {"button_id": "submit"})
        
        # Save the store
        self.storage.save_store(store)
        
        # Check that the index file exists
        store_file = Path(self.temp_dir) / "message_store.json"
        self.assertTrue(store_file.exists())
        
        # Check that conversation files exist
        conv1_file = Path(self.temp_dir) / "conversations" / "test-conv-1.json"
        conv2_file = Path(self.temp_dir) / "conversations" / "test-conv-2.json"
        self.assertTrue(conv1_file.exists())
        self.assertTrue(conv2_file.exists())
        
        # Load the store
        loaded_store = self.storage.load_store()
        
        # Check that it loaded correctly
        self.assertIsNotNone(loaded_store)
        self.assertEqual(len(loaded_store.conversations), 2)
        self.assertIn("test-conv-1", loaded_store.conversations)
        self.assertIn("test-conv-2", loaded_store.conversations)
        
        # Check conversation 1
        loaded_conv1 = loaded_store.get_conversation("test-conv-1")
        self.assertEqual(loaded_conv1.title, "Conversation 1")
        self.assertEqual(len(loaded_conv1.messages), 1)
        self.assertEqual(loaded_conv1.messages[0].content, "Hello from conv1")
        
        # Check conversation 2
        loaded_conv2 = loaded_store.get_conversation("test-conv-2")
        self.assertEqual(loaded_conv2.title, "Conversation 2")
        self.assertEqual(len(loaded_conv2.messages), 1)
        self.assertEqual(loaded_conv2.messages[0].content, "Hello from conv2")
        self.assertEqual(len(loaded_conv2.actions), 1)
        self.assertEqual(loaded_conv2.actions[0].action_type, "button_click")
    
    def test_list_conversation_ids(self):
        """Test listing conversation IDs."""
        # Create some conversations
        conv1 = Conversation(id="test-conv-1", title="Conversation 1")
        conv2 = Conversation(id="test-conv-2", title="Conversation 2")
        
        # Save them
        self.storage.save_conversation(conv1)
        self.storage.save_conversation(conv2)
        
        # List conversation IDs
        conv_ids = self.storage.list_conversation_ids()
        
        # Check the result
        self.assertEqual(len(conv_ids), 2)
        self.assertIn("test-conv-1", conv_ids)
        self.assertIn("test-conv-2", conv_ids)


class TestPersistentMessageStore(unittest.TestCase):
    """Test the PersistentMessageStore class."""
    
    def setUp(self):
        """Set up a temporary directory for testing."""
        self.temp_dir = tempfile.mkdtemp()
        print(f"\nTest temp dir: {self.temp_dir}")
        self.storage = JsonFileStorage(storage_dir=self.temp_dir)
        self.storage.initialize()
        self.store = PersistentMessageStore(storage_provider=self.storage)
        self.store.initialize()
    
    def tearDown(self):
        """Clean up the temporary directory."""
        shutil.rmtree(self.temp_dir)
    
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
        
        # Create a new store and load from the same storage
        new_storage = JsonFileStorage(storage_dir=self.temp_dir)
        new_storage.initialize()
        new_store = PersistentMessageStore(storage_provider=new_storage)
        new_store.initialize()
        
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
        
        # Create a new store and load from the same storage
        new_storage = JsonFileStorage(storage_dir=self.temp_dir)
        new_storage.initialize()
        new_store = PersistentMessageStore(storage_provider=new_storage)
        new_store.initialize()
        
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
        
        # Create a new store and load from the same storage
        new_storage = JsonFileStorage(storage_dir=self.temp_dir)
        new_storage.initialize()
        new_store = PersistentMessageStore(storage_provider=new_storage)
        new_store.initialize()
        
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
    
    def test_explicit_save(self):
        """Test explicitly saving the store."""
        # Create a conversation
        conversation = self.store.create_conversation(
            id="test-conv-1",
            title="Test Conversation"
        )
        
        # Modify the conversation title directly (bypassing persistence)
        conversation.title = "Modified Title"
        
        # Save explicitly
        self.store.save()
        
        # Check file contents
        conv_file = Path(self.temp_dir) / "conversations" / "test-conv-1.json"
        with open(conv_file, 'r') as f:
            conv_data = json.load(f)
            print(f"Conversation file contents: {json.dumps(conv_data, indent=2)}")
        
        # Create a new store and load from the same storage
        new_storage = JsonFileStorage(storage_dir=self.temp_dir)
        new_storage.initialize()
        new_store = PersistentMessageStore(storage_provider=new_storage)
        new_store.initialize()
        
        # Check that the modified title was saved
        loaded_conv = new_store.get_conversation("test-conv-1")
        print(f"Loaded conversation: {loaded_conv}")
        if loaded_conv:
            print(f"Loaded conversation title: {loaded_conv.title}")
        
        # Check store contents
        print(f"New store conversations: {list(new_store.conversations.keys())}")
        
        self.assertIsNotNone(loaded_conv)
        self.assertEqual(loaded_conv.title, "Modified Title")


if __name__ == "__main__":
    unittest.main() 