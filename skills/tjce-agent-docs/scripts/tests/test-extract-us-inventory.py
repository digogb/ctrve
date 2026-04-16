"""Unit tests for extract-us-inventory.py"""

from __future__ import annotations

import importlib.util
from pathlib import Path

_script_path = Path(__file__).parent.parent / "extract-us-inventory.py"
_spec = importlib.util.spec_from_file_location("extract_us_inventory", _script_path)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

extract_stories = _mod.extract_stories
build_inventory = _mod.build_inventory


def test_extract_colon_format():
    text = "US-001: Cadastrar processo com formulario\nUS-002: Integrar com CNJ"
    stories = extract_stories(text)
    assert len(stories) == 2
    assert stories[0]["id"] == "US-001"
    assert "Cadastrar" in stories[0]["title"]


def test_extract_dash_format():
    text = "US-001 - Cadastrar processo com tela de cadastro"
    stories = extract_stories(text)
    assert len(stories) == 1
    assert stories[0]["has_screen_interaction"] is True


def test_extract_heading_format():
    text = "### US-001: Visualizar processo\nO usuario acessa a tela..."
    stories = extract_stories(text)
    assert len(stories) == 1
    assert stories[0]["has_screen_interaction"] is True


def test_screen_detection_positive():
    text = "US-001: Cadastrar parte\nO usuario preenche o formulario de cadastro."
    stories = extract_stories(text)
    assert stories[0]["has_screen_interaction"] is True


def test_screen_detection_negative():
    text = "US-001: Sincronizar dados com CNJ\nIntegracao batch noturna."
    stories = extract_stories(text)
    assert stories[0]["has_screen_interaction"] is False


def test_dedup_by_id():
    text = "US-001: Cadastrar\nUS-001: Cadastrar processo"
    stories = extract_stories(text)
    assert len(stories) == 1


def test_build_inventory_summary():
    text = """\
US-001: Cadastrar processo com tela
O usuario preenche o formulario.

US-002: Integrar com CNJ via batch
Processamento noturno sem interacao.

US-003: Consultar processo
O usuario visualiza a lista de processos.
"""
    inv = build_inventory(text)
    assert inv["summary"]["total"] == 3
    assert inv["summary"]["with_screen"] == 2  # US-001 and US-003
    assert inv["summary"]["without_screen"] == 1  # US-002 (batch)


def test_empty_input():
    assert build_inventory("nada aqui")["stories"] == []


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
