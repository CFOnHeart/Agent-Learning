import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from smolagents import CodeAgent
from smolagents import LiteLLMModel
from src.tools.local_store_tool import receipt_query
from rich.console import Console

console = Console()
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
agent = CodeAgent(tools=[receipt_query], model=model, stream_outputs=True)

agent.run("Which guy consumes the most expensive order and which guy pay the most expensive tip?")