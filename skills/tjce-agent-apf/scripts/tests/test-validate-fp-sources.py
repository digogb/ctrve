"""Unit tests for validate-fp-sources.py"""

import importlib.util
from pathlib import Path

_script_path = Path(__file__).parent.parent / "validate-fp-sources.py"
_spec = importlib.util.spec_from_file_location("validate_fp_sources", _script_path)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

extract_us_ids = _mod.extract_us_ids
extract_rn_ids = _mod.extract_rn_ids
extract_functions = _mod.extract_functions
validate_sources = _mod.validate_sources


# --- ID extraction ---

def test_extract_us_ids():
    assert extract_us_ids("US-001 e US-002 e US-001") == {"US-001", "US-002"}


def test_extract_rn_ids():
    assert extract_rn_ids("RN-001 e RN-003") == {"RN-001", "RN-003"}


def test_extract_ids_empty():
    assert extract_us_ids("no ids") == set()
    assert extract_rn_ids("no ids") == set()


# --- Function extraction ---

def test_extract_functions_basic():
    text = """\
# Contagem

## Funcoes de Dados

| ID | Nome | Tipo | DER | RLR | Complexidade | PF | Fonte (US/RN) |
|----|------|------|-----|-----|--------------|----|---------------|
| FD-001 | Processo | ALI | 15 | 2 | Baixa | 7 | US-003, RN-001 |
| FD-002 | Parte | ALI | 10 | 1 | Baixa | 7 | US-003 |

## Funcoes Transacionais

| ID | Nome | Tipo | DER | ALR | Complexidade | PF | Fonte (US/RN) |
|----|------|------|-----|-----|--------------|----|---------------|
| FT-001 | Cadastrar | EE | 12 | 2 | Media | 4 | US-003, RN-002 |
"""
    fns = extract_functions(text)
    assert len(fns) == 3
    assert fns[0]["id"] == "FD-001"
    assert set(fns[0]["sources"]) == {"US-003", "RN-001"}
    assert fns[2]["id"] == "FT-001"
    assert fns[2]["type"] == "EE"


def test_extract_functions_skips_headers():
    text = """\
| ID | Nome | Tipo | Fonte (US/RN) |
|----|------|------|---------------|
| FD-001 | A | ALI | US-001 |
"""
    fns = extract_functions(text)
    assert len(fns) == 1
    assert fns[0]["id"] == "FD-001"


def test_extract_functions_empty():
    assert extract_functions("no tables here") == []


# --- Validation ---

def test_all_sourced_valid():
    fns = [
        {"id": "FD-001", "name": "A", "type": "ALI", "source_cell": "US-001",
         "sources": ["US-001"]},
        {"id": "FT-001", "name": "B", "type": "EE", "source_cell": "RN-001",
         "sources": ["RN-001"]},
    ]
    result = validate_sources(fns, {"US-001"}, {"RN-001"})
    assert result["valid"] is True
    assert result["sourceless"] == []
    assert result["orphan"] == []


def test_sourceless_function():
    fns = [
        {"id": "FD-001", "name": "A", "type": "ALI", "source_cell": "",
         "sources": []},
    ]
    result = validate_sources(fns, {"US-001"}, {"RN-001"})
    assert result["valid"] is False
    assert len(result["sourceless"]) == 1
    assert result["sourceless"][0]["id"] == "FD-001"


def test_orphan_function():
    fns = [
        {"id": "FD-001", "name": "A", "type": "ALI", "source_cell": "US-999",
         "sources": ["US-999"]},
    ]
    result = validate_sources(fns, {"US-001"}, {"RN-001"})
    assert result["valid"] is False
    assert len(result["orphan"]) == 1
    assert "US-999" in result["orphan"][0]["invalid_refs"]


def test_partial_orphan():
    # Function has one valid and one invalid reference — still orphan
    fns = [
        {"id": "FD-001", "name": "A", "type": "ALI",
         "source_cell": "US-001, RN-999", "sources": ["US-001", "RN-999"]},
    ]
    result = validate_sources(fns, {"US-001"}, {"RN-001"})
    assert result["valid"] is False
    assert result["orphan"][0]["invalid_refs"] == ["RN-999"]


def test_empty_function_list():
    result = validate_sources([], {"US-001"}, {"RN-001"})
    assert result["valid"] is True
    assert result["total_functions"] == 0


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
