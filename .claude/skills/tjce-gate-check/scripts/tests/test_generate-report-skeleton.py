#!/usr/bin/env python3
"""Tests for generate-report-skeleton.py"""

import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "generate-report-skeleton.py"


def run_script(output_folder: str, *args: str) -> dict:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), output_folder, *args],
        capture_output=True,
        text=True,
    )
    return {"returncode": result.returncode, "stdout": result.stdout}


def _create_verdict(base: Path, **overrides):
    reports = base / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    verdict = {
        "score": 95.0,
        "threshold": 90,
        "status": "PASS",
        "fail_reason": None,
        "timestamp": "2026-04-16T20:00:00+00:00",
        "layer_scores": {
            "completeness": 40.0,
            "cross-reference": 27.0,
            "quality": 28.0,
        },
        "missing_inputs": [],
        "warnings": [],
        "task_type": None,
        "manual_required": False,
        "data_model_required": False,
        "apf_estimate": None,
    }
    verdict.update(overrides)
    (reports / "gate-check-verdict.json").write_text(
        json.dumps(verdict, indent=2), encoding="utf-8"
    )
    return verdict


def _create_findings(base: Path, name: str, findings: list):
    reports = base / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    (reports / name).write_text(
        json.dumps({"findings": findings}), encoding="utf-8"
    )


def test_basic_report(tmp_path):
    _create_verdict(tmp_path)
    result = run_script(str(tmp_path))
    assert result["returncode"] == 0
    assert "Score:" in result["stdout"]
    assert "95.0" in result["stdout"]
    assert "PASS" in result["stdout"]


def test_fail_report_shows_reason(tmp_path):
    _create_verdict(tmp_path, status="FAIL", score=75.0,
                    fail_reason="Score 75.0 abaixo do minimo 90")
    result = run_script(str(tmp_path))
    assert "FAIL" in result["stdout"]
    assert "abaixo" in result["stdout"]


def test_layer_scores_table(tmp_path):
    _create_verdict(tmp_path)
    result = run_script(str(tmp_path))
    assert "Completude" in result["stdout"]
    assert "Consistencia" in result["stdout"]
    assert "Qualidade" in result["stdout"]


def test_findings_included(tmp_path):
    _create_verdict(tmp_path)
    _create_findings(tmp_path, "artifacts-findings.json", [
        {"severity": "critical", "issue": "user-stories.md ausente", "fix": "Gere o artefato"},
    ])
    result = run_script(str(tmp_path))
    assert "user-stories.md" in result["stdout"]


def test_complementary_decisions(tmp_path):
    _create_verdict(tmp_path, task_type="mudanca", manual_required=True,
                    data_model_required=True, apf_estimate=42.5)
    result = run_script(str(tmp_path))
    assert "mudanca" in result["stdout"]
    assert "42.5" in result["stdout"]


def test_output_to_file(tmp_path):
    _create_verdict(tmp_path)
    out_file = tmp_path / "report.md"
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(tmp_path), "-o", str(out_file)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    content = out_file.read_text()
    assert "Gate Check" in content


def test_missing_verdict(tmp_path):
    (tmp_path / "reports").mkdir(parents=True)
    result = run_script(str(tmp_path))
    assert result["returncode"] == 0
    assert "Erro" in result["stdout"]


def test_warnings_section(tmp_path):
    _create_verdict(tmp_path, warnings=[
        {"severity": "medium", "issue": "US-999 orfao"},
    ])
    result = run_script(str(tmp_path))
    assert "US-999" in result["stdout"]
