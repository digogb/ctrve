#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# ///
"""
Validate release artifacts for completeness and correctness.

Checks:
- No empty sections in any release artifact
- No placeholder text (TODO, TBD, PENDENTE without context)
- Rollback plan present and non-empty
- US references in PML/CHANGELOG match user-stories.md (if provided)

Usage:
    python3 validate-release-artifacts.py /path/to/release/
    python3 validate-release-artifacts.py /path/to/release/ --stories user-stories.md
    python3 validate-release-artifacts.py /path/to/release/ -o validation.json

Exit codes:
    0 = all checks pass
    1 = validation warnings (artifacts exist but have issues)
    2 = critical failure (missing required artifacts)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

_PLACEHOLDER_PATTERNS = [
    re.compile(r"\bTODO\b", re.IGNORECASE),
    re.compile(r"\bTBD\b", re.IGNORECASE),
    re.compile(r"\bFIXME\b", re.IGNORECASE),
    re.compile(r"\bXXX\b"),
    re.compile(r"\[preencher\]", re.IGNORECASE),
    re.compile(r"\[inserir\]", re.IGNORECASE),
    re.compile(
        r"(?i)\bpendente\b(?!\s+(?:de|d[oa]s?|em|por|para|a[os]?"
        r"|nas?|nos?|com|sobre|entre|sem|at[eé]))"
    ),
]

_US_PATTERN = re.compile(r"US-\d{3,}")

_EXPECTED_ARTIFACTS = {
    "PML.md": True,
    "CHANGELOG.md": True,
    "deploy-checklist.md": True,
    "rollback-plan.md": True,
}


def _heading_level(line: str) -> int:
    stripped = line.lstrip()
    count = 0
    for ch in stripped:
        if ch == "#":
            count += 1
        else:
            break
    return count


def check_empty_sections(text: str, filename: str) -> list[dict]:
    findings: list[dict] = []
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.strip().startswith("##"):
            heading = line.strip()
            level = _heading_level(line)
            body_lines: list[str] = []
            j = i + 1
            while j < len(lines):
                next_line = lines[j].strip()
                if next_line.startswith("#"):
                    next_level = _heading_level(lines[j])
                    if next_level <= level:
                        break
                body_lines.append(lines[j])
                j += 1
            body = "\n".join(body_lines).strip()
            if not body:
                findings.append({
                    "severity": "high",
                    "category": "empty-section",
                    "file": filename,
                    "line": i + 1,
                    "issue": f"Secao vazia: {heading}",
                    "fix": "Preencher secao com conteudo relevante",
                })
            i = j
        else:
            i += 1
    return findings


def check_placeholders(text: str, filename: str) -> list[dict]:
    findings: list[dict] = []
    for i, line in enumerate(text.splitlines(), start=1):
        for pattern in _PLACEHOLDER_PATTERNS:
            if pattern.search(line):
                findings.append({
                    "severity": "high",
                    "category": "placeholder",
                    "file": filename,
                    "line": i,
                    "issue": f"Texto placeholder detectado: {line.strip()[:80]}",
                    "fix": "Substituir placeholder por conteudo real",
                })
                break
    return findings


def check_rollback_present(release_dir: Path) -> list[dict]:
    rollback = release_dir / "rollback-plan.md"
    if not rollback.is_file():
        return [{
            "severity": "critical",
            "category": "missing-artifact",
            "file": "rollback-plan.md",
            "line": 0,
            "issue": "Rollback plan ausente — artefato obrigatorio",
            "fix": "Gerar rollback-plan.md com procedimento de reversao",
        }]
    text = rollback.read_text(encoding="utf-8", errors="replace").strip()
    if len(text) < 50:
        return [{
            "severity": "critical",
            "category": "incomplete-artifact",
            "file": "rollback-plan.md",
            "line": 0,
            "issue": "Rollback plan com conteudo insuficiente",
            "fix": "Expandir rollback plan com procedimento completo",
        }]
    return []


def check_us_references(
    release_dir: Path, stories_path: Path | None
) -> list[dict]:
    if not stories_path or not stories_path.is_file():
        return []

    stories_text = stories_path.read_text(encoding="utf-8", errors="replace")
    valid_us = set(_US_PATTERN.findall(stories_text))
    if not valid_us:
        return []

    findings: list[dict] = []
    for artifact in ["PML.md", "CHANGELOG.md"]:
        path = release_dir / artifact
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        referenced = set(_US_PATTERN.findall(text))
        invalid = referenced - valid_us
        for us_id in sorted(invalid):
            findings.append({
                "severity": "medium",
                "category": "invalid-reference",
                "file": artifact,
                "line": 0,
                "issue": f"{us_id} referenciado mas nao encontrado em user-stories.md",
                "fix": f"Verificar se {us_id} e valido ou corrigir referencia",
            })
    return findings


def validate(release_dir: Path, stories_path: Path | None) -> dict:
    findings: list[dict] = []
    missing: list[str] = []
    checked: list[str] = []

    for artifact, required in _EXPECTED_ARTIFACTS.items():
        path = release_dir / artifact
        if not path.is_file():
            if required:
                missing.append(artifact)
                findings.append({
                    "severity": "critical",
                    "category": "missing-artifact",
                    "file": artifact,
                    "line": 0,
                    "issue": f"Artefato obrigatorio ausente: {artifact}",
                    "fix": f"Gerar {artifact}",
                })
            continue

        checked.append(artifact)
        text = path.read_text(encoding="utf-8", errors="replace")
        findings.extend(check_empty_sections(text, artifact))
        findings.extend(check_placeholders(text, artifact))

    findings.extend(check_rollback_present(release_dir))
    findings.extend(check_us_references(release_dir, stories_path))

    has_critical = any(f["severity"] == "critical" for f in findings)
    has_warnings = any(f["severity"] in ("high", "medium") for f in findings)

    return {
        "release_dir": str(release_dir),
        "artifacts_checked": checked,
        "artifacts_missing": missing,
        "findings": findings,
        "findings_count": len(findings),
        "critical_count": sum(1 for f in findings if f["severity"] == "critical"),
        "warning_count": sum(
            1 for f in findings if f["severity"] in ("high", "medium")
        ),
        "valid": not has_critical and not has_warnings,
        "exit_code": 2 if has_critical else (1 if has_warnings else 0),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Validate release artifacts for completeness"
    )
    parser.add_argument(
        "release_dir", help="Path to release/ directory with artifacts"
    )
    parser.add_argument(
        "--stories", help="Path to user-stories.md for reference validation"
    )
    parser.add_argument("-o", "--output", help="Output JSON path (default: stdout)")
    args = parser.parse_args()

    release_dir = Path(args.release_dir)
    if not release_dir.is_dir():
        print(json.dumps({
            "error": f"{args.release_dir} is not a directory",
            "valid": False,
        }))
        sys.exit(2)

    stories_path = Path(args.stories) if args.stories else None
    result = validate(release_dir, stories_path)

    output = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(output, encoding="utf-8")
        print(json.dumps({
            "written": args.output,
            "valid": result["valid"],
            "findings_count": result["findings_count"],
        }))
    else:
        print(output)

    sys.exit(result["exit_code"])


if __name__ == "__main__":
    main()
