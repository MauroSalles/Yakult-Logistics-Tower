"""Tests for core calculation and configuration modules.

All tests are pure-Python unit tests that do NOT require a running Streamlit
server, so they execute in under a few seconds via ``pytest``.
"""

import datetime
import os
import sys

import pytest

# Ensure workspace root is on path so modules can be imported during tests.
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

# ── Config sanity checks ────────────────────────────────────────────────────


class TestConfig:
    """Validate that config values are within reasonable bounds."""

    def test_emission_constants_positive(self):
        assert EFICIENCIA_DIESEL_KM_L > 0
        assert CO2_DIESEL_KG_L > 0
        assert 0 < CO2_HIBRID_FATOR < 1

    def test_cost_parameters_positive(self):
        assert CUSTO_DIESEL_POR_KM > 0
        assert CUSTO_PEDAGIO_POR_EIXO_KM > 0

    def test_temperature_thresholds_ordered(self):
        assert TEMP_ATENCAO < TEMP_CRITICO

    def test_veiculos_catalogue_non_empty(self):
        assert len(VEICULOS) >= 1
        for label, axles in VEICULOS.items():
            assert isinstance(label, str)
            assert axles >= 2

    def test_rota_padrao_non_empty(self):
        assert len(ROTA_PADRAO) >= 1

    def test_aliases_match_config(self):
        """Backward-compat aliases in app_logistica must mirror config."""
        assert _EFICIENCIA_DIESEL_KM_L == EFICIENCIA_DIESEL_KM_L
        assert _CO2_DIESEL_KG_L == CO2_DIESEL_KG_L
        assert _CO2_HIBRID_FATOR == CO2_HIBRID_FATOR


# ── calcula_custos ───────────────────────────────────────────────────────────


def test_calcula_custos_zero_distance():
    total, ped = calcula_custos(0, 4)
    assert total == 0
    assert ped == 0


def test_calcula_custos_simple():
    total, ped = calcula_custos(100, 2)
    # diesel = 100*2.15 = 215; pedagio = 100*(2*0.48)=96 -> total = 311
    assert pytest.approx(total, rel=1e-3) == 311
    assert pytest.approx(ped, rel=1e-3) == 96


def test_calcula_custos_uses_config_constants():
    """Verify the function honours the centralised cost parameters."""
    dist, eixos = 200.0, 3
    total, ped = calcula_custos(dist, eixos)
    expected_ped = dist * (eixos * CUSTO_PEDAGIO_POR_EIXO_KM)
    expected_diesel = dist * CUSTO_DIESEL_POR_KM
    assert pytest.approx(ped, rel=1e-6) == expected_ped
    assert pytest.approx(total, rel=1e-6) == expected_diesel + expected_ped


def test_calcula_custos_large_distance():
    """Smoke test with a realistic long-haul distance."""
    total, ped = calcula_custos(5000, 6)
    assert total > 0
    assert ped > 0
    assert total > ped  # diesel cost is always > 0

# ── buscar_coords ────────────────────────────────────────────────────────────

# buscar_coords depends on external service; check that invalid input returns None

def test_buscar_coords_invalid():
    assert buscar_coords("CidadeInexistenteXYZ123") is None


def test_buscar_coords_empty_string():
    assert buscar_coords("") is None


# ── formatar_tempo_conducao ──────────────────────────────────────────────────

def test_formatar_tempo_conducao_zero():
    assert formatar_tempo_conducao(0) == "0h 00min"


def test_formatar_tempo_conducao_exact_hours():
    # 144 km at 72 km/h = 2 h exactly
    assert formatar_tempo_conducao(144) == "2h 00min"


def test_formatar_tempo_conducao_with_minutes():
    # 108 km at 72 km/h = 1.5 h = 1h 30min
    assert formatar_tempo_conducao(108) == "1h 30min"


def test_formatar_tempo_conducao_invalid_speed():
    assert formatar_tempo_conducao(100, velocidade=0) == "—"


def test_formatar_tempo_conducao_negative_speed():
    assert formatar_tempo_conducao(100, velocidade=-10) == "—"


def test_formatar_tempo_conducao_custom_speed():
    # 100 km at 100 km/h = 1 h exactly
    assert formatar_tempo_conducao(100, velocidade=100) == "1h 00min"


# ── calcular_eta_paradas ─────────────────────────────────────────────────────

def test_calcular_eta_paradas_single_stop():
    rota = ["Lorena, SP"]
    h = datetime.time(8, 0)
    eta = calcular_eta_paradas(rota, 500, h)
    assert len(eta) == 1
    # single stop should depart at h_partida with "Partida" status
    assert eta[0]["Previsão"] == "08:00"
    assert eta[0]["Status"] == "Partida 🚀"


def test_calcular_eta_paradas_first_stop_is_departure():
    rota = ["A", "B", "C"]
    h = datetime.time(8, 0)
    eta = calcular_eta_paradas(rota, 144, h)
    # first stop always at departure time with "Partida" status
    assert eta[0]["Previsão"] == "08:00"
    assert eta[0]["Status"] == "Partida 🚀"


def test_calcular_eta_paradas_last_stop_is_full_distance():
    rota = ["A", "B"]
    h = datetime.time(8, 0)
    # 144 km at 72 km/h = 2 h → arrive at 10:00
    eta = calcular_eta_paradas(rota, 144, h)
    assert eta[-1]["Previsão"] == "10:00"


def test_calcular_eta_paradas_intermediate_stop():
    rota = ["A", "B", "C"]
    h = datetime.time(8, 0)
    # 144 km total, 2 segments of 72 km each at 72 km/h = 1 h each
    eta = calcular_eta_paradas(rota, 144, h)
    assert eta[1]["Previsão"] == "09:00"
    assert eta[2]["Previsão"] == "10:00"


def test_calcular_eta_paradas_non_first_stops_status():
    rota = ["X", "Y", "Z"]
    h = datetime.time(6, 0)
    eta = calcular_eta_paradas(rota, 100, h)
    for row in eta[1:]:
        assert row["Status"] == "No Prazo ✅"


def test_calcular_eta_paradas_custom_speed():
    rota = ["A", "B"]
    h = datetime.time(0, 0)
    # 100 km at 100 km/h = 1 h
    eta = calcular_eta_paradas(rota, 100, h, velocidade=100)
    assert eta[-1]["Previsão"] == "01:00"


def test_calcular_eta_paradas_zero_distance():
    """All stops at same time when distance is zero."""
    rota = ["A", "B", "C"]
    h = datetime.time(10, 0)
    eta = calcular_eta_paradas(rota, 0, h)
    for row in eta:
        assert row["Previsão"] == "10:00"


# ── calcular_co2 ─────────────────────────────────────────────────────────────

def test_calcular_co2_zero_distance():
    diesel, hibrido, eletrico = calcular_co2(0)
    assert diesel == 0.0
    assert hibrido == 0.0
    assert eletrico == 0.0


def test_calcular_co2_electric_always_zero():
    _, _, eletrico = calcular_co2(5000)
    assert eletrico == 0.0


def test_calcular_co2_diesel_formula():
    dist = 320.0  # 100 litres at 3.2 km/L
    diesel, _, _ = calcular_co2(dist)
    expected = (dist / _EFICIENCIA_DIESEL_KM_L) * _CO2_DIESEL_KG_L
    assert pytest.approx(diesel, rel=1e-6) == expected


def test_calcular_co2_hybrid_is_fraction_of_diesel():
    dist = 500.0
    diesel, hibrido, _ = calcular_co2(dist)
    assert pytest.approx(hibrido, rel=1e-6) == diesel * _CO2_HIBRID_FATOR


def test_calcular_co2_hybrid_less_than_diesel():
    dist = 1000.0
    diesel, hibrido, _ = calcular_co2(dist)
    assert hibrido < diesel


def test_calcular_co2_metric_matches_chart():
    """Metric and ESG chart should use the same formula (no inconsistency)."""
    dist = 1000.0
    diesel, hibrido, _ = calcular_co2(dist)
    # Both are derived from the same constants — verify ratio is stable
    assert pytest.approx(hibrido / diesel, rel=1e-6) == _CO2_HIBRID_FATOR

