#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Lightweight self-test for lexia-change-summary.py."""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().with_name("lexia-change-summary.py")


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class LexiaChangeSummaryTest(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = load_module("lexia_change_summary", SCRIPT)
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_parse_porcelain_z_handles_normal_and_rename(self) -> None:
        data = b" M scripts/a.py\0?? outputs/x.html\0R  docs/new.md\0docs/old.md\0"
        changes = self.mod.parse_porcelain_z(data)
        self.assertEqual(" M", changes[0].status)
        self.assertEqual("scripts/a.py", changes[0].path)
        self.assertEqual("??", changes[1].status)
        self.assertEqual("outputs/x.html", changes[1].path)
        self.assertEqual("R ", changes[2].status)
        self.assertEqual("docs/new.md", changes[2].path)
        self.assertEqual("docs/old.md", changes[2].original_path)

    def test_category_for_path(self) -> None:
        cases = {
            "scripts/check.py": "ROOT_TOOLING",
            "scripts/lex/build-lite-lex.py": "GENERATION_TOOLING",
            "scripts/tx-build-typeA.py": "GENERATION_TOOLING",
            "scripts/validate-tx-core.py": "GENERATION_TOOLING",
            "scripts/build_fillin_template.py": "GENERATION_TOOLING",
            "docs/validate-guide.md": "DOCS",
            "inputs/build_notes.txt": "INPUTS",
            "outputs/ux/a.html": "GENERATED_SYNC_HTML",
            "references/r.html": "GENERATED_SYNC_HTML",
            "outputs/001_JX/_failed/a.html": "QUARANTINED_OUTPUT",
            "canonical/ARIADNE.html": "CANONICAL",
            "docs/a.md": "DOCS",
            "inputs/a.txt": "INPUTS",
            "work/a.tmp": "WORK",
            ".claude/settings.local.json": "LOCAL_CONFIG",
            "README.md": "ROOT_TOOLING",
        }
        for path, category in cases.items():
            with self.subTest(path=path):
                self.assertEqual(category, self.mod.category_for_path(path))

    def test_payload_is_schema_versioned_and_grouped(self) -> None:
        changes = [
            self.mod.Change("??", "outputs/ux/a.html"),
            self.mod.Change(" M", "scripts/a.py"),
        ]
        payload = self.mod.build_payload(changes)
        self.assertEqual(self.mod.SCHEMA_VERSION, payload["schemaVersion"])
        self.assertEqual("all", payload["untrackedFiles"])
        self.assertEqual(2, payload["total"])
        self.assertEqual([], payload["failPresets"])
        self.assertEqual([], payload["failGroups"])
        self.assertEqual(0, payload["failCount"])
        self.assertEqual([], payload["failItems"])
        self.assertEqual(["ROOT_TOOLING", "GENERATED_SYNC_HTML"], [group["group"] for group in payload["groups"]])
        self.assertNotIn("generatedAt", payload)

    def test_generation_tooling_is_separate_from_root_tooling(self) -> None:
        changes = [
            self.mod.Change(" M", "scripts/lex/build-lite-lex.py"),
            self.mod.Change(" M", "scripts/check.py"),
        ]
        payload = self.mod.build_payload(changes, fail_presets=["root-tooling-only"])
        self.assertEqual(["ROOT_TOOLING", "GENERATION_TOOLING"], [group["group"] for group in payload["groups"]])
        self.assertIn("GENERATION_TOOLING", payload["failGroups"])
        self.assertEqual(1, payload["failCount"])
        self.assertEqual(["scripts/lex/build-lite-lex.py"], [item["path"] for item in payload["failItems"]])

    def test_payload_records_untracked_mode(self) -> None:
        payload = self.mod.build_payload([], untracked_files="normal")
        self.assertEqual("normal", payload["untrackedFiles"])

    def test_validate_payload_accepts_tooling_only_manifest(self) -> None:
        changes = [
            self.mod.Change(" M", "scripts/check.py"),
            self.mod.Change(" M", "scripts/lex/build-lite-lex.py"),
        ]
        payload = self.mod.build_payload(changes, fail_presets=["tooling-only"])
        self.assertEqual([], self.mod.validate_payload(payload))

    def test_validate_payload_rejects_schema_count_and_preset_drift(self) -> None:
        payload = self.mod.build_payload([self.mod.Change(" M", "scripts/check.py")])
        payload["schemaVersion"] = "old"
        payload["failPresets"] = ["unknown"]
        payload["total"] = 2
        payload["groups"][0]["count"] = 2
        errors = self.mod.validate_payload(payload)
        self.assertIn("schemaVersion must be 'lexia-change-summary/v1'", errors)
        self.assertIn("failPresets must be an array of known presets", errors)
        self.assertIn("groups[0].count must match items length", errors)
        self.assertIn("total must match grouped item count", errors)

    def test_fail_groups_are_ordered_and_counted(self) -> None:
        changes = [
            self.mod.Change("??", "work/a.py"),
            self.mod.Change("??", "outputs/ux/a.html"),
            self.mod.Change(" M", "scripts/a.py"),
        ]
        payload = self.mod.build_payload(changes, fail_groups=["WORK", "GENERATED_SYNC_HTML"])
        self.assertEqual(["GENERATED_SYNC_HTML", "WORK"], payload["failGroups"])
        self.assertEqual(2, payload["failCount"])
        self.assertEqual(["outputs/ux/a.html", "work/a.py"], [item["path"] for item in payload["failItems"]])

    def test_fail_preset_root_tooling_only_expands_to_other_groups(self) -> None:
        changes = [
            self.mod.Change(" M", "scripts/a.py"),
            self.mod.Change("??", "docs/a.md"),
            self.mod.Change("??", "work/a.py"),
        ]
        payload = self.mod.build_payload(changes, fail_presets=["root-tooling-only"])
        self.assertEqual(["root-tooling-only"], payload["failPresets"])
        self.assertNotIn("ROOT_TOOLING", payload["failGroups"])
        self.assertIn("DOCS", payload["failGroups"])
        self.assertIn("WORK", payload["failGroups"])
        self.assertEqual(2, payload["failCount"])

    def test_fail_preset_tooling_only_allows_root_and_generation_tooling(self) -> None:
        changes = [
            self.mod.Change(" M", "scripts/check.py"),
            self.mod.Change(" M", "scripts/lex/build-lite-lex.py"),
            self.mod.Change(" M", "outputs/ux/a.html"),
            self.mod.Change("??", "docs/a.md"),
        ]
        payload = self.mod.build_payload(changes, fail_presets=["tooling-only"])
        self.assertEqual(["tooling-only"], payload["failPresets"])
        self.assertNotIn("ROOT_TOOLING", payload["failGroups"])
        self.assertNotIn("GENERATION_TOOLING", payload["failGroups"])
        self.assertEqual(2, payload["failCount"])
        self.assertEqual(["outputs/ux/a.html", "docs/a.md"], [item["path"] for item in payload["failItems"]])

    def test_fail_preset_sync_ready_ignores_generated_html_but_blocks_scratch(self) -> None:
        changes = [
            self.mod.Change(" M", "outputs/ux/a.html"),
            self.mod.Change("??", "outputs/001_JX/_failed/a.html"),
            self.mod.Change("??", "work/a.py"),
            self.mod.Change(" M", ".claude/settings.local.json"),
            self.mod.Change("??", "misc.tmp"),
        ]
        payload = self.mod.build_payload(changes, fail_presets=["sync-ready"])
        self.assertEqual(["sync-ready"], payload["failPresets"])
        self.assertNotIn("GENERATED_SYNC_HTML", payload["failGroups"])
        self.assertEqual(["QUARANTINED_OUTPUT", "WORK", "LOCAL_CONFIG", "OTHER"], payload["failGroups"])
        self.assertEqual(4, payload["failCount"])
        self.assertEqual(
            [
                "outputs/001_JX/_failed/a.html",
                "work/a.py",
                ".claude/settings.local.json",
                "misc.tmp",
            ],
            [item["path"] for item in payload["failItems"]],
        )

    def test_write_text_if_changed_skips_identical_content(self) -> None:
        path = self.root / "summary.json"
        self.assertTrue(self.mod.write_text_if_changed(path, "{}\n"))
        before = path.stat().st_mtime_ns
        self.assertFalse(self.mod.write_text_if_changed(path, "{}\n"))
        self.assertEqual(before, path.stat().st_mtime_ns)


if __name__ == "__main__":
    unittest.main(verbosity=2)
