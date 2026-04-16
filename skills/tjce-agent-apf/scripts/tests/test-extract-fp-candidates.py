"""Unit tests for extract-fp-candidates.py"""

import importlib.util
from pathlib import Path

_script_path = Path(__file__).parent.parent / "extract-fp-candidates.py"
_spec = importlib.util.spec_from_file_location("extract_fp_candidates", _script_path)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

extract_entities = _mod.extract_entities
extract_user_stories = _mod.extract_user_stories
extract_business_rules = _mod.extract_business_rules
build_candidates = _mod.build_candidates


# --- Entities ---

def test_extract_entities_from_headings():
    text = """\
# Modelo de Dados

## Processo
Campos...

## Parte
Campos...

### Anexo
Campos...
"""
    entities = extract_entities(text)
    names = [e["name"] for e in entities]
    assert "Processo" in names
    assert "Parte" in names
    assert "Anexo" in names


def test_extract_entities_skips_meta():
    text = """\
## Entidades

## Relacionamentos

## Processo
"""
    names = [e["name"] for e in extract_entities(text)]
    assert "Processo" in names
    assert "Entidades" not in names
    assert "Relacionamentos" not in names


def test_extract_entities_dedup():
    text = "## Processo\n\n## Processo\n"
    assert len(extract_entities(text)) == 1


# --- User stories ---

def test_extract_us_with_titles():
    text = "US-001: Cadastrar processo\nUS-002 - Consultar processo"
    stories = extract_user_stories(text)
    ids = {s["id"]: s["title"] for s in stories}
    assert ids["US-001"] == "Cadastrar processo"
    assert "Consultar processo" in ids["US-002"]


def test_extract_us_bare_ids():
    text = "Veja US-003 para detalhes."
    stories = extract_user_stories(text)
    assert any(s["id"] == "US-003" for s in stories)


def test_extract_us_dedup_keeps_titled():
    text = "US-001: Titulo longo\nVeja tambem US-001."
    stories = extract_user_stories(text)
    us_001 = [s for s in stories if s["id"] == "US-001"]
    assert len(us_001) == 1
    assert "Titulo" in us_001[0]["title"]


# --- Business rules ---

def test_extract_rn_ids():
    text = "RN-001, RN-002 e novamente RN-001"
    assert extract_business_rules(text) == ["RN-001", "RN-002"]


def test_extract_rn_empty():
    assert extract_business_rules("nada aqui") == []


# --- Combined ---

def test_build_candidates_summary():
    us = "US-001: Cadastrar\nUS-002: Consultar"
    rn = "RN-001\nRN-002\nRN-003"
    dm = "## Processo\n## Parte"
    c = build_candidates(us, rn, dm)
    assert c["summary"]["us_count"] == 2
    assert c["summary"]["rn_count"] == 3
    assert c["summary"]["entity_count"] == 2


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
