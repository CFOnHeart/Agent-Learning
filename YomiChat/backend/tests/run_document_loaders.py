from tools.retrieve_docs import retrieve_docs
from smolagents import CodeAgent, InferenceClientModel, LiteLLMModel
from config import settings
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

if not settings.has_azure_config:
    raise ValueError("Azure configuration is required. Please set AZURE_API_KEY and AZURE_API_BASE.")

# Create the model
model = LiteLLMModel(
    model_id=settings.model_id,
    api_key=settings.azure_api_key,
    api_base=settings.azure_api_base
)

agent = CodeAgent(
    tools=[retrieve_docs],
    model=model,
    max_steps=5
)

agent.run("""
用户的问题是:
What is the ResNet Mean? What's benefit of it?

为了回答问题，首先调用 retrieve_docs("<<用户问题>>")；
如果返回的列表中有相应内容，就基于这些文档内容总结答案，
并展示每个文档的 source；
否则，请使用你原有的知识回答这个问题。
""")
