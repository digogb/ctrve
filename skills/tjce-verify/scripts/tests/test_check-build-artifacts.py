#!/usr/bin/env python3
"""Tests for check-build-artifacts.py"""

import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "check-build-artifacts.py"


def run_script(output_folder: str) -> dict:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), output_folder],
        capture_output=True,
        text=True,
    )
    return {"returncode": result.returncode, "output": json.loads(result.stdout)}


def test_all_required_present(tmp_path):
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test-cases.md").write_text("# Test Cases")
    (tmp_path / "reports").mkdir()
    (tmp_path / "reports" / "code-review.md").write_text("# Review")
    (tmp_path / "reports" / "coverage-report.md").write_text("# Coverage")

    result = run_script(str(tmp_path))
    assert result["returncode"] == 0
    assert result["output"]["status"] == "pass"
    assert result["output"]["summary"]["critical"] == 0


def test_missing_required_artifact(tmp_path):
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test-cases.md").write_text("# Test Cases")
    (tmp_path / "reports").mkdir()
    # Missing: code-review.md and coverage-report.md

    result = run_script(str(tmp_path))
    assert result["returncode"] == 1
    assert result["output"]["status"] == "fail"
    assert result["output"]["summary"]["critical"] == 2


def test_optional_missing_does_not_block(tmp_path):
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test-cases.md").write_text("# Test Cases")
    (tmp_path / "reports").mkdir()
    (tmp_path / "reports" / "code-review.md").write_text("# Review")
    (tmp_path / "reports" / "coverage-report.md").write_text("# Coverage")
    # architecture/data-model.md is optional and missing

    result = run_script(str(tmp_path))
    assert result["returncode"] == 0
    assert result["output"]["status"] == "pass"
    # Should have an info finding for optional artifact
    info_findings = [f for f in result["output"]["findings"] if f["severity"] == "info"]
    assert len(info_findings) == 1
    assert "data-model.md" in info_findings[0]["issue"]


def test_all_present_including_optional(tmp_path):
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test-cases.md").write_text("# Test Cases")
    (tmp_path / "reports").mkdir()
    (tmp_path / "reports" / "code-review.md").write_text("# Review")
    (tmp_path / "reports" / "coverage-report.md").write_text("# Coverage")
    (tmp_path / "architecture").mkdir()
    (tmp_path / "architecture" / "data-model.md").write_text("# Data Model")

    result = run_script(str(tmp_path))
    assert result["returncode"] == 0
    assert result["output"]["status"] == "pass"
    assert result["output"]["summary"]["total"] == 0


def test_empty_directory(tmp_path):
    result = run_script(str(tmp_path))
    assert result["returncode"] == 1
    assert result["output"]["status"] == "fail"
    assert result["output"]["summary"]["critical"] == 3
