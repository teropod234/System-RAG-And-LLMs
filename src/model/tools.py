"""
Tools de LangChain para el agente RAG.

Paso B — Tool 1: búsqueda semántica en Chroma (opiniones de usuarios).
"""

from __future__ import annotations

from langchain_core.documents import Document
from langchain_core.tools import BaseTool, tool

from src.model.settings import SEARCH_TOP_K
from src.model.vectorstore import semantic_search


def _format_review_hits(documents: list[Document]) -> str:
    if not documents:
        return "No se encontraron reseñas u opiniones relevantes para esa consulta."

    blocks: list[str] = []
    for i, doc in enumerate(documents, start=1):
        meta = doc.metadata
        product_id = meta.get("product_id", "desconocido")
        product_name = meta.get("product_name", "sin nombre")
        category = meta.get("category", "")
        rating = meta.get("rating", "")
        brand = meta.get("brand", "")
        recommended = meta.get("is_recommended", "")
        author = meta.get("review_author", "")

        blocks.append(
            f"[{i}] product_id={product_id}\n"
            f"    producto: {product_name}\n"
            f"    categoría: {category} | marca: {brand} | rating: {rating}\n"
            f"    autor reseña: {author} | recomendado: {recommended}\n"
            f"    texto: {doc.page_content.strip()}"
        )
    return "\n\n".join(blocks)


@tool
def buscar_opiniones_usuarios(consulta: str) -> str:
    """
    Busca en reseñas y opiniones de usuarios usando similitud semántica (ChromaDB).

    Úsala cuando la pregunta del usuario hable de:
    - experiencias de uso, calidad percibida, satisfacción
    - si un producto es recomendable o no según usuarios
    - pros/contras mencionados en reseñas
    - comparaciones subjetivas (bueno, malo, excelente, decepcionante…)

    NO uses esta herramienta para precio exacto, stock o filtros numéricos estrictos;
    para eso existe filtrar_catalogo_productos.

    Args:
        consulta: Pregunta o tema a buscar en lenguaje natural (en español o inglés).

    Returns:
        Fragmentos de reseñas relevantes con product_id y contexto del producto.
    """
    documentos = semantic_search(consulta, k=SEARCH_TOP_K)
    return _format_review_hits(documentos)


def get_semantic_search_tool() -> BaseTool:
    """Devuelve la Tool 1 lista para registrar en un agente LangChain."""
    return buscar_opiniones_usuarios


def get_rag_tools_step_b() -> list[BaseTool]:
    """Lista de tools del paso B (solo Chroma)."""
    return [buscar_opiniones_usuarios]
