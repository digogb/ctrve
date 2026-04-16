#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# ///
"""
Calculate Function Points via deterministic IFPUG CPM 4.3.1 matrices.

Given a function type (ALI, AIE, EE, SE, CE) and its sizing attributes
(DER + RLR for data functions; DER + ALR for transactional functions),
returns the complexity classification and PF count according to the
IFPUG CPM 4.3.1 complexity tables.

Usage:
    python3 calculate-fp.py --type ALI --der 15 --rlr 2
    python3 calculate-fp.py --type EE --der 8 --alr 2
    python3 calculate-fp.py --type SE --der 20 --alr 4 --json

Exit codes:
    0 = calculation successful
    1 = invalid input
    2 = unknown error
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# IFPUG CPM 4.3.1 complexity matrices

# Data Functions (ALI/AIE): DER bands x RLR bands
# DER bands: 1-19, 20-50, >50
# RLR bands: 1, 2-5, >5
_DATA_MATRIX = {
    # (rlr_band, der_band): complexity
    (0, 0): "Baixa", (0, 1): "Baixa", (0, 2): "Media",
    (1, 0): "Baixa", (1, 1): "Media", (1, 2): "Alta",
    (2, 0): "Media", (2, 1): "Alta",  (2, 2): "Alta",
}

# Transactional EE: DER bands x ALR bands
# DER bands: 1-4, 5-15, >15
# ALR bands: 0-1, 2, >2
_EE_MATRIX = {
    (0, 0): "Baixa", (0, 1): "Baixa", (0, 2): "Media",
    (1, 0): "Baixa", (1, 1): "Media", (1, 2): "Alta",
    (2, 0): "Media", (2, 1): "Alta",  (2, 2): "Alta",
}

# Transactional SE/CE: DER bands x ALR bands
# DER bands: 1-5, 6-19, >19
# ALR bands: 0-1, 2-3, >3
_SE_CE_MATRIX = {
    (0, 0): "Baixa", (0, 1): "Baixa", (0, 2): "Media",
    (1, 0): "Baixa", (1, 1): "Media", (1, 2): "Alta",
    (2, 0): "Media", (2, 1): "Alta",  (2, 2): "Alta",
}

# PF weights per (type, complexity)
_PF_WEIGHTS = {
    "ALI": {"Baixa": 7, "Media": 10, "Alta": 15},
    "AIE": {"Baixa": 5, "Media": 7, "Alta": 10},
    "EE":  {"Baixa": 3, "Media": 4, "Alta": 6},
    "SE":  {"Baixa": 4, "Media": 5, "Alta": 7},
    "CE":  {"Baixa": 3, "Media": 4, "Alta": 6},
}


def _data_rlr_band(rlr: int) -> int:
    if rlr <= 1:
        return 0
    if rlr <= 5:
        return 1
    return 2


def _data_der_band(der: int) -> int:
    if der <= 19:
        return 0
    if der <= 50:
        return 1
    return 2


def _ee_der_band(der: int) -> int:
    if der <= 4:
        return 0
    if der <= 15:
        return 1
    return 2


def _ee_alr_band(alr: int) -> int:
    if alr <= 1:
        return 0
    if alr == 2:
        return 1
    return 2


def _se_ce_der_band(der: int) -> int:
    if der <= 5:
        return 0
    if der <= 19:
        return 1
    return 2


def _se_ce_alr_band(alr: int) -> int:
    if alr <= 1:
        return 0
    if alr <= 3:
        return 1
    return 2


def classify(
    func_type: str,
    der: int,
    rlr: int | None = None,
    alr: int | None = None,
) -> dict:
    """Classify a function and return {complexity, pf, type, der, rlr/alr}."""
    func_type = func_type.upper()

    if func_type in ("ALI", "AIE"):
        if rlr is None:
            raise ValueError(f"{func_type} requires --rlr")
        if der < 1 or rlr < 1:
            raise ValueError(f"DER and RLR must be >= 1 for {func_type}")
        key = (_data_rlr_band(rlr), _data_der_band(der))
        complexity = _DATA_MATRIX[key]
    elif func_type == "EE":
        if alr is None:
            raise ValueError("EE requires --alr")
        if der < 1 or alr < 0:
            raise ValueError("DER must be >= 1 and ALR must be >= 0 for EE")
        key = (_ee_alr_band(alr), _ee_der_band(der))
        complexity = _EE_MATRIX[key]
    elif func_type in ("SE", "CE"):
        if alr is None:
            raise ValueError(f"{func_type} requires --alr")
        if der < 1 or alr < 0:
            raise ValueError(f"DER must be >= 1 and ALR must be >= 0 for {func_type}")
        key = (_se_ce_alr_band(alr), _se_ce_der_band(der))
        complexity = _SE_CE_MATRIX[key]
    else:
        raise ValueError(
            f"Unknown type '{func_type}'. Expected: ALI, AIE, EE, SE, CE."
        )

    pf = _PF_WEIGHTS[func_type][complexity]
    result = {
        "type": func_type,
        "der": der,
        "complexity": complexity,
        "pf": pf,
    }
    if rlr is not None:
        result["rlr"] = rlr
    if alr is not None:
        result["alr"] = alr
    return result


def classify_batch(functions: list[dict]) -> list[dict]:
    """Classify multiple functions at once. Each input item needs type + der + rlr/alr.

    Preserves caller-provided id/name/source fields in the output.
    """
    results = []
    for fn in functions:
        ftype = fn.get("type", "")
        der = fn.get("der")
        rlr = fn.get("rlr")
        alr = fn.get("alr")
        if der is None:
            raise ValueError(f"Missing DER for function {fn.get('id', '?')}")
        classified = classify(ftype, int(der), rlr, alr)
        # Preserve caller metadata (id, name, source, etc.) alongside classification
        merged = {**fn, **classified}
        results.append(merged)
    return results


def main():
    parser = argparse.ArgumentParser(
        description="Calculate IFPUG CPM 4.3.1 Function Points"
    )
    parser.add_argument("--type", choices=["ALI", "AIE", "EE", "SE", "CE"],
                        help="Function type (single-function mode)")
    parser.add_argument("--der", type=int, help="Data Element Types (single-function mode)")
    parser.add_argument("--rlr", type=int, help="Record Element Types (for ALI/AIE)")
    parser.add_argument("--alr", type=int, help="Referenced File Types (for EE/SE/CE)")
    parser.add_argument(
        "--batch", metavar="JSON_PATH",
        help="Batch mode: JSON file with list of functions to classify in one call",
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    # Batch mode
    if args.batch:
        try:
            text = Path(args.batch).read_text(encoding="utf-8")
            functions = json.loads(text)
            results = classify_batch(functions)
        except FileNotFoundError as e:
            print(f"ERROR: {e}", file=sys.stderr)
            sys.exit(2)
        except (ValueError, json.JSONDecodeError) as e:
            if args.json:
                print(json.dumps({"error": str(e)}))
            else:
                print(f"ERROR: {e}", file=sys.stderr)
            sys.exit(1)

        if args.json:
            print(json.dumps(results, ensure_ascii=False, indent=2))
        else:
            for r in results:
                ident = r.get("id") or r.get("name") or "?"
                sizing = f"DER={r['der']}"
                if "rlr" in r and r["rlr"] is not None:
                    sizing += f", RLR={r['rlr']}"
                if "alr" in r and r["alr"] is not None:
                    sizing += f", ALR={r['alr']}"
                print(
                    f"{ident} [{r['type']}] ({sizing}) -> "
                    f"{r['complexity']} -> {r['pf']} PF"
                )
        sys.exit(0)

    # Single-function mode
    if not args.type or args.der is None:
        print(
            "ERROR: provide --type and --der (single mode) or --batch JSON_PATH",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        result = classify(args.type, args.der, args.rlr, args.alr)
    except ValueError as e:
        if args.json:
            print(json.dumps({"error": str(e)}))
        else:
            print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(result, ensure_ascii=False))
    else:
        sizing = f"DER={result['der']}"
        if "rlr" in result:
            sizing += f", RLR={result['rlr']}"
        if "alr" in result:
            sizing += f", ALR={result['alr']}"
        print(
            f"{result['type']} ({sizing}) -> {result['complexity']} -> {result['pf']} PF"
        )

    sys.exit(0)


if __name__ == "__main__":
    main()
