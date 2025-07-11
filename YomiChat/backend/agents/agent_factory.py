"""
Agent factory for creating and configuring chat agents
"""
import sys
from typing import List, Optional
from smolagents import CodeAgent, LiteLLMModel
from config.settings import settings
from tools import tavily_search
from streaming.output_interceptor import OutputInterceptor


def create_chat_agent(tools: Optional[List] = None) -> CodeAgent:
    """
    Create and configure a chat agent with the specified tools
    
    Args:
        tools: List of tools to provide to the agent. If None, uses default tools.
        
    Returns:
        Configured CodeAgent instance
    """
    if not settings.has_azure_config:
        raise ValueError("Azure configuration is required. Please set AZURE_API_KEY and AZURE_API_BASE.")
    
    # Create the model
    model = LiteLLMModel(
        model_id=settings.model_id,
        api_key=settings.azure_api_key,
        api_base=settings.azure_api_base
    )
    
    # Use default tools if none provided
    if tools is None:
        tools = [tavily_search]
    
    # Create the agent
    agent = CodeAgent(tools=tools, model=model, stream_outputs=True)
    
    return agent


def enhance_agent_with_streaming(agent: CodeAgent, stream_callback):
    """
    Enhance an agent with streaming capabilities by monkey-patching its run method
    
    Args:
        agent: The agent to enhance
        stream_callback: Callback function for streaming messages
    """
    # Store original run method
    original_run = agent.run
    
    def enhanced_run(task, **kwargs):
        """Enhanced run method with streaming capabilities"""
        # Set up output interceptor
        original_stdout = sys.stdout
        interceptor = OutputInterceptor(original_stdout, stream_callback)
        
        try:
            # Redirect stdout to our interceptor
            sys.stdout = interceptor
            
            # Add some expected thinking steps
            if stream_callback:
                stream_callback("Initializing agent reasoning...", "thinking")
            
            # Run original method
            result = original_run(task, **kwargs)
            
            if stream_callback:
                stream_callback("Task completed successfully!", "success")
            
            return result
            
        except Exception as e:
            if stream_callback:
                stream_callback(f"Error during execution: {str(e)}", "error")
            raise
        finally:
            # Restore original stdout
            sys.stdout = original_stdout
    
    # Apply the enhancement
    agent.run = enhanced_run
    return agent
