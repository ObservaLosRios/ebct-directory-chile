"""Core transformation functions for the EBCT ETL pipeline."""
from __future__ import annotations

from typing import List

import pandas as pd

COLUMN_ORDER = [
    "empresa",
    "region_casa_matriz",
    "sector_actividad_principal",
    "verticales_tecnologicas",
]


def rename_and_trim_columns(raw_df: pd.DataFrame) -> pd.DataFrame:
    """Rename columns to snake_case and drop extraneous whitespace."""
    df = raw_df.copy()
    rename_map = {}
    for idx, target_name in enumerate(COLUMN_ORDER):
        try:
            rename_map[raw_df.columns[idx]] = target_name
        except IndexError as exc:  # pragma: no cover - defensive guard
            raise ValueError("La tabla de entrada no tiene todas las columnas esperadas") from exc

    df = df.rename(columns=rename_map)[COLUMN_ORDER]

    for col in COLUMN_ORDER:
        df[col] = df[col].fillna("").astype(str).str.strip()

    return df


def derive_vertical_lists(df: pd.DataFrame) -> pd.DataFrame:
    """Split the technology vertical column into normalized lists."""
    df = df.copy()
    df["verticales_lista"] = df["verticales_tecnologicas"].apply(_split_verticals)
    df["numero_verticales"] = df["verticales_lista"].apply(len)
    return df


def build_vertical_exploded(df: pd.DataFrame) -> pd.DataFrame:
    """Return a long-form table with one row per company/vertical."""
    exploded = df[["empresa", "region_casa_matriz", "verticales_lista"]].explode(
        "verticales_lista"
    )
    exploded = exploded.dropna(subset=["verticales_lista"]).rename(
        columns={"verticales_lista": "vertical"}
    )
    exploded["vertical"] = exploded["vertical"].str.strip()
    return exploded.reset_index(drop=True)


def build_regional_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Count companies by region and sector."""
    summary = (
        df.groupby(["region_casa_matriz", "sector_actividad_principal"], dropna=False)
        .size()
        .reset_index(name="numero_empresas")
        .sort_values(by=["numero_empresas"], ascending=False)
    )
    return summary


def _split_verticals(row_value: str) -> List[str]:
    parts = [part.strip() for part in row_value.split(",")]
    return [part for part in parts if part]
