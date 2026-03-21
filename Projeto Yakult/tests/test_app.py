"""Testes para os módulos de cálculo e configuração.

Todos os testes são testes unitários Python puros que NÃO exigem um servidor
Streamlit em execução, então rodam em poucos segundos via ``pytest``.
"""

import datetime
import os
import sys

import pytest

# Garante que a raiz do workspace esteja no path para importação dos módulos.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app_logistica import (
    _CO2_DIESEL_KG_L,
    _CO2_HIBRID_FATOR,
    _EFICIENCIA_DIESEL_KM_L,
    buscar_coords,
    calcula_custos,
    calcular_co2,
    calcular_eta_paradas,
    formatar_tempo_conducao,
)
from config import (
    CO2_DIESEL_KG_L,
    CO2_HIBRID_FATOR,
    CUSTO_DIESEL_POR_KM,
    CUSTO_PEDAGIO_POR_EIXO_KM,
    EFICIENCIA_DIESEL_KM_L,
    ROTA_PADRAO,
    TEMP_ATENCAO,
    TEMP_CRITICO,
    VEICULOS,
)

# ── Verificações de sanidade da configuração ────────────────────────────────


class TestConfig:
    """Valida que os valores de configuração estão dentro de limites razoáveis."""

    def test_constantes_emissao_positivas(self):
        assert EFICIENCIA_DIESEL_KM_L > 0
        assert CO2_DIESEL_KG_L > 0
        assert 0 < CO2_HIBRID_FATOR < 1

    def test_parametros_custo_positivos(self):
        assert CUSTO_DIESEL_POR_KM > 0
        assert CUSTO_PEDAGIO_POR_EIXO_KM > 0

    def test_limiares_temperatura_ordenados(self):
        assert TEMP_ATENCAO < TEMP_CRITICO

    def test_catalogo_veiculos_nao_vazio(self):
        assert len(VEICULOS) >= 1
        for rotulo, eixos in VEICULOS.items():
            assert isinstance(rotulo, str)
            assert eixos >= 2

    def test_rota_padrao_nao_vazia(self):
        assert len(ROTA_PADRAO) >= 1

    def test_aliases_correspondem_config(self):
        """Aliases de compatibilidade em app_logistica devem espelhar config."""
        assert _EFICIENCIA_DIESEL_KM_L == EFICIENCIA_DIESEL_KM_L
        assert _CO2_DIESEL_KG_L == CO2_DIESEL_KG_L
        assert _CO2_HIBRID_FATOR == CO2_HIBRID_FATOR


# ── calcula_custos ───────────────────────────────────────────────────────────


def test_calcula_custos_distancia_zero():
    total, ped = calcula_custos(0, 4)
    assert total == 0
    assert ped == 0


def test_calcula_custos_simples():
    total, ped = calcula_custos(100, 2)
    # diesel = 100*2.15 = 215; pedagio = 100*(2*0.48)=96 -> total = 311
    assert pytest.approx(total, rel=1e-3) == 311
    assert pytest.approx(ped, rel=1e-3) == 96


def test_calcula_custos_usa_constantes_config():
    """Verifica se a função respeita os parâmetros centralizados de custo."""
    dist, eixos = 200.0, 3
    total, ped = calcula_custos(dist, eixos)
    expected_ped = dist * (eixos * CUSTO_PEDAGIO_POR_EIXO_KM)
    expected_diesel = dist * CUSTO_DIESEL_POR_KM
    assert pytest.approx(ped, rel=1e-6) == expected_ped
    assert pytest.approx(total, rel=1e-6) == expected_diesel + expected_ped


def test_calcula_custos_distancia_grande():
    """Teste de fumaça com uma distância realista de longa distância."""
    total, ped = calcula_custos(5000, 6)
    assert total > 0
    assert ped > 0
    assert total > ped  # custo diesel é sempre > 0

# ── buscar_coords ────────────────────────────────────────────────────────────

# buscar_coords depende de serviço externo; verifica que entrada inválida retorna None

def test_buscar_coords_invalido():
    assert buscar_coords("CidadeInexistenteXYZ123") is None


def test_buscar_coords_string_vazia():
    assert buscar_coords("") is None


# ── formatar_tempo_conducao ──────────────────────────────────────────────────

def test_formatar_tempo_conducao_zero():
    assert formatar_tempo_conducao(0) == "0h 00min"


def test_formatar_tempo_conducao_horas_exatas():
    # 144 km a 72 km/h = 2 h exatas
    assert formatar_tempo_conducao(144) == "2h 00min"


def test_formatar_tempo_conducao_com_minutos():
    # 108 km a 72 km/h = 1.5 h = 1h 30min
    assert formatar_tempo_conducao(108) == "1h 30min"


def test_formatar_tempo_conducao_velocidade_invalida():
    assert formatar_tempo_conducao(100, velocidade=0) == "—"


def test_formatar_tempo_conducao_velocidade_negativa():
    assert formatar_tempo_conducao(100, velocidade=-10) == "—"


def test_formatar_tempo_conducao_velocidade_customizada():
    # 100 km a 100 km/h = 1 h exata
    assert formatar_tempo_conducao(100, velocidade=100) == "1h 00min"


# ── calcular_eta_paradas ─────────────────────────────────────────────────────

def test_calcular_eta_paradas_parada_unica():
    rota = ["Lorena, SP"]
    h = datetime.time(8, 0)
    eta = calcular_eta_paradas(rota, 500, h)
    assert len(eta) == 1
    # parada única deve partir no h_partida com status "Partida"
    assert eta[0]["Previsão"] == "08:00"
    assert eta[0]["Status"] == "Partida 🚀"


def test_calcular_eta_paradas_primeira_parada_e_partida():
    rota = ["A", "B", "C"]
    h = datetime.time(8, 0)
    eta = calcular_eta_paradas(rota, 144, h)
    # primeira parada sempre no horário de partida com status "Partida"
    assert eta[0]["Previsão"] == "08:00"
    assert eta[0]["Status"] == "Partida 🚀"


def test_calcular_eta_paradas_ultima_parada_distancia_total():
    rota = ["A", "B"]
    h = datetime.time(8, 0)
    # 144 km a 72 km/h = 2 h → chegada às 10:00
    eta = calcular_eta_paradas(rota, 144, h)
    assert eta[-1]["Previsão"] == "10:00"


def test_calcular_eta_paradas_parada_intermediaria():
    rota = ["A", "B", "C"]
    h = datetime.time(8, 0)
    # 144 km total, 2 segmentos de 72 km cada a 72 km/h = 1 h cada
    eta = calcular_eta_paradas(rota, 144, h)
    assert eta[1]["Previsão"] == "09:00"
    assert eta[2]["Previsão"] == "10:00"


def test_calcular_eta_paradas_status_paradas_nao_iniciais():
    rota = ["X", "Y", "Z"]
    h = datetime.time(6, 0)
    eta = calcular_eta_paradas(rota, 100, h)
    for row in eta[1:]:
        assert row["Status"] == "No Prazo ✅"


def test_calcular_eta_paradas_velocidade_customizada():
    rota = ["A", "B"]
    h = datetime.time(0, 0)
    # 100 km a 100 km/h = 1 h
    eta = calcular_eta_paradas(rota, 100, h, velocidade=100)
    assert eta[-1]["Previsão"] == "01:00"


def test_calcular_eta_paradas_distancia_zero():
    """Todas as paradas no mesmo horário quando a distância é zero."""
    rota = ["A", "B", "C"]
    h = datetime.time(10, 0)
    eta = calcular_eta_paradas(rota, 0, h)
    for row in eta:
        assert row["Previsão"] == "10:00"


# ── calcular_co2 ─────────────────────────────────────────────────────────────

def test_calcular_co2_distancia_zero():
    diesel, hibrido, eletrico = calcular_co2(0)
    assert diesel == 0.0
    assert hibrido == 0.0
    assert eletrico == 0.0


def test_calcular_co2_eletrico_sempre_zero():
    _, _, eletrico = calcular_co2(5000)
    assert eletrico == 0.0


def test_calcular_co2_formula_diesel():
    dist = 320.0  # 100 litros a 3.2 km/L
    diesel, _, _ = calcular_co2(dist)
    expected = (dist / _EFICIENCIA_DIESEL_KM_L) * _CO2_DIESEL_KG_L
    assert pytest.approx(diesel, rel=1e-6) == expected


def test_calcular_co2_hibrido_e_fracao_do_diesel():
    dist = 500.0
    diesel, hibrido, _ = calcular_co2(dist)
    assert pytest.approx(hibrido, rel=1e-6) == diesel * _CO2_HIBRID_FATOR


def test_calcular_co2_hibrido_menor_que_diesel():
    dist = 1000.0
    diesel, hibrido, _ = calcular_co2(dist)
    assert hibrido < diesel


def test_calcular_co2_metrica_igual_grafico():
    """A métrica e o gráfico ESG devem usar a mesma fórmula (sem inconsistência)."""
    dist = 1000.0
    diesel, hibrido, _ = calcular_co2(dist)
    # Ambos derivam das mesmas constantes — verificar que a proporção é estável
    assert pytest.approx(hibrido / diesel, rel=1e-6) == _CO2_HIBRID_FATOR

