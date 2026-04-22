#!/usr/bin/env python3
"""Tests for check-artifacts-exist.py"""

import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "check-artifacts-exist.py"


def run_script(*args: str) -> dict:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
    )
    return {"returncode": result.returncode, "output": json.loads(result.stdout)}


def _create_full_spec(base: Path):
    (base / "requirements").mkdir(parents=True)
    (base / "requirements" / "user-stories.md").write_text("# US\n\nUS-001 story")
    (base / "requirements" / "business-rules.md").write_text("# RN\n\nRN-001 rule")
    (base / "requirements" / "messages.md").write_text("# MSG\n\nMSG-001 msg")
    (base / "requirements" / "product-vision.md").write_text("# Vision\n\nVision content")
    (base / "architecture").mkdir()
    (base / "architecture" / "tech-design.md").write_text("# Tech Design")
    (base / "tests").mkdir()
    (base / "tests" / "test-cases.md").write_text("# CT\n\nCT-001 test")


def test_all_present(tmp_path):
    _create_full_spec(tmp_path)
    result = run_script(str(tmp_path))
    assert result["returncode"] == 0
    assert result["output"]["status"] == "pass"


def test_missing_user_stories(tmp_path):
    _create_full_spec(tmp_path)
    (tmp_path / "requirements" / "user-stories.md").unlink()
    result = run_script(str(tmp_path))
    assert result["returncode"] == 1
    assert result["output"]["summary"]["critical"] >= 1
    issues = [f["issue"] for f in result["output"]["findings"]]
    assert any("user-stories.md" in i for i in issues)


def test_empty_artifact(tmp_path):
    _create_full_spec(tmp_path)
    (tmp_path / "requirements" / "business-rules.md").write_text("")
    result = run_script(str(tmp_path))
    assert result["returncode"] == 1
    issues = [f["issue"] for f in result["output"]["findings"]]
    assert any("vazio" in i.lower() for i in issues)


def test_missing_architecture(tmp_path):
    _create_full_spec(tmp_path)
    for f in (tmp_path / "architecture").iterdir():
        f.unlink()
    (tmp_path / "architecture").rmdir()
    result = run_script(str(tmp_path))
    assert result["returncode"] == 1
    issues = [f["issue"] for f in result["output"]["findings"]]
    assert any("architecture" in i for i in issues)


def test_architecture_without_tech_design(tmp_path):
    _create_full_spec(tmp_path)
    (tmp_path / "architecture" / "tech-design.md").unlink()
    (tmp_path / "architecture" / "other.md").write_text("# Other")
    result = run_script(str(tmp_path))
    assert result["returncode"] == 1
    issues = [f["issue"] for f in result["output"]["findings"]]
    assert any("tech-design" in i for i in issues)


def test_data_model_flag_required(tmp_path):
    _create_full_spec(tmp_path)
    result = run_script(str(tmp_path), "--data-model")
    assert result["returncode"] == 1
    issues = [f["issue"] for f in result["output"]["findings"]]
    assert any("data-model" in i for i in issues)


def test_data_model_present(tmp_path):
    _create_full_spec(tmp_path)
    (tmp_path / "architecture" / "data-model.md").write_text("# Data Model")
    result = run_script(str(tmp_path), "--data-model")
    assert result["returncode"] == 0


def test_ux_flag_required(tmp_path):
    _create_full_spec(tmp_path)
    result = run_script(str(tmp_path), "--ux")
    assert result["returncode"] == 1
    issues = [f["issue"] for f in result["output"]["findings"]]
    assert any("ux" in i.lower() for i in issues)


def test_recommended_artifact_not_blocking(tmp_path):
    _create_full_spec(tmp_path)
    result = run_script(str(tmp_path))
    assert result["returncode"] == 0
    low_findings = [f for f in result["output"]["findings"] if f["severity"] == "low"]
    assert any("threat-model" in f["issue"] for f in low_findings)


def test_empty_directory(tmp_path):
    result = run_script(str(tmp_path))
    assert result["returncode"] == 1
    assert result["output"]["summary"]["critical"] >= 5
