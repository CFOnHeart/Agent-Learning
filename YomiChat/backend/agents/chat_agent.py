"""
Main chat agent implementation
"""
from typing import Generator
from .agent_factory import create_chat_agent, enhance_agent_with_streaming
from streaming import stream_manager


class ChatAgent:
    """High-level chat agent interface"""
    
    def __init__(self):
        self.agent = create_chat_agent()
        enhance_agent_with_streaming(self.agent, stream_manager.stream_message)
    
    def chat(self, message: str) -> str:
        """
        Send a message to the agent and get a response
        
        Args:
            message: User message
            
        Returns:
            Agent response
        """
        return self.agent.run(message)
    
    def chat_stream(self, message: str) -> Generator[str, None, None]:
        """
        Send a message to the agent and get a streaming response
        
        Args:
            message: User message
            
        Yields:
            Streaming response chunks
        """
        return stream_manager.create_streaming_generator(self.agent.run, message)


# Global chat agent instance
chat_agent = ChatAgent()
