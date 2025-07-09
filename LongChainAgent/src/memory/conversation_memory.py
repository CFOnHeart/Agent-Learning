from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
    trim_messages,
)
from langchain_core.messages.utils import count_tokens_approximately
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from src.model.azure_openai_model import get_openai_model

trimmer = trim_messages(
    # Keep the last <= n_count tokens of the messages.
    strategy="last",
    # Remember to adjust based on your model
    # or else pass a custom token_counter
    token_counter=count_tokens_approximately,
    # Most chat models expect that chat history starts with either:
    # (1) a HumanMessage or
    # (2) a SystemMessage followed by a HumanMessage
    # Remember to adjust based on the desired conversation
    # length
    max_tokens=1024,
    # Most chat models expect that chat history starts with either:
    # (1) a HumanMessage or
    # (2) a SystemMessage followed by a HumanMessage
    start_on="human",
    # Most chat models expect that chat history ends with either:
    # (1) a HumanMessage or
    # (2) a ToolMessage
    end_on=("human", "tool"),
    # Usually, we want to keep the SystemMessage
    # if it's present in the original history.
    # The SystemMessage has special instructions for the model.
    include_system=True,
    allow_partial=False,
)
llm = get_openai_model()

messages = [
    SystemMessage("you're a good assistant.")
]

chat_history = InMemoryChatMessageHistory(messages=messages[:-1])
def dummy_get_session_history(session_id):
    if session_id != "1":
        return InMemoryChatMessageHistory()
    return chat_history

chain = trimmer | llm
chain_with_history = RunnableWithMessageHistory(chain, dummy_get_session_history)
print(chain_with_history.invoke(
    [HumanMessage("My name is Bob")],
    config={"configurable": {"session_id": "1"}},
))
print(chain_with_history.invoke(
    [HumanMessage("I like color light green a lot, and I hope you can like it as well")],
    config={"configurable": {"session_id": "1"}},
))
print(chain_with_history.invoke(
    [HumanMessage("Do you what's my name")],
    config={"configurable": {"session_id": "1"}},
))
print(chain_with_history.invoke(
    [HumanMessage("Do you know what's my favorite color")],
    config={"configurable": {"session_id": "1"}},
))