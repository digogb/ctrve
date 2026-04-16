"""Unit tests for calculate-fp.py — IFPUG CPM 4.3.1 matrices."""

import importlib.util
import pytest
from pathlib import Path

_script_path = Path(__file__).parent.parent / "calculate-fp.py"
_spec = importlib.util.spec_from_file_location("calculate_fp", _script_path)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

classify = _mod.classify
classify_batch = _mod.classify_batch


# --- ALI (Arquivo Logico Interno) ---
# Matrix: DER bands {1-19, 20-50, >50} x RLR bands {1, 2-5, >5}
# PF: Baixa=7, Media=10, Alta=15

def test_ali_low_low():
    r = classify("ALI", der=10, rlr=1)
    assert r["complexity"] == "Baixa"
    assert r["pf"] == 7


def test_ali_boundary_der_19_rlr_1():
    r = classify("ALI", der=19, rlr=1)
    assert r["complexity"] == "Baixa"
    assert r["pf"] == 7


def test_ali_boundary_der_20_rlr_1():
    r = classify("ALI", der=20, rlr=1)
    assert r["complexity"] == "Baixa"
    assert r["pf"] == 7


def test_ali_boundary_der_51_rlr_1():
    r = classify("ALI", der=51, rlr=1)
    assert r["complexity"] == "Media"
    assert r["pf"] == 10


def test_ali_mid_avg():
    r = classify("ALI", der=25, rlr=3)
    assert r["complexity"] == "Media"
    assert r["pf"] == 10


def test_ali_high_complexity():
    r = classify("ALI", der=60, rlr=6)
    assert r["complexity"] == "Alta"
    assert r["pf"] == 15


def test_ali_rlr_boundary_5_6():
    assert classify("ALI", der=10, rlr=5)["complexity"] == "Baixa"
    assert classify("ALI", der=10, rlr=6)["complexity"] == "Media"


# --- AIE (Arquivo de Interface Externa) ---
# Same matrix as ALI, different weights: Baixa=5, Media=7, Alta=10

def test_aie_low():
    r = classify("AIE", der=10, rlr=1)
    assert r["complexity"] == "Baixa"
    assert r["pf"] == 5


def test_aie_high():
    r = classify("AIE", der=60, rlr=6)
    assert r["complexity"] == "Alta"
    assert r["pf"] == 10


# --- EE (Entrada Externa) ---
# DER bands {1-4, 5-15, >15} x ALR bands {0-1, 2, >2}
# PF: Baixa=3, Media=4, Alta=6

def test_ee_low():
    r = classify("EE", der=3, alr=0)
    assert r["complexity"] == "Baixa"
    assert r["pf"] == 3


def test_ee_der_boundary_4_5():
    assert classify("EE", der=4, alr=1)["complexity"] == "Baixa"
    assert classify("EE", der=5, alr=1)["complexity"] == "Baixa"
    assert classify("EE", der=15, alr=2)["complexity"] == "Media"
    assert classify("EE", der=16, alr=2)["complexity"] == "Alta"


def test_ee_alr_boundary():
    # ALR 2 moves up a band vs. ALR 0-1
    assert classify("EE", der=10, alr=1)["complexity"] == "Baixa"
    assert classify("EE", der=10, alr=2)["complexity"] == "Media"
    assert classify("EE", der=10, alr=3)["complexity"] == "Alta"


def test_ee_high():
    r = classify("EE", der=20, alr=5)
    assert r["complexity"] == "Alta"
    assert r["pf"] == 6


# --- SE (Saida Externa) ---
# DER bands {1-5, 6-19, >19} x ALR bands {0-1, 2-3, >3}
# PF: Baixa=4, Media=5, Alta=7

def test_se_low():
    r = classify("SE", der=3, alr=0)
    assert r["complexity"] == "Baixa"
    assert r["pf"] == 4


def test_se_der_boundary_5_6():
    assert classify("SE", der=5, alr=1)["complexity"] == "Baixa"
    assert classify("SE", der=6, alr=1)["complexity"] == "Baixa"
    assert classify("SE", der=19, alr=2)["complexity"] == "Media"
    assert classify("SE", der=20, alr=2)["complexity"] == "Alta"


def test_se_alr_boundary():
    assert classify("SE", der=10, alr=1)["complexity"] == "Baixa"
    assert classify("SE", der=10, alr=3)["complexity"] == "Media"
    assert classify("SE", der=10, alr=4)["complexity"] == "Alta"


def test_se_high():
    r = classify("SE", der=25, alr=5)
    assert r["complexity"] == "Alta"
    assert r["pf"] == 7


# --- CE (Consulta Externa) ---
# Same DER/ALR matrix as SE; weights: Baixa=3, Media=4, Alta=6

def test_ce_low():
    r = classify("CE", der=3, alr=0)
    assert r["complexity"] == "Baixa"
    assert r["pf"] == 3


def test_ce_high():
    r = classify("CE", der=25, alr=5)
    assert r["complexity"] == "Alta"
    assert r["pf"] == 6


# --- Input validation ---

def test_missing_rlr_for_ali():
    with pytest.raises(ValueError, match="(?i)rlr"):
        classify("ALI", der=10)


def test_missing_alr_for_ee():
    with pytest.raises(ValueError, match="(?i)alr"):
        classify("EE", der=10)


def test_invalid_type():
    with pytest.raises(ValueError, match="Unknown type"):
        classify("XX", der=10, rlr=1)


def test_der_must_be_positive():
    with pytest.raises(ValueError):
        classify("ALI", der=0, rlr=1)


def test_lowercase_type_accepted():
    r = classify("ali", der=10, rlr=1)
    assert r["type"] == "ALI"
    assert r["pf"] == 7


# --- Batch mode ---

def test_classify_batch_preserves_metadata():
    functions = [
        {"id": "FD-001", "name": "Processo", "source": "US-003", "type": "ALI", "der": 15, "rlr": 2},
        {"id": "FT-001", "name": "Cadastrar", "source": "US-003, RN-002", "type": "EE", "der": 8, "alr": 2},
    ]
    results = classify_batch(functions)
    assert len(results) == 2
    assert results[0]["id"] == "FD-001"
    assert results[0]["source"] == "US-003"
    assert results[0]["complexity"] == "Baixa"
    assert results[0]["pf"] == 7
    assert results[1]["complexity"] == "Media"
    assert results[1]["pf"] == 4


def test_classify_batch_missing_der():
    with pytest.raises(ValueError, match="DER"):
        classify_batch([{"id": "X", "type": "ALI", "rlr": 1}])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
