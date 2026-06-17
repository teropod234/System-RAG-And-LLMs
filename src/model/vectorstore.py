"""Chunking, indexación y búsqueda en ChromaDB."""

from __future__ import annotations

import shutil
from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.model.documents import load_documents_from_csv
from src.model.embeddings import get_embeddings
from src.model.settings import (
    CHROMA_DIR,
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    COLLECTION_NAME,
    SEARCH_TOP_K,
)


def _split_documents(documents: list[Document]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    return splitter.split_documents(documents)


def build_vectorstore(
    csv_path: Path | None = None,
    replace: bool = True,
) -> Chroma:
    """
    Lee el CSV, trocea el texto, genera embeddings con Gemini y guarda en Chroma.
    """
    if replace and CHROMA_DIR.exists():
        shutil.rmtree(CHROMA_DIR)
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)

    raw_docs = load_documents_from_csv(csv_path)
    chunks = _split_documents(raw_docs)
    embeddings = get_embeddings()

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(CHROMA_DIR),
        collection_name=COLLECTION_NAME,
    )
    return vectorstore


def get_vectorstore() -> Chroma:
    """Abre el índice existente (debe haberse construido antes)."""
    if not CHROMA_DIR.exists():
        raise FileNotFoundError(
            f"No existe el índice en {CHROMA_DIR}. "
            "Ejecuta: uv run python src/scripts/build_vectorstore.py"
        )
    return Chroma(
        persist_directory=str(CHROMA_DIR),
        embedding_function=get_embeddings(),
        collection_name=COLLECTION_NAME,
    )


def semantic_search(query: str, k: int = SEARCH_TOP_K) -> list[Document]:
    """Tool 1: búsqueda semántica sobre reseñas indexadas."""
    store = get_vectorstore()
    return store.similarity_search(query, k=k)
