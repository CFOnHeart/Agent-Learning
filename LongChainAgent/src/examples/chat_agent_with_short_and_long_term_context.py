from src.model.azure_openai_model import get_openai_model
import uuid
from IPython.display import Image, display
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph

# Define a new graph
workflow = StateGraph(state_schema=MessagesState)

# Define a chat model
model = get_openai_model()


# Define the function that calls the model
def call_model(state: MessagesState):
    response = model.invoke(state["messages"])
    # We return a list, because this will get added to the existing list
    return {"messages": response}


# Define the two nodes we will cycle between
workflow.add_edge(START, "model")
workflow.add_node("model", call_model)

memory = MemorySaver()
app = workflow.compile(checkpointer=memory)
thread_id = uuid.uuid4()
config = {"configurable": {"thread_id": thread_id}}

input_message = HumanMessage(content="hi! I'm bob")
for event in app.stream({"messages": [input_message]}, config, stream_mode="values"):
    event["messages"][-1].pretty_print()

# Here, let's confirm that the AI remembers our name!
input_message = HumanMessage(content="what was my name?")
for event in app.stream({"messages": [input_message]}, config, stream_mode="values"):
    event["messages"][-1].pretty_print()

# 使用示例
# print(runnable_with_memory.invoke(
#     {"input": "I'd like to give you some information of myself to help you answer following questions?"},
#     config={"configurable": {"session_id": "test_session"}}
# ))
#
# print(runnable_with_memory.invoke(
#     {"input": "My Name is Bob"},
#     config={"configurable": {"session_id": "test_session"}}
# ))
#
# print(runnable_with_memory.invoke(
#     {"input": "My favorite color is Blue, because that's the color of sky."},
#     config={"configurable": {"session_id": "test_session"}}
# ))
#
# print(runnable_with_memory.invoke(
#     {"input": "I'm from Suzhou, a city of JiangSu province in China"},
#     config={"configurable": {"session_id": "test_session"}}
# ))
#
# print(runnable_with_memory.invoke(
#     {"input": "Do you know what's my name"},
#     config={"configurable": {"session_id": "test_session"}}
# ))
#
# print(runnable_with_memory.invoke(
#     {"input": "Do you know which country I'm from"},
#     config={"configurable": {"session_id": "test_session"}}
# ))