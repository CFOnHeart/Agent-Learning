"""
Text formatting utilities for cleaning ANSI codes and formatting agent output
"""
import re
from typing import Optional


def clean_ansi_codes(text: str) -> str:
    """
    Clean ANSI escape sequences to make text suitable for web display
    
    Args:
        text: Text potentially containing ANSI escape sequences
        
    Returns:
        Cleaned text without ANSI codes
    """
    if not text:
        return ""
    
    # Remove ANSI color and style codes
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    cleaned = ansi_escape.sub('', text)
    
    # Remove other control characters
    cleaned = re.sub(r'\x1b\[[0-9;]*m', '', cleaned)
    
    # Handle box-drawing characters, convert to simple text format
    box_chars = {
        '╭': '+', '╮': '+', '╰': '+', '╯': '+',
        '─': '-', '│': '|', '┌': '+', '┐': '+',
        '└': '+', '┘': '+', '├': '+', '┤': '+',
        '┬': '+', '┴': '+', '┼': '+',
        '═': '=', '║': '|', '╔': '+', '╗': '+',
        '╚': '+', '╝': '+', '╠': '+', '╣': '+',
        '╦': '+', '╩': '+', '╬': '+'
    }
    
    for unicode_char, replacement in box_chars.items():
        cleaned = cleaned.replace(unicode_char, replacement)
    
    return cleaned


def extract_meaningful_content(text: str) -> str:
    """
    Extract meaningful content from smolagents' decorated output
    
    Args:
        text: Text potentially containing decorative elements
        
    Returns:
        Extracted meaningful content
    """
    cleaned = clean_ansi_codes(text)
    
    # If it's a decorative border, try to extract the content inside
    lines = cleaned.split('\n')
    meaningful_lines = []
    
    for line in lines:
        line = line.strip()
        # Skip lines that are mainly special characters (decorative)
        if len(line) > 0 and not re.match(r'^[+\-=|]+$', line):
            # Remove leading/trailing decorative characters
            content = re.sub(r'^[+|]+\s*', '', line)
            content = re.sub(r'\s*[+|]+$', '', content)
            if content.strip():
                meaningful_lines.append(content.strip())
    
    return '\n'.join(meaningful_lines) if meaningful_lines else cleaned


def format_message_by_type(message: str, msg_type: str) -> str:
    """
    Format message according to its type, cleaning ANSI codes and adding appropriate formatting
    
    Args:
        message: The message to format
        msg_type: Type of message (start, thinking, planning, tool, result, error, etc.)
        
    Returns:
        Formatted message ready for display
    """
    if not message or not message.strip():
        return ""
    
    # First clean ANSI codes and extract meaningful content
    if msg_type in ["info", "result"] and any(char in message for char in ['╭', '╮', '╰', '╯', '─', '│']):
        # This is decorative output box, extract content
        formatted = extract_meaningful_content(message)
    else:
        # Regular message, just clean ANSI codes
        formatted = clean_ansi_codes(message).strip()
    
    if not formatted:
        return ""
    
    # Add appropriate formatting based on message type
    emoji_map = {
        "start": "🚀",
        "thinking": "🤔",
        "planning": "📝",
        "execution": "⚙️",
        "tool": "🔧",
        "success": "✅",
        "result": "📋",
        "error": "❌",
        "info": "💭"
    }
    
    emoji = emoji_map.get(msg_type, "")
    prefix = f"{emoji} " if emoji else ""
    
    if msg_type == "tool":
        return f"{prefix}**Tool Activity:** {formatted}\n\n"
    elif msg_type == "result":
        return f"{prefix}**Result:** {formatted}\n\n"
    elif msg_type == "error":
        return f"{prefix}**Error:** {formatted}\n\n"
    else:
        return f"{prefix}{formatted}\n\n"
