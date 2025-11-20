"""Data loading helpers."""
from __future__ import annotations

from pathlib import Path

import pandas as pd


def write_dataframe(df: pd.DataFrame, target_path: Path) -> Path:
    """Persist a DataFrame ensuring the destination directory exists."""
    target_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(target_path, index=False)
    return target_path
