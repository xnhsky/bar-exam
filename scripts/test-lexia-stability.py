#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Lightweight self-test for check-lexia-stability.py."""
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().with_name("check-lexia-stability.py")


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class LexiaStabilityTest(unittest.TestCase):
    def setUp(self) -> None:
        self.checker = load_module("check_lexia_stability", SCRIPT)
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_diff_snapshots_detects_added_removed_and_changed(self) -> None:
        before = {
            "a.html": {"bytes": 1, "sha256": "aaa"},
            "b.html": {"bytes": 1, "sha256": "bbb"},
        }
        after = {
            "b.html": {"bytes": 2, "sha256": "changed"},
            "c.html": {"bytes": 1, "sha256": "ccc"},
        }
        diff = self.checker.diff_snapshots(before, after)
        self.assertEqual(["c.html"], diff["added"])
        self.assertEqual(["a.html"], diff["removed"])
        self.assertEqual(["b.html"], diff["changed"])

    def test_snapshot_only_tracks_html_files(self) -> None:
        (self.root / "a.html").write_text("<html>a</html>", encoding="utf-8")
        (self.root / "b.txt").write_text("ignore", encoding="utf-8")
        files, errors = self.checker.snapshot([self.root])
        self.assertEqual([], errors)
        self.assertEqual([str((self.root / "a.html").resolve())], list(files))

    def test_payload_is_schema_versioned_without_timestamp(self) -> None:
        payload = self.checker.build_payload(
            [self.root],
            0,
            {"a.html": {"bytes": 1, "sha256": "aaa"}},
            {"a.html": {"bytes": 1, "sha256": "aaa"}},
            {"added": [], "removed": [], "changed": []},
            [],
        )
        self.assertEqual(self.checker.SCHEMA_VERSION, payload["schemaVersion"])
        self.assertTrue(payload["stable"])
        self.assertNotIn("generatedAt", payload)

    def test_write_text_if_changed_skips_identical_content(self) -> None:
        path = self.root / "report.json"
        self.assertTrue(self.checker.write_text_if_changed(path, "{}\n"))
        before = path.stat().st_mtime_ns
        self.assertFalse(self.checker.write_text_if_changed(path, "{}\n"))
        self.assertEqual(before, path.stat().st_mtime_ns)

    def test_run_check_reports_stable_files(self) -> None:
        (self.root / "a.html").write_text("<html>a</html>", encoding="utf-8")
        payload = self.checker.run_check([self.root], 0)
        self.assertTrue(payload["stable"], json.dumps(payload, ensure_ascii=False))
        self.assertEqual(1, payload["beforeCount"])
        self.assertEqual(1, payload["afterCount"])
        self.assertEqual(1, payload["attempt"])
        self.assertEqual(1, payload["attempts"])

    def test_run_until_stable_retries_until_payload_stable(self) -> None:
        calls: list[int] = []
        sleeps: list[float] = []

        def fake_run_check(roots, settle_seconds, attempt=1, attempts=1):
            calls.append(attempt)
            changed = [] if attempt == 2 else ["a.html"]
            return self.checker.build_payload(
                roots,
                settle_seconds,
                {"a.html": {"bytes": 1, "sha256": "aaa"}},
                {"a.html": {"bytes": 2, "sha256": "bbb"}},
                {"added": [], "removed": [], "changed": changed},
                [],
                attempt=attempt,
                attempts=attempts,
            )

        original_run_check = self.checker.run_check
        original_sleep = self.checker.time.sleep
        self.checker.run_check = fake_run_check
        self.checker.time.sleep = lambda seconds: sleeps.append(seconds)
        try:
            payload = self.checker.run_until_stable([self.root], 0, attempts=3, retry_delay_seconds=0.5)
        finally:
            self.checker.run_check = original_run_check
            self.checker.time.sleep = original_sleep

        self.assertTrue(payload["stable"])
        self.assertEqual([1, 2], calls)
        self.assertEqual([0.5], sleeps)
        self.assertEqual(2, payload["attempt"])
        self.assertEqual(3, payload["attempts"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
