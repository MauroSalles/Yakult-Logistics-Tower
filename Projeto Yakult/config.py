"""Configurações centralizadas do Yakult Logistics Tower.

Todas as constantes, parâmetros de custo, limiares e configurações de
conexão ficam neste módulo para facilitar manutenção e evitar valores
"mágicos" espalhados pelo código.
"""

from __future__ import annotations

import os

# ---------------------------------------------------------------------------
# Aplicação
# ---------------------------------------------------------------------------
APP_TITLE = "Yakult Elite Logistics"
APP_VERSION = "6.0"
APP_ICON = "🚀"

# ---------------------------------------------------------------------------
# Banco de Dados (Nuvem) — lê de variáveis de ambiente ou st.secrets
# ---------------------------------------------------------------------------
DATABASE_URL: str = os.getenv("DATABASE_URL", "")

# ---------------------------------------------------------------------------
# Geocodificação
# ---------------------------------------------------------------------------
NOMINATIM_USER_AGENT = "yakult_elite_v6"

# ---------------------------------------------------------------------------
# OSRM (Open Source Routing Machine)
# ---------------------------------------------------------------------------
OSRM_BASE_URL = "http://router.project-osrm.org"
OSRM_TIMEOUT_S = 10

# ---------------------------------------------------------------------------
# Custos operacionais (R$ / km)
# ---------------------------------------------------------------------------
CUSTO_DIESEL_POR_KM = 2.15
CUSTO_PEDAGIO_POR_EIXO_KM = 0.48

# ---------------------------------------------------------------------------
# Emissões de CO₂
# ---------------------------------------------------------------------------
EFICIENCIA_DIESEL_KM_L = 3.2    # km por litro (caminhão pesado)
CO2_DIESEL_KG_L = 2.61          # kg de CO₂ por litro de diesel
CO2_HIBRID_FATOR = 0.54         # híbrido emite ~54 % do diesel

# ---------------------------------------------------------------------------
# Cadeia de Frio — limiares de temperatura (°C)
# ---------------------------------------------------------------------------
TEMP_CRITICA = 8
TEMP_ATENCAO = 6

# ---------------------------------------------------------------------------
# Velocidade padrão (km/h)
# ---------------------------------------------------------------------------
VELOCIDADE_PADRAO = 72.0

# ---------------------------------------------------------------------------
# Rota padrão
# ---------------------------------------------------------------------------
ROTA_PADRAO: list[str] = [
    "Lorena, SP, Brazil",
    "Buenos Aires, Argentina",
    "Santiago, Chile",
]
