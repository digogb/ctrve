#!/usr/bin/env python3
"""Tests for calculate-gate-score.py"""

import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "calculate-gate-score.py"


def run_script(*args: str) -> dict:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
    )
    return {"returncode": result.returncode, "output": json.loads(result.stdout)}


def _write_findings(reports_dir: Path, name: str, findings: list):
    reports_dir.mkdir(parents=True, exist_ok=True)
    data = {"findings": findings}
    (reports_dir / name).write_text(json.dumps(data), encoding="utf-8")


def _make_finding(severity: str, category: str, issue: str = "test issue") -> dict:
    return {
        "severity": severity,
        "category": category,
        "location": {"file": "test.md"},
        "issue": issue,
        "fix": "fix it",
    }


def test_perfect_score(tmp_path):
    reports = tmp_path / "reports"
    _write_findings(reports, "artifacts-findings.json", [])
    _write_findings(reports, "crossref-findings.json", [])
    _write_findings(reports, "placeholder-findings.json", [])
    _write_findings(reports, "quality-findings.json", [])

    result = run_script(str(tmp_path), "--task-type", "nova_funcionalidade")
    assert result["returncode"] == 0
    assert result["output"]["status"] == "PASS"
    assert result["output"]["score"] == 100.0


def test_critical_artifact_fails(tmp_path):
    reports = tmp_path / "reports"
    _write_findings(reports, "artifacts-findings.json", [
        _make_finding("critical", "completeness", "Missing user-stories.md"),
    ])
    _write_findings(reports, "crossref-findings.json", [])
    _write_findings(reports, "placeholder-findings.json", [])
    _write_findings(reports, "quality-findings.json", [])

    result = run_script(str(tmp_path))
    assert result["returncode"] == 1
    assert result["output"]["status"] == "FAIL"
    assert "obrigatorios" in result["output"]["fail_reason"].lower()


def test_placeholder_fails(tmp_path):
    reports = tmp_path / "reports"
    _write_findings(reports, "artifacts-findings.json", [])
    _write_findings(reports, "crossref-findings.json", [])
    _write_findings(reports, "placeholder-findings.json", [
        _make_finding("critical", "placeholder", "TODO found"),
    ])
    _write_findings(reports, "quality-findings.json", [])

    result = run_script(str(tmp_path))
    assert result["returncode"] == 1
    assert result["output"]["status"] == "FAIL"
    assert "placeholder" in result["output"]["fail_reason"].lower()


def test_cross_reference_deductions(tmp_path):
    reports = tmp_path / "reports"
    _write_findings(reports, "artifacts-findings.json", [])
    _write_findings(reports, "crossref-findings.json", [
        _make_finding("high", "cross-reference", "RN-001 no link"),
        _make_finding("high", "cross-reference", "RN-002 no link"),
    ])
    _write_findings(reports, "placeholder-findings.json", [])
    _write_findings(reports, "quality-findings.json", [])

    result = run_script(str(tmp_path))
    assert result["output"]["score"] < 100
    assert result["output"]["layer_scores"]["cross-reference"] < 30


def test_below_threshold_fails(tmp_path):
    reports = tmp_path / "reports"
    _write_findings(reports, "artifacts-findings.json", [
        _make_finding("high", "completeness", f"issue {i}") for i in range(10)
    ])
    _write_findings(reports, "crossref-findings.json", [
        _make_finding("high", "cross-reference", f"xref {i}") for i in range(10)
    ])
    _write_findings(reports, "placeholder-findings.json", [
        _make_finding("high", "empty-section", f"section {i}") for i in range(10)
    ])
    _write_findings(reports, "quality-findings.json", [])

    result = run_script(str(tmp_path))
    assert result["returncode"] == 1
    assert result["output"]["status"] == "FAIL"
    assert result["output"]["score"] < 90


def test_complementary_decisions_recorded(tmp_path):
    reports = tmp_path / "reports"
    _write_findings(reports, "artifacts-findings.json", [])
    _write_findings(reports, "crossref-findings.json", [])
    _write_findings(reports, "placeholder-findings.json", [])
    _write_findings(reports, "quality-findings.json", [])

    result = run_script(
        str(tmp_path),
        "--task-type", "mudanca",
        "--manual",
        "--data-model",
        "--apf-estimate", "42.5",
    )
    out = result["output"]
    assert out["task_type"] == "mudanca"
    assert out["manual_required"] is True
    assert out["data_model_required"] is True
    assert out["apf_estimate"] == 42.5


def test_missing_findings_files(tmp_path):
    (tmp_path / "reports").mkdir(parents=True)
    result = run_script(str(tmp_path))
    assert result["output"]["status"] == "FAIL"
    assert result["output"]["layer_scores"]["quality"] == 0
    assert result["output"]["score"] == 70.0
    assert len(result["output"]["missing_inputs"]) == 4


def test_warnings_not_blocking(tmp_path):
    reports = tmp_path / "reports"
    _write_findings(reports, "artifacts-findings.json", [])
    _write_findings(reports, "crossref-findings.json", [
        _make_finding("medium", "orphan-id", "US-999 orphan"),
    ])
    _write_findings(reports, "placeholder-findings.json", [])
    _write_findings(reports, "quality-findings.json", [])

    result = run_script(str(tmp_path))
    assert result["output"]["status"] == "PASS"
    assert len(result["output"]["warnings"]) >= 1


def test_output_to_file(tmp_path):
    reports = tmp_path / "reports"
    _write_findings(reports, "artifacts-findings.json", [])
    _write_findings(reports, "crossref-findings.json", [])
    _write_findings(reports, "placeholder-findings.json", [])
    _write_findings(reports, "quality-findings.json", [])

    out_file = tmp_path / "verdict.json"
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(tmp_path), "-o", str(out_file)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    data = json.loads(out_file.read_text())
    assert data["status"] == "PASS"
