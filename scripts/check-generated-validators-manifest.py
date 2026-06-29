#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate generated-validators.json produced by check-generated-validators.py."""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

try:
    sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", line_buffering=True)
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[1]
GENERATED_VALIDATORS_SCRIPT = ROOT / "scripts" / "check-generated-validators.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_generated_validators_module():
    return load_module("check_generated_validators", GENERATED_VALIDATORS_SCRIPT)


def resolve_path(path_arg: str) -> Path:
    path = Path(path_arg)
    return path if path.is_absolute() else ROOT / path


def read_json(path: Path) -> tuple[Any | None, list[str]]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), []
    except OSError as exc:
        return None, [f"{path}: cannot read JSON: {exc}"]
    except json.JSONDecodeError as exc:
        return None, [f"{path}: invalid JSON: {exc}"]


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate generated validators manifest JSON")
    ap.add_argument("json_path", help="generated-validators.json")
    ap.add_argument("--verify-current", action="store_true", help="現在の outputs/ux に対する横断 validator 結果と一致するか検証")
    args = ap.parse_args()

    mod = load_generated_validators_module()
    path = resolve_path(args.json_path)
    payload, errors = read_json(path)
    if not errors:
        errors.extend(mod.validate_payload(payload))
    if args.verify_current and not errors:
        errors.extend(mod.validate_against_current(payload))

    print("=== generated validators manifest schema check ===")
    print(f"path={path}")
    if errors:
        for error in errors:
            print(f"[ERROR] {error}")
    print("\n=== summary ===")
    print(f"ERROR={len(errors)}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
