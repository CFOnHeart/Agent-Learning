import os
from dotenv import load_dotenv
from smolagents import CodeAgent
from smolagents import LiteLLMModel
from langchain_tavily import TavilySearch
from src.tools.web_search import tavily_search
from src.tools.local_store_tool import receipt_query
try:
    # load environment variables from .env file (requires `python-dotenv`)
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass
print(os.environ.get("AZURE_API_KEY"))
print(os.environ.get("AZURE_API_BASE"))

model = LiteLLMModel(
                    model_id="azure/gpt-4-32k",
                    api_key=os.environ.get("AZURE_API_KEY"),
                    api_base=os.environ.get("AZURE_API_BASE")
                )
agent = CodeAgent(tools=[tavily_search], model=model, stream_outputs=True)

agent.run("what was the result of 2024 US elections?")