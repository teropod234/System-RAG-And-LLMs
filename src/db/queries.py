"""
Tool 2: consultas estrictas a MySQL (precio, stock, catálogo).

Pensado para que el agente filtre con datos exactos, no por similitud semántica.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from sqlalchemy import and_, create_engine, select
from sqlalchemy.engine import Engine

from src.db.config import get_mysql_settings
from src.db.schema import products_table


@dataclass
class ProductRecord:
    product_id: str
    product_name: str
    category: str
    price_usd: float
    stock: int
    rating: float | None = None
    review_count: int | None = None
    brand: str | None = None
    is_recommended: bool | None = None
    review_author: str | None = None
    short_review: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def get_engine() -> Engine:
    settings = get_mysql_settings()
    return create_engine(settings.database_url)


def _row_to_product(row) -> ProductRecord:
    return ProductRecord(
        product_id=row.product_id,
        product_name=row.product_name,
        category=row.category,
        price_usd=float(row.price_usd),
        stock=int(row.stock),
        rating=float(row.rating) if row.rating is not None else None,
        review_count=int(row.review_count) if row.review_count is not None else None,
        brand=row.brand,
        is_recommended=bool(row.is_recommended) if row.is_recommended is not None else None,
        review_author=row.review_author,
        short_review=row.short_review,
    )


def get_product_by_id(product_id: str) -> ProductRecord | None:
    """
    Devuelve un producto por ID exacto (precio y stock en tiempo real desde MySQL).
    """
    stmt = select(products_table).where(products_table.c.product_id == product_id)
    with get_engine().connect() as conn:
        row = conn.execute(stmt).mappings().first()
    if row is None:
        return None
    return _row_to_product(row)


def filter_products(
    *,
    max_price: float | None = None,
    min_price: float | None = None,
    min_stock: int = 1,
    category: str | None = None,
    brand: str | None = None,
    only_recommended: bool | None = None,
    min_rating: float | None = None,
    limit: int = 20,
) -> list[ProductRecord]:
    """
    Filtro estricto de catálogo.

    Ejemplos:
        filter_products(max_price=500, category="Audio")
        filter_products(min_stock=10, only_recommended=True)
    """
    conditions = [products_table.c.stock >= min_stock]

    if max_price is not None:
        conditions.append(products_table.c.price_usd <= max_price)
    if min_price is not None:
        conditions.append(products_table.c.price_usd >= min_price)
    if category is not None:
        conditions.append(products_table.c.category.ilike(f"%{category.strip()}%"))
    if brand is not None:
        conditions.append(products_table.c.brand.ilike(f"%{brand.strip()}%"))
    if only_recommended is True:
        conditions.append(products_table.c.is_recommended.is_(True))
    elif only_recommended is False:
        conditions.append(products_table.c.is_recommended.is_(False))
    if min_rating is not None:
        conditions.append(products_table.c.rating >= min_rating)

    stmt = (
        select(products_table)
        .where(and_(*conditions))
        .order_by(products_table.c.rating.desc(), products_table.c.price_usd.asc())
        .limit(limit)
    )

    with get_engine().connect() as conn:
        rows = conn.execute(stmt).mappings().all()

    return [_row_to_product(row) for row in rows]


def get_products_by_ids(product_ids: list[str]) -> list[ProductRecord]:
    """Varios productos por lista de IDs (útil tras una búsqueda en Chroma)."""
    if not product_ids:
        return []

    stmt = select(products_table).where(products_table.c.product_id.in_(product_ids))
    with get_engine().connect() as conn:
        rows = conn.execute(stmt).mappings().all()

    by_id = {_row_to_product(row).product_id: _row_to_product(row) for row in rows}
    return [by_id[pid] for pid in product_ids if pid in by_id]


def check_stock(product_id: str, min_stock: int = 1) -> dict[str, Any]:
    """
    Comprueba stock de un producto.

    Returns:
        {"product_id", "in_stock", "stock", "price_usd", "product_name"}
    """
    product = get_product_by_id(product_id)
    if product is None:
        return {
            "product_id": product_id,
            "found": False,
            "in_stock": False,
            "stock": 0,
            "price_usd": None,
            "product_name": None,
        }
    return {
        "product_id": product.product_id,
        "found": True,
        "in_stock": product.stock >= min_stock,
        "stock": product.stock,
        "price_usd": product.price_usd,
        "product_name": product.product_name,
    }


def format_products_for_agent(products: list[ProductRecord]) -> str:
    """Texto legible para devolver al LLM desde la Tool 2."""
    if not products:
        return "No se encontraron productos con esos filtros."

    lines = []
    for p in products:
        rec = "sí" if p.is_recommended else "no"
        lines.append(
            f"- {p.product_id} | {p.product_name} | {p.category} | "
            f"${p.price_usd:.2f} | stock={p.stock} | rating={p.rating} | "
            f"recomendado={rec}"
        )
    return "\n".join(lines)
