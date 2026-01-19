import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
import requests
import pandas as pd
import datetime

# 1. SETUP DE ALTA PERFORMANCE
st.set_page_config(page_title="Yakult Elite Logistics", layout="wide", page_icon="🚀")
geolocator = Nominatim(user_agent="yakult_elite_v5")

# Estilo para os Cards de Métricas
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 28px; color: #1E88E5; }
    .stDataFrame { border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. MOTORES DE CÁLCULO
@st.cache_data
def buscar_coords(cidade):
    try:
        loc = geolocator.geocode(cidade)
        return (loc.latitude, loc.longitude) if loc else None
    except: return None

def calcular_rota_osrm(pontos):
    locs = ";".join([f"{lon},{lat}" for lat, lon in pontos])
    url = f"http://router.project-osrm.org/route/v1/driving/{locs}?overview=full&geometries=geojson"
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        if data['code'] == 'Ok':
            return data['routes'][0]['geometry']['coordinates'], data['routes'][0]['distance']
    except: return None, 0
    return None, 0

# 3. BARRA LATERAL - TELEMETRIA E CONFIGURAÇÃO
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/f/f1/Yakult_Logo.svg/2560px-Yakult_Logo.svg.png", width=120)
    st.title("🎮 Centro de Comando")
    
    # Gestão de Itinerário
    if 'rota' not in st.session_state:
        st.session_state.rota = ["Lorena, SP, Brazil", "Buenos Aires, Argentina", "Santiago, Chile"]
    
    with st.expander("📍 Editar Itinerário", expanded=False):
        nova_cidade = st.text_input("Nova Parada:")
        if st.button("➕ Adicionar"):
            st.session_state.rota.append(nova_cidade); st.rerun()
        if st.button("🗑️ Resetar"):
            st.session_state.rota = ["Lorena, SP, Brazil"]; st.rerun()

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
pontos_validos = []
for c in st.session_state.rota:
    coords = buscar_coords(c)
    if coords: pontos_validos.append(coords)

geometria, dist_m = calcular_rota_osrm(pontos_validos)
dist_km = dist_m / 1000
custo_diesel = dist_km * 2.15
custo_pedagio = dist_km * (eixos * 0.48) # Estimativa por eixo/km
custo_total = custo_diesel + custo_pedagio

# 5. DASHBOARD PRINCIPAL
st.title("🚛 Yakult Tower 5.0 - Central de Inteligência")

m1, m2, m3, m4 = st.columns(4)
m1.metric("Distância Total", f"{dist_km:.1f} km")
m2.metric("Custo Operacional", f"R$ {custo_total:.2f}", f"Eixos: {eixos}")
m3.metric("Tempo Est. Direção", f"{int(dist_km/72)}h")
m4.metric("Pegada CO2", f"{(dist_km/3.2)*2.61:.1f} kg", "ESG")

# 6. MAPA TÁTICO (DARK MODE)
st.subheader("🗺️ Monitoramento Tático de Rota")
m = folium.Map(location=[-28.0, -55.0], zoom_start=4, tiles="cartodb dark_matter")

if geometria:
    folium_coords = [[p[1], p[0]] for p in geometria]
    folium.PolyLine(folium_coords, color="#00FFCC", weight=5, opacity=0.8).add_to(m)

for i, coords in enumerate(pontos_validos):
    folium.Marker(coords, popup=st.session_state.rota[i], 
                  icon=folium.Icon(color='blue', icon='truck', prefix='fa')).add_to(m)

st_folium(m, width=1200, height=450, key="mapa_v5")

# 7. LOGÍSTICA PREDITIVA E ESG
col_plan, col_esg = st.columns([2, 1])

with col_plan:
    st.subheader("📅 Planejamento de Chegada (ETA)")
    h_partida = st.time_input("Horário de Partida:", datetime.time(8, 0))
    
    eta_list = []
    tempo_total = 0
    for i, cid in enumerate(st.session_state.rota):
        parada_km = (dist_km / len(st.session_state.rota)) * i
        tempo_h = parada_km / 72
        chegada = (datetime.datetime.combine(datetime.date.today(), h_partida) + datetime.timedelta(hours=tempo_h))
        eta_list.append({"Cidade": cid, "Previsão": chegada.strftime("%H:%M"), "Status": "No Prazo ✅"})
    
    st.table(pd.DataFrame(eta_list))

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
else:
    st.success(f"✅ Temperatura Estável: {temp}°C")

st.caption(f"Yakult Elite Logistics v5.0 - {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}")