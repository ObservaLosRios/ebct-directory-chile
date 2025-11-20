# EBCT Directory Chile – ETL y Visualizaciones

Pipeline ETL y set de visualizaciones interactivas para explorar el directorio EBCT Chile 2025. Incluye limpieza de datos, generación de artefactos analíticos y un sitio estático con gráficos Highcharts.

## Estructura

```
config/               # Configuración YAML del pipeline
data/raw/             # Datos originales (solo lectura)
data/processed/       # Artefactos generados por el ETL
docs/                 # Sitio estático e informes HTML
logs/                 # Logging estructurado
notebooks/            # Exploración y prototipos
scripts/              # Entrypoints ejecutables
src/etl/              # Código fuente desacoplado por capas
tests/                # Pruebas unitarias (pytest)
```

## Requisitos y entorno

- Python 3.10+
- Crear entorno virtual y dependencias:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 1. Ejecutar el ETL

```bash
python -m scripts.run_etl --config config/pipeline.yml
```

Salida principal:
- `data/processed/companies_clean.csv`
- `data/processed/companies_tech_focus.csv`
- `data/processed/summary_region_sector.csv`

Los logs se guardan en `logs/pipeline.log` y se muestran en consola.

## 2. Exportar visualizaciones

Ambos scripts generan archivos HTML autónomos en `docs/` y además alimentan `docs/index.html` (donde se incrustan juntos).

```bash
# Treemap de participación regional
python scripts/export_treemap_html.py

# Ranking de empresas por región
python scripts/export_region_chart_html.py
```

Características destacadas:
- Highcharts con modo claro/oscuro sincronizado.
- Treemap prioriza Los Ríos y muestra totales formateados.
- Barra horizontal reutiliza la paleta del treemap para consistencia visual.

## 3. Visualizar el sitio estático

El dashboard principal vive en `docs/index.html`. Para probar localmente:

```bash
python -m http.server --directory docs 8000
# Visita http://localhost:8000
```

## Pruebas automatizadas

```bash
pytest
```

## Datos derivados

La carpeta `data/processed/` contiene los CSV listos para consumo externo o futuros análisis. Cada vez que se corren los scripts ETL se sobrescriben, por lo que conviene versionar solo los artefactos necesarios.
