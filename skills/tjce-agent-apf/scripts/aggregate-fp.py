#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# ///
"""
Aggregate Function Point counts: compute VAF, PF Brutos, PF Ajustado, and
distribution by function type from a JSON list of classified functions.

Input JSON format (one function per item):
    [
      {"id": "FD-001", "name": "Processo", "type": "ALI", "pf": 7, "complexity": "Baixa"},
      {"id": "FT-001", "name": "Cadastrar", "type": "EE", "pf": 4, "complexity": "Media"},
      ...
    ]

Usage:
    python3 aggregate-fp.py functions.json --tdi 35
    python3 aggregate-fp.py functions.json --tdi 35 --json
    python3 aggregate-fp.py functions.json --tdi 35 --markdown

Exit codes:
    0 = aggregation successful
    1 = invalid input (malformed JSON, unknown type)
    2 = file not found
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

VALID_TYPES = {"ALI", "AIE", "EE", "SE", "CE"}


def aggregate(functions: list[dict], tdi: int) -> dict:
    """Aggregate classified functions into totals, VAF, PF ajustado, distribution."""
    if not 0 <= tdi <= 70:
        raise ValueError(f"TDI must be between 0 and 70, got {tdi}")

    by_type: dict[str, dict] = {t: {"count": 0, "pf": 0} for t in VALID_TYPES}
    total_pf = 0

    for fn in functions:
        ftype = fn.get("type", "").upper()
        if ftype not in VALID_TYPES:
            raise ValueError(
                f"Function {fn.get('id', '?')} has unknown type '{ftype}'"
            )
        pf = int(fn.get("pf", 0))
        by_type[ftype]["count"] += 1
        by_type[ftype]["pf"] += pf
        total_pf += pf

    vaf = round((tdi * 0.01) + 0.65, 2)
    pf_ajustado = round(total_pf * vaf, 2)

    distribution = []
    for ftype in ["ALI", "AIE", "EE", "SE", "CE"]:
        entry = by_type[ftype]
        pct = round((entry["pf"] / total_pf * 100) if total_pf else 0.0, 1)
        distribution.append({
            "type": ftype,
            "count": entry["count"],
            "pf": entry["pf"],
            "pct": pct,
        })

    return {
        "total_functions": len(functions),
        "pf_brutos": total_pf,
        "tdi": tdi,
        "vaf": vaf,
        "pf_ajustado": pf_ajustado,
        "distribution": distribution,
    }


def render_markdown(result: dict) -> str:
    """Render aggregation as the resumo-apf.md body."""
    lines = [
        "| Metrica | Valor |",
        "|---------|-------|",
        f"| PF Brutos | {result['pf_brutos']} |",
        f"| TDI | {result['tdi']} |",
        f"| VAF | {result['vaf']} |",
        f"| **PF Ajustado** | **{result['pf_ajustado']}** |",
        "",
        "## Distribuicao por Tipo",
        "",
        "| Tipo | Qtde | PF | % |",
        "|------|------|----|----|",
    ]
    for d in result["distribution"]:
        lines.append(
            f"| {d['type']} | {d['count']} | {d['pf']} | {d['pct']}% |"
        )
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Aggregate classified APF functions"
    )
    parser.add_argument("functions_json", help="Path to functions JSON file")
    parser.add_argument(
        "--tdi", type=int, required=True,
        help="Total Degree of Influence (0-70); use 35 for neutral VAF=1.0",
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument(
        "--markdown", action="store_true",
        help="Output as markdown (resumo-apf.md body)",
    )
    args = parser.parse_args()

    try:
        text = Path(args.functions_json).read_text(encoding="utf-8")
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(2)

    try:
        functions = json.loads(text)
    except json.JSONDecodeError as e:
        print(f"ERROR: JSON invalido: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        result = aggregate(functions, args.tdi)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    if args.markdown:
        print(render_markdown(result))
    elif args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(
            f"PF Brutos: {result['pf_brutos']} | "
            f"VAF: {result['vaf']} | "
            f"PF Ajustado: {result['pf_ajustado']}"
        )
        for d in result["distribution"]:
            print(f"  {d['type']}: {d['count']} funcoes, {d['pf']} PF ({d['pct']}%)")

    sys.exit(0)


if __name__ == "__main__":
    main()
