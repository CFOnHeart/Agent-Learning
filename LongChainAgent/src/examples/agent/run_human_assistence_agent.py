from src.agent.human_assistence_agent import HumanAssistenceAgent
from dotenv import load_dotenv
from src.tools.simple.human_assistance import personal_info_update_human_assistance

load_dotenv()

agent = HumanAssistenceAgent([personal_info_update_human_assistance])

# memory save in the simple agent
agent.stream_graph_updates("Can you look up when LangGraph was released? When you have the answer, use the human_assistance tool for review.")
agent.human_command_stream_graph_updates()


