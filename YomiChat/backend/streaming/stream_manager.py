"""
Stream manager for handling real-time agent output streaming
"""
import threading
import time
from queue import Queue, Empty
from typing import Callable, Generator, Optional, Tuple
from .text_formatter import format_message_by_type


class SimpleStreamCapture:
    """Simple message queue for capturing streaming messages"""
    
    def __init__(self):
        self.messages = Queue()
        
    def add_message(self, message: str, msg_type: str = "info"):
        """Add a message to the stream queue"""
        self.messages.put((message, msg_type))
        
    def get_message(self) -> Tuple[Optional[str], Optional[str]]:
        """Get the next message from the queue"""
        try:
            return self.messages.get_nowait()
        except Empty:
            return None, None


class StreamManager:
    """Manages streaming of agent output"""
    
    def __init__(self):
        self._stream_callback: Optional[Callable] = None
    
    def set_stream_callback(self, callback: Optional[Callable]):
        """Set the global stream callback function"""
        self._stream_callback = callback
    
    def stream_message(self, message: str, msg_type: str = "info"):
        """Send a stream message if callback is set"""
        if self._stream_callback:
            self._stream_callback(message, msg_type)
    
    def create_streaming_generator(self, 
                                 agent_function: Callable, 
                                 *args, **kwargs) -> Generator[str, None, None]:
        """
        Create a generator that yields streaming chunks from agent execution
        
        Args:
            agent_function: The agent function to execute
            *args, **kwargs: Arguments to pass to the agent function
            
        Yields:
            Formatted message chunks ready for streaming
        """
        capture = SimpleStreamCapture()
        
        # Set the stream callback to capture messages
        self.set_stream_callback(capture.add_message)
        
        def run_agent_in_thread():
            """Run agent in a separate thread"""
            try:
                # Execute the agent function
                result = agent_function(*args, **kwargs)
                
                # Add final result
                capture.add_message(f"**Final Answer:**\n\n{result}", "result")
                capture.add_message("__FINISHED__", "end")
                
            except Exception as e:
                capture.add_message(f"Unexpected error: {str(e)}", "error")
                capture.add_message("__FINISHED__", "end")
            finally:
                # Clear callback
                self.set_stream_callback(None)
        
        # Start agent in background thread
        agent_thread = threading.Thread(target=run_agent_in_thread)
        agent_thread.daemon = True
        agent_thread.start()
        
        # Stream output in real-time
        while True:
            message, msg_type = capture.get_message()
            if message:
                if message == "__FINISHED__":
                    break
                else:
                    # Format and yield the message
                    formatted_message = format_message_by_type(message, msg_type)
                    if formatted_message:
                        yield formatted_message
            else:
                time.sleep(0.1)  # Short wait for new messages
                
                # If thread ended, get all remaining messages
                if not agent_thread.is_alive():
                    remaining_messages = []
                    while True:
                        message, msg_type = capture.get_message()
                        if not message:
                            break
                        if message == "__FINISHED__":
                            break
                        remaining_messages.append((message, msg_type))
                    
                    # Output remaining messages
                    for message, msg_type in remaining_messages:
                        formatted_message = format_message_by_type(message, msg_type)
                        if formatted_message:
                            yield formatted_message
                    break
        
        # Ensure thread is completely finished
        if agent_thread.is_alive():
            agent_thread.join(timeout=2)


# Global stream manager instance
stream_manager = StreamManager()
