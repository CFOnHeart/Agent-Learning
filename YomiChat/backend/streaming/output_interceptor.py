"""
Output interceptor for capturing agent stdout/stderr
"""
import sys
import re
from typing import Callable, Optional
from .text_formatter import clean_ansi_codes, extract_meaningful_content


class OutputInterceptor:
    """Intercepts stdout/stderr to capture agent output for streaming"""
    
    def __init__(self, original_stdout, stream_callback: Optional[Callable] = None):
        self.original_stdout = original_stdout
        self.captured_output = []
        self.stream_callback = stream_callback
        
    def write(self, text):
        """Write method called by redirected stdout"""
        # Send output to original stdout (keep console display)
        self.original_stdout.write(text)
        
        # Analyze and stream the output if callback is set
        if text.strip() and self.stream_callback:
            self.analyze_and_stream(text.strip())
            
    def flush(self):
        """Flush the output buffer"""
        self.original_stdout.flush()
        
    def analyze_and_stream(self, text: str):
        """Analyze agent output and stream it with appropriate formatting"""
        # First clean ANSI codes
        cleaned_text = clean_ansi_codes(text)
        
        if not cleaned_text.strip():
            return
            
        text_lower = cleaned_text.lower()
        
        # Detect smolagents' special output formats
        if any(char in text for char in ['╭', '╮', '╰', '╯', '─', '│']):
            # This is decorative frame output, extract content
            meaningful_content = extract_meaningful_content(text)
            if meaningful_content and len(meaningful_content) > 5:
                # Check if it's "New run" start
                if 'new run' in meaningful_content.lower():
                    self.stream_callback(f"Starting new task: {meaningful_content}", "start")
                else:
                    self.stream_callback(meaningful_content, "info")
        # Detect different types of agent activities
        elif any(keyword in text_lower for keyword in ['thinking', 'analyzing', 'considering']):
            self.stream_callback(cleaned_text, "thinking")
        elif any(keyword in text_lower for keyword in ['calling', 'using tool', 'executing', 'tool call']):
            self.stream_callback(cleaned_text, "tool")
        elif any(keyword in text_lower for keyword in ['planning', 'strategy', 'approach']):
            self.stream_callback(cleaned_text, "planning")
        elif any(keyword in text_lower for keyword in ['result', 'output', 'response']):
            self.stream_callback(cleaned_text, "result")
        elif any(keyword in text_lower for keyword in ['error', 'failed', 'exception']):
            self.stream_callback(cleaned_text, "error")
        else:
            # If output is long enough and meaningful, consider it useful information
            if len(cleaned_text) > 15 and not re.match(r'^[+\-=|]+$', cleaned_text):
                self.stream_callback(cleaned_text, "info")
