#!/usr/bin/env python3
"""Tests for detect-deploy-changes.py"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parent.parent / "detect-deploy-changes.py"


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


def _commit(repo: Path, message: str, files: dict[str, str] | None = None):
    if files:
        for fname, content in files.items():
            fpath = repo / fname
            fpath.parent.mkdir(parents=True, exist_ok=True)
            fpath.write_text(content, encoding="utf-8")
            subprocess.run(
                ["git", "add", fname], cwd=str(repo), capture_output=True,
            )
    else:
        fname = message.replace(" ", "-")[:20] + ".txt"
        (repo / fname).write_text(message, encoding="utf-8")
        subprocess.run(
            ["git", "add", fname], cwd=str(repo), capture_output=True,
        )
    subprocess.run(
        ["git", "commit", "-m", message],
        cwd=str(repo), capture_output=True,
    )


def _tag(repo: Path, tag: str):
    subprocess.run(["git", "tag", tag], cwd=str(repo), capture_output=True)


def test_detect_migrations(tmp_path):
    repo = _init_repo(tmp_path)
    _commit(repo, "initial")
    _tag(repo, "v1.0.0")
    _commit(repo, "add migration", {
        "alembic/versions/abc123_add_users_table.py": "# migration",
    })

    result = run_script(str(repo), "--since", "v1.0.0")
    assert result["returncode"] == 0
    assert result["output"]["has_migrations"] is True
    assert len(result["output"]["migrations"]) == 1
    assert result["output"]["migrations"][0]["revision"] == "abc123"


def test_detect_backend_deps(tmp_path):
    repo = _init_repo(tmp_path)
    _commit(repo, "initial", {"requirements.txt": "flask==2.0\n"})
    _tag(repo, "v1.0.0")
    _commit(repo, "add dep", {"requirements.txt": "flask==2.0\ncelery==5.0\n"})

    result = run_script(str(repo), "--since", "v1.0.0")
    assert result["returncode"] == 0
    assert result["output"]["has_backend_deps"] is True
    assert any("celery" in d for d in result["output"]["backend_deps"]["added"])


def test_detect_frontend_deps(tmp_path):
    repo = _init_repo(tmp_path)
    _commit(repo, "initial", {"package.json": '{"dependencies": {}}\n'})
    _tag(repo, "v1.0.0")
    _commit(repo, "add react", {
        "package.json": '{"dependencies": {"react": "^18.0"}}\n',
    })

    result = run_script(str(repo), "--since", "v1.0.0")
    assert result["returncode"] == 0
    assert result["output"]["has_frontend_deps"] is True


def test_detect_config_changes(tmp_path):
    repo = _init_repo(tmp_path)
    _commit(repo, "initial", {".env.example": "DB_HOST=localhost\n"})
    _tag(repo, "v1.0.0")
    _commit(repo, "add config", {
        ".env.example": "DB_HOST=localhost\nREDIS_URL=redis://localhost\n",
    })

    result = run_script(str(repo), "--since", "v1.0.0")
    assert result["returncode"] == 0
    assert result["output"]["has_config_changes"] is True
    assert len(result["output"]["config_changes"]) >= 1


def test_no_changes(tmp_path):
    repo = _init_repo(tmp_path)
    _commit(repo, "initial")
    _tag(repo, "v1.0.0")

    result = run_script(str(repo), "--since", "v1.0.0")
    assert result["returncode"] == 1
    assert result["output"]["changed_files"] == 0


def test_not_a_git_repo(tmp_path):
    result = run_script(str(tmp_path))
    assert result["returncode"] == 2


def test_output_to_file(tmp_path):
    repo = _init_repo(tmp_path)
    _commit(repo, "initial")
    _tag(repo, "v1.0.0")
    _commit(repo, "change", {"app.py": "print('hello')"})

    out_file = tmp_path / "output" / "deploy.json"
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(repo), "--since", "v1.0.0",
         "-o", str(out_file)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    data = json.loads(out_file.read_text())
    assert data["changed_files"] > 0


def test_auto_detect_since(tmp_path):
    repo = _init_repo(tmp_path)
    _commit(repo, "initial")
    _tag(repo, "v0.5.0")
    _commit(repo, "new feature", {"feature.py": "x = 1"})

    result = run_script(str(repo))
    assert result["returncode"] == 0
    assert result["output"]["since"] == "v0.5.0"


def test_multiple_migration_files(tmp_path):
    repo = _init_repo(tmp_path)
    _commit(repo, "initial")
    _tag(repo, "v1.0.0")
    _commit(repo, "migrations", {
        "alembic/versions/aaa111_create_users.py": "# m1",
        "alembic/versions/bbb222_add_roles.py": "# m2",
    })

    result = run_script(str(repo), "--since", "v1.0.0")
    assert result["output"]["has_migrations"] is True
    assert len(result["output"]["migrations"]) == 2
