"""Configuración del vectorstore (Chroma + Gemini embeddings)."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

from src.config.paths import project_root

load_dotenv(project_root() / ".env")

MODEL_DIR = Path(__file__).resolve().parent
CHROMA_DIR = MODEL_DIR / "chroma_db"
COLLECTION_NAME = "product_reviews"
# text-embedding-004 fue retirado; usar gemini-embedding-001 (ver ai.google.dev/gemini-api/docs/embeddings)
EMBEDDING_MODEL = "models/gemini-embedding-001"
DEFAULT_CSV = project_root() / "src" / "data" / "clean" / "Products_clean.csv"

CHUNK_SIZE = 400
CHUNK_OVERLAP = 50
SEARCH_TOP_K = 5


def get_google_api_key() -> str:
    key = os.getenv("GOOGLE_API_KEY", "").strip()
    if not key:
        raise ValueError(
            "Falta GOOGLE_API_KEY en .env. Obtén una clave en Google AI Studio."
        )
    return key
