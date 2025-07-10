import os
from dotenv import load_dotenv
from smolagents import (
    CodeAgent, ToolCallingAgent, ManagedAgent, DuckDuckGoSearchTool, LiteLLMModel
)
from smoltools.jinaai import scrape_page_with_jina_ai

load_dotenv()

# 1. 创建可调用工具的子 Agent
web_agent = ToolCallingAgent(
    tools=[DuckDuckGoSearchTool(), scrape_page_with_jina_ai],
    model=LiteLLMModel(model_id="gpt-4o-mini"),
    max_steps=10,
)

# 2. 封装成 ManagedAgent
managed_web_agent = ManagedAgent(
    agent=web_agent,
    name="search",
    description="Handle web searches and scraping"
)

# 3. 顶层 CodeAgent
manager_agent = CodeAgent(
    tools=[], 
    model=LiteLLMModel(model_id="gpt-4o-mini"),
    managed_agents=[managed_web_agent],
    additional_authorized_imports=["time", "numpy", "pandas"]
)

def chat_with_agent(user_message: str) -> str:
    """
    调用 manager_agent，返回 agent 的回复字符串（支持 Markdown）。
    """
    return manager_agent.run(user_message)
