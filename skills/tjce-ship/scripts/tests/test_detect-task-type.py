#!/usr/bin/env python3
"""Tests for detect-task-type.py"""

import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "detect-task-type.py"


def run_script(*args: str) -> dict:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
    )
    return {"returncode": result.returncode, "output": json.loads(result.stdout)}


def test_explicit_type_nova_funcionalidade(tmp_path):
    result = run_script(str(tmp_path), "--type", "nova_funcionalidade")
    assert result["returncode"] == 0
    assert result["output"]["status"] == "pass"
    assert result["output"]["task_type"] == "nova_funcionalidade"
    assert result["output"]["detection_source"] == "cli"


def test_explicit_type_correcao_garantia(tmp_path):
    result = run_script(str(tmp_path), "--type", "correcao_garantia")
    assert result["returncode"] == 0
    assert result["output"]["task_type"] == "correcao_garantia"


def test_explicit_manual_flag(tmp_path):
    result = run_script(str(tmp_path), "--type", "mudanca", "--manual")
    assert result["returncode"] == 0
    assert result["output"]["manual_necessario"] is True


def test_no_manual_flag_default(tmp_path):
    result = run_script(str(tmp_path), "--type", "mudanca")
    assert result["returncode"] == 0
    assert result["output"]["manual_necessario"] is False


def test_infer_from_config_json(tmp_path):
    (tmp_path / "config.json").write_text(json.dumps({"task_type": "mudanca"}))
    result = run_script(str(tmp_path))
    assert result["returncode"] == 0
    assert result["output"]["task_type"] == "mudanca"
    assert "config.json" in result["output"]["detection_source"]


def test_infer_from_requirements(tmp_path):
    reqs = tmp_path / "requirements"
    reqs.mkdir()
    (reqs / "requirements.md").write_text("# Requisitos\nTipo: correcao em garantia\n")
    result = run_script(str(tmp_path))
    assert result["returncode"] == 0
    assert result["output"]["task_type"] == "correcao_garantia"


def test_no_detection_source_fails(tmp_path):
    result = run_script(str(tmp_path))
    assert result["returncode"] == 1
    assert result["output"]["status"] == "fail"
    assert result["output"]["task_type"] is None


def test_cli_type_overrides_config(tmp_path):
    (tmp_path / "config.json").write_text(json.dumps({"task_type": "mudanca"}))
    result = run_script(str(tmp_path), "--type", "nova_funcionalidade")
    assert result["returncode"] == 0
    assert result["output"]["task_type"] == "nova_funcionalidade"
    assert result["output"]["detection_source"] == "cli"
