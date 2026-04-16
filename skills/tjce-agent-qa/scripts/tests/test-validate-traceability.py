"""Unit tests for validate-traceability.py"""

import importlib.util
from pathlib import Path

_script_path = Path(__file__).parent.parent / "validate-traceability.py"
_spec = importlib.util.spec_from_file_location("validate_traceability", _script_path)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

extract_rn_ids = _mod.extract_rn_ids
extract_ct_rn_refs = _mod.extract_ct_rn_refs
validate_traceability = _mod.validate_traceability


# --- extract_rn_ids ---

def test_extract_rn_ids_basic():
    text = "| RN-001 | Regra um |\n| RN-002 | Regra dois |\n| RN-003 | Regra tres |"
    assert extract_rn_ids(text) == ["RN-001", "RN-002", "RN-003"]


def test_extract_rn_ids_empty():
    assert extract_rn_ids("no RNs here") == []


def test_extract_rn_ids_dedup():
    text = "RN-001 appears twice RN-001"
    assert extract_rn_ids(text) == ["RN-001"]


# --- extract_ct_rn_refs ---

def test_extract_ct_rn_refs_basic():
    text = """\
| ID | Titulo | RN | Tipo |
|----|--------|-----|------|
| CT-001 | Teste um | RN-001 | unitario |
| CT-002 | Teste dois | RN-001, RN-002 | unitario |
"""
    result = extract_ct_rn_refs(text)
    assert "CT-001" in result
    assert result["CT-001"] == ["RN-001"]
    assert "CT-002" in result
    assert result["CT-002"] == ["RN-001", "RN-002"]


def test_extract_ct_rn_refs_no_table():
    assert extract_ct_rn_refs("no table") == {}


# --- validate_traceability ---

def test_full_coverage():
    rn_ids = ["RN-001", "RN-002"]
    ct_rn_map = {
        "CT-001": ["RN-001"],
        "CT-002": ["RN-002"],
    }
    result = validate_traceability(rn_ids, ct_rn_map)
    assert result["all_covered"] is True
    assert result["uncovered_rn"] == []
    assert result["coverage_pct"] == 100.0


def test_partial_coverage():
    rn_ids = ["RN-001", "RN-002", "RN-003"]
    ct_rn_map = {"CT-001": ["RN-001"]}
    result = validate_traceability(rn_ids, ct_rn_map)
    assert result["all_covered"] is False
    assert set(result["uncovered_rn"]) == {"RN-002", "RN-003"}
    assert result["covered_rn"] == 1


def test_no_coverage():
    rn_ids = ["RN-001"]
    ct_rn_map = {}
    result = validate_traceability(rn_ids, ct_rn_map)
    assert result["all_covered"] is False
    assert result["uncovered_rn"] == ["RN-001"]


def test_empty_rns():
    result = validate_traceability([], {})
    assert result["all_covered"] is True
    assert result["coverage_pct"] == 0


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
