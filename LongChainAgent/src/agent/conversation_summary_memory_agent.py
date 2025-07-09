import os
from langgraph.graph import StateGraph, START, END
from src.graph.model.state import State
from src.model.azure_openai_model import get_azure_openai_model
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai.embeddings import AzureOpenAIEmbeddings
from src.embeddings.azure_openai_embeddings import get_azure_openai_embeddings

class ConversationSummaryAgent:
    def __init__(self):
        self.graph_builder = StateGraph(State)
        self.embeddings = get_azure_openai_embeddings()
        self.llm = get_azure_openai_model()
        self.memory_store = InMemoryVectorStore(self.embeddings)
        self._setup_graph()
        self.IMAGE_FILE_PATH = "../../picture/graph_workflow.png"
        self.thread_config = {"configurable": {"thread_id": "1"}}

    def _setup_graph(self):
        self.graph_builder.add_node("chatbot", self.chatbot)
        self.graph_builder.add_edge(START, "chatbot")
        self.graph_builder.add_edge("chatbot", END)
        self.graph = self.graph_builder.compile()

    def chatbot(self, state: State):
        user_input = state.get("messages")[-1].content
        combined_messages = self._retrieve_memories(user_input) + user_input
        response = self.llm.invoke(combined_messages)
        self._save_memory(user_input, response)
        return {"messages": [response]}

    def _save_memory(self, user_input, response):
        self.memory_store.add_texts(["user_input:" + user_input])
        self.memory_store.add_texts(["response:" + response.content])

    def _retrieve_memories(self, user_input):
        memories = self.memory_store.search(user_input, search_type='similarity')
        return "\n".join([memory.page_content for memory in memories])

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
            except:
                user_input = "What do you know about LangGraph?"
                print("User: " + user_input)
                self.stream_graph_updates(user_input)
                break

if __name__ == "__main__":
    agent = ConversationSummaryAgent()
    agent.display_graph()
    agent.start_agent()
