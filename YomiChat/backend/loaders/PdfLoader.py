from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS

loader = PyPDFLoader("docs/mydocs.pdf")
docs = loader.load()
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, overlap=200)
chunks = splitter.split_documents(docs)

embeddings = OpenAIEmbeddings()
vectordb = FAISS.from_documents(chunks, embeddings)

from smolagents import tool, CodeAgent
import json

@tool
def retrieve_docs(query: str) -> str:
    docs = vectordb.similarity_search(query, k=5)
    outputs = []
    for doc in docs:
        outputs.append({
            "content": doc.page_content,
            "metadata": doc.metadata
        })
    return json.dumps(outputs)
