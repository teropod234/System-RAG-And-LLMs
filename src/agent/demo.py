"""
Modo demo: ejecuta Tool 1 + Tool 2 sin llamar al LLM.

Útil cuando Gemini devuelve 429 (cuota agotada).
"""

from __future__ import annotations

import re

from src.agent.agent import AgentRunResult
from src.agent.schemas import RecomendacionProducto
from src.agent.tools import buscar_opiniones_usuarios, filtrar_catalogo_productos
from src.db.queries import filter_products, get_product_by_id


def _parse_max_price(consulta: str) -> float | None:
    m = re.search(r"(?:menos de|under|max|máximo|hasta)\s*(\d+)", consulta, re.I)
    if m:
        return float(m.group(1))
    m = re.search(r"(\d+)\s*(?:dólares|dolares|dollars|usd|\$)", consulta, re.I)
    if m:
        return float(m.group(1))
    return None


def _parse_category(consulta: str) -> str | None:
    q = consulta.lower()
    mapping = {
        "audio": "Audio",
        "laptop": "Laptops",
        "portátil": "Laptops",
        "portatil": "Laptops",
        "accessor": "Accessories",
        "accesorio": "Accessories",
        "phone": "Phones",
        "teléfono": "Phones",
        "telefono": "Phones",
    }
    for key, cat in mapping.items():
        if key in q:
            return cat
    return None


def ejecutar_agente_demo(consulta: str) -> AgentRunResult:
    """Orquesta tools manualmente y arma RecomendacionProducto sin Gemini."""
    pasos: list[str] = []

    max_price = _parse_max_price(consulta)
    category = _parse_category(consulta)
    only_rec = "recomend" in consulta.lower()

    pasos.append(
        f"-> [demo] filtrar_catalogo max_price={max_price}, category={category}, "
        f"only_recommended={only_rec}"
    )
    catalogo = filter_products(
        max_price=max_price,
        category=category,
        only_recommended=True if only_rec else None,
        min_stock=1,
        limit=5,
    )
    pasos.append(f"<- [demo] catálogo: {len(catalogo)} productos")

    pasos.append(f"-> [demo] buscar_opiniones_usuarios: {consulta!r}")
    opiniones = buscar_opiniones_usuarios.invoke({"consulta": consulta})
    pasos.append(f"<- [demo] opiniones recuperadas ({len(opiniones)} chars)")

    if not catalogo:
        raise ValueError(
            "Modo demo: ningún producto cumple los filtros. "
            "Prueba otra consulta o revisa MySQL."
        )

    elegido = catalogo[0]
    producto = get_product_by_id(elegido.product_id) or elegido

    pros = []
    if producto.short_review:
        pros.append(producto.short_review)
    if producto.is_recommended:
        pros.append("Marcado como recomendado en el catálogo")
    if producto.rating and producto.rating >= 4.0:
        pros.append(f"Rating alto ({producto.rating})")
    if not pros:
        pros.append("Valoración positiva según datos del catálogo")

    contras = []
    if producto.rating and producto.rating < 4.0:
        contras.append(f"Rating moderado ({producto.rating})")
    if producto.stock < 20:
        contras.append(f"Stock limitado ({producto.stock} unidades)")
    if not contras:
        contras.append("Pocos contras reportados en los datos disponibles")

    confianza = 0.65
    if producto.is_recommended:
        confianza += 0.1
    if producto.rating and producto.rating >= 4.5:
        confianza += 0.1
    confianza = min(confianza, 0.85)

    recomendacion = RecomendacionProducto(
        producto_recomendado=producto.product_name,
        product_id=producto.product_id,
        categoria=producto.category,
        pros_segun_usuarios=pros,
        contras_tecnicos=contras,
        precio_actual=producto.price_usd,
        stock_disponible=producto.stock,
        puntuacion_confianza=round(confianza, 2),
    )

    return AgentRunResult(
        consulta=consulta,
        recomendacion=recomendacion,
        pasos=pasos,
        mensajes=[],
    )
