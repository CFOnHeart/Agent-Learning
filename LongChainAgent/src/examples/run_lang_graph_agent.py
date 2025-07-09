import asyncio
import os
from typing import Annotated

from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from src.graph.model.state import State

from src.graph.tool_node import BasicToolNode, route_tools
from src.model.azure_openai_model import get_openai_model


# The first argument is the unique node name
# The second argument is the function or object that will be called whenever
# the node is used.

graph_builder = StateGraph(State)

llm = get_openai_model()
# 2. Add tools - web search
# https://langchain-ai.github.io/langgraph/tutorials/get-started/2-add-tools/#1-install-the-search-engine
from src.tools.subclass.GoogleSearch import GoogleSearchTool
from src.tools.subclass.web_search import BigModelSearchTool
from src.tools.subclass.math import AddCalculatorTool, MultiplyCalculatorTool
#tool = google_search_tool = GoogleSearchTool(api_key=os.environ.get("GOOGLE_SEARCH_API_KEY"), cse_id=os.environ.get("GOOGLE_SEARCH_CSE_ID"))
#tool = BigModelSearchTool(api_key=os.environ["BIGMODEL_API_KEY"])
add_math_tool = AddCalculatorTool()
mul_math_tool = MultiplyCalculatorTool()
tools = [AddCalculatorTool(), MultiplyCalculatorTool()]
llm_with_tools = llm.bind_tools(tools)

def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

tool_node = BasicToolNode(tools=tools)
graph_builder.add_node("tools", tool_node)
graph_builder.add_node("chatbot", chatbot)

graph_builder.add_edge(START, "chatbot")
graph_builder.add_conditional_edges(
    "chatbot",
    route_tools,
    # The following dictionary lets you tell the graph to interpret the condition's outputs as a specific node
    # It defaults to the identity function, but if you
    # want to use a node named something else apart from "tools",
    # You can update the value of the dictionary to something else
    # e.g., "tools": "my_tools"
    {"tools": "tools", END: END},
)
graph_builder.add_edge("chatbot", END)

graph = graph_builder.compile()

from IPython.display import Image, display

try:
    graph_mermaid_image = graph.get_graph().draw_mermaid_png()
    image_file = "../../picture/graph_workflow.png"
    with open("../../picture/graph_workflow.png", "wb") as f:
        f.write(graph_mermaid_image)
        print ("The picture written into the file: " + os.getcwd() + "/" + image_file)

    display(Image(graph_mermaid_image))
except Exception:
    # This requires some extra dependencies and is optional
    pass

def stream_graph_updates(user_input: str):
    for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)


def start_agent():
    print ("You can start to chat with the agent, if you hope to exit, you can input 'exit', 'quit'")
    while True:
        try:
            user_input = input("User: ")
            if user_input.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break
            stream_graph_updates(user_input)
        except:
            # fallback if input() is not available
            user_input = "What do you know about LangGraph?"
            print("User: " + user_input)
            stream_graph_updates(user_input)
            break


# print(add_math_tool.invoke("what is the benefit of MCP (Model Context Protocol)?"))

start_agent()