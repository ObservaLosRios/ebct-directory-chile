"""High-level ETL pipeline orchestration."""
from __future__ import annotations

import logging
from dataclasses import dataclass

import pandas as pd

from .config_loader import PipelineConfig
from .extract import read_company_directory
from .load import write_dataframe
from .transformations import (
    build_regional_summary,
    build_vertical_exploded,
    derive_vertical_lists,
    rename_and_trim_columns,
)


@dataclass
class PipelineArtifacts:
    """Collection of processed artefacts returned by the pipeline."""

    companies: pd.DataFrame
    tech_focus: pd.DataFrame
    regional_summary: pd.DataFrame


class ETLPipeline:
    """Small, testable ETL pipeline object."""

    def __init__(self, config: PipelineConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)

    def run(self) -> PipelineArtifacts:
        self.logger.info("Iniciando ETL...")
        raw = read_company_directory(self.config.paths.raw_dataset)
        self.logger.info("Archivo %s leído con %s filas", self.config.paths.raw_dataset, len(raw))

        cleaned = rename_and_trim_columns(raw)
        enriched = derive_vertical_lists(cleaned)
        verticals = build_vertical_exploded(enriched)
        regional_summary = build_regional_summary(enriched)

        write_dataframe(enriched, self.config.paths.processed_companies)
        write_dataframe(verticals, self.config.paths.tech_focus)
        write_dataframe(regional_summary, self.config.paths.regional_summary)

        self.logger.info("ETL finalizado. Archivos guardados en data/processed")

        return PipelineArtifacts(
            companies=enriched,
            tech_focus=verticals,
            regional_summary=regional_summary,
        )
