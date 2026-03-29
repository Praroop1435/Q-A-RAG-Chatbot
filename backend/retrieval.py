import torch
from typing import List

from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS


def create_vector_store(chunks):
    embeddings = HuggingFaceEmbeddings(
        model_name="BAAI/bge-base-en-v1.5",
        model_kwargs={"device": "mps"}
    )
    return FAISS.from_documents(chunks, embeddings)


def create_retriever(vector_store: FAISS, k: int = 8):
    return vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": k}
    )