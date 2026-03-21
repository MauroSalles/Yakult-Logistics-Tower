"""Configuração centralizada do Yakult Logística Elite.

Todas as constantes ajustáveis ficam aqui para que o restante do código importe
uma única fonte de verdade.  Os valores são lidos de variáveis de ambiente quando
disponíveis, usando padrões sensatos como fallback.
"""

from __future__ import annotations

import os

# ---------------------------------------------------------------------------
# Interface / Dashboard
# ---------------------------------------------------------------------------
APP_TITLE: str = "Yakult Logística Elite"
APP_VERSION: str = "5.1"
APP_ICON: str = "🚀"

# ---------------------------------------------------------------------------
# Configurações de APIs externas
# ---------------------------------------------------------------------------
OSRM_BASE_URL: str = os.getenv(
    "OSRM_BASE_URL",
    "http://router.project-osrm.org",
)
OSRM_TIMEOUT_SECONDS: int = int(os.getenv("OSRM_TIMEOUT_SECONDS", "10"))
NOMINATIM_USER_AGENT: str = os.getenv(
    "NOMINATIM_USER_AGENT",
    f"yakult_elite_logistics/{APP_VERSION} (https://github.com/MauroSalles/Yakult-Logistics-Tower)",
)

# ---------------------------------------------------------------------------
# Parâmetros de custo
# ---------------------------------------------------------------------------
CUSTO_DIESEL_POR_KM: float = float(os.getenv("CUSTO_DIESEL_POR_KM", "2.15"))
CUSTO_PEDAGIO_POR_EIXO_KM: float = float(
    os.getenv("CUSTO_PEDAGIO_POR_EIXO_KM", "0.48"),
)

# ---------------------------------------------------------------------------
# Fatores de emissão de CO₂
# ---------------------------------------------------------------------------
EFICIENCIA_DIESEL_KM_L: float = float(
    os.getenv("EFICIENCIA_DIESEL_KM_L", "3.2"),
)
CO2_DIESEL_KG_L: float = float(os.getenv("CO2_DIESEL_KG_L", "2.61"))
CO2_HIBRID_FATOR: float = float(os.getenv("CO2_HIBRID_FATOR", "0.54"))

# ---------------------------------------------------------------------------
# Limiares da cadeia de frio (°C)
# ---------------------------------------------------------------------------
TEMP_CRITICO: int = int(os.getenv("TEMP_CRITICO", "8"))
TEMP_ATENCAO: int = int(os.getenv("TEMP_ATENCAO", "6"))

# ---------------------------------------------------------------------------
# Catálogo de veículos  {rótulo: qtd_eixos}
# ---------------------------------------------------------------------------
VEICULOS: dict[str, int] = {
    "Carreta (6 eixos)": 6,
    "Truck (3 eixos)": 3,
    "VUC (2 eixos)": 2,
}

# ---------------------------------------------------------------------------
# Rota padrão
# ---------------------------------------------------------------------------
ROTA_PADRAO: list[str] = [
    "Lorena, SP, Brazil",
    "Buenos Aires, Argentina",
    "Santiago, Chile",
]

# ---------------------------------------------------------------------------
# Limites operacionais
# ---------------------------------------------------------------------------
VELOCIDADE_MIN: int = 40
VELOCIDADE_MAX: int = 120
VELOCIDADE_PADRAO: int = 72
VELOCIDADE_STEP: int = 5

# ---------------------------------------------------------------------------
# Interface / Dashboard (continuação)
# ---------------------------------------------------------------------------
MAP_CENTER: tuple[float, float] = (-28.0, -55.0)
MAP_ZOOM: int = 4
MAP_TILES: str = "cartodb dark_matter"
ROUTE_COLOUR: str = "#00FFCC"
YAKULT_LOGO_URL: str = (
    "https://upload.wikimedia.org/wikipedia/commons/thumb/"
    "f/f1/Yakult_Logo.svg/2560px-Yakult_Logo.svg.png"
)
