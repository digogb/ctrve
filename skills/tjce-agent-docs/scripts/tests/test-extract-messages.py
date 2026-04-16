"""Unit tests for extract-messages.py"""

from __future__ import annotations

import importlib.util
from pathlib import Path

_script_path = Path(__file__).parent.parent / "extract-messages.py"
_spec = importlib.util.spec_from_file_location("extract_messages", _script_path)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

extract_messages = _mod.extract_messages
build_catalog = _mod.build_catalog


def test_table_format():
    text = """\
| ID | Texto | Contexto |
|----|-------|----------|
| MSG-001 | Processo cadastrado com sucesso | Apos salvar cadastro |
| MSG-002 | CPF invalido | Validacao de campo |
"""
    msgs = extract_messages(text)
    assert len(msgs) == 2
    assert msgs[0]["id"] == "MSG-001"
    assert "cadastrado" in msgs[0]["text"]
    assert "salvar" in msgs[0]["context"]


def test_heading_format():
    text = """\
### MSG-001 — Processo cadastrado com sucesso
Exibida apos o usuario salvar.

### MSG-002 — CPF invalido
Exibida quando CPF nao passa validacao.
"""
    msgs = extract_messages(text)
    assert len(msgs) == 2
    assert msgs[0]["text"] == "Processo cadastrado com sucesso"
    assert "salvar" in msgs[0]["context"]


def test_colon_format():
    text = "MSG-001: Processo salvo\nExibida na tela de cadastro."
    msgs = extract_messages(text)
    assert len(msgs) == 1
    assert "salvo" in msgs[0]["text"]


def test_dedup():
    text = """\
| MSG-001 | Texto A | Ctx A |
### MSG-001 — Texto B
"""
    msgs = extract_messages(text)
    assert len(msgs) == 1  # first occurrence wins


def test_empty_input():
    assert extract_messages("nada aqui") == []


def test_build_catalog_summary():
    text = """\
| MSG-001 | Sucesso | Apos salvar |
| MSG-002 | Erro | |
| MSG-003 | Aviso | Campo obrigatorio |
"""
    cat = build_catalog(text)
    assert cat["summary"]["total"] == 3
    assert cat["summary"]["with_context"] == 2  # MSG-002 has empty context


def test_table_without_context_column():
    text = """\
| MSG-001 | Processo salvo |
"""
    msgs = extract_messages(text)
    assert len(msgs) == 1
    assert msgs[0]["context"] == ""


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
