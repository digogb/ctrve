#!/usr/bin/env python3
"""Tests for validate-pml.py"""

import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "validate-pml.py"


def run_script(pml_path: str) -> dict:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), pml_path],
        capture_output=True,
        text=True,
    )
    return {"returncode": result.returncode, "output": json.loads(result.stdout)}


def test_valid_pml(tmp_path):
    pml = tmp_path / "PML.md"
    pml.write_text("# PML\n\n## Objetivo\n\nDescrever a mudanca.\n\n## Escopo\n\nAlteracoes no modulo X.\n")

    result = run_script(str(pml))
    assert result["returncode"] == 0
    assert result["output"]["status"] == "pass"
    assert len(result["output"]["sections"]) == 2


def test_pml_not_found(tmp_path):
    result = run_script(str(tmp_path / "PML.md"))
    assert result["returncode"] == 1
    assert result["output"]["status"] == "fail"
    assert result["output"]["summary"]["critical"] == 1


def test_empty_pml(tmp_path):
    pml = tmp_path / "PML.md"
    pml.write_text("")

    result = run_script(str(pml))
    assert result["returncode"] == 1
    assert result["output"]["summary"]["critical"] == 1


def test_empty_section(tmp_path):
    pml = tmp_path / "PML.md"
    pml.write_text("# PML\n\n## Objetivo\n\nDescrever a mudanca.\n\n## Escopo\n\n\n## Rollback\n\nProcedimentos.\n")

    result = run_script(str(pml))
    assert result["returncode"] == 1
    issues = [f["issue"] for f in result["output"]["findings"]]
    assert any("Escopo" in i for i in issues)


def test_todo_placeholder(tmp_path):
    pml = tmp_path / "PML.md"
    pml.write_text("# PML\n\n## Objetivo\n\nTODO: preencher objetivo\n\n## Escopo\n\nAlteracoes.\n")

    result = run_script(str(pml))
    assert result["returncode"] == 1
    issues = [f["issue"] for f in result["output"]["findings"]]
    assert any("placeholder" in i.lower() or "TODO" in i for i in issues)


def test_a_definir_placeholder(tmp_path):
    pml = tmp_path / "PML.md"
    pml.write_text("# PML\n\n## Objetivo\n\nA definir posteriormente.\n")

    result = run_script(str(pml))
    assert result["returncode"] == 1


def test_tbd_placeholder(tmp_path):
    pml = tmp_path / "PML.md"
    pml.write_text("# PML\n\n## Plano\n\nTBD.\n")

    result = run_script(str(pml))
    assert result["returncode"] == 1


def test_pendente_placeholder(tmp_path):
    pml = tmp_path / "PML.md"
    pml.write_text("# PML\n\n## Riscos\n\nPendente de avaliacao.\n")

    result = run_script(str(pml))
    assert result["returncode"] == 1


def test_no_sections(tmp_path):
    pml = tmp_path / "PML.md"
    pml.write_text("# PML\n\nAlgum conteudo sem secoes H2/H3.\n")

    result = run_script(str(pml))
    assert result["returncode"] == 1
    assert result["output"]["summary"]["critical"] == 1


def test_section_statuses_reported(tmp_path):
    pml = tmp_path / "PML.md"
    pml.write_text("# PML\n\n## Bom\n\nConteudo valido.\n\n## Ruim\n\nTODO completar.\n")

    result = run_script(str(pml))
    sections = result["output"]["sections"]
    assert len(sections) == 2
    statuses = {s["title"]: s["status"] for s in sections}
    assert statuses["Bom"] == "pass"
    assert statuses["Ruim"] == "fail"
