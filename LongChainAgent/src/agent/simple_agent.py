import asyncio
import os

from langgraph.graph import StateGraph, START, END
from src.graph.model.state import State
from src.model.azure_openai_model import get_openai_model
from langgraph.checkpoint.memory import MemorySaver

class Agent:
    def __init__(self):
        self.graph_builder = StateGraph(State)
        self.llm = get_openai_model()
        self._setup_graph()
        self.IMAGE_FILE_PATH = "../../picture/graph_workflow.png"
        self.thread_config = {"configurable": {"thread_id": "1"}}

    def _setup_graph(self):
        self.graph_builder.add_node("chatbot", self.chatbot)
        self.graph_builder.add_edge(START, "chatbot")
        self.graph_builder.add_edge("chatbot", END)

        memory = MemorySaver()
        self.graph = self.graph_builder.compile(checkpointer=memory)

    def chatbot(self, state: State):
        return {"messages": [self.llm.invoke(state["messages"])]}

    def display_graph(self):
        try:
            graph_mermaid_image = self.graph.get_graph().draw_mermaid_png()
            with open(self.IMAGE_FILE_PATH, "wb") as f:
                f.write(graph_mermaid_image)
                print("The picture written into the file: " + os.getcwd() + "/" + self.IMAGE_FILE_PATH)
        except Exception:
            pass

    def stream_graph_updates(self, user_input: str):
        for event in self.graph.stream(
            {"messages": [{"role": "user", "content": user_input}]},
            self.thread_config,
            stream_mode = "values"
        ):
            event["messages"][-1].pretty_print()


    def start_agent(self):
        print("You can start to chat with the agent, if you hope to exit, you can input 'exit', 'quit'")
        while True:
            try:
                user_input = input("User: ")
                if user_input.lower() in ["quit", "exit", "q"]:
                    print("Goodbye!")
                    break
                self.stream_graph_updates(user_input)
                snapshot = self.graph.get_state(self.thread_config)
                print(snapshot)
            except:
                user_input = "What do you know about LangGraph?"
                print("User: " + user_input)
                self.stream_graph_updates(user_input)
                break

if __name__ == "__main__":
    agent = Agent()
    agent.display_graph()
    agent.start_agent()
