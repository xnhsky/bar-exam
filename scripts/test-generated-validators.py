#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Lightweight self-test for check-generated-validators.py."""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().with_name("check-generated-validators.py")


def load_module():
    spec = importlib.util.spec_from_file_location("check_generated_validators", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class GeneratedValidatorsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = load_module()

    def test_build_plan_finds_ariadne_rx_groups_and_tree_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ariadne = root / "001_ARIADNE" / "001_刑法"
            rx = root / "002_RX" / "001_刑法" / "刑JX001"
            tree = root / "003_TREE" / "001_刑法"
            ariadne.mkdir(parents=True)
            rx.mkdir(parents=True)
            tree.mkdir(parents=True)
            (ariadne / "刑JX001_ARIADNE.html").write_text("", encoding="utf-8")
            (rx / "刑RX001_1.html").write_text("", encoding="utf-8")
            (rx / "刑RX001_2.html").write_text("", encoding="utf-8")
            (tree / "刑JX001_TREE.html").write_text("", encoding="utf-8")

            plan = self.mod.build_plan(root, ["ariadne", "rx", "tree"])

        self.assertEqual(["ariadne", "rx", "tree"], [item.kind for item in plan])
        self.assertTrue(plan[1].label.endswith("刑RX001_*.html"))
        self.assertIn("validate-rx.py", plan[1].command[1])

    def test_parse_counts_for_each_validator_summary(self) -> None:
        self.assertEqual(
            (0, 2),
            self.mod.parse_counts("ariadne", "=== ARIADNE 検証: PASS 27 / WARN 2 / ERROR 0 ===", 0),
        )
        self.assertEqual((1, 3), self.mod.parse_counts("rx", "ERROR=1, WARNING=3", 1))
        self.assertEqual((0, 4), self.mod.parse_counts("tree", "ERROR=0  WARNING=4", 0))

    def test_summarize_plan_counts_targets(self) -> None:
        plan = [
            self.mod.PlanItem("ariadne", "a", ["python"]),
            self.mod.PlanItem("rx", "r", ["python"]),
            self.mod.PlanItem("rx", "r2", ["python"]),
        ]
        self.assertEqual({"ariadne": 1, "rx": 2, "tree": 0}, self.mod.summarize_plan(plan))

    def test_warning_lines_extracts_ariadne_and_tree_warning_prefixes(self) -> None:
        output = "\n".join([
            "[PASS] A1: ok",
            "[WARN]  A25: 深掘り層が薄い",
            "[WARN ] T4: 幹分枝が少ない",
        ])
        self.assertEqual(
            ["[WARN]  A25: 深掘り層が薄い", "[WARN ] T4: 幹分枝が少ない"],
            self.mod.warning_lines(output),
        )

    def test_build_payload_is_schema_versioned_and_stable(self) -> None:
        plan = [
            self.mod.PlanItem("ariadne", "a.html", ["python"]),
            self.mod.PlanItem("tree", "t.html", ["python"]),
        ]
        results = [
            self.mod.ValidationResult("ariadne", "a.html", "python validate-ariadne.py a.html", 0, 0, 1, ["[WARN] A25"]),
            self.mod.ValidationResult("tree", "t.html", "python validate-tree.py t.html", 1, 2, 3, ["[WARN ] T4"]),
        ]
        payload = self.mod.build_payload(Path.cwd(), ["ariadne", "tree"], plan, results)

        self.assertEqual("generated-validators/v1", payload["schemaVersion"])
        self.assertEqual(["ariadne", "tree"], payload["targets"])
        self.assertEqual({"ariadne": 1, "tree": 1}, payload["planned"])
        self.assertEqual({"items": 1, "failures": 0, "errors": 0, "warnings": 1}, payload["summary"]["ariadne"])
        self.assertEqual({"items": 1, "failures": 1, "errors": 2, "warnings": 3}, payload["summary"]["tree"])
        self.assertEqual(["a.html", "t.html"], [item["label"] for item in payload["warnings"]])
        self.assertEqual(["t.html"], [item["label"] for item in payload["failures"]])
        self.assertEqual([], self.mod.validate_payload(payload))

    def test_write_text_if_changed_skips_identical_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "nested" / "generated.json"
            self.assertTrue(self.mod.write_text_if_changed(path, "{}\n"))
            self.assertFalse(self.mod.write_text_if_changed(path, "{}\n"))
            self.assertTrue(self.mod.write_text_if_changed(path, "[]\n"))

    def test_validate_payload_rejects_schema_and_count_drift(self) -> None:
        payload = self.mod.build_payload(
            Path.cwd(),
            ["ariadne"],
            [self.mod.PlanItem("ariadne", "a.html", ["python"])],
            [self.mod.ValidationResult("ariadne", "a.html", "python validate-ariadne.py a.html", 0, 0, 1, ["[WARN] A25"])],
        )
        payload["schemaVersion"] = "bad"
        payload["planned"]["ariadne"] = 2
        payload["warnings"][0]["label"] = ""
        errors = self.mod.validate_payload(payload)
        self.assertTrue(any("schemaVersion mismatch" in error for error in errors), errors)
        self.assertTrue(any("items must match planned" in error for error in errors), errors)
        self.assertTrue(any("label: expected non-empty string" in error for error in errors), errors)

    def test_validate_against_current_detects_stale_summary(self) -> None:
        payload = self.mod.build_payload(
            Path.cwd(),
            ["tree"],
            [self.mod.PlanItem("tree", "t.html", ["python"])],
            [self.mod.ValidationResult("tree", "t.html", "python validate-tree.py t.html", 0, 0, 0, [])],
        )
        current = self.mod.build_payload(
            Path.cwd(),
            ["tree"],
            [self.mod.PlanItem("tree", "t.html", ["python"])],
            [self.mod.ValidationResult("tree", "t.html", "python validate-tree.py t.html", 1, 1, 0, [])],
        )
        old_current_payload = self.mod.current_payload
        try:
            self.mod.current_payload = lambda _root, _targets: current
            errors = self.mod.validate_against_current(payload)
        finally:
            self.mod.current_payload = old_current_payload
        self.assertTrue(any("current summary mismatch" in error for error in errors), errors)
        self.assertTrue(any("current failures mismatch" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main(verbosity=2)
