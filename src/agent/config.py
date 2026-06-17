"""Configuración del agente (LLM Gemini)."""

from __future__ import annotations

import os

from dotenv import load_dotenv

from src.config.paths import project_root
from src.model.settings import get_google_api_key

load_dotenv(project_root() / ".env")

DEFAULT_GEMINI_MODEL = "gemini-2.5-flash"


def get_gemini_model_name() -> str:
    return os.getenv("GEMINI_MODEL", DEFAULT_GEMINI_MODEL).strip()
