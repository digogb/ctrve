#!/usr/bin/env python3
"""Tests for format-security-report.py"""

import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "format-security-report.py"


def run_script(secrets_json: str, security_json: str) -> dict:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), secrets_json, security_json],
        capture_output=True,
        text=True,
    )
    return {"returncode": result.returncode, "stdout": result.stdout, "stderr": result.stderr}


def _write_json(path: Path, data: dict):
    path.write_text(json.dumps(data), encoding="utf-8")


def test_clean_results(tmp_path):
    secrets = tmp_path / "secrets.json"
    security = tmp_path / "security.json"
    _write_json(secrets, {"findings": [], "summary": {"total": 0}})
    _write_json(security, {"findings": [], "summary": {"total": 0}})

    result = run_script(str(secrets), str(security))
    assert result["returncode"] == 0
    assert "PASS" in result["stdout"]
    assert "Nenhuma vulnerabilidade" in result["stdout"]


def test_critical_findings_exit_1(tmp_path):
    secrets = tmp_path / "secrets.json"
    security = tmp_path / "security.json"
    _write_json(secrets, {"findings": [
        {"severity": "critical", "category": "secrets",
         "location": {"file": "app.py", "line": 10},
         "issue": "API key found", "fix": "Remove it"},
    ]})
    _write_json(security, {"findings": []})

    result = run_script(str(secrets), str(security))
    assert result["returncode"] == 1
    assert "BLOQUEADO" in result["stdout"]


def test_combines_both_sources(tmp_path):
    secrets = tmp_path / "secrets.json"
    security = tmp_path / "security.json"
    _write_json(secrets, {"findings": [
        {"severity": "high", "category": "secrets",
         "location": {"file": "config.py", "line": 5},
         "issue": "Token found", "fix": "Use env var"},
    ]})
    _write_json(security, {"findings": [
        {"severity": "medium", "category": "cors",
         "location": {"file": "settings.py", "line": 12},
         "issue": "Wildcard CORS", "fix": "Restrict origins"},
    ]})

    result = run_script(str(secrets), str(security))
    assert result["returncode"] == 0
    assert "ATENCAO" in result["stdout"]
    assert "config.py" in result["stdout"]
    assert "settings.py" in result["stdout"]


def test_output_to_file(tmp_path):
    secrets = tmp_path / "secrets.json"
    security = tmp_path / "security.json"
    output = tmp_path / "report.md"
    _write_json(secrets, {"findings": []})
    _write_json(security, {"findings": []})

    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(secrets), str(security), "-o", str(output)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert output.exists()
    assert "PASS" in output.read_text()


def test_missing_file_exits_2(tmp_path):
    secrets = tmp_path / "nonexistent.json"
    security = tmp_path / "also_nonexistent.json"

    result = run_script(str(secrets), str(security))
    assert result["returncode"] == 2
