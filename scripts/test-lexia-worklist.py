#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Lightweight self-test for check-lexia-worklist.py."""
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().with_name("check-lexia-worklist.py")


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class LexiaWorklistManifestTest(unittest.TestCase):
    def setUp(self) -> None:
        self.checker = load_module("check_lexia_worklist", SCRIPT)
        self.worklist = self.checker.load_worklist_module()
        self.contract = self.checker.load_contract_module()

    def item(self, **overrides):
        data = {
            "target": "刑JX001",
            "severity": "WARN",
            "kind": "FILE",
            "category": "ARIADNE",
            "path": "outputs/ux/001_ARIADNE/001_刑法/刑JX001_ARIADNE.html",
            "message": "data-rx 重複 1 件: 刑RX001_1",
            "action": "ARIADNE 想起カードの data-rx 割当を確認し、必要なら対応 RX へ振り分け",
            "validators": [
                r"python scripts\validate-ariadne.py outputs\ux\001_ARIADNE\001_刑法\刑JX001_ARIADNE.html",
                self.worklist.CONTENT_PREFLIGHT_CMD,
            ],
        }
        data.update(overrides)
        return data

    def payload(self, items=None, **overrides):
        items = items if items is not None else [self.item()]
        data = {
            "schemaVersion": self.worklist.SCHEMA_VERSION,
            "roots": ["outputs", "references"],
            "filters": {"target": [], "includeFailed": True},
            "targets": len({item["target"] for item in items if isinstance(item, dict) and "target" in item}),
            "counts": {"ERROR": 0, "WARN": 1, "TODO": 0},
            "categories": {"ARIADNE": 1},
            "kinds": {"FILE": 1},
            "items": items,
        }
        data.update(overrides)
        return data

    def test_valid_manifest_passes(self) -> None:
        errors = self.checker.validate_worklist(self.worklist, self.contract, self.payload())
        self.assertEqual([], errors)

    def test_items_array_is_rejected(self) -> None:
        errors = self.checker.validate_worklist(self.worklist, self.contract, [self.item()])
        self.assertTrue(any("worklist manifest object expected" in error for error in errors), errors)

    def test_counts_and_sort_are_checked(self) -> None:
        items = [
            self.item(target="刑JX002", path="outputs/ux/001_ARIADNE/001_刑法/刑JX002_ARIADNE.html"),
            self.item(),
        ]
        payload = self.payload(
            items=items,
            targets=1,
            counts={"ERROR": 0, "WARN": 1, "TODO": 0},
            categories={"ARIADNE": 2},
            kinds={"FILE": 2},
        )
        errors = self.checker.validate_worklist(self.worklist, self.contract, payload)
        self.assertTrue(any("targets mismatch" in error for error in errors), errors)
        self.assertTrue(any("counts mismatch" in error for error in errors), errors)
        self.assertTrue(any("order is not stable-sorted" in error for error in errors), errors)

    def test_item_values_are_checked(self) -> None:
        item = self.item(severity="BAD", path=r"outputs\bad.html", validators=[""])
        payload = self.payload(items=[item], counts={"ERROR": 0, "WARN": 0, "TODO": 0})
        errors = self.checker.validate_worklist(self.worklist, self.contract, payload)
        self.assertTrue(any("unknown severity" in error for error in errors), errors)
        self.assertTrue(any("forward slashes" in error for error in errors), errors)
        self.assertTrue(any("validators" in error for error in errors), errors)

    def test_item_required_text_and_validator_tail_are_checked(self) -> None:
        item = self.item(
            target="",
            action="",
            path="outputs/ux/001_ARIADNE/../bad.html",
            validators=[r"python scripts\validate-ariadne.py outputs\ux\001_ARIADNE\001_刑法\刑JX001_ARIADNE.html"],
        )
        payload = self.payload(items=[item], counts={"ERROR": 0, "WARN": 1, "TODO": 0})
        errors = self.checker.validate_worklist(self.worklist, self.contract, payload)
        self.assertTrue(any("items[0].target" in error and "non-empty string" in error for error in errors), errors)
        self.assertTrue(any("items[0].action" in error and "non-empty string" in error for error in errors), errors)
        self.assertTrue(any("parent path segments" in error for error in errors), errors)
        self.assertTrue(any("final validator" in error for error in errors), errors)

    def test_filters_are_checked(self) -> None:
        payload = self.payload(filters={"target": ["刑JX001", ""], "includeFailed": "yes"})
        errors = self.checker.validate_worklist(self.worklist, self.contract, payload)
        self.assertTrue(any("filters.target" in error for error in errors), errors)
        self.assertTrue(any("filters.includeFailed" in error for error in errors), errors)

    def test_verify_current_detects_stale_worklist(self) -> None:
        payload = self.payload()
        current = self.payload(items=[self.item(message="changed")])
        old_current_payload = self.checker.current_payload
        try:
            self.checker.current_payload = lambda _worklist, _contract, _roots, _filters: self.checker.comparable_payload(current)
            errors = self.checker.validate_against_current(self.worklist, self.contract, payload)
        finally:
            self.checker.current_payload = old_current_payload
        self.assertTrue(any("current items mismatch" in error for error in errors), errors)

    def test_verify_current_passes_when_projection_matches(self) -> None:
        payload = self.payload()
        old_current_payload = self.checker.current_payload
        try:
            self.checker.current_payload = lambda _worklist, _contract, _roots, _filters: self.checker.comparable_payload(payload)
            errors = self.checker.validate_against_current(self.worklist, self.contract, payload)
        finally:
            self.checker.current_payload = old_current_payload
        self.assertEqual([], errors)


if __name__ == "__main__":
    unittest.main(verbosity=2)
