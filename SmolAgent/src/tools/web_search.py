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
