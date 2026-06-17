"""
Paso D — ejecutar el agente InsightMarket desde terminal.

Requisitos: GOOGLE_API_KEY, MySQL cargado, Chroma indexado.

    uv run python src/scripts/run_agent.py
    uv run python src/scripts/run_agent.py --query "audio recomendable menos de 600 dolares"
    uv run python src/scripts/run_agent.py --demo   # sin Gemini (cuota 429)
    uv run python src/scripts/test_gemini_api.py    # diagnosticar API key
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.agent.agent import ejecutar_agente
from src.agent.config import get_gemini_model_name
from src.agent.demo import ejecutar_agente_demo


def main() -> None:
    parser = argparse.ArgumentParser(description="InsightMarket AI — agente RAG")
    parser.add_argument(
        "--query",
        type=str,
        default=(
            "Busco un producto de audio recomendable por usuarios "
            "y que cueste menos de 600 dólares"
        ),
        help="Consulta del usuario",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Modo sin LLM (tools + JSON manual). Útil si Gemini devuelve 429.",
    )
    args = parser.parse_args()

    print(f"Modo: {'demo (sin Gemini)' if args.demo else 'agente + Gemini'}")
    if not args.demo:
        print(f"Modelo: {get_gemini_model_name()}")
    print(f"Consulta: {args.query}\n")

    try:
        resultado = (
            ejecutar_agente_demo(args.query)
            if args.demo
            else ejecutar_agente(args.query)
        )
    except Exception as exc:
        msg = str(exc)
        if not args.demo and ("429" in msg or "RESOURCE_EXHAUSTED" in msg):
            print(
                "Error de cuota Gemini (429).\n"
                "  • No suele ser la API key 'mala': suele ser cuota free tier agotada\n"
                "    o límite 0 para ese modelo (gemini-2.0-flash en free tier).\n"
                "  • Ejecuta: uv run python src/scripts/test_gemini_api.py\n"
                "  • Pon en .env un modelo que funcione, ej: GEMINI_MODEL=gemini-2.5-flash\n"
                "  • O prueba sin LLM: uv run python src/scripts/run_agent.py --demo\n"
            )
        raise

    if resultado.pasos:
        print("=== Pasos del agente ===")
        for paso in resultado.pasos:
            print(paso)
        print()

    print("=== Recomendación (JSON) ===")
    print(resultado.recomendacion.to_json())


if __name__ == "__main__":
    main()
