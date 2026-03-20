# 🚛 Yakult Elite Logistics

> Interactive logistics dashboard for the Yakult cold-chain distribution network across South America.

![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/streamlit-1.54-red)
![License: MIT](https://img.shields.io/badge/license-MIT-green)

---

## Overview

**Yakult Elite Logistics** is a Streamlit-based command-and-control dashboard that
provides real-time route planning, cost analysis, CO₂ footprint estimation, and
cold-chain integrity monitoring for the Yakult distribution fleet operating in
Brazil, Argentina, and Chile.

### Key features

| Feature | Description |
|---------|-------------|
| **Route planning** | Add / remove stops, geocode via Nominatim, and compute optimal driving routes through the OSRM API |
| **Cost analysis** | Diesel + toll breakdown per km, with configurable vehicle type (2 / 3 / 6 axles) |
| **ETA forecast** | Per-stop arrival time based on adjustable average speed (40 – 120 km/h) with CSV export |
| **ESG dashboard** | Side-by-side CO₂ comparison — Diesel vs Hybrid vs Electric |
| **Cold-chain monitor** | Temperature slider with 3-level alert system (stable / warning / critical) |
| **Tactical map** | Dark-mode Folium map with GeoJSON route overlay and truck markers |

---

## Prerequisites

- **Python 3.10+** (tested on 3.11 / 3.12)
- A virtual environment is recommended

## Quick start

```bash
# 1. Clone the repository
git clone https://github.com/MauroSalles/Yakult-Logistics-Tower.git
cd Yakult-Logistics-Tower/Projeto\ Yakult

# 2. Create & activate a virtual environment
python -m venv .venv
source .venv/bin/activate   # Linux / macOS
# .venv\Scripts\activate    # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Launch the dashboard
streamlit run app_logistica.py
```

The dashboard opens automatically in your default browser.

---

## Project structure

```
Projeto Yakult/
├── app_logistica.py          # Main Streamlit application
├── config.py                 # Centralised configuration (constants, thresholds, API settings)
├── tests/
│   └── test_app.py           # Pytest test suite (31 tests)
├── mapa_yakult.ipynb          # Exploratory Jupyter notebook
├── requirements.txt           # Pinned Python dependencies
├── pyproject.toml             # Project metadata + tool configs (ruff, pytest)
├── Makefile                   # Developer shortcuts (run, test, lint, format)
├── Relatorio_Logistica_Yakult.pdf  # Final project report
└── LICENSE                    # MIT
```

## Configuration

All tunable parameters are centralised in [`config.py`](Projeto%20Yakult/config.py).
Every constant can be overridden via environment variables — no code changes required:

```bash
export OSRM_BASE_URL="http://your-osrm-instance:5000"
export CUSTO_DIESEL_POR_KM="2.50"
export TEMP_CRITICO="10"
streamlit run app_logistica.py
```

See the full list of configurable values in the file header.

---

## Testing

```bash
# Run the full suite
make test
# or
python -m pytest

# Run with verbose output
python -m pytest -v
```

The suite covers: `calcula_custos`, `formatar_tempo_conducao`, `calcular_eta_paradas`,
`calcular_co2`, `buscar_coords`, and the configuration module.

## Development

```bash
# Lint (read-only)
make lint

# Auto-format
make format

# Remove caches
make clean
```

---

## Architecture

```
┌──────────────┐   HTTP/JSON   ┌───────────────────┐
│  Nominatim   │◄─────────────►│                   │
│  (geocoding) │               │   app_logistica   │
└──────────────┘               │      .py          │
                               │                   │
┌──────────────┐   HTTP/JSON   │   ┌───────────┐   │   ┌────────────┐
│   OSRM API   │◄─────────────►│   │ config.py │   │──►│  Streamlit │
│  (routing)   │               │   └───────────┘   │   │  Browser   │
└──────────────┘               └───────────────────┘   └────────────┘
```

## License

This project is licensed under the [MIT License](Projeto%20Yakult/LICENSE).
