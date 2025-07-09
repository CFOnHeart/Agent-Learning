import getpass
import os

try:
    # load environment variables from .env file (requires `python-dotenv`)
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

print (os.environ.get("OPENAI_API_KEY"))

from langchain.chat_models import init_chat_model

model = init_chat_model("gpt-4.1", model_provider="openai")

from langchain_core.prompts import ChatPromptTemplate

system_template = "Translate the following from English into {language}"

prompt_template = ChatPromptTemplate.from_messages(
    [("system", system_template), ("user", "{text}")]
)
prompt = prompt_template.invoke({"language": "Italian", "text": "I'm so happy today, because it's a sunny day!"})

for token in model.stream(prompt):
    print(token.content, end = "")