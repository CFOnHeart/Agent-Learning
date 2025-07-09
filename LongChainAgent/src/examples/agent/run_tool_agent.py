from src.agent.tool_agent import ToolAgent
from src.tools.subclass.math import AddCalculatorTool, MultiplyCalculatorTool
from langchain_tavily import TavilySearch
from dotenv import load_dotenv

load_dotenv()

tools = [AddCalculatorTool(), MultiplyCalculatorTool(), TavilySearch(max_results=2)]
agent = ToolAgent(tools)
agent.stream_graph_updates("What is 3 * 12?")
agent.stream_graph_updates("What is 3 + 12?")
agent.stream_graph_updates("What's the weather of Shanghai today?") # go to TavilySearch tool

