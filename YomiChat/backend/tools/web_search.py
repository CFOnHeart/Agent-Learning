"""
Web search tool using Tavily API
"""
import os
from smolagents import tool
from config.settings import settings

try:
    from tavily import TavilyClient
except ImportError:
    TavilyClient = None


@tool
def tavily_search(query: str) -> str:
    """
    Search the web using Tavily API.

    Args:
        query: The search query string

    Returns:
        Search results as a formatted string
    """
    if not TavilyClient:
        return "Tavily client not available. Please install the tavily package."
    
    if not settings.has_tavily_config:
        return "Tavily API key not configured. Please set TAVILY_API_KEY environment variable."
    
    try:
        client = TavilyClient(api_key=settings.tavily_api_key)
        response = client.search(query, max_results=4)

        results = []
        for result in response.get('results', []):
            results.append(
                f"Title: {result.get('title', '')}\n"
                f"URL: {result.get('url', '')}\n"
                f"Content: {result.get('content', '')}\n"
            )

        return "\n".join(results) if results else "No search results found."
        
    except Exception as e:
        return f"Search error: {str(e)}"
