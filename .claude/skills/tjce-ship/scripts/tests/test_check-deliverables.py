#!/usr/bin/env python3
"""Tests for check-deliverables.py"""

import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "check-deliverables.py"


def run_script(*args: str) -> dict:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
    )
    return {"returncode": result.returncode, "output": json.loads(result.stdout)}


def _create_base_artifacts(release_dir: Path):
    release_dir.mkdir(parents=True, exist_ok=True)
    (release_dir / "CHANGELOG.md").write_text("# Changelog\n")
    (release_dir / "deploy-checklist.md").write_text("# Deploy\n")
    (release_dir / "rollback-plan.md").write_text("# Rollback\n")
    (release_dir / "PML.md").write_text("# PML\n")


def _create_apf_artifacts(release_dir: Path):
    apf_dir = release_dir / "apf"
    apf_dir.mkdir(parents=True, exist_ok=True)
    (apf_dir / "contagem-detalhada.md").write_text("# Contagem\n")
    (apf_dir / "resumo-apf.md").write_text("# Resumo\n")


def _create_manual_artifact(release_dir: Path):
    manual_dir = release_dir / "manual"
    manual_dir.mkdir(parents=True, exist_ok=True)
    (manual_dir / "manual-usuario.md").write_text("# Manual\n")


def test_all_present_nova_funcionalidade(tmp_path):
    release = tmp_path / "release"
    _create_base_artifacts(release)
    _create_apf_artifacts(release)

    result = run_script(str(tmp_path), "--task-type", "nova_funcionalidade")
    assert result["returncode"] == 0
    assert result["output"]["status"] == "pass"
    assert result["output"]["summary"]["critical"] == 0


def test_all_present_with_manual(tmp_path):
    release = tmp_path / "release"
    _create_base_artifacts(release)
    _create_apf_artifacts(release)
    _create_manual_artifact(release)

    result = run_script(str(tmp_path), "--task-type", "nova_funcionalidade", "--manual-required")
    assert result["returncode"] == 0
    assert result["output"]["status"] == "pass"


def test_missing_rollback_plan(tmp_path):
    release = tmp_path / "release"
    _create_base_artifacts(release)
    _create_apf_artifacts(release)
    (release / "rollback-plan.md").unlink()

    result = run_script(str(tmp_path), "--task-type", "nova_funcionalidade")
    assert result["returncode"] == 1
    assert result["output"]["summary"]["critical"] == 1
    issues = [f["issue"] for f in result["output"]["findings"]]
    assert any("rollback-plan.md" in i for i in issues)


def test_correcao_garantia_skips_apf(tmp_path):
    release = tmp_path / "release"
    _create_base_artifacts(release)
    apf_dir = release / "apf"
    apf_dir.mkdir(parents=True)
    (apf_dir / "resumo-apf.md").write_text("PF = 0\n")

    result = run_script(str(tmp_path), "--task-type", "correcao_garantia")
    assert result["returncode"] == 0
    assert result["output"]["status"] == "pass"


def test_missing_manual_when_required(tmp_path):
    release = tmp_path / "release"
    _create_base_artifacts(release)
    _create_apf_artifacts(release)

    result = run_script(str(tmp_path), "--task-type", "mudanca", "--manual-required")
    assert result["returncode"] == 1
    issues = [f["issue"] for f in result["output"]["findings"]]
    assert any("manual-usuario.md" in i for i in issues)


def test_empty_artifact_detected(tmp_path):
    release = tmp_path / "release"
    _create_base_artifacts(release)
    _create_apf_artifacts(release)
    (release / "PML.md").write_text("")

    result = run_script(str(tmp_path), "--task-type", "nova_funcionalidade")
    assert result["returncode"] == 1
    issues = [f["issue"] for f in result["output"]["findings"]]
    assert any("vazio" in i.lower() for i in issues)


def test_checklist_includes_all_artifacts(tmp_path):
    release = tmp_path / "release"
    _create_base_artifacts(release)
    _create_apf_artifacts(release)

    result = run_script(str(tmp_path), "--task-type", "nova_funcionalidade")
    checklist_artifacts = [c["artifact"] for c in result["output"]["checklist"]]
    assert "CHANGELOG.md" in checklist_artifacts
    assert "PML.md" in checklist_artifacts
    assert "apf/resumo-apf.md" in checklist_artifacts


def test_empty_directory_all_missing(tmp_path):
    result = run_script(str(tmp_path), "--task-type", "mudanca")
    assert result["returncode"] == 1
    assert result["output"]["summary"]["critical"] >= 4
