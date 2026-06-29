# -*- coding: utf-8 -*-
"""Lightweight self-test for compare-lexia-manifests.py."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().with_name("compare-lexia-manifests.py")


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class LexiaManifestDiffTest(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = load_module("compare_lexia_manifests", SCRIPT)
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def entry(self, code: str, **overrides):
        source_path = overrides.pop("sourcePath", f"outputs/001_JX/001_刑法/{code}.html")
        data = {
            "sourcePath": source_path,
            "fileName": source_path.rsplit("/", 1)[-1],
            "code": code,
            "baseCode": code,
            "title": code,
            "subject": "刑法",
            "subjectDir": "001_刑法",
            "category": "JX",
            "bytes": 20480,
            "textLength": 1200,
            "stableSha256": "a" * 64,
            "generated": "2026-06-28T00:00+09:00",
        }
        data.update(overrides)
        return data

    def payload(self, entries):
        return {
            "schemaVersion": "lexia-sync-contract/v3",
            "roots": ["outputs", "references"],
            "html": len(entries),
            "classified": len(entries),
            "categories": {"JX": len(entries)},
            "errorCount": 0,
            "warningCount": 0,
            "entries": entries,
        }

    def test_build_diff_payload_classifies_manifest_drift(self) -> None:
        before = self.payload(
            [
                self.entry("刑JX001"),
                self.entry("刑JX002"),
                self.entry("刑JX003"),
                self.entry("刑JX004"),
            ]
        )
        after = self.payload(
            [
                self.entry("刑JX001", generated="2026-06-29T00:00+09:00"),
                self.entry("刑JX002", bytes=20490, textLength=1210, generated="2026-06-29T00:00:00+09:00"),
                self.entry("刑JX003", stableSha256="b" * 64, bytes=40960, textLength=1600),
                self.entry("刑JX005"),
            ]
        )
        payload = self.mod.build_diff_payload(
            self.root / "before.json",
            before,
            self.root / "after.json",
            after,
        )
        self.assertEqual(self.mod.SCHEMA_VERSION, payload["schemaVersion"])
        self.assertNotIn("generatedAt", payload)
        self.assertEqual(4, payload["counts"]["beforeEntries"])
        self.assertEqual(4, payload["counts"]["afterEntries"])
        self.assertEqual(1, payload["counts"]["removed"])
        self.assertEqual(1, payload["counts"]["added"])
        self.assertEqual(2, payload["counts"]["generatedOnly"])
        self.assertEqual(1, payload["counts"]["contentChanged"])
        self.assertEqual(["刑JX004"], [item["code"] for item in payload["removed"]])
        self.assertEqual(["刑JX005"], [item["code"] for item in payload["added"]])
        self.assertEqual(["刑JX001", "刑JX002"], [item["code"] for item in payload["generatedOnly"]])
        self.assertEqual(["刑JX003"], [item["code"] for item in payload["contentChanged"]])

    def test_metadata_only_and_size_only_are_classified(self) -> None:
        before = self.entry("刑JX001")
        metadata_after = self.entry("刑JX001", title="刑JX001 updated")
        size_after = self.entry("刑JX001", bytes=20481)
        self.assertEqual("metadataOnly", self.mod.classify_change(before, metadata_after, ["title"]))
        self.assertEqual("sizeOnly", self.mod.classify_change(before, size_after, ["bytes"]))

    def test_changed_fields_include_extra_fields_stably(self) -> None:
        before = self.entry("刑JX001", extraA="old")
        after = self.entry("刑JX001", extraA="new", extraB="new")
        self.assertEqual(["extraA", "extraB"], self.mod.changed_fields(before, after)[-2:])

    def test_cli_fail_on_content_change_returns_one_and_writes_json(self) -> None:
        before = self.payload([self.entry("刑JX001")])
        after = self.payload([self.entry("刑JX001", stableSha256="b" * 64, bytes=40960, textLength=1600)])
        before_path = self.root / "before.json"
        after_path = self.root / "after.json"
        diff_path = self.root / "diff.json"
        before_path.write_text(json.dumps(before, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        after_path.write_text(json.dumps(after, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        completed = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(before_path),
                str(after_path),
                "--json",
                str(diff_path),
                "--fail-on-content-change",
            ],
            cwd=SCRIPT.parents[1],
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
        )

        self.assertEqual(1, completed.returncode)
        self.assertIn("contentChanged=1", completed.stdout)
        payload = json.loads(diff_path.read_text(encoding="utf-8"))
        self.assertEqual(self.mod.SCHEMA_VERSION, payload["schemaVersion"])
        self.assertEqual(1, payload["counts"]["contentChanged"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
