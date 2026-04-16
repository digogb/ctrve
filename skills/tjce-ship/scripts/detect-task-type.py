#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Detect task type and manual flag from CLI args, config, or requirements."""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

VALID_TYPES = ("nova_funcionalidade", "mudanca", "correcao_garantia")


def detect_task_type(output_folder: Path, explicit_type: str | None, explicit_manual: bool) -> dict:
    findings = []
    task_type = explicit_type
    manual_necessario = explicit_manual
    source = None

    if task_type:
        source = "cli"
    else:
        task_type, source = _infer_from_config(output_folder)

    if task_type and task_type not in VALID_TYPES:
        findings.append({
            "severity": "critical",
            "category": "configuration",
            "location": {"file": source or "cli"},
            "issue": f"Tipo de tarefa invalido: '{task_type}'. Valores aceitos: {', '.join(VALID_TYPES)}",
            "fix": "Use --type com um dos valores aceitos",
        })
        return _build_result(output_folder, "fail", findings, task_type=None, manual=manual_necessario, source=source)

    if task_type is None:
        findings.append({
            "severity": "high",
            "category": "configuration",
            "location": {"file": str(output_folder)},
            "issue": "Tipo de tarefa nao detectado automaticamente",
            "fix": "Use --type nova_funcionalidade|mudanca|correcao_garantia",
        })
        return _build_result(output_folder, "fail", findings, task_type=None, manual=manual_necessario, source=source)

    return _build_result(output_folder, "pass", findings, task_type=task_type, manual=manual_necessario, source=source)


def _infer_from_config(output_folder: Path) -> tuple[str | None, str | None]:
    config_path = output_folder / "config.json"
    if config_path.exists():
        try:
            data = json.loads(config_path.read_text(encoding="utf-8"))
            t = data.get("task_type")
            if t:
                return t, str(config_path)
        except (json.JSONDecodeError, OSError):
            pass

    for yaml_name in ("config.yaml", "config.user.yaml"):
        yaml_path = output_folder.parent / "_bmad" / yaml_name
        if yaml_path.exists():
            try:
                content = yaml_path.read_text(encoding="utf-8")
                match = re.search(r"task_type\s*:\s*(\S+)", content)
                if match:
                    return match.group(1), str(yaml_path)
            except OSError:
                pass

    req_path = output_folder / "requirements" / "requirements.md"
    if req_path.exists():
        try:
            content = req_path.read_text(encoding="utf-8", errors="ignore").lower()
            if "correcao" in content and "garantia" in content:
                return "correcao_garantia", str(req_path)
            if "nova funcionalidade" in content or "new feature" in content:
                return "nova_funcionalidade", str(req_path)
        except OSError:
            pass

    return None, None


def _build_result(output_folder, status, findings, task_type, manual, source):
    critical = sum(1 for f in findings if f["severity"] == "critical")
    high = sum(1 for f in findings if f["severity"] == "high")
    return {
        "script": "detect-task-type",
        "version": "1.0.0",
        "output_folder": str(output_folder),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "task_type": task_type,
        "manual_necessario": manual,
        "detection_source": source,
        "findings": findings,
        "summary": {
            "total": len(findings),
            "critical": critical,
            "high": high,
            "medium": 0,
            "low": 0,
        },
    }


def main():
    parser = argparse.ArgumentParser(
        description="Detect task type and manual flag for the SHIP pipeline.",
    )
    parser.add_argument(
        "output_folder",
        type=Path,
        help="Path to the output folder (e.g., _bmad-output)",
    )
    parser.add_argument(
        "--type",
        choices=VALID_TYPES,
        help="Explicit task type",
    )
    parser.add_argument(
        "--manual",
        action="store_true",
        help="Flag that user manual is required",
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
        print(f"Detecting task type in: {args.output_folder}", file=sys.stderr)

    result = detect_task_type(args.output_folder, args.type, args.manual)

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
