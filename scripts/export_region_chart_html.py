"""Generate a Highcharts bar chart HTML for company concentration by region."""
from __future__ import annotations

import json
from pathlib import Path
from textwrap import dedent

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data/processed/companies_clean.csv"
OUTPUT_HTML = PROJECT_ROOT / "docs/region_companies.html"


def load_region_counts() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH, usecols=["empresa", "region_casa_matriz"])
    return (
        df.groupby("region_casa_matriz")
        .size()
        .reset_index(name="numero_empresas")
        .sort_values("numero_empresas", ascending=True)
    )


def build_chart_payload(counts: pd.DataFrame) -> tuple[list[str], list[int]]:
    categories = counts["region_casa_matriz"].tolist()
    values = counts["numero_empresas"].astype(int).tolist()
    return categories, values


def build_html(categories_json: str, values_json: str) -> str:
    template = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>Concentración de empresas por región</title>
        <script src="https://code.highcharts.com/highcharts.js"></script>
        <script src="https://code.highcharts.com/modules/exporting.js"></script>
        <script src="https://code.highcharts.com/modules/export-data.js"></script>
        <style>
            :root {
                font-family: 'Georgia', 'Inter', sans-serif;
                color: #1f2933;
            }
            body {
                margin: 0;
                background: transparent;
            }
            .chart-wrapper {
                max-width: 1000px;
                margin: 0 auto;
                padding: 20px;
                background: #ffffff;
                border-radius: 12px;
                box-shadow: 0 8px 30px rgba(15, 23, 42, 0.08);
                position: relative;
                transition: background-color 0.3s ease, box-shadow 0.3s ease;
            }
            .chart-stage {
                position: relative;
            }
            #regionBarContainer {
                min-height: 600px;
            }
        </style>
    </head>
    <body>
        <div class="chart-wrapper">
            <div class="chart-stage">
                <div id="regionBarContainer"></div>
            </div>
        </div>
        <script>
            const CATEGORIES = __CATEGORIES__;
            const SERIES_VALUES = __VALUES__;

            const exportingOptions = {
                enabled: true,
                buttons: {
                    contextButton: {
                        menuItems: [
                            'viewFullscreen',
                            'printChart',
                            'separator',
                            'downloadPNG',
                            'downloadJPEG',
                            'downloadSVG',
                            'separator',
                            'downloadCSV',
                            'downloadXLS',
                            'viewData'
                        ]
                    }
                }
            };

            const chartOptions = {
                chart: {
                    type: 'bar',
                    backgroundColor: '#ffffff'
                },
                title: {
                    text: 'Concentración de empresas por región'
                },
                subtitle: {
                    text: 'Fuente: EBCT Chile 2025'
                },
                xAxis: {
                    categories: CATEGORIES,
                    title: { text: null },
                    gridLineWidth: 1,
                    lineWidth: 0
                },
                yAxis: {
                    min: 0,
                    title: {
                        text: 'Número de empresas',
                        align: 'high'
                    },
                    labels: {
                        overflow: 'justify'
                    },
                    gridLineWidth: 0
                },
                tooltip: {
                    valueSuffix: ' empresas'
                },
                plotOptions: {
                    bar: {
                        borderRadius: '50%',
                        dataLabels: {
                            enabled: true,
                            format: '{point.y}'
                        },
                        groupPadding: 0.1
                    }
                },
                legend: {
                    layout: 'vertical',
                    align: 'right',
                    verticalAlign: 'top',
                    x: -40,
                    y: 80,
                    floating: true,
                    borderWidth: 1,
                    backgroundColor: 'var(--highcharts-background-color, #ffffff)',
                    shadow: true
                },
                credits: { enabled: false },
                exporting: exportingOptions,
                series: [{
                    name: 'Número de empresas',
                    data: SERIES_VALUES,
                    color: '#0f8b8d'
                }]
            };

            Highcharts.chart('regionBarContainer', chartOptions);
        </script>
    </body>
    </html>
    """
    return (
        dedent(template)
        .replace("__CATEGORIES__", categories_json)
        .replace("__VALUES__", values_json)
        .strip()
    )


def main() -> None:
    counts = load_region_counts()
    categories, values = build_chart_payload(counts)
    html = build_html(json.dumps(categories, ensure_ascii=False), json.dumps(values))
    OUTPUT_HTML.write_text(html, encoding="utf-8")
    print(f"Reporte HTML generado en {OUTPUT_HTML.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
