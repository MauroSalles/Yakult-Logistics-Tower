import os
import sys
import pytest

# ensure workspace root is on path so modules can be imported during tests
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app_logistica import calcula_custos, buscar_coords


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
