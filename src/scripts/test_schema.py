"""
Probar el esquema Pydantic del paso C.

    uv run python src/scripts/test_schema.py
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.agent.schemas import RecomendacionProducto, get_response_json_schema


def main() -> None:
    ejemplo = RecomendacionProducto(
        producto_recomendado="Power Bank Model-58",
        product_id="AZ1014",
        categoria="Audio",
        pros_segun_usuarios=[
            "Muy buena relación calidad-precio según reseñas",
            "Los usuarios lo recomiendan de forma consistente",
        ],
        contras_tecnicos=[
            "Rating medio del catálogo inferior a otros competidores en la misma franja",
            "Stock limitado en algunos periodos",
        ],
        precio_actual=321.92,
        stock_disponible=220,
        puntuacion_confianza=0.87,
    )

    print("=== Ejemplo validado ===")
    print(ejemplo.to_json())
    print("\n=== JSON Schema (para el agente) ===")
    import json

    print(json.dumps(get_response_json_schema(), indent=2, ensure_ascii=False)[:800], "...")

    # Simular parseo de respuesta del LLM
    json_llm = """
    {
        "producto_recomendado": "Smart Watch Model-27",
        "product_id": "AZ1010",
        "pros_segun_usuarios": "Excelente valoración y comentarios positivos",
        "contras_tecnicos": ["Precio bajo puede implicar menos funciones premium"],
        "precio_actual": 35.02,
        "puntuacion_confianza": 0.91
    }
    """
    parsed = RecomendacionProducto.from_json(json_llm)
    print("\n=== Parseo desde JSON del LLM ===")
    print(parsed.to_json())


if __name__ == "__main__":
    main()
