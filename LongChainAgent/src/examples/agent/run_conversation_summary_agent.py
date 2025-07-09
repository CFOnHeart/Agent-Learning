from src.agent.conversation_summary_memory_agent import ConversationSummaryAgent
from dotenv import load_dotenv

load_dotenv()

agent = ConversationSummaryAgent()

# memory save in the simple agent
agent.stream_graph_updates("Hi, my name is Jun from China?")
agent.stream_graph_updates("Do you remember my name?")
agent.stream_graph_updates("Could you recommend some popular cities of my country for travling?")

