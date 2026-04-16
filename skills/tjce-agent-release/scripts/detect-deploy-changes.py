#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# ///
"""
Detect deployment-relevant changes from Git diff.

Analyzes files changed between a ref and HEAD to identify:
- Alembic/migration files
- Backend dependency changes (requirements.txt, pyproject.toml)
- Frontend dependency changes (package.json)
- Config/environment changes (.env.example, config files)

Usage:
    python3 detect-deploy-changes.py /path/to/repo
    python3 detect-deploy-changes.py /path/to/repo --since v1.0.0
    python3 detect-deploy-changes.py /path/to/repo -o deploy-changes.json

Exit codes:
    0 = analysis successful
    1 = no changes detected
    2 = not a git repo or path error
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

_MIGRATION_PATTERNS = [
    re.compile(r"alembic/versions/"),
    re.compile(r"migrations/versions/"),
    re.compile(r"migrations/\d+"),
]

_BACKEND_DEP_FILES = {
    "requirements.txt", "requirements-dev.txt", "requirements-prod.txt",
    "pyproject.toml", "setup.py", "setup.cfg", "Pipfile", "Pipfile.lock",
    "poetry.lock",
}

_FRONTEND_DEP_FILES = {
    "package.json", "package-lock.json", "yarn.lock", "pnpm-lock.yaml",
}

_CONFIG_PATTERNS = [
    re.compile(r"\.env\.example"),
    re.compile(r"\.env\.sample"),
    re.compile(r"\.env\.template"),
    re.compile(r"config/"),
    re.compile(r"settings/"),
    re.compile(r"\.config\."),
]


def get_last_tag(repo: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"],
            capture_output=True, text=True, cwd=str(repo),
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except OSError:
        pass
    return None


def get_first_commit(repo: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-list", "--max-parents=0", "HEAD"],
            capture_output=True, text=True, cwd=str(repo),
        )
        if result.returncode == 0:
            lines = result.stdout.strip().splitlines()
            return lines[0] if lines else None
    except OSError:
        pass
    return None


def get_changed_files(repo: Path, since: str) -> list[str]:
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", f"{since}..HEAD"],
            capture_output=True, text=True, cwd=str(repo),
        )
        if result.returncode == 0:
            return [f for f in result.stdout.strip().splitlines() if f]
    except OSError:
        pass
    return []


def get_file_diff(repo: Path, since: str, filepath: str) -> str:
    try:
        result = subprocess.run(
            ["git", "diff", f"{since}..HEAD", "--", filepath],
            capture_output=True, text=True, cwd=str(repo),
        )
        if result.returncode == 0:
            return result.stdout
    except OSError:
        pass
    return ""


def parse_dep_diff(diff_text: str) -> dict:
    added: list[str] = []
    removed: list[str] = []
    for line in diff_text.splitlines():
        if line.startswith("+") and not line.startswith("+++"):
            dep = line[1:].strip()
            if dep and not dep.startswith("#"):
                added.append(dep)
        elif line.startswith("-") and not line.startswith("---"):
            dep = line[1:].strip()
            if dep and not dep.startswith("#"):
                removed.append(dep)
    return {"added": added, "removed": removed, "changed": []}


def detect_migrations(files: list[str]) -> list[dict]:
    migrations: list[dict] = []
    for f in files:
        for pattern in _MIGRATION_PATTERNS:
            if pattern.search(f):
                name = Path(f).stem
                rev_match = re.match(r"([a-f0-9]+)_(.+)", name)
                migrations.append({
                    "file": f,
                    "revision": rev_match.group(1) if rev_match else name,
                    "message": (
                        rev_match.group(2).replace("_", " ")
                        if rev_match else name
                    ),
                })
                break
    return migrations


def detect_config_changes(
    files: list[str], repo: Path, since: str
) -> list[dict]:
    config_files: list[str] = []
    for f in files:
        for pattern in _CONFIG_PATTERNS:
            if pattern.search(f):
                config_files.append(f)
                break

    changes: list[dict] = []
    for cf in config_files:
        diff = get_file_diff(repo, since, cf)
        added_keys: list[str] = []
        removed_keys: list[str] = []
        for line in diff.splitlines():
            if line.startswith("+") and "=" in line and not line.startswith("+++"):
                key = line.lstrip("+").split("=", 1)[0].strip()
                if key:
                    added_keys.append(key)
            elif line.startswith("-") and "=" in line and not line.startswith("---"):
                key = line.lstrip("-").split("=", 1)[0].strip()
                if key:
                    removed_keys.append(key)
        changes.append({
            "file": cf,
            "added_keys": added_keys,
            "removed_keys": removed_keys,
        })
    return changes


def analyze(repo: Path, since: str) -> dict:
    files = get_changed_files(repo, since)
    if not files:
        return {
            "since": since,
            "changed_files": 0,
            "migrations": [],
            "backend_deps": {"added": [], "removed": [], "changed": []},
            "frontend_deps": {"added": [], "removed": [], "changed": []},
            "config_changes": [],
            "has_migrations": False,
            "has_backend_deps": False,
            "has_frontend_deps": False,
            "has_config_changes": False,
        }

    migrations = detect_migrations(files)

    backend_deps: dict = {"added": [], "removed": [], "changed": []}
    for f in files:
        if Path(f).name in _BACKEND_DEP_FILES:
            diff = get_file_diff(repo, since, f)
            parsed = parse_dep_diff(diff)
            backend_deps["added"].extend(parsed["added"])
            backend_deps["removed"].extend(parsed["removed"])

    frontend_deps: dict = {"added": [], "removed": [], "changed": []}
    for f in files:
        if Path(f).name in _FRONTEND_DEP_FILES:
            diff = get_file_diff(repo, since, f)
            parsed = parse_dep_diff(diff)
            frontend_deps["added"].extend(parsed["added"])
            frontend_deps["removed"].extend(parsed["removed"])

    config_changes = detect_config_changes(files, repo, since)

    return {
        "since": since,
        "changed_files": len(files),
        "migrations": migrations,
        "backend_deps": backend_deps,
        "frontend_deps": frontend_deps,
        "config_changes": config_changes,
        "has_migrations": len(migrations) > 0,
        "has_backend_deps": (
            len(backend_deps["added"]) > 0
            or len(backend_deps["removed"]) > 0
        ),
        "has_frontend_deps": (
            len(frontend_deps["added"]) > 0
            or len(frontend_deps["removed"]) > 0
        ),
        "has_config_changes": len(config_changes) > 0,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Detect deployment-relevant changes from Git diff"
    )
    parser.add_argument("repo", help="Path to Git repository root")
    parser.add_argument(
        "--since",
        help="Git ref to start from (tag or SHA). Default: last tag or first commit",
    )
    parser.add_argument("-o", "--output", help="Output JSON path (default: stdout)")
    args = parser.parse_args()

    repo = Path(args.repo)
    git_check = subprocess.run(
        ["git", "rev-parse", "--git-dir"],
        capture_output=True, text=True, cwd=str(repo),
    )
    if git_check.returncode != 0:
        print(json.dumps({"error": f"{args.repo} is not a git repository"}))
        sys.exit(2)

    since = args.since
    if not since:
        since = get_last_tag(repo)
    if not since:
        since = get_first_commit(repo)
    if not since:
        since = "4b825dc642cb6eb9a060e54bf899d15363d7d95f"

    result = analyze(repo, since)

    if result["changed_files"] == 0:
        output = json.dumps(result, ensure_ascii=False, indent=2)
        if args.output:
            Path(args.output).parent.mkdir(parents=True, exist_ok=True)
            Path(args.output).write_text(output, encoding="utf-8")
            print(json.dumps({"written": args.output, "changed_files": 0}))
        else:
            print(output)
        sys.exit(1)

    output = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(output, encoding="utf-8")
        print(json.dumps({
            "written": args.output,
            "changed_files": result["changed_files"],
            "has_migrations": result["has_migrations"],
            "has_backend_deps": result["has_backend_deps"],
            "has_frontend_deps": result["has_frontend_deps"],
            "has_config_changes": result["has_config_changes"],
        }))
    else:
        print(output)


if __name__ == "__main__":
    main()
