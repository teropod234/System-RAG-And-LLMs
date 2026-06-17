"""
Paso 3: crear la base MySQL y cargar productos desde Products_clean.csv.

1. Copia .env.example a .env y pon tu contraseña de MySQL.
2. Ejecuta:
       uv run python src/scripts/load_products_mysql.py
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from sqlalchemy import create_engine, select, text
from sqlalchemy.exc import OperationalError

from src.db.config import get_mysql_settings
from src.db.loader import load_products_from_csv
from src.db.schema import products_table


def main() -> None:
    settings = get_mysql_settings()
    print(f"Conectando a MySQL ({settings.host}:{settings.port})...")
    print(f"Usuario: {settings.user}")
    print(f"Base de datos: {settings.database}")

    try:
        rows = load_products_from_csv()
    except OperationalError as exc:
        if "1045" in str(exc):
            print(
                "\nError de autenticación (1045): MySQL rechazó usuario o contraseña.\n"
                "Revisa tu archivo `.env`:\n"
                "  - MYSQL_USER y MYSQL_PASSWORD deben coincidir con MySQL Workbench\n"
                "  - Sin comillas extra: MYSQL_PASSWORD=tu_clave\n"
                "  - Si la clave tiene @, # o %, ya está soportado; revisa que no haya espacios\n"
                "Prueba entrar en Workbench con el mismo usuario/clave antes de volver a ejecutar."
            )
        raise

    print(f"Cargados {rows} productos en la tabla `products`.")

    engine = create_engine(settings.database_url)
    with engine.connect() as conn:
        total = conn.execute(text("SELECT COUNT(*) FROM products")).scalar_one()
        sample = conn.execute(
            select(
                products_table.c.product_id,
                products_table.c.product_name,
                products_table.c.price_usd,
                products_table.c.stock,
                products_table.c.category,
            ).limit(5)
        ).fetchall()

    print(f"Total en BD: {total}")
    print("\nMuestra:")
    for row in sample:
        print(f"  {row.product_id} | {row.product_name[:30]:30} | ${row.price_usd:.2f} | stock={row.stock}")


if __name__ == "__main__":
    main()
