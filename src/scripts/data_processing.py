from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import pandas as pd

from src.utils.data_clean import data_cleaning

RAW_DATA_DIR = _ROOT / "src" / "data" / "raw"
CLEAN_DATA_DIR = _ROOT / "src" / "data" / "clean"


def main() -> None:
    input_path = RAW_DATA_DIR / "Amazon_Big_Sales_Dataset_2026.csv"
    output_path = CLEAN_DATA_DIR / "Products_clean.csv"

    df = pd.read_csv(input_path)
    df_clean = data_cleaning(df)

    CLEAN_DATA_DIR.mkdir(parents=True, exist_ok=True)
    df_clean.to_csv(output_path, index=False)


if __name__ == "__main__":
    main()
