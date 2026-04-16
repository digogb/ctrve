#!/usr/bin/env python3
"""Tests for check-placeholders.py"""

import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "check-placeholders.py"


def run_script(output_folder: str) -> dict:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), output_folder],
        capture_output=True,
        text=True,
    )
    return {"returncode": result.returncode, "output": json.loads(result.stdout)}


def _create_clean_spec(base: Path):
    (base / "requirements").mkdir(parents=True)
    (base / "requirements" / "user-stories.md").write_text(
        "# User Stories\n\n## US-001\nComo admin, quero gerenciar usuarios, para que possa controlar acessos.\n"
    )
    (base / "requirements" / "business-rules.md").write_text(
        "# Regras\n\n| id | descricao | condicao | acao | excecao |\n| -- | --------- | -------- | ---- | ------- |\n| RN-001 | Regra | Se X | Entao Y | Caso Z |\n"
    )
    (base / "requirements" / "messages.md").write_text(
        "# Mensagens\n\nTipo erro: MSG-001\nTipo sucesso: MSG-002\nTipo validacao: MSG-003\nTipo confirmacao: MSG-004\n"
    )
    (base / "requirements" / "product-vision.md").write_text("# Visao\n\nConteudo da visao.\n")
    (base / "tests").mkdir()
    (base / "tests" / "test-cases.md").write_text("# Testes\n\n## CT-001\nTeste completo.\n")


def test_clean_spec_passes(tmp_path):
    _create_clean_spec(tmp_path)
    result = run_script(str(tmp_path))
    assert result["output"]["status"] == "pass"
    assert result["output"]["summary"]["critical"] == 0


def test_todo_detected(tmp_path):
    _create_clean_spec(tmp_path)
    (tmp_path / "requirements" / "user-stories.md").write_text("# US\n\nTODO: completar historias\n")
    result = run_script(str(tmp_path))
    assert result["returncode"] == 1
    assert result["output"]["summary"]["critical"] >= 1


def test_preencher_detected(tmp_path):
    _create_clean_spec(tmp_path)
    (tmp_path / "requirements" / "business-rules.md").write_text("# RN\n\n[PREENCHER] regras\n")
    result = run_script(str(tmp_path))
    assert result["returncode"] == 1


def test_tbd_detected(tmp_path):
    _create_clean_spec(tmp_path)
    (tmp_path / "requirements" / "messages.md").write_text("# MSG\n\nMSG-001: TBD\n")
    result = run_script(str(tmp_path))
    assert result["returncode"] == 1


def test_empty_section_detected(tmp_path):
    _create_clean_spec(tmp_path)
    (tmp_path / "requirements" / "product-vision.md").write_text("# Visao\n\n## Objetivo\n\nConteudo.\n\n## Escopo\n\n\n## Fora\n\nAlgo.\n")
    result = run_script(str(tmp_path))
    findings = [f for f in result["output"]["findings"] if f["category"] == "empty-section"]
    assert any("Escopo" in f["issue"] for f in findings)


def test_user_story_format_check(tmp_path):
    _create_clean_spec(tmp_path)
    (tmp_path / "requirements" / "user-stories.md").write_text("# US\n\n## US-001\nO sistema deve permitir login.\n")
    result = run_script(str(tmp_path))
    findings = [f for f in result["output"]["findings"] if f["category"] == "format"]
    assert any("formato" in f["issue"].lower() for f in findings)


def test_rn_missing_columns(tmp_path):
    _create_clean_spec(tmp_path)
    (tmp_path / "requirements" / "business-rules.md").write_text("# RN\n\n| id | descricao |\n| -- | --------- |\n| RN-001 | Regra |\n")
    result = run_script(str(tmp_path))
    findings = [f for f in result["output"]["findings"] if f["category"] == "format"]
    assert any("colunas" in f["issue"].lower() for f in findings)


def test_message_types_coverage(tmp_path):
    _create_clean_spec(tmp_path)
    (tmp_path / "requirements" / "messages.md").write_text("# MSG\n\nMSG-001 mensagem de erro.\n")
    result = run_script(str(tmp_path))
    findings = [f for f in result["output"]["findings"] if f["category"] == "coverage"]
    assert len(findings) >= 1


def test_missing_files_no_crash(tmp_path):
    result = run_script(str(tmp_path))
    assert result["returncode"] == 0
    assert result["output"]["status"] == "pass"
