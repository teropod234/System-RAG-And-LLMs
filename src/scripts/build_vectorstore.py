"""
Paso 4: chunking + embeddings (Gemini) + ChromaDB.

Requisito: GOOGLE_API_KEY en .env

    uv run python src/scripts/build_vectorstore.py
    uv run python src/scripts/build_vectorstore.py --query "portátil buena batería"
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.model.settings import CHROMA_DIR, DEFAULT_CSV, EMBEDDING_MODEL
from src.model.vectorstore import build_vectorstore, semantic_search


def main() -> None:
    parser = argparse.ArgumentParser(description="Construir o consultar el índice Chroma.")
    parser.add_argument(
        "--csv",
        type=Path,
        default=DEFAULT_CSV,
        help="CSV limpio a indexar",
    )
    parser.add_argument(
        "--no-replace",
        action="store_true",
        help="No borrar el índice anterior antes de indexar",
    )
    parser.add_argument(
        "--query",
        type=str,
        default=None,
        help="Probar una búsqueda semántica tras indexar (o sobre índice existente)",
    )
    parser.add_argument(
        "--search-only",
        action="store_true",
        help="Solo buscar, sin reindexar",
    )
    args = parser.parse_args()

    if not args.search_only:
        print(f"Indexando desde: {args.csv}")
        print(f"Modelo embeddings: {EMBEDDING_MODEL}")
        try:
            store = build_vectorstore(csv_path=args.csv, replace=not args.no_replace)
            count = store._collection.count()  # noqa: SLF001
        except Exception as exc:
            msg = str(exc)
            if "404" in msg and "embedding" in msg.lower():
                print(
                    "\nEl modelo de embeddings no está disponible con tu API key.\n"
                    f"Modelo actual: {EMBEDDING_MODEL}\n"
                    "Comprueba en https://ai.google.dev/gemini-api/docs/embeddings\n"
                )
            raise
        print(f"Índice guardado en: {CHROMA_DIR}")
        print(f"Chunks en Chroma: {count}")

    query = args.query
    if query:
        print(f"\nBúsqueda: {query!r}\n")
        results = semantic_search(query)
        for i, doc in enumerate(results, start=1):
            meta = doc.metadata
            print(f"--- Resultado {i} ---")
            print(f"product_id: {meta.get('product_id')} | {meta.get('product_name')}")
            print(doc.page_content[:300])
            print()


if __name__ == "__main__":
    main()
