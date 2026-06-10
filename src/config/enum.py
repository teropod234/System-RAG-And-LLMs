"""
Rutas de datos centralizadas.

Usar un Enum (o StrEnum) para nombres lógicos de ficheros está bien: evitas
"magic strings" repartidos por el código. Las rutas absolutas deben
construirse con pathlib a partir de la raíz del proyecto, no con placeholders
en strings.
"""

from __future__ import annotations

from enum import Enum
from pathlib import Path


def project_root() -> Path:
    """Raíz del repo (carpeta que contiene `pyproject.toml`)."""
    return Path(__file__).resolve().parent.parent.parent


def raw_data_dir() -> Path:
    """Carpeta de CSV crudos (ajústala si prefieres `data/raw` en la raíz)."""
    return project_root() / "src" / "data" / "raw"


class DataFormat(str, Enum):
    """Formatos de ingesta previstos (útil más adelante para pipelines)."""

    JSON = "json"
    CSV = "csv"
    XML = "xml"


class DataCsv(Enum):
    """CSV conocidos bajo `src/data/raw`. El valor del miembro es solo el nombre del fichero."""

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
    """Todos los `.csv` en la carpeta raw (por si añades ficheros sin tocar el Enum)."""
    d = raw_data_dir()
    if not d.is_dir():
        return []
    return sorted(d.glob("*.csv"))
