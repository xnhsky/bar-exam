#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Lightweight self-test for check-rx-coverage.py."""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().with_name("check-rx-coverage.py")


def load_rx_module():
    spec = importlib.util.spec_from_file_location("check_rx_coverage", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class RxCoverageTest(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = load_rx_module()
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.old_root = self.mod.ROOT
        self.old_rx_base = self.mod.RX_BASE
        self.old_ari_base = self.mod.ARI_BASE
        self.mod.ROOT = self.root
        self.mod.RX_BASE = self.root / "outputs" / "ux" / "002_RX"
        self.mod.ARI_BASE = self.root / "outputs" / "ux" / "001_ARIADNE"
        self.mod.set_color(False)

    def tearDown(self) -> None:
        self.mod.ROOT = self.old_root
        self.mod.RX_BASE = self.old_rx_base
        self.mod.ARI_BASE = self.old_ari_base
        self.mod.set_color(True)
        self.tmp.cleanup()

    def test_classify_uncovered_distinguishes_anchor_and_cap(self) -> None:
        unreachable, safetynet = self.mod.classify_uncovered({"刑RX001_2", "刑RX001_9"}, has_anchor=True)
        self.assertEqual([("刑RX001_9", "_9 > 手繰り上限 _8")], unreachable)
        self.assertEqual(["刑RX001_2"], safetynet)

        unreachable, safetynet = self.mod.classify_uncovered({"刑RX001_1"}, has_anchor=False)
        self.assertEqual([("刑RX001_1", "data-rx 起点なし")], unreachable)
        self.assertEqual([], safetynet)

    def test_referenced_in_ariadne_dedupes_and_ignores_empty_values(self) -> None:
        path = self.root / "a.html"
        path.write_text(
            '<div data-rx="刑RX001_1"></div>'
            "<div data-rx='刑RX001_2'></div>"
            '<div data-rx=" "></div>'
            '<div data-rx="刑RX001_1"></div>',
            encoding="utf-8",
        )
        self.assertEqual({"刑RX001_1", "刑RX001_2"}, self.mod.referenced_in_ariadne(path))

    def test_check_subject_counts_dangling_unreachable_and_safety_net(self) -> None:
        rx_dir = self.mod.RX_BASE / "001_刑法" / "刑JX001"
        rx_dir.mkdir(parents=True)
        for name in ("刑RX001_1.html", "刑RX001_2.html", "刑RX001_9.html"):
            (rx_dir / name).write_text("<html></html>", encoding="utf-8")

        ari_dir = self.mod.ARI_BASE / "001_刑法"
        ari_dir.mkdir(parents=True)
        (ari_dir / "刑JX001_ARIADNE.html").write_text(
            '<div class="self-check-quiz" data-rx="刑RX001_1"></div>'
            '<div class="self-check-quiz" data-rx="刑RX001_3"></div>',
            encoding="utf-8",
        )

        with contextlib.redirect_stdout(io.StringIO()):
            stats = self.mod.check_subject(self.mod.RX_BASE / "001_刑法", summary=True)

        self.assertEqual(3, stats["present"])
        self.assertEqual(2, stats["referenced"])
        self.assertEqual(2, stats["uncovered"])
        self.assertEqual(1, stats["safetynet"])
        self.assertEqual(1, stats["unreachable"])
        self.assertEqual(1, stats["dangling"])

    def test_manifest_payload_is_schema_versioned_and_stable(self) -> None:
        stats = {
            "subject": "001_刑法",
            "jx": 1,
            "present": 2,
            "referenced": 1,
            "uncovered": 1,
            "unreachable": 0,
            "safetynet": 1,
            "dangling": 0,
            "ok": 1,
            "ari_missing": 0,
            "dangling_detail": [],
            "unreachable_detail": [("刑JX001", [("刑RX001_9", "_9 > 手繰り上限 _8")])],
        }
        grand = {key: stats[key] for key in (
            "jx", "present", "referenced", "uncovered", "unreachable",
            "safetynet", "dangling", "ok", "ari_missing"
        )}
        payload = self.mod.build_payload("刑", strict=True, checked=[stats], skipped=["002_刑事訴訟法"], grand=grand)
        self.assertEqual(self.mod.SCHEMA_VERSION, payload["schemaVersion"])
        self.assertEqual("刑", payload["filter"])
        self.assertEqual(1, payload["counts"]["safetynet"])
        self.assertEqual(["002_刑事訴訟法"], payload["skippedSubjects"])
        dumped = json.dumps(payload, ensure_ascii=False, indent=2)
        self.assertEqual(
            dumped,
            json.dumps(self.mod.build_payload("刑", True, [stats], ["002_刑事訴訟法"], grand), ensure_ascii=False, indent=2),
        )

    def test_write_text_if_changed_skips_identical_content(self) -> None:
        path = self.root / "rx.json"
        self.assertTrue(self.mod.write_text_if_changed(path, "one\n"))
        self.assertFalse(self.mod.write_text_if_changed(path, "one\n"))
        self.assertTrue(self.mod.write_text_if_changed(path, "two\n"))
        self.assertEqual("two\n", path.read_text(encoding="utf-8"))

    def test_no_color_clears_ansi_globals(self) -> None:
        self.mod.set_color(False)
        self.assertEqual("", self.mod.RED)
        self.assertEqual("", self.mod.RST)
        self.mod.set_color(True)
        self.assertIn("\033", self.mod.RED)


if __name__ == "__main__":
    unittest.main(verbosity=2)
