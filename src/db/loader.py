"""Carga del CSV limpio en MySQL."""

from __future__ import annotations

import hashlib

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.dialects.mysql import insert

from src.config.paths import raw_data_dir_clean
from src.db.config import get_mysql_settings
from src.db.schema import create_database_if_not_exists, create_tables, products_table


def _stable_stock(product_id: str, minimum: int = 5, maximum: int = 250) -> int:
    """Stock sintético pero estable por producto (misma fila = mismo stock)."""
    digest = hashlib.md5(product_id.encode("utf-8")).hexdigest()
    span = maximum - minimum + 1
    return minimum + int(digest, 16) % span


def _prepare_products_df(csv_path: str | None = None) -> pd.DataFrame:
    path = csv_path or (raw_data_dir_clean() / "Products_clean.csv")
    df = pd.read_csv(path)

    rename_map = {
        "Product_ID": "product_id",
        "Product_Name": "product_name",
        "Category": "category",
        "Price_USD": "price_usd",
        "Rating": "rating",
        "Review_Count": "review_count",
    }
    df = df.rename(columns=rename_map)

    if "stock" not in df.columns:
        df["stock"] = df["product_id"].astype(str).map(_stable_stock)

    df["is_recommended"] = df["is_recommended"].astype(bool)

    columns = [
        "product_id",
        "product_name",
        "category",
        "price_usd",
        "rating",
        "review_count",
        "brand",
        "stock",
        "review_author",
        "short_review",
        "is_recommended",
    ]
    return df[columns]


def load_products_from_csv(csv_path: str | None = None, replace: bool = True) -> int:
    """
    Crea la BD/tabla si no existen y carga productos desde el CSV limpio.

    Returns:
        Número de filas insertadas o actualizadas.
    """
    settings = get_mysql_settings()
    create_database_if_not_exists(settings)

    engine = create_engine(settings.database_url)
    create_tables(engine)

    df = _prepare_products_df(csv_path)
    records = df.to_dict(orient="records")

    if not records:
        return 0

    with engine.begin() as conn:
        if replace:
            conn.execute(products_table.delete())

        stmt = insert(products_table).values(records)
        upsert = stmt.on_duplicate_key_update(
            product_name=stmt.inserted.product_name,
            category=stmt.inserted.category,
            price_usd=stmt.inserted.price_usd,
            rating=stmt.inserted.rating,
            review_count=stmt.inserted.review_count,
            brand=stmt.inserted.brand,
            stock=stmt.inserted.stock,
            review_author=stmt.inserted.review_author,
            short_review=stmt.inserted.short_review,
            is_recommended=stmt.inserted.is_recommended,
        )
        conn.execute(upsert)

    return len(records)
