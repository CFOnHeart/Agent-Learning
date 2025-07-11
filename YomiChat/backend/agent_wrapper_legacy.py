"""
Legacy agent wrapper for backward compatibility
This file provides the same interface as the old agent_wrapper.py but uses the new modular structure
"""

# Import the new modular components
from agents import chat_agent

# Legacy function names for backward compatibility
def chat_with_agent(user_message: str) -> str:
    """Legacy function - use chat_agent.chat() instead"""
    return chat_agent.chat(user_message)

def chat_with_agent_stream(user_message: str):
    """Legacy function - use chat_agent.chat_stream() instead"""
    return chat_agent.chat_stream(user_message)

# For any code that might import these directly
__all__ = ['chat_with_agent', 'chat_with_agent_stream']
