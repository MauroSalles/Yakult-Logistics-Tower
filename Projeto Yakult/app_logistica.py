"""Yakult Elite Logistics – interactive Streamlit dashboard.

Provides route planning, cost analysis, CO₂ estimation, and cold-chain
monitoring for the Yakult distribution network in South America.
"""

from __future__ import annotations

import datetime
import logging

import folium
import pandas as pd
import requests
import streamlit as st
from geopy.geocoders import Nominatim
from streamlit_folium import st_folium

from config import (
    APP_ICON,
    APP_TITLE,
    APP_VERSION,
    CO2_DIESEL_KG_L,
    CO2_HIBRID_FATOR,
    CUSTO_DIESEL_POR_KM,
    CUSTO_PEDAGIO_POR_EIXO_KM,
    EFICIENCIA_DIESEL_KM_L,
    MAP_CENTER,
    MAP_TILES,
    MAP_ZOOM,
    NOMINATIM_USER_AGENT,
    OSRM_BASE_URL,
    OSRM_TIMEOUT_SECONDS,
    ROTA_PADRAO,
    ROUTE_COLOUR,
    TEMP_ATENCAO,
    TEMP_CRITICO,
    VEICULOS,
    VELOCIDADE_MAX,
    VELOCIDADE_MIN,
    VELOCIDADE_PADRAO,
    VELOCIDADE_STEP,
    YAKULT_LOGO_URL,
)

# ---------------------------------------------------------------------------
# 1. SETUP
# ---------------------------------------------------------------------------

st.set_page_config(page_title=APP_TITLE, layout="wide", page_icon=APP_ICON)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s:%(message)s",
)
logger = logging.getLogger(__name__)

geolocator = Nominatim(user_agent=NOMINATIM_USER_AGENT)

st.markdown(
    """
    <style>
    [data-testid="stMetricValue"] { font-size: 28px; color: #1E88E5; }
    .stDataFrame { border-radius: 10px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# 2. MOTORES DE CÁLCULO
# ---------------------------------------------------------------------------

# Public aliases so test_app.py can keep importing them by old name.
_EFICIENCIA_DIESEL_KM_L: float = EFICIENCIA_DIESEL_KM_L
_CO2_DIESEL_KG_L: float = CO2_DIESEL_KG_L
_CO2_HIBRID_FATOR: float = CO2_HIBRID_FATOR

@st.cache_data(show_spinner=False)
def buscar_coords(cidade: str) -> tuple[float, float] | None:
    """Return ``(latitude, longitude)`` for *cidade*, or ``None`` on failure.

    Results are cached by Streamlit so repeated calls for the same city do not
    hit the Nominatim service again during the same session.  Up to two retries
    are attempted for transient network errors.
    """
    tentativas = 2
    for tentativa in range(1, tentativas + 1):
        try:
            loc = geolocator.geocode(cidade, timeout=OSRM_TIMEOUT_SECONDS)
            if loc:
                logger.debug("Geocoded %s -> %s,%s", cidade, loc.latitude, loc.longitude)
                return (loc.latitude, loc.longitude)
            logger.warning("Não foi possível geocodificar: %s", cidade)
            return None  # city not found — no point retrying
        except Exception:
            logger.warning(
                "Tentativa %d/%d falhou ao geocodificar '%s'",
                tentativa,
                tentativas,
                cidade,
                exc_info=True,
            )
    return None

def calcular_rota_osrm(pontos: list[tuple[float, float]]) -> tuple[list, float]:
    """Calculate a driving route through *pontos* via the OSRM API.

    Returns ``(geometry, distance_metres)`` where *geometry* is a list of
    ``[lon, lat]`` coordinate pairs.  On failure returns ``([], 0.0)``.
    """
    locs = ";".join(f"{lon},{lat}" for lat, lon in pontos)
    url = f"{OSRM_BASE_URL}/route/v1/driving/{locs}?overview=full&geometries=geojson"
    try:
        resp = requests.get(url, timeout=OSRM_TIMEOUT_SECONDS)
        resp.raise_for_status()
        data = resp.json()
        if data.get("code") == "Ok":
            route = data["routes"][0]
            return route["geometry"]["coordinates"], route["distance"]
        logger.warning("OSRM retornou código diferente de Ok: %s", data.get("code"))
    except requests.RequestException:
        logger.error("Falha na chamada OSRM", exc_info=True)
    return [], 0.0

def calcula_custos(dist_km: float, eixos: int) -> tuple[float, float]:
    """Return ``(custo_total, custo_pedagio)`` for a given distance and axle count."""
    custo_diesel = dist_km * CUSTO_DIESEL_POR_KM
    custo_pedagio = dist_km * (eixos * CUSTO_PEDAGIO_POR_EIXO_KM)
    return custo_diesel + custo_pedagio, custo_pedagio

def calcular_co2(dist_km: float) -> tuple[float, float, float]:
    """Return ``(co2_diesel_kg, co2_hibrido_kg, co2_eletrico_kg)`` for the route.

    Uses consistent fuel-efficiency and emission-factor constants so the
    summary metric and the ESG comparison chart always agree.
    """
    co2_diesel = (dist_km / EFICIENCIA_DIESEL_KM_L) * CO2_DIESEL_KG_L
    co2_hibrido = co2_diesel * CO2_HIBRID_FATOR
    return co2_diesel, co2_hibrido, 0.0

def formatar_tempo_conducao(dist_km: float, velocidade: float = 72.0) -> str:
    """Return driving time as a human-readable string (e.g. ``'14h 30min'``)."""
    if velocidade <= 0:
        return "—"
    total_min = int((dist_km / velocidade) * 60)
    return f"{total_min // 60}h {total_min % 60:02d}min"

def calcular_eta_paradas(
    rota: list[str],
    dist_km: float,
    h_partida: datetime.time,
    velocidade: float = 72.0,
) -> list[dict]:
    """Return a list of ETA dicts for each stop in *rota*.

    The first stop is always at departure time (0 km travelled).  The last stop
    arrives after the full *dist_km*.  Intermediate stops are spaced evenly.
    """
    n = len(rota)
    partida = datetime.datetime.combine(datetime.date.today(), h_partida)
    eta_list: list[dict] = []
    for i, cid in enumerate(rota):
        parada_km = (dist_km / (n - 1)) * i if n > 1 else 0.0
        tempo_h = parada_km / velocidade if velocidade > 0 else 0.0
        chegada = partida + datetime.timedelta(hours=tempo_h)
        status = "Partida 🚀" if i == 0 else "No Prazo ✅"
        eta_list.append({
            "Cidade": cid,
            "Previsão": chegada.strftime("%H:%M"),
            "Status": status,
        })
    return eta_list

# ---------------------------------------------------------------------------
# 3. BARRA LATERAL — TELEMETRIA E CONFIGURAÇÃO
# ---------------------------------------------------------------------------
with st.sidebar:
    st.image(YAKULT_LOGO_URL, width=120)
    st.title("🎮 Centro de Comando")

    # Gestão de Itinerário
    if "rota" not in st.session_state:
        st.session_state.rota = list(ROTA_PADRAO)

    with st.expander("📍 Editar Itinerário", expanded=True):
        nova_cidade = st.text_input("Nova Parada:")
        col_add, col_reset = st.columns(2)
        with col_add:
            if st.button("➕ Adicionar", use_container_width=True):
                nova_stripped = nova_cidade.strip()
                if not nova_stripped:
                    st.warning("⚠️ Insira o nome de uma cidade.")
                elif nova_stripped in st.session_state.rota:
                    st.warning(f"⚠️ '{nova_stripped}' já está no itinerário.")
                else:
                    st.session_state.rota.append(nova_stripped)
                    st.rerun()
        with col_reset:
            if st.button("🗑️ Resetar", use_container_width=True):
                st.session_state.rota = list(ROTA_PADRAO[:1])
                st.rerun()

        st.markdown("**Paradas atuais:**")
        for idx, parada in enumerate(st.session_state.rota):
            c_nome, c_rem = st.columns([4, 1])
            c_nome.write(f"{idx + 1}. {parada}")
            if c_rem.button("✕", key=f"rm_{idx}", help=f"Remover {parada}"):
                st.session_state.rota.pop(idx)
                st.rerun()

    # Configuração do Veículo
    st.markdown("---")
    st.subheader("🚛 Configuração da Frota")
    modelo = st.selectbox("Modelo:", list(VEICULOS.keys()))
    eixos = VEICULOS[modelo]

    st.markdown("---")
    st.subheader("🚗 Parâmetros de Operação")
    velocidade_media = st.slider(
        "Velocidade Média (km/h):",
        VELOCIDADE_MIN,
        VELOCIDADE_MAX,
        VELOCIDADE_PADRAO,
        step=VELOCIDADE_STEP,
        help="Velocidade média utilizada para calcular o tempo de direção e as previsões de chegada (ETA).",
    )

    st.subheader("⚙️ Telemetria em Tempo Real")
    c_pneu, c_oleo = st.columns(2)
    c_pneu.metric("Pressão", "110 PSI", "✅")
    c_oleo.metric("Óleo", "85%", "⚠️")

# ---------------------------------------------------------------------------
# 4. PROCESSAMENTO DE DADOS
# ---------------------------------------------------------------------------

paradas_geocodificadas: list[tuple[str, tuple[float, float]]] = []
cidades_sem_coords: list[str] = []
for c in st.session_state.rota:
    coords = buscar_coords(c)
    if coords:
        paradas_geocodificadas.append((c, coords))
    else:
        cidades_sem_coords.append(c)

pontos_validos = [coords for _, coords in paradas_geocodificadas]

if cidades_sem_coords:
    st.warning(
        f"⚠️ Não foi possível localizar: {', '.join(cidades_sem_coords)}. "
        "Verifique os nomes e tente novamente.",
    )

geometria, dist_m = (
    calcular_rota_osrm(pontos_validos) if len(pontos_validos) >= 2 else ([], 0.0)
)
if len(pontos_validos) >= 2 and not geometria:
    st.warning("⚠️ Não foi possível calcular a rota via OSRM. Verifique sua conexão com a internet.")

dist_km = dist_m / 1000.0
custo_total, custo_pedagio = calcula_custos(dist_km, eixos)
custo_diesel_custo = custo_total - custo_pedagio
co2_diesel, co2_hibrido, co2_eletrico = calcular_co2(dist_km)

# ---------------------------------------------------------------------------
# 5. DASHBOARD PRINCIPAL
# ---------------------------------------------------------------------------
st.title(f"🚛 Yakult Tower {APP_VERSION} — Central de Inteligência")

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Distância Total", f"{dist_km:.1f} km")
m2.metric(
    "Custo Operacional",
    f"R$ {custo_total:,.2f}",
    help=f"Diesel: R$ {custo_diesel_custo:,.2f} | Pedágio: R$ {custo_pedagio:,.2f}",
)
m3.metric("Tempo Est. Direção", formatar_tempo_conducao(dist_km, velocidade_media))
m4.metric("Pegada CO₂", f"{co2_diesel:.1f} kg", "ESG")
m5.metric("Paradas", str(len(st.session_state.rota)))

# ---------------------------------------------------------------------------
# 6. MAPA TÁTICO (DARK MODE)
# ---------------------------------------------------------------------------
st.subheader("🗺️ Monitoramento Tático de Rota")
m = folium.Map(location=list(MAP_CENTER), zoom_start=MAP_ZOOM, tiles=MAP_TILES)

if geometria:
    folium_coords = [[p[1], p[0]] for p in geometria]
    folium.PolyLine(folium_coords, color=ROUTE_COLOUR, weight=5, opacity=0.8).add_to(m)

for cidade, coords in paradas_geocodificadas:
    folium.Marker(
        coords,
        popup=cidade,
        icon=folium.Icon(color="blue", icon="truck", prefix="fa"),
    ).add_to(m)

st_folium(m, width=1200, height=450, key="mapa_v5")

# ---------------------------------------------------------------------------
# 7. LOGÍSTICA PREDITIVA E ESG
# ---------------------------------------------------------------------------
col_plan, col_esg = st.columns([2, 1])

with col_plan:
    st.subheader("📅 Planejamento de Chegada (ETA)")
    h_partida = st.time_input("Horário de Partida:", datetime.time(8, 0))

    eta_list = calcular_eta_paradas(
        st.session_state.rota, dist_km, h_partida, velocidade_media,
    )
    df_eta = pd.DataFrame(eta_list)
    st.table(df_eta)
    st.download_button(
        "📥 Exportar ETA (CSV)",
        df_eta.to_csv(index=False),
        file_name="eta_rota.csv",
        mime="text/csv",
    )

with col_esg:
    st.subheader("📊 Sustentabilidade")
    dados_esg = pd.DataFrame({
        "Cenário": ["Diesel", "Híbrido", "Elétrico"],
        "CO₂ (kg)": [co2_diesel, co2_hibrido, co2_eletrico],
    })
    st.bar_chart(dados_esg, x="Cenário", y="CO₂ (kg)", color=ROUTE_COLOUR)

# ---------------------------------------------------------------------------
# 8. CADEIA DE FRIO
# ---------------------------------------------------------------------------
st.markdown("---")
st.subheader("🌡️ Integridade da Carga (Yakult Cold Chain)")
temp = st.slider("Temperatura do Baú (°C):", -2, 15, 4)
if temp > TEMP_CRITICO:
    st.error(f"🚨 ALERTA CRÍTICO: Temperatura em {temp}°C. Risco de perda de carga!")
elif temp > TEMP_ATENCAO:
    st.warning(f"⚠️ ATENÇÃO: Temperatura em {temp}°C. Monitore de perto.")
else:
    st.success(f"✅ Temperatura Estável: {temp}°C")

st.caption(
    f"{APP_TITLE} v{APP_VERSION} — {datetime.datetime.now(tz=datetime.timezone.utc).strftime('%d/%m/%Y %H:%M')} UTC",
)
