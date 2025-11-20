"""Generate a Highcharts treemap HTML report focused on region/company names."""
from __future__ import annotations

import json
from pathlib import Path
from textwrap import dedent

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data/processed/companies_clean.csv"
OUTPUT_HTML = PROJECT_ROOT / "docs/region_treemap.html"
PRIMARY_REGION = "Los Ríos"
PRIMARY_REGION_MULTIPLIER = 5
COLOR_PALETTE = [
    "#0F8B8D",
    "#F4D35E",
    "#EE964B",
    "#9B5DE5",
    "#00BBF9",
    "#F15BB5",
    "#00A5CF",
    "#7AE582",
]


def slugify(value: str) -> str:
    return (
        value.lower()
        .replace("á", "a")
        .replace("é", "e")
        .replace("í", "i")
        .replace("ó", "o")
        .replace("ú", "u")
        .replace("ñ", "n")
        .replace(" ", "-")
    )


def build_treemap_data(df: pd.DataFrame) -> list[dict[str, object]]:
    regions = sorted(df["region_casa_matriz"].unique())
    if PRIMARY_REGION in regions:
        regions.remove(PRIMARY_REGION)
        regions.insert(0, PRIMARY_REGION)

    nodes: list[dict[str, object]] = []
    children: list[dict[str, object]] = []

    for idx, region in enumerate(regions):
        node_id = slugify(region)
        color = COLOR_PALETTE[idx % len(COLOR_PALETTE)]
        subset = df[df["region_casa_matriz"] == region]
        nodes.append(
            {
                "id": node_id,
                "name": region,
                "color": color,
                "displayValue": int(subset.shape[0]),
            }
        )
        weight = PRIMARY_REGION_MULTIPLIER if region == PRIMARY_REGION else 1
        for company in subset["empresa"]:
            children.append(
                {
                    "name": company,
                    "parent": node_id,
                    "value": weight,
                    "displayValue": 1,
                }
            )

    return nodes + children


def build_html(data_json: str) -> str:
    template = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>Treemap Empresas por Región</title>
        <script src="https://code.highcharts.com/highcharts.js"></script>
        <script src="https://code.highcharts.com/modules/treemap.js"></script>
        <script src="https://code.highcharts.com/modules/accessibility.js"></script>
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
                max-width: 1200px;
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
            #regionTreemapContainer {
                min-height: 650px;
                position: relative;
            }
            .theme-toggle {
                position: absolute;
                top: 18px;
                right: 18px;
                width: 38px;
                height: 38px;
                border-radius: 999px;
                border: 1px solid rgba(15, 23, 42, 0.25);
                background: rgba(255, 255, 255, 0.85);
                color: #0f172a;
                font-size: 1rem;
                cursor: pointer;
                transition: transform 0.2s ease, background-color 0.2s ease, color 0.2s ease;
                display: flex;
                align-items: center;
                justify-content: center;
                backdrop-filter: blur(10px);
                z-index: 2;
            }
            .theme-toggle:hover {
                transform: translateY(-1px);
            }
        </style>
    </head>
    <body>
        <div class="chart-wrapper">
            <div class="chart-stage">
                <div id="regionTreemapContainer"></div>
                <button id="themeToggle" class="theme-toggle" aria-label="Cambiar tema">☼</button>
            </div>
        </div>
        <script>
            const TREEMAP_DATA = __TREEMAP_DATA__;

            const chartOptions = {
                chart: {
                    backgroundColor: '#ffffff'
                },
                series: [{
                    type: 'treemap',
                    name: 'Empresas por región',
                    allowTraversingTree: true,
                    alternateStartingDirection: true,
                    dataLabels: {
                        format: '{point.name}',
                        style: {
                            textOutline: 'none'
                        }
                    },
                    borderRadius: 3,
                    nodeSizeBy: 'leaf',
                    levels: [{
                        level: 1,
                        layoutAlgorithm: 'sliceAndDice',
                        groupPadding: 3,
                        dataLabels: {
                            headers: true,
                            enabled: true,
                            style: {
                                fontSize: '0.6em',
                                fontWeight: 'normal',
                                textTransform: 'uppercase',
                                color: 'var(--highcharts-neutral-color-100, #000)'
                            }
                        },
                        borderRadius: 3,
                        borderWidth: 1,
                        colorByPoint: true
                    }, {
                        level: 2,
                        dataLabels: {
                            enabled: true,
                            inside: false
                        }
                    }],
                    data: TREEMAP_DATA
                }],
                title: {
                    text: 'Empresas biotecnológicas por región',
                    align: 'left'
                },
                subtitle: {
                    text: 'Fuente: EBCT Chile 2025',
                    align: 'left'
                },
                tooltip: {
                    useHTML: true,
                    formatter: function () {
                        const rawValue = this.point.displayValue ?? this.point.value ?? 0;
                        const label = rawValue === 1 ? 'empresa' : 'empresas';
                        return `<b>${this.point.name}</b><br/>Total: <b>${rawValue}</b> ${label}`;
                    }
                },
                credits: { enabled: false }
            };

            const chart = Highcharts.chart('regionTreemapContainer', chartOptions);

            const toggleBtn = document.getElementById('themeToggle');
            const chartWrapper = document.querySelector('.chart-wrapper');
            let darkMode = false;

            function applyTheme() {
                chart.update({
                    chart: {
                        backgroundColor: darkMode ? '#0f172a' : '#ffffff'
                    },
                    title: { style: { color: darkMode ? '#f8fafc' : '#0f172a' } },
                    subtitle: { style: { color: darkMode ? '#cbd5f5' : '#475569' } },
                    tooltip: {
                        backgroundColor: darkMode ? 'rgba(15,23,42,0.9)' : 'rgba(255,255,255,0.95)',
                        style: { color: darkMode ? '#f8fafc' : '#0f172a' }
                    },
                    plotOptions: {
                        treemap: {
                            dataLabels: { style: { color: darkMode ? '#f8fafc' : '#0f172a' } }
                        }
                    }
                });

                if (chartWrapper) {
                    chartWrapper.style.backgroundColor = darkMode ? '#0b1220' : '#ffffff';
                    chartWrapper.style.boxShadow = darkMode
                        ? '0 8px 30px rgba(0, 0, 0, 0.45)'
                        : '0 8px 30px rgba(15, 23, 42, 0.08)';
                }

                chart.series.forEach(series => {
                    series.points.forEach(point => {
                        if (point.dataLabel) {
                            point.dataLabel.css({ color: darkMode ? '#f8fafc' : '#0f172a' });
                        }
                        if (point.dataLabelUpper) {
                            point.dataLabelUpper.css({ color: darkMode ? '#f8fafc' : '#0f172a' });
                        }
                    });
                });
            }

            toggleBtn.addEventListener('click', () => {
                darkMode = !darkMode;
                toggleBtn.textContent = darkMode ? '☾' : '☼';
                toggleBtn.style.backgroundColor = darkMode ? 'rgba(15,23,42,0.75)' : 'rgba(255, 255, 255, 0.85)';
                toggleBtn.style.color = darkMode ? '#f8fafc' : '#0f172a';
                toggleBtn.style.borderColor = darkMode ? 'rgba(248, 250, 252, 0.45)' : 'rgba(15, 23, 42, 0.25)';
                applyTheme();
            });
        </script>
    </body>
    </html>
    """
    return dedent(template).replace("__TREEMAP_DATA__", data_json).strip()


def main() -> None:
    df = pd.read_csv(DATA_PATH, usecols=["empresa", "region_casa_matriz"])
    treemap_data = build_treemap_data(df)
    data_json = json.dumps(treemap_data, ensure_ascii=False)
    html = build_html(data_json)
    OUTPUT_HTML.write_text(html, encoding="utf-8")
    print(f"Reporte HTML generado en {OUTPUT_HTML.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
