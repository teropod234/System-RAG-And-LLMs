"""
Probar la Tool 1 (Chroma) del paso B.

    uv run python src/scripts/test_tools.py
    uv run python src/scripts/test_tools.py --query "audio recomendable buena calidad"
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.model.tools import buscar_opiniones_usuarios


def main() -> None:
    parser = argparse.ArgumentParser(description="Probar Tool 1: buscar_opiniones_usuarios")
    parser.add_argument(
        "--query",
        type=str,
        default="producto recomendable con buena experiencia de uso",
        help="Consulta en lenguaje natural",
    )
    args = parser.parse_args()

    print(f"Consulta: {args.query!r}\n")
    print("=== buscar_opiniones_usuarios ===\n")
    result = buscar_opiniones_usuarios.invoke({"consulta": args.query})
    print(result)


if __name__ == "__main__":
    main()
