# Backend Architecture Refactoring

This directory has been refactored to improve code organization and maintainability. The previous monolithic `agent_wrapper.py` has been split into modular components.

## New Structure

```
backend/
├── main.py                    # FastAPI application entry point
├── agent_wrapper_legacy.py    # Backward compatibility wrapper
├── config/
│   ├── __init__.py
│   └── settings.py           # Environment configuration and settings
├── tools/
│   ├── __init__.py
│   └── web_search.py         # Tavily web search tool
├── streaming/
│   ├── __init__.py
│   ├── stream_manager.py     # Stream management and message queuing
│   ├── output_interceptor.py # stdout/stderr interception
│   └── text_formatter.py    # ANSI code cleaning and text formatting
└── agents/
    ├── __init__.py
    ├── agent_factory.py      # Agent creation and configuration
    └── chat_agent.py         # Main chat agent implementation
```

## Key Components

### 1. Configuration (`config/`)
- `settings.py`: Centralized configuration management
- Environment variable handling
- Validation of required settings

### 2. Tools (`tools/`)
- `web_search.py`: Tavily search tool implementation
- Modular tool architecture for easy extension

### 3. Streaming (`streaming/`)
- `stream_manager.py`: Manages real-time output streaming
- `output_interceptor.py`: Captures agent stdout/stderr
- `text_formatter.py`: Cleans ANSI codes and formats output

### 4. Agents (`agents/`)
- `agent_factory.py`: Creates and configures agents
- `chat_agent.py`: High-level chat agent interface

## Usage

### Basic Chat
```python
from agents import chat_agent

response = chat_agent.chat("Hello, how are you?")
print(response)
```

### Streaming Chat
```python
from agents import chat_agent

for chunk in chat_agent.chat_stream("Tell me about Python"):
    print(chunk, end="", flush=True)
```

### Custom Agent Creation
```python
from agents import create_chat_agent
from tools import tavily_search

# Create agent with specific tools
agent = create_chat_agent(tools=[tavily_search])
response = agent.run("Search for latest news")
```

## Migration from Old Code

The old `agent_wrapper.py` functions are still available through `agent_wrapper_legacy.py`:

```python
# Old way (still works)
from agent_wrapper_legacy import chat_with_agent, chat_with_agent_stream

# New way (recommended)
from agents import chat_agent
```

## Benefits of New Structure

1. **Separation of Concerns**: Each module has a clear responsibility
2. **Testability**: Individual components can be tested in isolation
3. **Maintainability**: Easier to understand and modify specific functionality
4. **Extensibility**: Easy to add new tools, formatters, or streaming capabilities
5. **Reusability**: Components can be reused in different contexts

## Environment Variables

Make sure these environment variables are set:

```bash
AZURE_API_KEY=your_azure_api_key
AZURE_API_BASE=your_azure_api_base
TAVILY_API_KEY=your_tavily_api_key
```

## Dependencies

The refactored code maintains the same external dependencies:
- `smolagents`
- `fastapi`
- `pydantic`
- `python-dotenv` (optional)
- `tavily` (for web search)
