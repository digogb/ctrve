#!/usr/bin/env python3
"""Tests for manage-ship-state.py"""

import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "manage-ship-state.py"


def run_script(*args: str) -> dict:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
    )
    return {"returncode": result.returncode, "output": json.loads(result.stdout)}


def test_init_creates_state(tmp_path):
    state_path = tmp_path / "ship-state.json"
    result = run_script("init", str(state_path), "--task-type", "nova_funcionalidade")
    assert result["returncode"] == 0
    assert result["output"]["status"] == "ok"
    assert state_path.exists()

    state = json.loads(state_path.read_text())
    assert state["task_type"] == "nova_funcionalidade"
    assert state["stage"] == 1
    assert state["stage_status"] == "running"
    assert state["manual_necessario"] is False


def test_init_with_manual(tmp_path):
    state_path = tmp_path / "ship-state.json"
    result = run_script("init", str(state_path), "--task-type", "mudanca", "--manual")
    assert result["returncode"] == 0
    state = json.loads(state_path.read_text())
    assert state["manual_necessario"] is True


def test_init_fails_if_exists(tmp_path):
    state_path = tmp_path / "ship-state.json"
    state_path.write_text("{}")
    result = run_script("init", str(state_path), "--task-type", "mudanca")
    assert result["returncode"] == 1
    assert "already exists" in result["output"]["message"]


def test_update_stage(tmp_path):
    state_path = tmp_path / "ship-state.json"
    run_script("init", str(state_path), "--task-type", "mudanca")

    result = run_script("update", str(state_path), "--stage", "3", "--stage-status", "completed")
    assert result["returncode"] == 0
    state = result["output"]["state"]
    assert state["stage"] == 3
    assert state["stage_status"] == "completed"
    assert len(state["history"]) == 1


def test_update_pending_gate(tmp_path):
    state_path = tmp_path / "ship-state.json"
    run_script("init", str(state_path), "--task-type", "mudanca")

    result = run_script("update", str(state_path), "--stage", "4", "--pending-gate", "pml_validation")
    state = result["output"]["state"]
    assert state["pending_gate"] == "pml_validation"

    result = run_script("update", str(state_path), "--pending-gate", "none")
    state = result["output"]["state"]
    assert state["pending_gate"] is None


def test_update_rdm_and_deployment(tmp_path):
    state_path = tmp_path / "ship-state.json"
    run_script("init", str(state_path), "--task-type", "mudanca")

    result = run_script("update", str(state_path), "--rdm", "RDM-2024-001", "--deployment-date", "2024-03-15")
    state = result["output"]["state"]
    assert state["rdm"] == "RDM-2024-001"
    assert state["deployment_date"] == "2024-03-15"


def test_update_increment_ajustar(tmp_path):
    state_path = tmp_path / "ship-state.json"
    run_script("init", str(state_path), "--task-type", "mudanca")

    run_script("update", str(state_path), "--increment-ajustar")
    run_script("update", str(state_path), "--increment-ajustar")
    result = run_script("update", str(state_path), "--increment-ajustar")
    assert result["output"]["state"]["ajustar_iterations"] == 3


def test_update_not_found(tmp_path):
    result = run_script("update", str(tmp_path / "ship-state.json"), "--stage", "2")
    assert result["returncode"] == 1


def test_read_existing(tmp_path):
    state_path = tmp_path / "ship-state.json"
    run_script("init", str(state_path), "--task-type", "correcao_garantia")

    result = run_script("read", str(state_path))
    assert result["returncode"] == 0
    assert result["output"]["state"]["task_type"] == "correcao_garantia"


def test_read_not_found(tmp_path):
    result = run_script("read", str(tmp_path / "ship-state.json"))
    assert result["returncode"] == 0
    assert result["output"]["status"] == "not_found"


def test_resume_from_valid(tmp_path):
    state_path = tmp_path / "ship-state.json"
    run_script("init", str(state_path), "--task-type", "mudanca")
    run_script("update", str(state_path), "--stage", "4", "--stage-status", "awaiting_pml_validation", "--pending-gate", "pml_validation")

    result = run_script("resume-from", str(state_path), "--task-type", "mudanca")
    assert result["returncode"] == 0
    assert result["output"]["resume_stage"] == 4
    assert result["output"]["pending_gate"] == "pml_validation"
    assert len(result["output"]["warnings"]) == 0


def test_resume_from_mismatched_type(tmp_path):
    state_path = tmp_path / "ship-state.json"
    run_script("init", str(state_path), "--task-type", "mudanca")

    result = run_script("resume-from", str(state_path), "--task-type", "nova_funcionalidade")
    assert result["returncode"] == 0
    assert len(result["output"]["warnings"]) == 1
    assert "differs" in result["output"]["warnings"][0]


def test_atomic_write_no_corruption(tmp_path):
    state_path = tmp_path / "ship-state.json"
    run_script("init", str(state_path), "--task-type", "mudanca")

    for i in range(2, 10):
        run_script("update", str(state_path), "--stage", str(i), "--stage-status", "completed")

    state = json.loads(state_path.read_text())
    assert state["stage"] == 9
    assert len(state["history"]) == 8
    assert not (state_path.with_suffix(".tmp")).exists()
