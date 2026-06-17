"""
Rutas de datos centralizadas.
"""

from __future__ import annotations

from enum import Enum
from pathlib import Path


def project_root() -> Path:
    """Raíz del repo (carpeta que contiene `pyproject.toml`)."""
    return Path(__file__).resolve().parent.parent.parent


def raw_data_dir() -> Path:
    """Carpeta de CSV crudos."""
    return project_root() / "src" / "data" / "raw"


def raw_data_dir_clean() -> Path:
    """Carpeta de CSV limpios."""
    return project_root() / "src" / "data" / "clean"


class DataFormat(str, Enum):
    JSON = "json"
    CSV = "csv"
    XML = "xml"


class DataCsv(Enum):
    """CSV conocidos bajo `src/data/raw`."""

    AMAZON_BIG_SALES = "Amazon_Big_Sales_Dataset_2026.csv"
    AMAZON_GOOGLE = "amazon_google.csv"
    AMAZON_PRODUCT_CLEAN = "amazon_product_data_cleaned.csv"
    AMAZON_PRODUCT_SALES_CLEAN = "amazon_products_sales_data_cleaned.csv"
    DATA_ELECTRONICS_PRODUCTS = "DatafinitiElectronicsProductData.csv"

    @property
    def path(self) -> Path:
        return raw_data_dir() / str(self.value)

    def exists(self) -> bool:
        return self.path.is_file()


def list_raw_csv_paths() -> list[Path]:
    d = raw_data_dir()
    if not d.is_dir():
        return []
    return sorted(d.glob("*.csv"))


def list_clean_csv_paths() -> list[Path]:
    d = raw_data_dir_clean()
    if not d.is_dir():
        return []
    return sorted(d.glob("*.csv"))
