"""Data extraction utilities."""
from __future__ import annotations

from pathlib import Path

import pandas as pd


def read_company_directory(csv_path: Path) -> pd.DataFrame:
    """Read the EBCT directory from disk."""
    if not csv_path.exists():
        raise FileNotFoundError(f"No se encuentra el archivo de entrada: {csv_path}")

    return pd.read_csv(csv_path)
