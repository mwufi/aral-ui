# Aral: One-Line Agent Deployment Framework

## Overview

aral is a Python package that lets developers build, run, and deploy AI agents with minimal infrastructure overhead. Just like Streamlit revolutionized data app development, aral simplifies agent development with a clean API and instant deployment capabilities.

## Core Features

### 1. One-Line Deployment

```python
agent.run()  # Launches FastAPI server + UI instantly
```

### 2. Rich Base Agent Framework

```python
class MyAgent(BaseAgent):
    def init(self):
        self.ctx = Context()
        self.messages = MessageStore()
    
    def on_message(self, convo_id, message):
        # Handle incoming messages
        response = self.do_actions(activation_event=('message', convo_id, message))
        return response
```

### 3. Built-in UI

- Instant chat interface via Next.js
- No frontend knowledge required
- Automatic setup using Bun for optimal performance
- Themeable and customizable

### 4. Simplified Action System

```python
@agent.action
def search_web(query):
    # Implementation
    return results
```

### 5. Cloud Deployment

```python
agent.deploy(provider="cloud", region="us-east-1")
```

### 6. Memory & Context Management

- Built-in message history
- Structured context store for agent memory
- Efficient summarization capabilities

### 7. Middleware Support

```python
agent.add_middleware(RateLimiter(max_calls=10))
agent.add_middleware(Logger())
```

## Technical Implementation

### Package Structure

```
aral/
├── __init__.py             # Package initialization
├── agent.py                # BaseAgent implementation
├── ai.py                   # AI class for LLM interactions
├── storage/                # Storage components
├── actions/                # Action registration and execution
├── middleware/             # Middleware components
├── ui/                     # UI components with Next.js
└── deploy/                 # Deployment utilities
```

### UI Integration

- Bundled Next.js app for instant chat interface
- Optimized for Bun for faster startup and development
- Fallback to serving static files if needed

### Installation

```bash
# Using Rye
rye add aral

# Using pip
pip install aral
```

## User Experience

1. Install the package
2. Create an agent by subclassing BaseAgent
3. Run with `agent.run()`
4. Instantly get a working agent with UI at http://localhost:3000

## Development Roadmap

1. Core framework with BaseAgent class
2. FastAPI integration for message handling
3. Next.js UI with Bun optimization
4. Action system implementation
5. Memory and context management
6. Cloud deployment capabilities
7. Extended middleware support

This framework aims to do for agent development what Streamlit did for data apps - make it accessible to any Python developer without requiring deep infrastructure knowledge.