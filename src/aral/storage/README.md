# Aral MessageStore Persistence

This module provides persistence capabilities for the Aral MessageStore, allowing conversations, messages, and actions to be stored and retrieved from disk.

## Overview

The persistence layer is designed to be:

1. **Simple**: Easy to understand and use
2. **Reliable**: Ensures data isn't lost during application restarts
3. **Extensible**: Designed to allow for different storage backends in the future

## Components

### StorageProvider

An abstract interface that defines the operations required for persistence:

- `initialize()`: Set up the storage provider
- `save_store(store)`: Save the entire message store
- `load_store()`: Load the message store
- `save_conversation(conversation)`: Save a single conversation
- `load_conversation(conversation_id)`: Load a single conversation
- `list_conversation_ids()`: List all available conversation IDs

### JsonFileStorage

A concrete implementation of `StorageProvider` that stores data in JSON files:

- Stores each conversation in a separate file for better performance
- Uses atomic file operations to prevent data corruption
- Organizes conversations in a directory structure

### PersistentMessageStore

An extension of `MessageStore` that adds persistence capabilities:

- Automatically saves changes when conversations, messages, or actions are added
- Loads existing data on initialization
- Provides an explicit `save()` method for manual persistence

## Usage

```python
from aral.storage import JsonFileStorage, PersistentMessageStore

# Create a storage provider
storage = JsonFileStorage(storage_dir="./data")

# Create a persistent message store
store = PersistentMessageStore(storage_provider=storage)

# Initialize the store (loads existing data if available)
store.initialize()

# Use normally - changes are automatically persisted
conversation = store.create_conversation(title="New Conversation")
store.add_message(conversation.id, "Hello, world!", role="user")
store.add_action(conversation.id, "button_click", {"button_id": "submit"})

# Explicitly save the entire store (usually not needed)
store.save()
```

## File Structure

The JsonFileStorage provider creates the following file structure:

```
data/
├── message_store.json         # Index of all conversations
└── conversations/
    ├── conversation-id-1.json # Individual conversation data
    ├── conversation-id-2.json
    └── ...
```

## Future Extensions

The persistence layer is designed to be extensible. Future storage backends might include:

- SQLite storage for better query capabilities
- Remote database storage (PostgreSQL, MongoDB, etc.)
- Cloud storage (S3, Firebase, etc.)

To implement a new storage backend, simply create a new class that implements the `StorageProvider` interface. 