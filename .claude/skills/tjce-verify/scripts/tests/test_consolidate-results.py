#!/usr/bin/env python3
"""Tests for consolidate-results.py"""

import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "consolidate-results.py"


def run_script(output_folder: str, threshold: float = 80.0) -> dict:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), output_folder, "--threshold", str(threshold)],
        capture_output=True,
        text=True,
    )
    return {"returncode": result.returncode, "output": json.loads(result.stdout)}


def _setup_reports(tmp_path, coverage=85.0, alta=0, media=0, baixa=0,
                   sec_critical=0, sec_high=0):
    reports = tmp_path / "reports"
    reports.mkdir(parents=True, exist_ok=True)

    (reports / "verify-layer1-automated.md").write_text(
        f"# Layer 1\n\nCobertura: {coverage}%\n"
    )

    defect_lines = []
    for _ in range(alta):
        defect_lines.append("| DEF-001 | CT-001 | Alta | Crash | RN-001 | novo |")
    for _ in range(media):
        defect_lines.append("| DEF-002 | CT-002 | Media | Timeout | RN-002 | novo |")
    for _ in range(baixa):
        defect_lines.append("| DEF-003 | CT-003 | Baixa | Label errado | RN-003 | novo |")
    (reports / "test-cycle-1.md").write_text(
        "# Cycle 1\n\n| ID | CT | Severidade | Desc | RN | Status |\n"
        + "| -- | -- | -- | -- | -- | -- |\n"
        + "\n".join(defect_lines)
        + "\n"
    )

    sec_lines = []
    for _ in range(sec_critical):
        sec_lines.append("| SEC-001 | critico | injection | app.py:10 |")
    for _ in range(sec_high):
        sec_lines.append("| SEC-002 | alto | cors | config.py:5 |")
    (reports / "security-report.md").write_text(
        "# Security\n\n| ID | Severidade | Cat | Local |\n"
        + "| -- | -- | -- | -- |\n"
        + "\n".join(sec_lines)
        + "\n"
    )


def test_all_pass_go(tmp_path):
    _setup_reports(tmp_path, coverage=90.0)
    result = run_script(str(tmp_path))
    assert result["returncode"] == 0
    assert result["output"]["verdict"] == "GO"
    assert result["output"]["status"] == "pass"


def test_alta_defects_nogo(tmp_path):
    _setup_reports(tmp_path, coverage=90.0, alta=1)
    result = run_script(str(tmp_path))
    assert result["returncode"] == 1
    assert result["output"]["verdict"] == "NO-GO"
    assert result["output"]["metrics"]["defects_alta"] == 1


def test_critical_security_nogo(tmp_path):
    _setup_reports(tmp_path, coverage=90.0, sec_critical=1)
    result = run_script(str(tmp_path))
    assert result["returncode"] == 1
    assert result["output"]["verdict"] == "NO-GO"
    assert result["output"]["metrics"]["security_critical"] == 1


def test_low_coverage_nogo(tmp_path):
    _setup_reports(tmp_path, coverage=60.0)
    result = run_script(str(tmp_path))
    assert result["returncode"] == 1
    assert result["output"]["verdict"] == "NO-GO"


def test_media_defects_go_with_caveats(tmp_path):
    _setup_reports(tmp_path, coverage=85.0, media=2)
    result = run_script(str(tmp_path))
    assert result["returncode"] == 0
    assert result["output"]["verdict"] == "GO COM RESSALVAS"
    assert result["output"]["status"] == "warning"


def test_high_security_go_with_caveats(tmp_path):
    _setup_reports(tmp_path, coverage=85.0, sec_high=1)
    result = run_script(str(tmp_path))
    assert result["returncode"] == 0
    assert result["output"]["verdict"] == "GO COM RESSALVAS"


def test_missing_reports_error(tmp_path):
    (tmp_path / "reports").mkdir()
    result = run_script(str(tmp_path))
    assert result["returncode"] == 2
    assert result["output"]["status"] == "error"


def test_custom_threshold(tmp_path):
    _setup_reports(tmp_path, coverage=75.0)
    # 75% fails at default 80%
    result = run_script(str(tmp_path), threshold=80.0)
    assert result["output"]["verdict"] == "NO-GO"
    # 75% passes at 70%
    result = run_script(str(tmp_path), threshold=70.0)
    assert result["output"]["verdict"] == "GO"


def test_combined_alta_and_critical(tmp_path):
    _setup_reports(tmp_path, coverage=90.0, alta=1, sec_critical=2)
    result = run_script(str(tmp_path))
    assert result["returncode"] == 1
    assert result["output"]["verdict"] == "NO-GO"
    assert result["output"]["summary"]["critical"] >= 2


def test_unparseable_coverage_is_nogo(tmp_path):
    """Coverage that cannot be parsed from the report must be treated as NO-GO."""
    reports = tmp_path / "reports"
    reports.mkdir(parents=True)
    (reports / "verify-layer1-automated.md").write_text("# Layer 1\n\nNo coverage info here.\n")
    (reports / "test-cycle-1.md").write_text("# Cycle 1\n\n| ID | CT | Sev | Desc | RN | Status |\n| -- | -- | -- | -- | -- | -- |\n")
    (reports / "security-report.md").write_text("# Security\n\nNo findings.\n")

    result = run_script(str(tmp_path))
    assert result["returncode"] == 1
    assert result["output"]["verdict"] == "NO-GO"
    assert result["output"]["metrics"]["coverage_percent"] is None
    assert any("nao pode ser extraida" in f["issue"] for f in result["output"]["findings"])


def test_markdown_format(tmp_path):
    """--format markdown produces a markdown report."""
    _setup_reports(tmp_path, coverage=90.0)
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(tmp_path), "--format", "markdown"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "# Verify Summary" in result.stdout
    assert "GO" in result.stdout
    assert "90.0%" in result.stdout
