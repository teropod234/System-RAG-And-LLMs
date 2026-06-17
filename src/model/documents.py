"""Convierte el CSV limpio en documentos para indexar."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from langchain_core.documents import Document

from src.model.settings import DEFAULT_CSV


def _row_to_text(row: pd.Series) -> str:
    parts = [
        f"Producto: {row['product_name']}",
        f"Categoría: {row['category']}",
        f"Marca: {row['brand']}",
        f"Valoración: {row['rating']}",
        f"Reseña ({row['review_author']}): {row['short_review']}",
    ]
    return "\n".join(parts)


def load_documents_from_csv(csv_path: Path | None = None) -> list[Document]:
    path = csv_path or DEFAULT_CSV
    if not path.is_file():
        raise FileNotFoundError(f"No se encontró el CSV limpio: {path}")

    df = pd.read_csv(path)
    rename_map = {
        "Product_ID": "product_id",
        "Product_Name": "product_name",
        "Category": "category",
        "Price_USD": "price_usd",
        "Rating": "rating",
        "Review_Count": "review_count",
    }
    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})

    documents: list[Document] = []
    for _, row in df.iterrows():
        documents.append(
            Document(
                page_content=_row_to_text(row),
                metadata={
                    "product_id": str(row["product_id"]),
                    "product_name": str(row["product_name"]),
                    "category": str(row["category"]),
                    "brand": str(row.get("brand", "")),
                    "price_usd": float(row.get("price_usd", row.get("Price_USD", 0))),
                    "rating": float(row["rating"]),
                    "is_recommended": bool(row.get("is_recommended", False)),
                    "review_author": str(row.get("review_author", "")),
                },
            )
        )
    return documents
