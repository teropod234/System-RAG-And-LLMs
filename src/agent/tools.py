"""Tools MySQL (Tool 2) para el agente."""

from __future__ import annotations

from typing import Annotated

from langchain_core.tools import BaseTool, tool

from src.db.queries import (
    check_stock,
    filter_products,
    format_products_for_agent,
    get_product_by_id,
)
from src.model.tools import buscar_opiniones_usuarios


@tool
def filtrar_catalogo_productos(
    max_price: Annotated[
        float | None,
        "Precio máximo en USD. Ejemplo: 600 para productos por debajo de 600$.",
    ] = None,
    min_price: Annotated[float | None, "Precio mínimo en USD."] = None,
    min_stock: Annotated[int, "Stock mínimo requerido."] = 1,
    category: Annotated[
        str | None,
        "Categoría parcial, ej: Audio, Laptops, Accessories.",
    ] = None,
    brand: Annotated[str | None, "Marca parcial, ej: Samsung, Apple."] = None,
    only_recommended: Annotated[
        bool | None,
        "True para quedarte solo con productos marcados como recomendados.",
    ] = None,
    min_rating: Annotated[float | None, "Rating mínimo (0-5)."] = None,
    limit: Annotated[int, "Máximo de productos a devolver."] = 10,
) -> str:
    """
    Filtra el catálogo con precio, stock y criterios exactos desde MySQL.

    Úsala cuando necesites:
    - precio exacto o rangos de precio
    - comprobar stock disponible
    - listar productos de una categoría concreta
    - cruzar restricciones numéricas estrictas

    NO uses esta herramienta para opiniones subjetivas; para eso está buscar_opiniones_usuarios.
    """
    productos = filter_products(
        max_price=max_price,
        min_price=min_price,
        min_stock=min_stock,
        category=category,
        brand=brand,
        only_recommended=only_recommended,
        min_rating=min_rating,
        limit=limit,
    )
    return format_products_for_agent(productos)


@tool
def obtener_producto_por_id(
    product_id: Annotated[str, "ID exacto del producto, ej: AZ1014."],
) -> str:
    """Obtiene precio, stock y datos exactos de un producto por su product_id."""
    producto = get_product_by_id(product_id)
    if producto is None:
        return f"No existe ningún producto con id={product_id}"
    stock_info = check_stock(product_id)
    return (
        f"product_id={producto.product_id}\n"
        f"nombre={producto.product_name}\n"
        f"categoría={producto.category}\n"
        f"precio_usd={producto.price_usd:.2f}\n"
        f"stock={producto.stock}\n"
        f"rating={producto.rating}\n"
        f"marca={producto.brand}\n"
        f"recomendado={producto.is_recommended}\n"
        f"en_stock={stock_info['in_stock']}\n"
        f"reseña={producto.short_review}"
    )


def get_all_agent_tools() -> list[BaseTool]:
    """Tool 1 + Tool 2 listas para el agente."""
    return [
        buscar_opiniones_usuarios,
        filtrar_catalogo_productos,
        obtener_producto_por_id,
    ]
