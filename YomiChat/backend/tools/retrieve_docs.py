import os

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.vectorstores import FAISS

loader = PyPDFLoader("C:/Users/ganjun/Downloads/resnet-arxiv.pdf")
docs = loader.load()
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separators=["\n\n", "\n", " ", "。"],
    length_function=len,
    is_separator_regex=False
)
chunks = text_splitter.split_documents(docs)
embeddings = AzureOpenAIEmbeddings(
    deployment="text-embedding-ada-002",
    model="text-embedding-ada-002",
)
vectordb = FAISS.from_documents(chunks, embeddings)

from smolagents import tool, CodeAgent
import json
@tool
def retrieve_docs(query: str) -> list:
    """
        Retrieve relevant document chunks based on the query.

        Args:
            query: A string containing the user's question.

        Returns:
            A list of dictionaries, each with:
              - content: the chunk text (str)
              - metadata: metadata dict with keys like 'source', 'page', 'chunk'
    """
    docs = vectordb.similarity_search(query, k=5)
    return [
        {"content": doc.page_content, "metadata": doc.metadata}
        for doc in docs
    ]
