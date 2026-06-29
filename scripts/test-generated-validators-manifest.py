#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Lightweight self-test for check-generated-validators-manifest.py."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().with_name("check-generated-validators-manifest.py")
GENERATOR = Path(__file__).resolve().with_name("check-generated-validators.py")


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class GeneratedValidatorsManifestTest(unittest.TestCase):
    def setUp(self) -> None:
        self.checker = load_module("check_generated_validators_manifest", SCRIPT)
        self.generator = load_module("check_generated_validators", GENERATOR)

    def payload(self):
        return self.generator.build_payload(
            Path.cwd(),
            ["ariadne"],
            [self.generator.PlanItem("ariadne", "a.html", ["python"])],
            [self.generator.ValidationResult("ariadne", "a.html", "python validate-ariadne.py a.html", 0, 0, 1, ["[WARN] A25"])],
        )

    def test_load_generated_validators_module(self) -> None:
        mod = self.checker.load_generated_validators_module()
        self.assertEqual(self.generator.SCHEMA_VERSION, mod.SCHEMA_VERSION)

    def test_cli_valid_manifest_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "generated-validators.json"
            path.write_text(json.dumps(self.payload(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(path)],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("ERROR=0", result.stdout)

    def test_cli_invalid_manifest_fails(self) -> None:
        payload = self.payload()
        payload["schemaVersion"] = "bad"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "generated-validators.json"
            path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(path)],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
        self.assertEqual(1, result.returncode)
        self.assertIn("schemaVersion mismatch", result.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
