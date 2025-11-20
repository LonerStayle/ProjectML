from langchain_postgres import PGVector
from langchain_openai import OpenAIEmbeddings
from db.config import CONNECTION_URL, DBCollectionName
from langchain_core.documents import Document
from typing import List
from langchain_openai import OpenAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from enum.EmbeddingModel import EmbeddingModel


class DBRepository:
    def __init__(
        self,
        collection_name: DBCollectionName,
        embedding_model=EmbeddingModel,
    ):
        self.store = PGVector(
            connection_string=CONNECTION_URL,
            collection_name=collection_name,
            embedding_function=resolve_embedding(embedding_model),
        )

    def add_documents(self, docs:List[Document]):
        self.store.add_documents(docs)

    def search(self, query: str, k=5):
        return self.store.similarity_search(query, k=k)




def resolve_embedding(model: EmbeddingModel):
    """모델 Enum → 실제 Embedding 객체로 변환"""

    # OpenAI 계열
    if model in {
        EmbeddingModel.TEXT_EMBEDDING_3_LARGE,
        EmbeddingModel.TEXT_EMBEDDING_3_MEDIUM,
        EmbeddingModel.TEXT_EMBEDDING_3_SMALL,
    }:
        return OpenAIEmbeddings(model=model.value)

    # HuggingFace 계열
    if model in {
        EmbeddingModel.BGE_M3,
        EmbeddingModel.BGE_UPSKYY_KOREAN,
    }:
        return HuggingFaceEmbeddings(model_name=model.value)

    raise ValueError(f"Unknown embedding model: {model}")