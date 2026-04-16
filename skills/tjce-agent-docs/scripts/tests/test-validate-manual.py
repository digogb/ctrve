"""Unit tests for validate-manual.py"""

from __future__ import annotations

import importlib.util
from pathlib import Path

_script_path = Path(__file__).parent.parent / "validate-manual.py"
_spec = importlib.util.spec_from_file_location("validate_manual", _script_path)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

extract_us_ids = _mod.extract_us_ids
extract_msg_ids = _mod.extract_msg_ids
check_us_coverage = _mod.check_us_coverage
check_msg_coverage = _mod.check_msg_coverage
check_jargon = _mod.check_jargon
validate = _mod.validate


# --- ID extraction ---

def test_extract_us_ids():
    assert extract_us_ids("US-001 e US-002 e US-001") == ["US-001", "US-002"]


def test_extract_msg_ids():
    assert extract_msg_ids("MSG-001 e MSG-003") == ["MSG-001", "MSG-003"]


def test_extract_ids_empty():
    assert extract_us_ids("nada") == []
    assert extract_msg_ids("nada") == []


# --- US coverage ---

def test_us_full_coverage():
    manual = "## US-001 Cadastrar\n## US-002 Consultar"
    r = check_us_coverage(manual, ["US-001", "US-002"])
    assert r["uncovered"] == []
    assert r["coverage_pct"] == 100.0


def test_us_partial_coverage():
    manual = "## US-001 Cadastrar"
    r = check_us_coverage(manual, ["US-001", "US-002"])
    assert r["uncovered"] == ["US-002"]
    assert r["coverage_pct"] == 50.0


def test_us_no_stories():
    r = check_us_coverage("manual vazio", [])
    assert r["total"] == 0
    assert r["coverage_pct"] == 0


# --- MSG coverage ---

def test_msg_full_coverage():
    manual = "aparece MSG-001 e MSG-002"
    r = check_msg_coverage(manual, ["MSG-001", "MSG-002"])
    assert r["uncovered"] == []


def test_msg_partial_coverage():
    manual = "apenas MSG-001"
    r = check_msg_coverage(manual, ["MSG-001", "MSG-002"])
    assert r["uncovered"] == ["MSG-002"]


# --- Jargon check ---

def test_jargon_detects_prohibited():
    manual = "O endpoint retorna um JSON com os dados.\nO frontend exibe."
    findings = check_jargon(manual)
    terms = {f["term"] for f in findings}
    assert "endpoint" in terms
    assert "json" in terms
    assert "frontend" in terms


def test_jargon_clean_text():
    manual = "Clique em Salvar para gravar os dados.\nO sistema confirmara."
    assert check_jargon(manual) == []


def test_jargon_case_insensitive():
    manual = "A API foi configurada."
    findings = check_jargon(manual)
    assert any(f["term"] == "api" for f in findings)


def test_jargon_word_boundary():
    # "proposta" contains "prop" but should NOT match
    manual = "A proposta foi aprovada pelo token de seguranca."
    findings = check_jargon(manual)
    terms = {f["term"] for f in findings}
    assert "prop" not in terms
    assert "token" in terms


# --- Combined validation ---

def test_validate_all_pass():
    manual = "## US-001 Cadastrar\nMSG-001 aparece aqui.\nClique em Salvar."
    r = validate(manual, ["US-001"], ["MSG-001"])
    assert r["valid"] is True


def test_validate_fails_on_jargon():
    manual = "## US-001\nMSG-001\nO endpoint retorna dados."
    r = validate(manual, ["US-001"], ["MSG-001"])
    assert r["valid"] is False
    assert r["jargon_count"] > 0


def test_validate_fails_on_missing_us():
    manual = "MSG-001 presente.\nClique em Salvar."
    r = validate(manual, ["US-001"], ["MSG-001"])
    assert r["valid"] is False
    assert "US-001" in r["us_coverage"]["uncovered"]


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
