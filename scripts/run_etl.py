"""Command-line entrypoint for the EBCT ETL pipeline."""
from __future__ import annotations

import argparse
import logging
from pathlib import Path
import sys

# Ensure the src package is importable when invoking the script directly.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.etl.config_loader import PipelineConfig  # noqa  E402
from src.etl.pipeline import ETLPipeline  # noqa  E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the EBCT ETL pipeline")
    parser.add_argument(
        "--config",
        default="config/pipeline.yml",
        help="Ruta al archivo de configuración YAML (por defecto: config/pipeline.yml)",
    )
    return parser.parse_args()


def configure_logging(config: PipelineConfig) -> None:
    log_path = config.logging.log_file
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=getattr(logging, config.logging.level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_path, encoding="utf-8"),
        ],
    )


def main() -> None:
    args = parse_args()
    config = PipelineConfig.from_yaml(Path(args.config).resolve())
    configure_logging(config)

    pipeline = ETLPipeline(config)
    pipeline.run()


if __name__ == "__main__":
    main()
