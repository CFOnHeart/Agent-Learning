import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import os
from smolagents import CodeAgent
from smolagents import LiteLLMModel
import io
import contextlib
import threading
import time
import re
from queue import Queue, Empty

try:
    # load environment variables from .env file (requires `python-dotenv`)
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass
print(os.environ.get("AZURE_API_KEY"))
print(os.environ.get("AZURE_API_BASE"))


import os
from dotenv import load_dotenv
from smolagents import CodeAgent, WebSearchTool, InferenceClientModel, tool
from smolagents import LiteLLMModel
from tavily import TavilyClient

try:
    # load environment variables from .env file (requires `python-dotenv`)
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


@tool
def tavily_search(query: str) -> str:
    """
    Search the web using Tavily API.

    Args:
        query: The search query string

    Returns:
        Search results as a formatted string
    """
    client = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))
    response = client.search(query, max_results=4)

    results = []
    for result in response.get('results', []):
        results.append(
            f"Title: {result.get('title', '')}\nURL: {result.get('url', '')}\nContent: {result.get('content', '')}\n")

    return "\n".join(results)


model = LiteLLMModel(
                    model_id="azure/gpt-4-32k",
                    api_key=os.environ.get("AZURE_API_KEY"),
                    api_base=os.environ.get("AZURE_API_BASE")
                )

# 创建标准的CodeAgent
agent = CodeAgent(tools=[tavily_search], model=model, stream_outputs=True)

# 全局变量用于stream回调
_stream_callback = None

def set_stream_callback(callback):
    """设置全局stream回调"""
    global _stream_callback
    _stream_callback = callback

def stream_message(message, msg_type="info"):
    """发送stream消息"""
    if _stream_callback:
        _stream_callback(message, msg_type)

# 创建一个输出拦截器来捕获agent的打印输出
class OutputInterceptor:
    def __init__(self, original_stdout):
        self.original_stdout = original_stdout
        self.captured_output = []
        
    def write(self, text):
        # 将输出发送到原始stdout（保持控制台显示）
        self.original_stdout.write(text)
        
        # 同时分析并stream化输出
        if text.strip():
            self.analyze_and_stream(text.strip())
            
    def flush(self):
        self.original_stdout.flush()
        
    def analyze_and_stream(self, text):
        """分析agent输出并以适当的格式stream"""
        # 首先清理ANSI代码
        cleaned_text = clean_ansi_codes(text)
        
        if not cleaned_text.strip():
            return
            
        text_lower = cleaned_text.lower()
        
        # 检测smolagents的特殊输出格式
        if any(char in text for char in ['╭', '╮', '╰', '╯', '─', '│']):
            # 这是一个装饰性框架输出，提取内容
            meaningful_content = extract_meaningful_content(text)
            if meaningful_content and len(meaningful_content) > 5:
                # 检查是否是"New run"开始
                if 'new run' in meaningful_content.lower():
                    stream_message(f"Starting new task: {meaningful_content}", "start")
                else:
                    stream_message(meaningful_content, "info")
        # 检测不同类型的agent活动
        elif any(keyword in text_lower for keyword in ['thinking', 'analyzing', 'considering']):
            stream_message(cleaned_text, "thinking")
        elif any(keyword in text_lower for keyword in ['calling', 'using tool', 'executing', 'tool call']):
            stream_message(cleaned_text, "tool")
        elif any(keyword in text_lower for keyword in ['planning', 'strategy', 'approach']):
            stream_message(cleaned_text, "planning")
        elif any(keyword in text_lower for keyword in ['result', 'output', 'response']):
            stream_message(cleaned_text, "result")
        elif any(keyword in text_lower for keyword in ['error', 'failed', 'exception']):
            stream_message(cleaned_text, "error")
        else:
            # 如果输出足够长且有意义，认为是有用的信息
            if len(cleaned_text) > 15 and not re.match(r'^[+\-=|]+$', cleaned_text):
                stream_message(cleaned_text, "info")

# Monkey patch agent的关键方法来捕获思考过程
original_agent_run = agent.run

def enhanced_agent_run(task, **kwargs):
    """增强的agent run方法，捕获思考过程"""
    # 设置输出拦截器
    original_stdout = sys.stdout
    interceptor = OutputInterceptor(original_stdout)
    
    try:
        stream_message(f"� **Starting task:** {task}", "start")
        
        # 重定向stdout到我们的拦截器
        sys.stdout = interceptor
        
        # 添加一些预期的思考步骤
        stream_message("🤔 **Initializing agent reasoning...**", "thinking")
        time.sleep(0.5)
        
        # 运行原始方法
        result = original_agent_run(task, **kwargs)
        
        stream_message("✅ **Task completed successfully!**", "success")
        
        return result
        
    except Exception as e:
        stream_message(f"❌ **Error during execution:** {str(e)}", "error")
        raise
    finally:
        # 恢复原始stdout
        sys.stdout = original_stdout

# 应用monkey patch
agent.run = enhanced_agent_run

# 简化的流捕获类
class SimpleStreamCapture:
    def __init__(self):
        self.messages = Queue()
        
    def add_message(self, message, msg_type="info"):
        self.messages.put((message, msg_type))
        
    def get_message(self):
        try:
            return self.messages.get_nowait()
        except Empty:
            return None, None

def chat_with_agent(user_message: str) -> str:
    return agent.run(user_message)

def chat_with_agent_stream(user_message: str):
    """
    Generator function that yields streaming chunks from the agent including all thinking process
    """
    capture = SimpleStreamCapture()
    
    # 设置全局流式回调
    set_stream_callback(capture.add_message)
    
    def run_agent_in_thread():
        """在单独线程中运行agent"""
        try:
            # 运行agent，这会触发我们的monkey patched方法
            result = agent.run(user_message)
            
            # 添加最终结果
            capture.add_message(f"**Final Answer:**\n\n{result}", "result")
            capture.add_message("__FINISHED__", "end")
            
        except Exception as e:
            capture.add_message(f"❌ **Unexpected error:** {str(e)}", "error")
            capture.add_message("__FINISHED__", "end")
        finally:
            # 清除回调
            set_stream_callback(None)
    
    # 启动agent在后台线程运行
    agent_thread = threading.Thread(target=run_agent_in_thread)
    agent_thread.daemon = True
    agent_thread.start()
    
    # 实时stream输出
    while True:
        message, msg_type = capture.get_message()
        if message:
            if message == "__FINISHED__":
                break
            else:
                # 根据消息类型格式化输出
                formatted_message = format_message_by_type(message, msg_type)
                if formatted_message:
                    yield formatted_message
        else:
            time.sleep(0.1)  # 短暂等待新消息
            
            # 如果线程结束，获取所有剩余消息
            if not agent_thread.is_alive():
                # 获取剩余消息
                remaining_messages = []
                while True:
                    message, msg_type = capture.get_message()
                    if not message:
                        break
                    if message == "__FINISHED__":
                        break
                    remaining_messages.append((message, msg_type))
                
                # 输出剩余消息
                for message, msg_type in remaining_messages:
                    formatted_message = format_message_by_type(message, msg_type)
                    if formatted_message:
                        yield formatted_message
                break
    
    # 确保线程完全结束
    if agent_thread.is_alive():
        agent_thread.join(timeout=2)

def clean_ansi_codes(text: str) -> str:
    """
    清理ANSI转义序列，使文本适合在网页中显示
    """
    if not text:
        return ""
    
    # 移除ANSI颜色和样式代码
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    cleaned = ansi_escape.sub('', text)
    
    # 移除其他控制字符
    cleaned = re.sub(r'\x1b\[[0-9;]*m', '', cleaned)
    
    # 处理box-drawing characters，将其转换为简单的文本格式
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
    从smolagents的输出中提取有意义的内容
    """
    cleaned = clean_ansi_codes(text)
    
    # 如果是装饰性的边框，尝试提取中间的内容
    lines = cleaned.split('\n')
    meaningful_lines = []
    
    for line in lines:
        line = line.strip()
        # 跳过主要由特殊字符组成的装饰行
        if len(line) > 0 and not re.match(r'^[+\-=|]+$', line):
            # 移除行首的装饰字符
            content = re.sub(r'^[+|]+\s*', '', line)
            content = re.sub(r'\s*[+|]+$', '', content)
            if content.strip():
                meaningful_lines.append(content.strip())
    
    return '\n'.join(meaningful_lines) if meaningful_lines else cleaned

def format_message_by_type(message: str, msg_type: str) -> str:
    """
    根据消息类型格式化消息，清理ANSI代码并添加适当格式
    """
    if not message or not message.strip():
        return ""
    
    # 首先清理ANSI代码和提取有意义的内容
    if msg_type in ["info", "result"] and any(char in message for char in ['╭', '╮', '╰', '╯', '─', '│']):
        # 这是一个装饰性的输出框，提取其中的内容
        formatted = extract_meaningful_content(message)
    else:
        # 普通消息，只清理ANSI代码
        formatted = clean_ansi_codes(message).strip()
    
    if not formatted:
        return ""
    
    # 根据消息类型添加特殊格式
    if msg_type == "start":
        return f"🚀 {formatted}\n\n"
    elif msg_type == "thinking":
        return f"🤔 {formatted}\n\n"
    elif msg_type == "planning":
        return f"📝 {formatted}\n\n"
    elif msg_type == "execution":
        return f"⚙️ {formatted}\n\n"
    elif msg_type == "tool":
        return f"🔧 **Tool Activity:** {formatted}\n\n"
    elif msg_type == "success":
        return f"✅ {formatted}\n\n"
    elif msg_type == "result":
        return f"📋 **Result:** {formatted}\n\n"
    elif msg_type == "error":
        return f"❌ **Error:** {formatted}\n\n"
    elif msg_type == "info":
        return f"💭 {formatted}\n\n"
    else:
        return f"{formatted}\n\n"
