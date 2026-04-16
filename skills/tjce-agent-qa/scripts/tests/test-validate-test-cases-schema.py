"""Unit tests for validate-test-cases-schema.py"""

import importlib.util
from pathlib import Path

_script_path = Path(__file__).parent.parent / "validate-test-cases-schema.py"
_spec = importlib.util.spec_from_file_location("validate_test_cases_schema", _script_path)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

parse_table = _mod.parse_table
validate_schema = _mod.validate_schema


# --- parse_table ---

def test_parse_table_basic():
    text = """\
| ID | Titulo | RN | Pre-condicao | Passos | Resultado Esperado | Tipo |
|----|--------|-----|--------------|--------|-------------------|------|
| CT-001 | Teste | RN-001 | Nenhuma | Clicar | Sucesso | unitario |
"""
    headers, rows = parse_table(text)
    assert "ID" in headers
    assert len(rows) == 1
    assert rows[0]["ID"] == "CT-001"


def test_parse_table_empty():
    headers, rows = parse_table("no table here")
    assert headers == []
    assert rows == []


# --- validate_schema ---

def test_valid_schema():
    headers = ["ID", "Titulo", "RN", "Pre-condicao", "Passos", "Resultado Esperado", "Tipo"]
    rows = [
        {"ID": "CT-001", "Titulo": "Teste", "RN": "RN-001", "Pre-condicao": "N/A",
         "Passos": "1. Fazer algo", "Resultado Esperado": "Sucesso", "Tipo": "unitario"},
    ]
    result = validate_schema(headers, rows)
    assert result["valid"] is True
    assert result["violations"] == []


def test_missing_column():
    headers = ["ID", "Titulo", "RN"]
    rows = [{"ID": "CT-001", "Titulo": "Teste", "RN": "RN-001"}]
    result = validate_schema(headers, rows)
    assert result["valid"] is False
    assert "Pre-condicao" in result["missing_columns"]


def test_empty_cell():
    headers = ["ID", "Titulo", "RN", "Pre-condicao", "Passos", "Resultado Esperado", "Tipo"]
    rows = [
        {"ID": "CT-001", "Titulo": "", "RN": "RN-001", "Pre-condicao": "N/A",
         "Passos": "1. Fazer", "Resultado Esperado": "OK", "Tipo": "unitario"},
    ]
    result = validate_schema(headers, rows)
    assert result["valid"] is False
    assert any("Titulo" in v["issue"] for v in result["violations"])


def test_todo_placeholder():
    headers = ["ID", "Titulo", "RN", "Pre-condicao", "Passos", "Resultado Esperado", "Tipo"]
    rows = [
        {"ID": "CT-001", "Titulo": "TODO", "RN": "RN-001", "Pre-condicao": "N/A",
         "Passos": "1. Fazer", "Resultado Esperado": "OK", "Tipo": "unitario"},
    ]
    result = validate_schema(headers, rows)
    assert result["valid"] is False
    assert any("placeholder" in v["issue"] for v in result["violations"])


def test_invalid_id_format():
    headers = ["ID", "Titulo", "RN", "Pre-condicao", "Passos", "Resultado Esperado", "Tipo"]
    rows = [
        {"ID": "TC-01", "Titulo": "Teste", "RN": "RN-001", "Pre-condicao": "N/A",
         "Passos": "1. Fazer", "Resultado Esperado": "OK", "Tipo": "unitario"},
    ]
    result = validate_schema(headers, rows)
    assert result["valid"] is False
    assert any("CT-NNN" in v["issue"] for v in result["violations"])


def test_invalid_tipo():
    headers = ["ID", "Titulo", "RN", "Pre-condicao", "Passos", "Resultado Esperado", "Tipo"]
    rows = [
        {"ID": "CT-001", "Titulo": "Teste", "RN": "RN-001", "Pre-condicao": "N/A",
         "Passos": "1. Fazer", "Resultado Esperado": "OK", "Tipo": "stress"},
    ]
    result = validate_schema(headers, rows)
    assert result["valid"] is False
    assert any("stress" in v["issue"] for v in result["violations"])


def test_valid_types():
    headers = ["ID", "Titulo", "RN", "Pre-condicao", "Passos", "Resultado Esperado", "Tipo"]
    for tipo in ["unitario", "integracao", "e2e"]:
        rows = [
            {"ID": "CT-001", "Titulo": "Teste", "RN": "RN-001", "Pre-condicao": "N/A",
             "Passos": "1. Fazer", "Resultado Esperado": "OK", "Tipo": tipo},
        ]
        result = validate_schema(headers, rows)
        assert result["valid"] is True, f"Type '{tipo}' should be valid"


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
