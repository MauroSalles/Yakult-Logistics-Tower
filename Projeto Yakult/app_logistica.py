import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
import requests
import pandas as pd
import datetime

# 1. SETUP DE ALTA PERFORMANCE
import logging

st.set_page_config(page_title="Yakult Elite Logistics", layout="wide", page_icon="🚀")

# configure basic logging to console
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s:%(message)s')
logger = logging.getLogger(__name__)

# geocoder instance reused across calls
geolocator = Nominatim(user_agent="yakult_elite_v5")

# Estilo para os Cards de Métricas
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 28px; color: #1E88E5; }
    .stDataFrame { border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. MOTORES DE CÁLCULO

@st.cache_data(show_spinner=False)
def buscar_coords(cidade: str) -> tuple[float, float] | None:
    """Return latitude/longitude for a city string or None on failure.
    Caching avoids repeated network calls during the same session.
    """
    try:
        loc = geolocator.geocode(cidade)
        if loc:
            logger.debug(f"Geocoded {cidade} -> {loc.latitude},{loc.longitude}")
            return (loc.latitude, loc.longitude)
        else:
            logger.warning(f"Não foi possível geocodificar: {cidade}")
    except Exception as e:
        logger.error(f"Erro ao geocodificar {cidade}: {e}")
    return None

def calcular_rota_osrm(pontos: list[tuple[float, float]]) -> tuple[list, float]:
    """Call OSRM public API to compute a driving route passing through `pontos`.

    Returns a tuple (geometry, distance_meters). Geometry is a list of [lon,lat] points.
    """
    locs = ";".join([f"{lon},{lat}" for lat, lon in pontos])
    url = f"http://router.project-osrm.org/route/v1/driving/{locs}?overview=full&geometries=geojson"
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        if data.get('code') == 'Ok':
            return data['routes'][0]['geometry']['coordinates'], data['routes'][0]['distance']
        else:
            logger.warning("OSRM retornou código diferente de Ok: %s", data.get('code'))
    except requests.RequestException as e:
        logger.error(f"Falha na chamada OSRM: {e}")
    return [], 0.0

def calcula_custos(dist_km: float, eixos: int) -> tuple[float, float]:
    """Return (custo_total, custo_pedagio) for a given distance and number of eixo."""
    custo_diesel = dist_km * 2.15
    custo_pedagio = dist_km * (eixos * 0.48)
    custo_total = custo_diesel + custo_pedagio
    return custo_total, custo_pedagio

def formatar_tempo_conducao(dist_km: float, velocidade: float = 72.0) -> str:
    """Return driving time as a human-readable string (e.g. '14h 30min')."""
    if velocidade <= 0:
        return "—"
    total_min = int((dist_km / velocidade) * 60)
    hrs = total_min // 60
    mins = total_min % 60
    return f"{hrs}h {mins:02d}min"

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
    eta_list = []
    for i, cid in enumerate(rota):
        parada_km = (dist_km / (n - 1)) * i if n > 1 else 0.0
        tempo_h = parada_km / velocidade if velocidade > 0 else 0.0
        chegada = datetime.datetime.combine(datetime.date.today(), h_partida) + datetime.timedelta(hours=tempo_h)
        eta_list.append({"Cidade": cid, "Previsão": chegada.strftime("%H:%M"), "Status": "No Prazo ✅"})
    return eta_list

# 3. BARRA LATERAL - TELEMETRIA E CONFIGURAÇÃO
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/f/f1/Yakult_Logo.svg/2560px-Yakult_Logo.svg.png", width=120)
    st.title("🎮 Centro de Comando")

    # Gestão de Itinerário
    if 'rota' not in st.session_state:
        st.session_state.rota = ["Lorena, SP, Brazil", "Buenos Aires, Argentina", "Santiago, Chile"]

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
                st.session_state.rota = ["Lorena, SP, Brazil"]
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
    modelo = st.selectbox("Modelo:", ["Carreta (6 eixos)", "Truck (3 eixos)", "VUC (2 eixos)"])
    eixos = 6 if "6" in modelo else 3 if "3" in modelo else 2

    st.subheader("⚙️ Telemetria em Tempo Real")
    c_pneu, c_oleo = st.columns(2)
    c_pneu.metric("Pressão", "110 PSI", "✅")
    c_oleo.metric("Óleo", "85%", "⚠️")

# 4. PROCESSAMENTO DE DADOS

pontos_validos: list[tuple[float, float]] = []
cidades_sem_coords: list[str] = []
for c in st.session_state.rota:
    coords = buscar_coords(c)
    if coords:
        pontos_validos.append(coords)
    else:
        cidades_sem_coords.append(c)

if cidades_sem_coords:
    st.warning(f"⚠️ Não foi possível localizar: {', '.join(cidades_sem_coords)}. Verifique os nomes e tente novamente.")

geometria, dist_m = calcular_rota_osrm(pontos_validos) if len(pontos_validos) >= 2 else ([], 0.0)
dist_km = dist_m / 1000.0
custo_total, custo_pedagio = calcula_custos(dist_km, eixos)
custo_diesel = custo_total - custo_pedagio

# 5. DASHBOARD PRINCIPAL
st.title("🚛 Yakult Tower 5.0 - Central de Inteligência")

m1, m2, m3, m4 = st.columns(4)
m1.metric("Distância Total", f"{dist_km:.1f} km")
m2.metric(
    "Custo Operacional",
    f"R$ {custo_total:.2f}",
    help=f"Diesel: R$ {custo_diesel:.2f} | Pedágio: R$ {custo_pedagio:.2f}",
)
m3.metric("Tempo Est. Direção", formatar_tempo_conducao(dist_km))
m4.metric("Pegada CO2", f"{(dist_km/3.2)*2.61:.1f} kg", "ESG")

# 6. MAPA TÁTICO (DARK MODE)
st.subheader("🗺️ Monitoramento Tático de Rota")
m = folium.Map(location=[-28.0, -55.0], zoom_start=4, tiles="cartodb dark_matter")

if geometria:
    folium_coords = [[p[1], p[0]] for p in geometria]
    folium.PolyLine(folium_coords, color="#00FFCC", weight=5, opacity=0.8).add_to(m)

for i, coords in enumerate(pontos_validos):
    folium.Marker(
        coords,
        popup=st.session_state.rota[i],
        icon=folium.Icon(color='blue', icon='truck', prefix='fa'),
    ).add_to(m)

st_folium(m, width=1200, height=450, key="mapa_v5")

# 7. LOGÍSTICA PREDITIVA E ESG
col_plan, col_esg = st.columns([2, 1])

with col_plan:
    st.subheader("📅 Planejamento de Chegada (ETA)")
    h_partida = st.time_input("Horário de Partida:", datetime.time(8, 0))

    eta_list = calcular_eta_paradas(st.session_state.rota, dist_km, h_partida)
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
        'Cenário': ['Diesel', 'Híbrido', 'Elétrico'],
        'CO2 (kg)': [((dist_km/3)*2.6), ((dist_km/3)*1.4), 0]
    })
    st.bar_chart(dados_esg, x='Cenário', y='CO2 (kg)', color="#00FFCC")

# 8. CADEIA DE FRIO
st.markdown("---")
st.subheader("🌡️ Integridade da Carga (Yakult Cold Chain)")
temp = st.slider("Temperatura do Baú (°C):", -2, 15, 4)
if temp > 8:
    st.error(f"🚨 ALERTA CRÍTICO: Temperatura em {temp}°C. Risco de perda de carga!")
elif temp > 6:
    st.warning(f"⚠️ ATENÇÃO: Temperatura em {temp}°C. Monitore de perto.")
else:
    st.success(f"✅ Temperatura Estável: {temp}°C")

st.caption(f"Yakult Elite Logistics v5.0 - {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}")