import datetime
import os
import sys
import pytest

# ensure workspace root is on path so modules can be imported during tests
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app_logistica import calcula_custos, buscar_coords, formatar_tempo_conducao, calcular_eta_paradas


def test_calcula_custos_zero_distance():
    total, ped = calcula_custos(0, 4)
    assert total == 0
    assert ped == 0


def test_calcula_custos_simple():
    total, ped = calcula_custos(100, 2)
    # diesel = 100*2.15 = 215; pedagio = 100*(2*0.48)=96 -> total = 311
    assert pytest.approx(total, rel=1e-3) == 311
    assert pytest.approx(ped, rel=1e-3) == 96

# buscar_coords depends on external service; check that invalid input returns None

def test_buscar_coords_invalid():
    assert buscar_coords("CidadeInexistenteXYZ123") is None


# --- formatar_tempo_conducao ---

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


# --- calcular_eta_paradas ---

def test_calcular_eta_paradas_single_stop():
    rota = ["Lorena, SP"]
    h = datetime.time(8, 0)
    eta = calcular_eta_paradas(rota, 500, h)
    assert len(eta) == 1
    # single stop should depart at h_partida
    assert eta[0]["Previsão"] == "08:00"


def test_calcular_eta_paradas_origin_is_departure_time():
    rota = ["A", "B", "C"]
    h = datetime.time(8, 0)
    eta = calcular_eta_paradas(rota, 144, h)
    # first stop always at departure time
    assert eta[0]["Previsão"] == "08:00"


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


def test_calcular_eta_paradas_status_field():
    rota = ["X", "Y"]
    h = datetime.time(6, 0)
    eta = calcular_eta_paradas(rota, 100, h)
    for row in eta:
        assert row["Status"] == "No Prazo ✅"

