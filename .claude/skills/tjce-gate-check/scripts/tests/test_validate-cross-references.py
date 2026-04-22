#!/usr/bin/env python3
"""Tests for validate-cross-references.py"""

import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "validate-cross-references.py"


def run_script(output_folder: str) -> dict:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), output_folder],
        capture_output=True,
        text=True,
    )
    return {"returncode": result.returncode, "output": json.loads(result.stdout)}


def _create_linked_spec(base: Path):
    (base / "requirements").mkdir(parents=True)
    (base / "requirements" / "user-stories.md").write_text(
        "# User Stories\n\n## US-001\nComo admin, quero X.\n\n## US-002\nComo usuario, quero Y.\n"
    )
    (base / "requirements" / "business-rules.md").write_text(
        "# Regras\n\n## RN-001\nRegra vinculada a US-001.\n\n## RN-002\nRegra vinculada a US-002.\n"
    )
    (base / "requirements" / "messages.md").write_text(
        "# Mensagens\n\n## MSG-001\nMensagem de erro para RN-001.\n\n## MSG-002\nValidacao RN-002.\n"
    )
    (base / "tests").mkdir()
    (base / "tests" / "test-cases.md").write_text(
        "# Casos de Teste\n\n## CT-001\nTestar RN-001.\n\n## CT-002\nTestar RN-002.\n"
    )


def test_all_linked(tmp_path):
    _create_linked_spec(tmp_path)
    result = run_script(str(tmp_path))
    assert result["output"]["status"] == "pass"
    assert result["output"]["summary"]["high"] == 0


def test_rn_without_us_link(tmp_path):
    _create_linked_spec(tmp_path)
    (tmp_path / "requirements" / "business-rules.md").write_text(
        "# Regras\n\n## RN-001\nRegra sem vinculo a US.\n"
    )
    result = run_script(str(tmp_path))
    findings = [f for f in result["output"]["findings"] if f["category"] == "cross-reference"]
    assert any("RN-001" in f["issue"] for f in findings)


def test_ct_without_rn_link(tmp_path):
    _create_linked_spec(tmp_path)
    (tmp_path / "tests" / "test-cases.md").write_text(
        "# Casos de Teste\n\n## CT-001\nTeste sem referencia a regra.\n"
    )
    result = run_script(str(tmp_path))
    findings = [f for f in result["output"]["findings"] if f["category"] == "cross-reference"]
    assert any("CT-001" in f["issue"] for f in findings)


def test_msg_without_rn_link(tmp_path):
    _create_linked_spec(tmp_path)
    (tmp_path / "requirements" / "messages.md").write_text(
        "# Mensagens\n\n## MSG-001\nMensagem sem referencia.\n"
    )
    result = run_script(str(tmp_path))
    findings = [f for f in result["output"]["findings"] if f["category"] == "cross-reference"]
    assert any("MSG-001" in f["issue"] for f in findings)


def test_orphan_id_detected(tmp_path):
    _create_linked_spec(tmp_path)
    (tmp_path / "requirements" / "business-rules.md").write_text(
        "# Regras\n\n## RN-001\nRegra vinculada a US-999.\n"
    )
    result = run_script(str(tmp_path))
    orphan_findings = [f for f in result["output"]["findings"] if f["category"] == "orphan-id"]
    assert any("US-999" in f["issue"] for f in orphan_findings)


def test_defined_ids_reported(tmp_path):
    _create_linked_spec(tmp_path)
    result = run_script(str(tmp_path))
    defined = result["output"]["defined_ids"]
    assert "US-001" in defined.get("US", [])
    assert "RN-001" in defined.get("RN", [])


def test_empty_directory(tmp_path):
    result = run_script(str(tmp_path))
    assert result["returncode"] == 0
    assert result["output"]["status"] == "pass"
    assert result["output"]["summary"]["total"] == 0
