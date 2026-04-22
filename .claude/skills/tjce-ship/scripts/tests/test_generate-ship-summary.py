#!/usr/bin/env python3
"""Tests for generate-ship-summary.py"""

import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "generate-ship-summary.py"


def run_script(*args: str) -> dict:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
    )
    return {"returncode": result.returncode, "stdout": result.stdout, "stderr": result.stderr}


def _create_full_release(release_dir: Path, task_type: str = "nova_funcionalidade", manual: bool = False):
    release_dir.mkdir(parents=True, exist_ok=True)
    (release_dir / "CHANGELOG.md").write_text("# Changelog\n")
    (release_dir / "deploy-checklist.md").write_text("# Deploy\n")
    (release_dir / "rollback-plan.md").write_text("# Rollback\n")
    (release_dir / "PML.md").write_text("# PML\n")

    if task_type != "correcao_garantia":
        apf = release_dir / "apf"
        apf.mkdir(parents=True, exist_ok=True)
        (apf / "contagem-detalhada.md").write_text("# Contagem\n")
        (apf / "resumo-apf.md").write_text("# Resumo\n")
    else:
        apf = release_dir / "apf"
        apf.mkdir(parents=True, exist_ok=True)
        (apf / "resumo-apf.md").write_text("PF = 0\n")

    if manual:
        man = release_dir / "manual"
        man.mkdir(parents=True, exist_ok=True)
        (man / "manual-usuario.md").write_text("# Manual\n")


def test_complete_release_json(tmp_path):
    _create_full_release(tmp_path / "release")
    r = run_script(str(tmp_path), "--task-type", "nova_funcionalidade")
    assert r["returncode"] == 0
    data = json.loads(r["stdout"])
    assert data["verdict"] == "FECHADO"
    assert len(data["missing"]) == 0


def test_complete_release_markdown(tmp_path):
    _create_full_release(tmp_path / "release")
    r = run_script(str(tmp_path), "--task-type", "nova_funcionalidade", "--format", "markdown")
    assert r["returncode"] == 0
    assert "FECHADO" in r["stdout"]
    assert "Artefatos de Entrega" in r["stdout"]


def test_missing_artifacts_incompleto(tmp_path):
    release = tmp_path / "release"
    release.mkdir(parents=True)
    (release / "CHANGELOG.md").write_text("# Changelog\n")

    r = run_script(str(tmp_path), "--task-type", "nova_funcionalidade")
    assert r["returncode"] == 1
    data = json.loads(r["stdout"])
    assert data["verdict"] == "INCOMPLETO"
    assert len(data["missing"]) > 0


def test_correcao_garantia_no_apf_detail(tmp_path):
    _create_full_release(tmp_path / "release", task_type="correcao_garantia")
    r = run_script(str(tmp_path), "--task-type", "correcao_garantia")
    assert r["returncode"] == 0
    data = json.loads(r["stdout"])
    assert data["verdict"] == "FECHADO"
    artifact_names = [a["artifact"] for a in data["artifacts"]]
    assert "apf/contagem-detalhada.md" not in artifact_names
    assert "apf/resumo-apf.md" in artifact_names


def test_rdm_number_included(tmp_path):
    _create_full_release(tmp_path / "release")
    r = run_script(str(tmp_path), "--task-type", "nova_funcionalidade", "--rdm", "RDM-2024-001")
    data = json.loads(r["stdout"])
    assert data["rdm"] == "RDM-2024-001"


def test_rdm_in_markdown(tmp_path):
    _create_full_release(tmp_path / "release")
    r = run_script(str(tmp_path), "--task-type", "mudanca", "--rdm", "RDM-2024-002", "--format", "markdown")
    assert "RDM-2024-002" in r["stdout"]


def test_manual_required_complete(tmp_path):
    _create_full_release(tmp_path / "release", manual=True)
    r = run_script(str(tmp_path), "--task-type", "nova_funcionalidade", "--manual-required")
    assert r["returncode"] == 0
    data = json.loads(r["stdout"])
    assert data["verdict"] == "FECHADO"


def test_manual_required_but_missing(tmp_path):
    _create_full_release(tmp_path / "release")
    r = run_script(str(tmp_path), "--task-type", "nova_funcionalidade", "--manual-required")
    assert r["returncode"] == 1
    data = json.loads(r["stdout"])
    assert data["verdict"] == "INCOMPLETO"
    assert "manual/manual-usuario.md" in data["missing"]


def test_ship_state_included(tmp_path):
    _create_full_release(tmp_path / "release")
    state = {"stage": 9, "status": "closed", "timestamp": "2024-01-01T00:00:00Z"}
    (tmp_path / "release" / "ship-state.json").write_text(json.dumps(state))

    r = run_script(str(tmp_path), "--task-type", "nova_funcionalidade")
    data = json.loads(r["stdout"])
    assert data["ship_state"] is not None
    assert data["ship_state"]["stage"] == 9


def test_output_to_file(tmp_path):
    _create_full_release(tmp_path / "release")
    out_file = tmp_path / "result.json"
    r = run_script(str(tmp_path), "--task-type", "nova_funcionalidade", "-o", str(out_file))
    assert r["returncode"] == 0
    data = json.loads(out_file.read_text())
    assert data["verdict"] == "FECHADO"
