import os

from langgraph.graph import StateGraph, START, END
from src.graph.model.state import PersonState
from src.graph.tool_node import BasicToolNode, route_tools
from src.model.azure_openai_model import get_openai_model
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command
from langgraph.prebuilt import ToolNode, tools_condition

class HumanAssistenceAgent:
    """
    An agent that assists humans with their tasks using a state graph.
    Please pass at least one human assistance tool inside the tools to the constructor.
    """
    def __init__(self, tools=None):
        self.graph_builder = StateGraph(PersonState)
        self.llm = get_openai_model()
        self.tools = tools
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        self._setup_graph()
        self.IMAGE_FILE_PATH = "../../picture/human_assistence_graph_workflow.png"
        self.thread_config = {"configurable": {"thread_id": "1"}}

    def _setup_graph(self):
        tool_node = ToolNode(tools=self.tools)
        self.graph_builder.add_node("tools", tool_node)
        self.graph_builder.add_node("chatbot", self.chatbot)
        self.graph_builder.add_edge(START, "chatbot")
        self.graph_builder.add_conditional_edges(
            "chatbot",
            tools_condition,
        )
        self.graph_builder.add_edge("tools","chatbot")

        memory = MemorySaver()
        self.graph = self.graph_builder.compile(checkpointer=memory)

    def chatbot(self, state: PersonState):
        message = self.llm_with_tools.invoke(state["messages"])
        assert (len(message.tool_calls) <= 1)
        return {"messages": [self.llm_with_tools.invoke(state["messages"])]}

    def display_graph(self):
        try:
            graph_mermaid_image = self.graph.get_graph().draw_mermaid_png()
            with open(self.IMAGE_FILE_PATH, "wb") as f:
                f.write(graph_mermaid_image)
                print("The picture written into the file: " + os.getcwd() + "/" + self.IMAGE_FILE_PATH)
        except Exception:
            pass

    def human_command_stream_graph_updates(self):
        human_command = Command(
            resume={
                "name": "LangGraph",
                "birthday": "Jan 17, 2024",
            },
        )

        for event in self.graph.stream(
            human_command,
            self.thread_config,
            stream_mode = "values"
        ):
            if "messages" in event:
                event["messages"][-1].pretty_print()

    def stream_graph_updates(self, user_input: str):
        for event in self.graph.stream(
            {"messages": [{"role": "user", "content": user_input}]},
            self.thread_config,
            stream_mode = "values"
        ):
            if "messages" in event:
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