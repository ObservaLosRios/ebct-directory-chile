"""Configuration helpers for the EBCT ETL pipeline."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

import yaml


@dataclass(frozen=True)
class PipelinePaths:
    """Normalized file-system locations used by the ETL pipeline."""

    raw_dataset: Path
    processed_companies: Path
    tech_focus: Path
    regional_summary: Path


@dataclass(frozen=True)
class LoggingConfig:
    """Minimal logging configuration."""

    level: str
    log_file: Path


@dataclass(frozen=True)
class PipelineConfig:
    """Top-level configuration container."""

    paths: PipelinePaths
    logging: LoggingConfig

    @classmethod
    def from_yaml(cls, config_path: Path) -> "PipelineConfig":
        """Load configuration from a YAML file."""
        with config_path.open("r", encoding="utf-8") as handle:
            raw_config: Dict[str, Any] = yaml.safe_load(handle)

        base_dir = config_path.parent.parent  # project root by convention
        paths_section = raw_config.get("paths", {})
        logging_section = raw_config.get("logging", {})

        paths = PipelinePaths(
            raw_dataset=_resolve(base_dir, paths_section["raw_dataset"]),
            processed_companies=_resolve(base_dir, paths_section["processed_companies"]),
            tech_focus=_resolve(base_dir, paths_section["tech_focus"]),
            regional_summary=_resolve(base_dir, paths_section["regional_summary"]),
        )

        logging_cfg = LoggingConfig(
            level=logging_section.get("level", "INFO"),
            log_file=_resolve(base_dir, logging_section.get("log_file", "logs/pipeline.log")),
        )

        return cls(paths=paths, logging=logging_cfg)


def _resolve(base_dir: Path, relative_path: str) -> Path:
    """Turn project-relative strings into absolute paths."""
    path = Path(relative_path)
    if not path.is_absolute():
        path = base_dir / path
    return path.expanduser().resolve()
