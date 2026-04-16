#!/usr/bin/env python3
"""Tests for extract-git-changelog.py"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parent.parent / "extract-git-changelog.py"


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


def _init_repo(path: Path) -> Path:
    """Create a git repo with some commits."""
    subprocess.run(["git", "init"], cwd=str(path), capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=str(path), capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Tester"],
        cwd=str(path), capture_output=True,
    )
    return path


def _commit(repo: Path, message: str, filename: str = ""):
    fname = filename or message.replace(" ", "-")[:20] + ".txt"
    (repo / fname).write_text(message, encoding="utf-8")
    subprocess.run(["git", "add", fname], cwd=str(repo), capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", message],
        cwd=str(repo), capture_output=True,
    )


def _tag(repo: Path, tag: str):
    subprocess.run(["git", "tag", tag], cwd=str(repo), capture_output=True)


def test_basic_extraction(tmp_path):
    repo = _init_repo(tmp_path)
    _commit(repo, "feat(US-001): add login page")
    _commit(repo, "fix(US-001): fix login validation")
    _commit(repo, "feat(US-002): add dashboard")
    _commit(repo, "chore: update CI config")

    result = run_script(str(repo))
    assert result["returncode"] == 0
    out = result["output"]
    assert out["total_commits"] == 4
    assert "US-001" in out["stories"]
    assert "US-002" in out["stories"]
    assert len(out["stories"]["US-001"]["commits"]) == 2
    assert len(out["stories"]["US-002"]["commits"]) == 1
    assert len(out["unmapped"]) == 1


def test_since_tag(tmp_path):
    repo = _init_repo(tmp_path)
    _commit(repo, "old commit")
    _tag(repo, "v1.0.0")
    _commit(repo, "feat(US-003): new feature after tag")

    result = run_script(str(repo), "--since", "v1.0.0")
    assert result["returncode"] == 0
    out = result["output"]
    assert out["total_commits"] == 1
    assert out["since"] == "v1.0.0"
    assert "US-003" in out["stories"]


def test_stories_enrichment(tmp_path):
    repo = _init_repo(tmp_path)
    _commit(repo, "feat(US-001): implement login")

    stories = tmp_path / "user-stories.md"
    stories.write_text(
        "# Estorias de Usuario\n\n"
        "## US-001 — Login de Usuario\n"
        "Como usuario quero fazer login.\n\n"
        "## US-002 — Dashboard\n"
        "Como usuario quero ver o dashboard.\n",
        encoding="utf-8",
    )

    result = run_script(str(repo), "--stories", str(stories))
    assert result["returncode"] == 0
    assert result["output"]["stories"]["US-001"]["title"] == "Login de Usuario"


def test_output_to_file(tmp_path):
    repo = _init_repo(tmp_path)
    _commit(repo, "feat(US-001): test commit")

    out_file = tmp_path / "output" / "changelog.json"
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(repo), "-o", str(out_file)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    data = json.loads(out_file.read_text())
    assert data["total_commits"] == 1


def test_no_commits_in_range(tmp_path):
    repo = _init_repo(tmp_path)
    _commit(repo, "initial commit")
    _tag(repo, "v1.0.0")

    result = run_script(str(repo), "--since", "v1.0.0")
    assert result["returncode"] == 1
    assert result["output"]["total_commits"] == 0


def test_not_a_git_repo(tmp_path):
    result = run_script(str(tmp_path))
    assert result["returncode"] == 2


def test_stats_computed(tmp_path):
    repo = _init_repo(tmp_path)
    _commit(repo, "feat(US-001): one")
    _commit(repo, "feat(US-001): two")
    _commit(repo, "chore: misc")

    result = run_script(str(repo))
    stats = result["output"]["stats"]
    assert stats["total"] == 3
    assert stats["mapped"] == 2
    assert stats["unmapped"] == 1
    assert stats["stories_count"] == 1


def test_commit_references_multiple_us(tmp_path):
    repo = _init_repo(tmp_path)
    _commit(repo, "feat(US-001, US-002): shared feature")

    result = run_script(str(repo))
    assert result["returncode"] == 0
    assert "US-001" in result["output"]["stories"]
    assert "US-002" in result["output"]["stories"]


def test_authors_collected(tmp_path):
    repo = _init_repo(tmp_path)
    _commit(repo, "feat(US-001): by tester")

    result = run_script(str(repo))
    assert "Tester" in result["output"]["authors"]


def test_auto_detect_last_tag(tmp_path):
    repo = _init_repo(tmp_path)
    _commit(repo, "old feature")
    _tag(repo, "v0.9.0")
    _commit(repo, "feat(US-005): new after tag")

    result = run_script(str(repo))
    assert result["returncode"] == 0
    assert result["output"]["since"] == "v0.9.0"
    assert result["output"]["total_commits"] == 1
