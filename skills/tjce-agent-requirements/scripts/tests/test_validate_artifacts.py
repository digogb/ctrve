"""Unit tests for validate-artifacts.py"""

import sys
from pathlib import Path

# Add parent directory to path so we can import the script
sys.path.insert(0, str(Path(__file__).parent.parent))

from validate_artifacts import (
    check_cross_refs,
    check_empty_cells,
    check_msg_type_coverage,
    check_na_justification,
    check_sequential_ids,
    count_coverage,
    extract_id_refs,
    extract_ids,
    parse_markdown_table,
)


# --- parse_markdown_table ---

def test_parse_markdown_table_basic():
    content = """
| ID | Descricao | Estoria |
|----|-----------|---------|
| RN-001 | Regra um | US-001 |
| RN-002 | Regra dois | US-001, US-002 |
"""
    rows = parse_markdown_table(content)
    assert len(rows) == 2
    assert rows[0]["ID"] == "RN-001"
    assert rows[1]["Estoria"] == "US-001, US-002"


def test_parse_markdown_table_empty():
    assert parse_markdown_table("No table here") == []


# --- extract_ids ---

def test_extract_ids_sequential():
    content = "### US-001\n### US-002\n### US-003\n"
    assert extract_ids(content, "US") == [1, 2, 3]


def test_extract_ids_empty():
    assert extract_ids("no ids here", "RN") == []


# --- extract_id_refs ---

def test_extract_id_refs_single():
    assert extract_id_refs("US-001", "US") == ["US-001"]


def test_extract_id_refs_multiple():
    assert extract_id_refs("US-001, US-003", "US") == ["US-001", "US-003"]


def test_extract_id_refs_none():
    assert extract_id_refs("nenhuma", "US") == []


# --- check_sequential_ids ---

def test_sequential_ids_pass():
    content = "US-001 US-002 US-003"
    assert check_sequential_ids(content, "US") == []


def test_sequential_ids_gap():
    content = "RN-001 RN-003"
    violations = check_sequential_ids(content, "RN")
    assert len(violations) == 1
    assert "RN-002" in violations[0]["issue"]


def test_sequential_ids_duplicate():
    content = "MSG-001 MSG-001 MSG-002"
    violations = check_sequential_ids(content, "MSG")
    assert any("Duplicate" in v["issue"] for v in violations)


def test_sequential_ids_not_starting_at_001():
    content = "US-002 US-003"
    violations = check_sequential_ids(content, "US")
    assert any("US-001 missing" in v["issue"] for v in violations)


# --- check_cross_refs ---

def test_cross_refs_pass():
    rows = [{"ID": "RN-001", "Estoria": "US-001, US-002"}]
    target_ids = {"US-001", "US-002", "US-003"}
    assert check_cross_refs(rows, "Estoria", target_ids, "RN", "US", "ID") == []


def test_cross_refs_bad_ref():
    rows = [{"ID": "RN-001", "Estoria": "US-099"}]
    target_ids = {"US-001"}
    violations = check_cross_refs(rows, "Estoria", target_ids, "RN", "US", "ID")
    assert len(violations) == 1
    assert "US-099" in violations[0]["issue"]


def test_cross_refs_no_ref():
    rows = [{"ID": "RN-001", "Estoria": "nenhuma"}]
    target_ids = {"US-001"}
    violations = check_cross_refs(rows, "Estoria", target_ids, "RN", "US", "ID")
    assert len(violations) == 1
    assert "no US references" in violations[0]["issue"]


# --- check_msg_type_coverage ---

def test_msg_types_all_present():
    rows = [
        {"Tipo": "erro"}, {"Tipo": "sucesso"},
        {"Tipo": "validacao"}, {"Tipo": "confirmacao"},
    ]
    assert check_msg_type_coverage(rows) == []


def test_msg_types_missing():
    rows = [{"Tipo": "erro"}, {"Tipo": "sucesso"}]
    violations = check_msg_type_coverage(rows)
    assert len(violations) == 1
    assert "confirmacao" in violations[0]["issue"]
    assert "validacao" in violations[0]["issue"]


def test_msg_types_invalid():
    rows = [
        {"Tipo": "erro"}, {"Tipo": "sucesso"},
        {"Tipo": "validacao"}, {"Tipo": "confirmacao"},
        {"Tipo": "aviso"},
    ]
    violations = check_msg_type_coverage(rows)
    assert any("aviso" in v["issue"] for v in violations)


# --- check_empty_cells ---

def test_empty_cells_pass():
    rows = [{"ID": "RN-001", "Descricao": "Algo valido", "Excecao": "Caso X"}]
    assert check_empty_cells(rows, "business-rules.md", "ID") == []


def test_empty_cells_todo():
    rows = [{"ID": "RN-001", "Descricao": "TODO"}]
    violations = check_empty_cells(rows, "business-rules.md", "ID")
    assert len(violations) == 1
    assert "TODO" in violations[0]["issue"]


def test_empty_cells_empty():
    rows = [{"ID": "RN-001", "Descricao": "   "}]
    violations = check_empty_cells(rows, "business-rules.md", "ID")
    assert len(violations) == 1


# --- check_na_justification ---

def test_na_with_justification():
    rows = [{"ID": "RN-001", "Excecao": "N/A — regra deterministica"}]
    assert check_na_justification(rows) == []


def test_na_without_justification():
    rows = [{"ID": "RN-001", "Excecao": "N/A"}]
    violations = check_na_justification(rows)
    assert len(violations) == 1
    assert "justification" in violations[0]["issue"].lower()


def test_na_with_dash_no_text():
    rows = [{"ID": "RN-001", "Excecao": "N/A — "}]
    violations = check_na_justification(rows)
    assert len(violations) == 1


def test_normal_exception():
    rows = [{"ID": "RN-001", "Excecao": "Retorna erro 403 se sem permissao"}]
    assert check_na_justification(rows) == []


# --- count_coverage ---

def test_coverage_full():
    us_content = "### US-001\n### US-002\n"
    rn_rows = [
        {"ID": "RN-001", "Estoria": "US-001"},
        {"ID": "RN-002", "Estoria": "US-002"},
    ]
    msg_rows = [
        {"Codigo": "MSG-001", "Regra": "RN-001"},
        {"Codigo": "MSG-002", "Regra": "RN-002"},
    ]
    cov = count_coverage(us_content, rn_rows, msg_rows)
    assert cov["total_us"] == 2
    assert cov["total_rn"] == 2
    assert cov["total_msg"] == 2
    assert cov["us_with_rules"] == 2
    assert cov["rn_with_messages"] == 2
    assert cov["us_without_rules"] == []
    assert cov["rn_without_messages"] == []


def test_coverage_gaps():
    us_content = "### US-001\n### US-002\n### US-003\n"
    rn_rows = [{"ID": "RN-001", "Estoria": "US-001"}]
    msg_rows = []
    cov = count_coverage(us_content, rn_rows, msg_rows)
    assert cov["us_without_rules"] == ["US-002", "US-003"]
    assert cov["rn_without_messages"] == ["RN-001"]


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
