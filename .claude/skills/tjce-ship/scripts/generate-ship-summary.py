#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Generate the final ship summary aggregating all release artifacts."""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ALWAYS_ARTIFACTS = [
    "CHANGELOG.md",
    "deploy-checklist.md",
    "rollback-plan.md",
    "PML.md",
]

APF_ARTIFACTS = [
    "apf/contagem-detalhada.md",
    "apf/resumo-apf.md",
]

MANUAL_ARTIFACTS = [
    "manual/manual-usuario.md",
]


def generate_summary(output_folder: Path, task_type: str, manual_required: bool, rdm: str | None) -> dict:
    release_dir = output_folder / "release"
    artifacts = []
    missing = []

    all_expected = list(ALWAYS_ARTIFACTS)
    if task_type != "correcao_garantia":
        all_expected.extend(APF_ARTIFACTS)
    else:
        all_expected.append("apf/resumo-apf.md")
    if manual_required:
        all_expected.extend(MANUAL_ARTIFACTS)

    for artifact in all_expected:
        path = release_dir / artifact
        if path.exists():
            artifacts.append({
                "artifact": artifact,
                "present": True,
                "size": path.stat().st_size,
            })
        else:
            artifacts.append({
                "artifact": artifact,
                "present": False,
                "size": 0,
            })
            missing.append(artifact)

    all_present = len(missing) == 0
    verdict = "FECHADO" if all_present else "INCOMPLETO"

    ship_state = _read_ship_state(release_dir)

    return {
        "script": "generate-ship-summary",
        "version": "1.0.0",
        "output_folder": str(output_folder),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "verdict": verdict,
        "task_type": task_type,
        "manual_required": manual_required,
        "rdm": rdm,
        "artifacts": artifacts,
        "missing": missing,
        "ship_state": ship_state,
    }


def _read_ship_state(release_dir: Path) -> dict | None:
    state_path = release_dir / "ship-state.json"
    if state_path.exists():
        try:
            return json.loads(state_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return None


def format_markdown(result: dict) -> str:
    lines = ["# Ship Summary — Relatorio Final de Entrega", ""]
    lines.append(f"**Verdict:** {result['verdict']}  ")
    lines.append(f"**Tipo:** {result['task_type']}  ")
    lines.append(f"**Manual requerido:** {'Sim' if result['manual_required'] else 'Nao'}  ")
    if result["rdm"]:
        lines.append(f"**RDM:** {result['rdm']}  ")
    lines.append(f"**Data:** {result['timestamp']}")
    lines.append("")

    lines.append("## Artefatos de Entrega")
    lines.append("")
    lines.append("| Artefato | Status | Tamanho |")
    lines.append("| -------- | ------ | ------- |")
    for a in result["artifacts"]:
        status = "Presente" if a["present"] else "**AUSENTE**"
        size = f"{a['size']} bytes" if a["present"] else "-"
        lines.append(f"| `{a['artifact']}` | {status} | {size} |")
    lines.append("")

    if result["missing"]:
        lines.append("## Artefatos Ausentes")
        lines.append("")
        for m in result["missing"]:
            lines.append(f"- `{m}`")
        lines.append("")

    if result["ship_state"]:
        lines.append("## Estado do Pipeline")
        lines.append("")
        state = result["ship_state"]
        if "stage" in state:
            lines.append(f"- **Stage:** {state['stage']}")
        if "status" in state:
            lines.append(f"- **Status:** {state['status']}")
        if "timestamp" in state:
            lines.append(f"- **Ultimo update:** {state['timestamp']}")
        lines.append("")

    lines.append("---")
    lines.append(f"*Gerado em {result['timestamp']}*")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(
        description="Generate the final ship summary.",
    )
    parser.add_argument(
        "output_folder",
        type=Path,
        help="Path to the output folder (e.g., _bmad-output)",
    )
    parser.add_argument(
        "--task-type",
        choices=("nova_funcionalidade", "mudanca", "correcao_garantia"),
        required=True,
        help="Task type",
    )
    parser.add_argument(
        "--manual-required",
        action="store_true",
        help="Whether user manual was required",
    )
    parser.add_argument(
        "--rdm",
        type=str,
        help="RDM (Requisicao de Mudanca) number",
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Write output to file instead of stdout",
    )
    parser.add_argument(
        "--format",
        choices=("json", "markdown"),
        default="json",
        help="Output format (default: json)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print diagnostic messages to stderr",
    )
    args = parser.parse_args()

    if args.verbose:
        print(f"Generating ship summary for: {args.output_folder}", file=sys.stderr)

    result = generate_summary(args.output_folder, args.task_type, args.manual_required, args.rdm)

    if args.format == "markdown":
        output_text = format_markdown(result)
    else:
        output_text = json.dumps(result, indent=2, ensure_ascii=False)

    if args.output:
        args.output.write_text(output_text, encoding="utf-8")
        if args.verbose:
            print(f"Output written to: {args.output}", file=sys.stderr)
    else:
        print(output_text)

    exit_code = 0 if result["verdict"] == "FECHADO" else 1
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
