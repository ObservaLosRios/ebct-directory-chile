"""Unit tests for ETL transformation helpers."""
from __future__ import annotations

import pandas as pd

from src.etl import transformations as t


def _sample_raw_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            [" Empresa Uno ", "Los Ríos ", " Sector A ", "IA, Robótica"],
            ["Empresa Dos", "Biobío", "Sector B", ""],
        ],
        columns=["Empresa", "Región Casa Matriz", "Sector Actividad Principal", ""],
    )


def test_rename_and_trim_columns_normalizes_headers() -> None:
    raw = _sample_raw_df()
    normalized = t.rename_and_trim_columns(raw)

    assert list(normalized.columns) == t.COLUMN_ORDER
    assert normalized.loc[0, "empresa"] == "Empresa Uno"
    assert normalized.loc[0, "verticales_tecnologicas"] == "IA, Robótica"


def test_derive_vertical_lists_creates_counts() -> None:
    normalized = t.rename_and_trim_columns(_sample_raw_df())
    enriched = t.derive_vertical_lists(normalized)

    assert enriched.loc[0, "numero_verticales"] == 2
    assert enriched.loc[1, "numero_verticales"] == 0


def test_build_vertical_exploded_creates_long_table() -> None:
    enriched = t.derive_vertical_lists(t.rename_and_trim_columns(_sample_raw_df()))
    exploded = t.build_vertical_exploded(enriched)

    assert len(exploded) == 2
    assert set(exploded["vertical"].unique()) == {"IA", "Robótica"}


def test_build_regional_summary_counts_rows() -> None:
    enriched = t.derive_vertical_lists(t.rename_and_trim_columns(_sample_raw_df()))
    summary = t.build_regional_summary(enriched)

    assert summary.loc[summary["region_casa_matriz"] == "Biobío", "numero_empresas"].iloc[0] == 1
