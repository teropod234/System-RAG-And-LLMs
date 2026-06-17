"""Embeddings con la API de Gemini."""

from __future__ import annotations

from langchain_core.embeddings import Embeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from src.model.settings import EMBEDDING_MODEL, get_google_api_key


class GeminiRagEmbeddings(Embeddings):
    """Documentos y consultas usan task_type distinto (recomendado por Google)."""

    def __init__(self) -> None:
        api_key = get_google_api_key()
        self._document = GoogleGenerativeAIEmbeddings(
            model=EMBEDDING_MODEL,
            google_api_key=api_key,
            task_type="retrieval_document",
        )
        self._query = GoogleGenerativeAIEmbeddings(
            model=EMBEDDING_MODEL,
            google_api_key=api_key,
            task_type="retrieval_query",
        )

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self._document.embed_documents(texts)

    def embed_query(self, text: str) -> list[float]:
        return self._query.embed_query(text)


def get_embeddings() -> GeminiRagEmbeddings:
    return GeminiRagEmbeddings()
