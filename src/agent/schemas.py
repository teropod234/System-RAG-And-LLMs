"""
Paso C — Esquemas Pydantic para la respuesta del agente.

Contrato de salida exigido por el enunciado (InsightMarket AI).
"""

from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel, Field, field_validator


class RecomendacionProducto(BaseModel):
    """Informe ejecutivo estructurado devuelto por el agente."""

    producto_recomendado: str = Field(
        ...,
        description="Nombre del producto recomendado (debe existir en el catálogo).",
        min_length=1,
    )
    pros_segun_usuarios: list[str] = Field(
        ...,
        description="Ventajas mencionadas en reseñas u opiniones de usuarios.",
        min_length=1,
    )
    contras_tecnicos: list[str] = Field(
        ...,
        description="Limitaciones técnicas, riesgos o puntos débiles del producto.",
        min_length=1,
    )
    precio_actual: float = Field(
        ...,
        description="Precio actual en USD según la base de datos relacional (MySQL).",
        ge=0,
    )
    puntuacion_confianza: float = Field(
        ...,
        description="Confianza de la recomendación entre 0.0 (baja) y 1.0 (alta).",
        ge=0.0,
        le=1.0,
    )
    product_id: str | None = Field(
        default=None,
        description="ID del producto en catálogo (opcional pero recomendado para trazabilidad).",
    )
    categoria: str | None = Field(
        default=None,
        description="Categoría del producto recomendado.",
    )
    stock_disponible: int | None = Field(
        default=None,
        description="Stock actual según MySQL.",
        ge=0,
    )

    @field_validator("pros_segun_usuarios", "contras_tecnicos", mode="before")
    @classmethod
    def _coerce_str_list(cls, value: Any) -> list[str]:
        """Acepta lista o un solo string (el LLM a veces devuelve un único párrafo)."""
        if isinstance(value, str):
            return [value.strip()] if value.strip() else []
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        raise TypeError("Se esperaba str o list[str]")

    def to_json(self, *, indent: int = 2) -> str:
        return self.model_dump_json(indent=indent, ensure_ascii=False)

    @classmethod
    def from_json(cls, data: str | dict[str, Any]) -> RecomendacionProducto:
        """Valida JSON crudo del LLM y devuelve el modelo."""
        if isinstance(data, str):
            payload = json.loads(data)
        else:
            payload = data
        return cls.model_validate(payload)


# Prompt de sistema (referencia para el paso D — agente)
SYSTEM_PROMPT_RECOMENDACION = """Eres InsightMarket AI, un analista experto de e-commerce.

Debes usar las herramientas disponibles para:
1) Buscar opiniones de usuarios (búsqueda semántica).
2) Consultar precio, stock y filtros exactos del catálogo (MySQL).

Reglas:
- No inventes precios ni stock: usa siempre los datos de la herramienta de catálogo.
- Basa los pros en reseñas reales recuperadas.
- Los contras pueden combinar limitaciones técnicas y señales negativas de reseñas.
- Responde ÚNICAMENTE con el JSON que cumple el esquema RecomendacionProducto.
"""


def get_response_json_schema() -> dict[str, Any]:
    """Esquema JSON para structured output de LangChain / Gemini."""
    return RecomendacionProducto.model_json_schema()
