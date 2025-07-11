import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import os
from smolagents import CodeAgent
from smolagents import LiteLLMModel

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
agent = CodeAgent(tools=[tavily_search], model=model, stream_outputs=True)

def chat_with_agent(user_message: str) -> str:
    return agent.run(user_message)
