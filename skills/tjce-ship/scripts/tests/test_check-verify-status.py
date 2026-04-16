#!/usr/bin/env python3
"""Tests for check-verify-status.py"""

import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "check-verify-status.py"


def run_script(output_folder: str) -> dict:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), output_folder],
        capture_output=True,
        text=True,
    )
    return {"returncode": result.returncode, "output": json.loads(result.stdout)}


def test_aprovado_from_verdict_json(tmp_path):
    reports = tmp_path / "reports"
    reports.mkdir()
    (reports / "verify-verdict.json").write_text(json.dumps({"verdict": "APROVADO"}))

    result = run_script(str(tmp_path))
    assert result["returncode"] == 0
    assert result["output"]["status"] == "pass"
    assert result["output"]["verify_status"] == "APROVADO"


def test_go_from_verdict_json(tmp_path):
    reports = tmp_path / "reports"
    reports.mkdir()
    (reports / "verify-verdict.json").write_text(json.dumps({"verdict": "GO"}))

    result = run_script(str(tmp_path))
    assert result["returncode"] == 0
    assert result["output"]["status"] == "pass"
    assert result["output"]["verify_status"] == "GO"


def test_rejected_from_verdict_json(tmp_path):
    reports = tmp_path / "reports"
    reports.mkdir()
    (reports / "verify-verdict.json").write_text(json.dumps({"verdict": "NO-GO"}))

    result = run_script(str(tmp_path))
    assert result["returncode"] == 1
    assert result["output"]["status"] == "fail"
    assert result["output"]["verify_status"] == "NO-GO"
    assert result["output"]["summary"]["critical"] == 1


def test_aprovado_from_summary_md(tmp_path):
    reports = tmp_path / "reports"
    reports.mkdir()
    (reports / "verify-summary.md").write_text("# Resultado\n\nStatus: APROVADO\n")

    result = run_script(str(tmp_path))
    assert result["returncode"] == 0
    assert result["output"]["status"] == "pass"
    assert result["output"]["verify_status"] == "APROVADO"


def test_aguardando_from_summary_md(tmp_path):
    reports = tmp_path / "reports"
    reports.mkdir()
    (reports / "verify-summary.md").write_text("Status: Aguardando Homologacao\n")

    result = run_script(str(tmp_path))
    assert result["returncode"] == 1
    assert result["output"]["verify_status"] == "AGUARDANDO HOMOLOGACAO"


def test_no_reports_found(tmp_path):
    result = run_script(str(tmp_path))
    assert result["returncode"] == 1
    assert result["output"]["status"] == "fail"
    assert result["output"]["verify_status"] is None
    assert result["output"]["summary"]["critical"] == 1


def test_verdict_json_takes_precedence(tmp_path):
    reports = tmp_path / "reports"
    reports.mkdir()
    (reports / "verify-verdict.json").write_text(json.dumps({"verdict": "APROVADO"}))
    (reports / "verify-summary.md").write_text("Status: REJEITADO\n")

    result = run_script(str(tmp_path))
    assert result["returncode"] == 0
    assert result["output"]["verify_status"] == "APROVADO"


def test_corrupt_verdict_json_falls_back_to_summary(tmp_path):
    reports = tmp_path / "reports"
    reports.mkdir()
    (reports / "verify-verdict.json").write_text("not valid json{{{")
    (reports / "verify-summary.md").write_text("Resultado: APROVADO pelo PO\n")

    result = run_script(str(tmp_path))
    assert result["returncode"] == 0
    assert result["output"]["verify_status"] == "APROVADO"
    assert "verify-summary.md" in result["output"]["verify_source"]
