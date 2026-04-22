#!/usr/bin/env python3
"""Tests for pre-analyze-test-cases.py"""

import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "pre-analyze-test-cases.py"


def run_script(output_folder: str) -> dict:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), output_folder],
        capture_output=True,
        text=True,
    )
    return {"returncode": result.returncode, "output": json.loads(result.stdout)}


def _create_good_tests(base: Path):
    (base / "tests").mkdir(parents=True, exist_ok=True)
    (base / "tests" / "test-cases.md").write_text(
        "# Casos de Teste\n\n"
        "## CT-001\nTestar RN-001: login com credenciais validas.\n"
        "Resultado esperado: sistema autentica e redireciona ao dashboard.\n\n"
        "## CT-002\nTestar RN-002: cadastro com dados incompletos.\n"
        "Resultado esperado: sistema exibe mensagem de erro MSG-001.\n"
    )


def test_good_tests_pass(tmp_path):
    _create_good_tests(tmp_path)
    result = run_script(str(tmp_path))
    assert result["returncode"] == 0
    assert result["output"]["status"] == "pass"
    assert result["output"]["ct_count"] == 2


def test_missing_rn_reference(tmp_path):
    (tmp_path / "tests").mkdir(parents=True)
    (tmp_path / "tests" / "test-cases.md").write_text(
        "# Casos de Teste\n\n## CT-001\nTestar login generico.\n"
        "Resultado esperado: sistema funciona corretamente.\n"
    )
    result = run_script(str(tmp_path))
    findings = [f for f in result["output"]["findings"] if "nao referencia" in f["issue"]]
    assert len(findings) >= 1


def test_missing_expected_result(tmp_path):
    (tmp_path / "tests").mkdir(parents=True)
    (tmp_path / "tests" / "test-cases.md").write_text(
        "# Casos de Teste\n\n## CT-001\nTestar RN-001: login valido.\n"
        "Passos: entrar credenciais.\n"
    )
    result = run_script(str(tmp_path))
    findings = [f for f in result["output"]["findings"] if "resultado esperado" in f["issue"]]
    assert len(findings) >= 1
    assert any(f.get("needs_llm_review") for f in findings)


def test_short_body(tmp_path):
    (tmp_path / "tests").mkdir(parents=True)
    (tmp_path / "tests" / "test-cases.md").write_text(
        "# Casos de Teste\n\n## CT-001\nRN-001 ok.\n"
    )
    result = run_script(str(tmp_path))
    findings = [f for f in result["output"]["findings"] if "curto" in f["issue"]]
    assert len(findings) >= 1


def test_no_test_file(tmp_path):
    result = run_script(str(tmp_path))
    assert result["returncode"] == 0
    assert result["output"]["ct_count"] == 0


def test_output_to_file(tmp_path):
    _create_good_tests(tmp_path)
    out_file = tmp_path / "preanalysis.json"
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(tmp_path), "-o", str(out_file)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    data = json.loads(out_file.read_text())
    assert data["status"] == "pass"


def test_multiple_issues_same_ct(tmp_path):
    (tmp_path / "tests").mkdir(parents=True)
    (tmp_path / "tests" / "test-cases.md").write_text(
        "# Casos de Teste\n\n## CT-001\nTeste.\n"
    )
    result = run_script(str(tmp_path))
    ct001_findings = [f for f in result["output"]["findings"] if "CT-001" in f["issue"]]
    assert len(ct001_findings) >= 2
