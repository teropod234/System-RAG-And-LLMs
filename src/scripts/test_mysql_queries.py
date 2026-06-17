"""
Probar las consultas MySQL (Paso A / Tool 2).

    uv run python src/scripts/test_mysql_queries.py
    uv run python src/scripts/test_mysql_queries.py --max-price 500 --category Audio
    uv run python src/scripts/test_mysql_queries.py --product-id AZ1001
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.db.queries import (
    check_stock,
    filter_products,
    format_products_for_agent,
    get_product_by_id,
    get_products_by_ids,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Probar consultas MySQL del catálogo.")
    parser.add_argument("--product-id", type=str, help="Buscar un producto por ID")
    parser.add_argument("--max-price", type=float, help="Precio máximo en USD")
    parser.add_argument("--min-price", type=float, help="Precio mínimo en USD")
    parser.add_argument("--min-stock", type=int, default=1, help="Stock mínimo")
    parser.add_argument("--category", type=str, help="Filtrar por categoría (parcial)")
    parser.add_argument("--brand", type=str, help="Filtrar por marca (parcial)")
    parser.add_argument("--only-recommended", action="store_true", help="Solo recomendados")
    parser.add_argument("--min-rating", type=float, help="Rating mínimo")
    parser.add_argument("--limit", type=int, default=10, help="Máximo de resultados")
    parser.add_argument(
        "--ids",
        type=str,
        nargs="+",
        help="Varios IDs: --ids AZ1001 AZ1002",
    )
    args = parser.parse_args()

    if args.product_id:
        product = get_product_by_id(args.product_id)
        print("=== get_product_by_id ===")
        print(json.dumps(product.to_dict() if product else None, indent=2, ensure_ascii=False))
        print("\n=== check_stock ===")
        print(json.dumps(check_stock(args.product_id), indent=2, ensure_ascii=False))
        return

    if args.ids:
        products = get_products_by_ids(args.ids)
        print("=== get_products_by_ids ===")
        print(format_products_for_agent(products))
        return

    products = filter_products(
        max_price=args.max_price,
        min_price=args.min_price,
        min_stock=args.min_stock,
        category=args.category,
        brand=args.brand,
        only_recommended=True if args.only_recommended else None,
        min_rating=args.min_rating,
        limit=args.limit,
    )
    print("=== filter_products ===")
    print(f"Resultados: {len(products)}\n")
    print(format_products_for_agent(products))


if __name__ == "__main__":
    main()
