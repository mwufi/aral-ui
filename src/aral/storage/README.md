# Aral MessageStore

This module provides a MessageStore for the Aral framework with built-in persistence capabilities, allowing conversations, messages, and actions to be stored and retrieved from disk.

## Overview

The MessageStore is designed to be:

1. **Simple**: Easy to understand and use
2. **Reliable**: Ensures data isn't lost during application restarts
3. **Extensible**: Designed to allow for different storage backends in the future

## Components

### MessageStore

The main class for storing conversations, messages, and actions:

- Can work in-memory (default) or with file persistence
- Automatically saves changes when conversations, messages, or actions are added
- Loads existing data on initialization

### Storage Backends (Internal Implementation)

The MessageStore uses storage backends internally:

- `MemoryStorageBackend`: Stores data in memory (default)
- `FileStorageBackend`: Stores data in JSON files on disk
- Future backends could include SQLite, database, or cloud storage

## Usage

```python
from aral.storage import MessageStore

# Create an in-memory message store (default)
memory_store = MessageStore()

# Create a message store with file persistence
file_store = MessageStore(save_dir="./data")  # Creates directory if not existing

# Use normally - changes are automatically persisted
conversation = file_store.create_conversation(title="New Conversation")
file_store.add_message(conversation.id, "Hello, world!", role="user")
file_store.add_action(conversation.id, "button_click", {"button_id": "submit"})
```

## File Structure

When using the file storage backend, the following file structure is created:

```
data/
├── message_store.json         # Index of all conversations
└── conversations/
    ├── conversation-id-1.json # Individual conversation data
    ├── conversation-id-2.json
    └── ...
```

## Future Extensions

The MessageStore is designed to be extensible. Future storage backends might include:

- SQLite storage for better query capabilities
- Remote database storage (PostgreSQL, MongoDB, etc.)
- Cloud storage (S3, Firebase, etc.)

To add a new storage backend, the backend implementation details are hidden from the user. The user only needs to specify the appropriate parameters when creating the MessageStore. 