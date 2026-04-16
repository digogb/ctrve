#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Layer 3 (partial): Detect placeholders, empty sections, and structural quality issues."""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

PLACEHOLDER_PATTERNS = [
    re.compile(r"(?i)\bTODO\b"),
    re.compile(r"(?i)\[PREENCHER\]"),
    re.compile(r"(?i)\bTBD\b"),
    re.compile(r"(?i)\ba definir\b"),
    re.compile(r"(?i)\bpendente\b"),
    re.compile(r"(?i)\bplaceholder\b"),
]

USER_STORY_PATTERN = re.compile(
    r"[Cc]omo\s+.+?,\s*quero\s+.+?,\s*para\s+que\s+",
)

RN_TABLE_HEADERS = ["id", "descri", "condi", "a", "exce"]

SCAN_FILES = [
    "requirements/user-stories.md",
    "requirements/business-rules.md",
    "requirements/messages.md",
    "requirements/product-vision.md",
    "tests/test-cases.md",
]

MESSAGE_TYPES = ["erro", "sucesso", "valida", "confirma"]


def check_placeholders(output_folder: Path) -> dict:
    findings = []

    for rel_path in SCAN_FILES:
        path = output_folder / rel_path
        if not path.exists():
            continue

        content = path.read_text(encoding="utf-8", errors="ignore")
        lines = content.split("\n")

        for i, line in enumerate(lines, 1):
            for pattern in PLACEHOLDER_PATTERNS:
                if pattern.search(line):
                    findings.append({
                        "severity": "critical",
                        "category": "placeholder",
                        "location": {"file": str(path), "line": i},
                        "issue": f"Placeholder encontrado: '{pattern.search(line).group()}'",
                        "fix": "Substitua o placeholder por conteudo real",
                    })
                    break

        _check_empty_sections(path, content, findings)

    _check_user_story_format(output_folder, findings)
    _check_rn_columns(output_folder, findings)
    _check_message_types(output_folder, findings)

    critical = sum(1 for f in findings if f["severity"] == "critical")
    high = sum(1 for f in findings if f["severity"] == "high")
    medium = sum(1 for f in findings if f["severity"] == "medium")
    return {
        "script": "check-placeholders",
        "version": "1.0.0",
        "output_folder": str(output_folder),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "fail" if critical > 0 else ("warning" if high > 0 else "pass"),
        "findings": findings,
        "summary": {
            "total": len(findings),
            "critical": critical,
            "high": high,
            "medium": medium,
            "low": 0,
        },
    }


def _check_empty_sections(path: Path, content: str, findings: list):
    lines = content.split("\n")
    sections = []
    for i, line in enumerate(lines):
        if re.match(r"^#{2,3}\s+\S", line):
            sections.append({"title": line.strip("# ").strip(), "line": i + 1, "start": i})

    for idx, section in enumerate(sections):
        end = sections[idx + 1]["start"] if idx + 1 < len(sections) else len(lines)
        body = "\n".join(lines[section["start"] + 1:end]).strip()
        if not body:
            findings.append({
                "severity": "high",
                "category": "empty-section",
                "location": {"file": str(path), "line": section["line"]},
                "issue": f"Secao vazia: '{section['title']}'",
                "fix": "Preencha a secao com conteudo relevante",
            })


def _check_user_story_format(output_folder: Path, findings: list):
    path = output_folder / "requirements" / "user-stories.md"
    if not path.exists():
        return

    content = path.read_text(encoding="utf-8", errors="ignore")
    us_ids = re.findall(r"\bUS[-_](\d{3})\b", content)

    if us_ids and not USER_STORY_PATTERN.search(content):
        findings.append({
            "severity": "medium",
            "category": "format",
            "location": {"file": str(path)},
            "issue": "User stories nao seguem formato 'Como [perfil], quero [acao], para que [valor]'",
            "fix": "Reformule as estorias no formato padrao",
        })


def _check_rn_columns(output_folder: Path, findings: list):
    path = output_folder / "requirements" / "business-rules.md"
    if not path.exists():
        return

    content = path.read_text(encoding="utf-8", errors="ignore").lower()
    table_lines = [l for l in content.split("\n") if "|" in l]

    if table_lines:
        header = table_lines[0]
        missing_cols = [col for col in RN_TABLE_HEADERS if col not in header]
        if missing_cols:
            findings.append({
                "severity": "medium",
                "category": "format",
                "location": {"file": str(path)},
                "issue": f"Tabela de RN com colunas faltando: {', '.join(missing_cols)}",
                "fix": "Adicione as colunas: ID, Descricao, Condicao, Acao, Excecao",
            })


def _check_message_types(output_folder: Path, findings: list):
    path = output_folder / "requirements" / "messages.md"
    if not path.exists():
        return

    content = path.read_text(encoding="utf-8", errors="ignore").lower()
    missing_types = [t for t in MESSAGE_TYPES if t not in content]

    if missing_types:
        findings.append({
            "severity": "medium",
            "category": "coverage",
            "location": {"file": str(path)},
            "issue": f"Tipos de mensagem nao cobertos: {', '.join(missing_types)}",
            "fix": "Adicione mensagens para os 4 tipos: erro, sucesso, validacao, confirmacao",
        })


def main():
    parser = argparse.ArgumentParser(
        description="Detect placeholders and structural quality issues in SPEC artifacts.",
    )
    parser.add_argument(
        "output_folder",
        type=Path,
        help="Path to the output folder (e.g., _bmad-output)",
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Write JSON output to file instead of stdout",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print diagnostic messages to stderr",
    )
    args = parser.parse_args()

    if args.verbose:
        print(f"Checking placeholders in: {args.output_folder}", file=sys.stderr)

    result = check_placeholders(args.output_folder)

    output = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output:
        args.output.write_text(output, encoding="utf-8")
        if args.verbose:
            print(f"Output written to: {args.output}", file=sys.stderr)
    else:
        print(output)

    sys.exit(0 if result["status"] == "pass" else 1)


if __name__ == "__main__":
    main()
