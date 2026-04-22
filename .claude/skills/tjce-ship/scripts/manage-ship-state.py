#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Manage ship-state.json with atomic writes and schema enforcement."""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

VALID_STAGES = list(range(1, 10))
VALID_STATUSES = [
    "running", "completed",
    "awaiting_pml_validation", "awaiting_deployment",
    "closed", "blocked",
]
VALID_TASK_TYPES = ["nova_funcionalidade", "mudanca", "correcao_garantia"]
VALID_GATES = ["pml_validation", "deployment"]


def cmd_init(state_path: Path, task_type: str, manual: bool) -> dict:
    if state_path.exists():
        return {"action": "init", "status": "error", "message": "ship-state.json already exists. Use 'update' or delete first."}

    state = {
        "schema_version": "1.0.0",
        "task_type": task_type,
        "manual_necessario": manual,
        "stage": 1,
        "stage_status": "running",
        "pending_gate": None,
        "rdm": None,
        "deployment_date": None,
        "ajustar_iterations": 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "history": [],
    }
    _atomic_write(state_path, state)
    return {"action": "init", "status": "ok", "state": state}


def cmd_update(state_path: Path, stage: int | None, stage_status: str | None,
               pending_gate: str | None, rdm: str | None, deployment_date: str | None,
               increment_ajustar: bool) -> dict:
    if not state_path.exists():
        return {"action": "update", "status": "error", "message": "ship-state.json not found. Run 'init' first."}

    state = _read_state(state_path)
    if state is None:
        return {"action": "update", "status": "error", "message": "ship-state.json is corrupt."}

    entry = {"timestamp": datetime.now(timezone.utc).isoformat(), "from_stage": state["stage"], "from_status": state["stage_status"]}

    if stage is not None:
        state["stage"] = stage
    if stage_status is not None:
        state["stage_status"] = stage_status
    if pending_gate is not None:
        state["pending_gate"] = pending_gate if pending_gate != "none" else None
    if rdm is not None:
        state["rdm"] = rdm
    if deployment_date is not None:
        state["deployment_date"] = deployment_date
    if increment_ajustar:
        state["ajustar_iterations"] = state.get("ajustar_iterations", 0) + 1

    entry["to_stage"] = state["stage"]
    entry["to_status"] = state["stage_status"]
    state["history"].append(entry)
    state["updated_at"] = datetime.now(timezone.utc).isoformat()

    _atomic_write(state_path, state)
    return {"action": "update", "status": "ok", "state": state}


def cmd_read(state_path: Path) -> dict:
    if not state_path.exists():
        return {"action": "read", "status": "not_found", "state": None}

    state = _read_state(state_path)
    if state is None:
        return {"action": "read", "status": "corrupt", "state": None}

    return {"action": "read", "status": "ok", "state": state}


def cmd_resume_from(state_path: Path, task_type: str | None, manual: bool | None) -> dict:
    if not state_path.exists():
        return {"action": "resume-from", "status": "error", "message": "ship-state.json not found."}

    state = _read_state(state_path)
    if state is None:
        return {"action": "resume-from", "status": "error", "message": "ship-state.json is corrupt."}

    warnings = []

    if task_type and task_type != state.get("task_type"):
        warnings.append(f"CLI task_type '{task_type}' differs from stored '{state.get('task_type')}'. Using stored value.")
    if manual is not None and manual != state.get("manual_necessario"):
        warnings.append(f"CLI manual flag differs from stored value. Using stored value.")

    return {
        "action": "resume-from",
        "status": "ok",
        "resume_stage": state["stage"],
        "resume_status": state["stage_status"],
        "pending_gate": state.get("pending_gate"),
        "warnings": warnings,
        "state": state,
    }


def _read_state(state_path: Path) -> dict | None:
    try:
        return json.loads(state_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _atomic_write(state_path: Path, state: dict):
    state_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = state_path.with_suffix(".tmp")
    tmp_path.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(str(tmp_path), str(state_path))


def main():
    parser = argparse.ArgumentParser(
        description="Manage ship-state.json lifecycle.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="Create initial ship-state.json")
    p_init.add_argument("state_path", type=Path)
    p_init.add_argument("--task-type", choices=VALID_TASK_TYPES, required=True)
    p_init.add_argument("--manual", action="store_true")

    p_update = sub.add_parser("update", help="Update ship-state.json fields")
    p_update.add_argument("state_path", type=Path)
    p_update.add_argument("--stage", type=int, choices=VALID_STAGES)
    p_update.add_argument("--stage-status", choices=VALID_STATUSES)
    p_update.add_argument("--pending-gate", choices=[*VALID_GATES, "none"])
    p_update.add_argument("--rdm", type=str)
    p_update.add_argument("--deployment-date", type=str)
    p_update.add_argument("--increment-ajustar", action="store_true")

    p_read = sub.add_parser("read", help="Read current ship state")
    p_read.add_argument("state_path", type=Path)

    p_resume = sub.add_parser("resume-from", help="Validate state for resume")
    p_resume.add_argument("state_path", type=Path)
    p_resume.add_argument("--task-type", choices=VALID_TASK_TYPES)
    p_resume.add_argument("--manual", action="store_true", default=None)

    args = parser.parse_args()

    if args.command == "init":
        result = cmd_init(args.state_path, args.task_type, args.manual)
    elif args.command == "update":
        result = cmd_update(
            args.state_path, args.stage, args.stage_status,
            args.pending_gate, args.rdm, args.deployment_date,
            args.increment_ajustar,
        )
    elif args.command == "read":
        result = cmd_read(args.state_path)
    elif args.command == "resume-from":
        result = cmd_resume_from(args.state_path, args.task_type, args.manual)

    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result["status"] in ("ok", "not_found") else 1)


if __name__ == "__main__":
    main()
