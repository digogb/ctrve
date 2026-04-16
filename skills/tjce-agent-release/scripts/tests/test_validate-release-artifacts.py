#!/usr/bin/env python3
"""Tests for validate-release-artifacts.py"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parent.parent / "validate-release-artifacts.py"


def run_script(*args: str) -> dict:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
    )
    return {
        "returncode": result.returncode,
        "output": json.loads(result.stdout) if result.stdout.strip() else {},
        "stderr": result.stderr,
    }


def _create_artifact(release_dir: Path, name: str, content: str):
    release_dir.mkdir(parents=True, exist_ok=True)
    (release_dir / name).write_text(content, encoding="utf-8")


def _good_pml():
    return (
        "# Plano de Mudanca e Liberacao\n\n"
        "## 1. Identificacao\n\n"
        "| Campo | Valor |\n|---|---|\n| Sistema | CTRVE |\n\n"
        "## 2. Descricao da Mudanca\n\n"
        "- US-001: Login implementado\n\n"
        "## 3. Analise de Impacto\n\n"
        "Sem alteracoes de banco.\n\n"
        "## 4. Procedimento de Implantacao\n\n"
        "1. Deploy backend\n\n"
        "## 5. Procedimento de Rollback\n\n"
        "1. Reverter deploy\n\n"
        "## 6. Validacao Pos-Implantacao\n\n"
        "- Verificar health check\n"
    )


def _good_changelog():
    return (
        "# CHANGELOG — CTRVE v1.0.0\n\n"
        "## Funcionalidades Implementadas\n\n"
        "### US-001 — Login\n"
        "- feat: add login (`abc1234`)\n\n"
        "## Estatisticas\n\n"
        "- Commits mapeados: 1/1 (100%)\n"
    )


def _good_checklist():
    return (
        "# Checklist de Implantacao\n\n"
        "## Pre-Deploy\n\n"
        "- [ ] Backup realizado\n\n"
        "## Deploy — Backend\n\n"
        "- [ ] Restart servico\n\n"
        "## Pos-Deploy\n\n"
        "- [ ] Health check OK\n"
    )


def _good_rollback():
    return (
        "# Plano de Rollback\n\n"
        "## Criterios para Rollback\n\n"
        "Executar se health check falhar.\n\n"
        "## Procedimento\n\n"
        "### 1. Backend\n"
        "- Deploy da versao anterior\n- Restart servico\n\n"
        "## Validacao Pos-Rollback\n\n"
        "- Health check OK\n"
    )


def _create_all_good(release_dir: Path):
    _create_artifact(release_dir, "PML.md", _good_pml())
    _create_artifact(release_dir, "CHANGELOG.md", _good_changelog())
    _create_artifact(release_dir, "deploy-checklist.md", _good_checklist())
    _create_artifact(release_dir, "rollback-plan.md", _good_rollback())


def test_all_valid(tmp_path):
    release = tmp_path / "release"
    _create_all_good(release)
    result = run_script(str(release))
    assert result["returncode"] == 0
    assert result["output"]["valid"] is True
    assert result["output"]["findings_count"] == 0


def test_missing_artifacts(tmp_path):
    release = tmp_path / "release"
    release.mkdir()
    result = run_script(str(release))
    assert result["returncode"] == 2
    assert result["output"]["valid"] is False
    assert len(result["output"]["artifacts_missing"]) == 4


def test_empty_section_detected(tmp_path):
    release = tmp_path / "release"
    _create_all_good(release)
    _create_artifact(release, "PML.md", (
        "# PML\n\n"
        "## 1. Identificacao\n\n"
        "| Campo | Valor |\n\n"
        "## 2. Descricao da Mudanca\n\n"
        "## 3. Analise de Impacto\n\n"
        "Nenhuma.\n"
    ))
    result = run_script(str(release))
    assert result["returncode"] == 1
    empty_findings = [
        f for f in result["output"]["findings"]
        if f["category"] == "empty-section"
    ]
    assert len(empty_findings) >= 1


def test_placeholder_detected(tmp_path):
    release = tmp_path / "release"
    _create_all_good(release)
    _create_artifact(release, "PML.md", (
        "# PML\n\n"
        "## 1. Identificacao\n\n"
        "TODO: preencher identificacao\n\n"
        "## 2. Descricao\n\n"
        "Mudancas implementadas.\n"
    ))
    result = run_script(str(release))
    placeholder_findings = [
        f for f in result["output"]["findings"]
        if f["category"] == "placeholder"
    ]
    assert len(placeholder_findings) >= 1


def test_rollback_missing(tmp_path):
    release = tmp_path / "release"
    _create_artifact(release, "PML.md", _good_pml())
    _create_artifact(release, "CHANGELOG.md", _good_changelog())
    _create_artifact(release, "deploy-checklist.md", _good_checklist())
    result = run_script(str(release))
    assert result["returncode"] == 2
    rollback_findings = [
        f for f in result["output"]["findings"]
        if "rollback" in f["issue"].lower() or "Rollback" in f["issue"]
    ]
    assert len(rollback_findings) >= 1


def test_rollback_too_short(tmp_path):
    release = tmp_path / "release"
    _create_all_good(release)
    _create_artifact(release, "rollback-plan.md", "# Rollback\n\nN/A\n")
    result = run_script(str(release))
    rollback_findings = [
        f for f in result["output"]["findings"]
        if f["category"] == "incomplete-artifact"
    ]
    assert len(rollback_findings) >= 1


def test_us_reference_validation(tmp_path):
    release = tmp_path / "release"
    _create_all_good(release)
    _create_artifact(release, "PML.md", (
        "# PML\n\n"
        "## 1. Identificacao\n\n"
        "Sistema CTRVE\n\n"
        "## 2. Descricao\n\n"
        "- US-001: Login\n- US-999: Feature inexistente\n\n"
        "## 3. Impacto\n\nNenhum\n"
    ))

    stories = tmp_path / "user-stories.md"
    stories.write_text(
        "# Estorias\n\n## US-001 — Login\nDescricao.\n",
        encoding="utf-8",
    )

    result = run_script(str(release), "--stories", str(stories))
    invalid_ref = [
        f for f in result["output"]["findings"]
        if f["category"] == "invalid-reference"
    ]
    assert len(invalid_ref) >= 1
    assert any("US-999" in f["issue"] for f in invalid_ref)


def test_output_to_file(tmp_path):
    release = tmp_path / "release"
    _create_all_good(release)
    out_file = tmp_path / "validation.json"
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(release), "-o", str(out_file)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    data = json.loads(out_file.read_text())
    assert data["valid"] is True


def test_not_a_directory(tmp_path):
    result = run_script(str(tmp_path / "nonexistent"))
    assert result["returncode"] == 2


def test_pendente_with_preposition_allowed(tmp_path):
    release = tmp_path / "release"
    _create_all_good(release)
    _create_artifact(release, "PML.md", (
        "# PML\n\n"
        "## 1. Identificacao\n\n"
        "Sistema CTRVE\n\n"
        "## 2. Descricao\n\n"
        "Item pendente de aprovacao pelo comite.\n"
    ))
    result = run_script(str(release))
    placeholder_in_pml = [
        f for f in result["output"]["findings"]
        if f["category"] == "placeholder" and f["file"] == "PML.md"
    ]
    assert len(placeholder_in_pml) == 0


def test_pendente_standalone_flagged(tmp_path):
    release = tmp_path / "release"
    _create_all_good(release)
    _create_artifact(release, "PML.md", (
        "# PML\n\n"
        "## 1. Identificacao\n\n"
        "Sistema CTRVE\n\n"
        "## 2. Descricao\n\n"
        "Status: PENDENTE\n"
    ))
    result = run_script(str(release))
    placeholder_in_pml = [
        f for f in result["output"]["findings"]
        if f["category"] == "placeholder" and f["file"] == "PML.md"
    ]
    assert len(placeholder_in_pml) >= 1


def test_cross_consistency_us_mismatch(tmp_path):
    release = tmp_path / "release"
    _create_all_good(release)
    _create_artifact(release, "PML.md", (
        "# PML\n\n"
        "## 1. Identificacao\n\nSistema CTRVE\n\n"
        "## 2. Descricao\n\n- US-001: Login\n- US-002: Dashboard\n"
    ))
    _create_artifact(release, "CHANGELOG.md", (
        "# CHANGELOG\n\n"
        "## Funcionalidades\n\n### US-001 — Login\n- feat: login\n\n"
        "## Estatisticas\n\n- 1/1\n"
    ))
    result = run_script(str(release))
    cross = [
        f for f in result["output"]["findings"]
        if f["category"] == "cross-consistency"
    ]
    assert any("US-002" in f["issue"] and "PML" in f["file"] for f in cross)


def test_cross_consistency_migration_without_rollback(tmp_path):
    release = tmp_path / "release"
    _create_all_good(release)
    _create_artifact(release, "deploy-checklist.md", (
        "# Checklist\n\n"
        "## Deploy — Banco\n\n"
        "- [ ] Executar: `alembic upgrade head`\n\n"
        "## Pos-Deploy\n\n- Health check\n"
    ))
    _create_artifact(release, "rollback-plan.md", (
        "# Rollback\n\n"
        "## Procedimento\n\n"
        "### 1. Backend\n- Deploy versao anterior\n- Restart servico\n\n"
        "## Validacao\n\n- Health check OK\n"
    ))
    result = run_script(str(release))
    cross = [
        f for f in result["output"]["findings"]
        if f["category"] == "cross-consistency" and "Alembic" in f["issue"]
    ]
    assert len(cross) >= 1


def test_cross_consistency_all_aligned(tmp_path):
    release = tmp_path / "release"
    _create_all_good(release)
    result = run_script(str(release))
    cross = [
        f for f in result["output"]["findings"]
        if f["category"] == "cross-consistency"
    ]
    assert len(cross) == 0
