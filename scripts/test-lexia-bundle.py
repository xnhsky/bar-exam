#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Lightweight self-test for check-lexia-bundle.py."""
from __future__ import annotations

import importlib.util
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path


SCRIPT = Path(__file__).resolve().with_name("check-lexia-bundle.py")


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class LexiaBundleTest(unittest.TestCase):
    def setUp(self) -> None:
        self.checker = load_module("check_lexia_bundle", SCRIPT)
        self.mods = self.checker.BundleModules()
        self.tmp = tempfile.TemporaryDirectory()
        self.bundle = Path(self.tmp.name)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def write_json(self, name: str, payload) -> None:
        (self.bundle / name).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def sync_entry(self, source_path: str, code: str, text_length: int, size: int):
        return {
            "sourcePath": source_path,
            "fileName": source_path.rsplit("/", 1)[-1],
            "code": code,
            "baseCode": code,
            "title": code,
            "subject": "刑法",
            "subjectDir": "001_刑法",
            "category": "JX",
            "bytes": size,
            "textLength": text_length,
            "stableSha256": "a" * 64,
            "generated": "2026-06-28T00:00+09:00",
        }

    def sync_manifest(self, entries=None):
        entries = entries if entries is not None else []
        return {
            "schemaVersion": self.mods.contract.SCHEMA_VERSION,
            "roots": ["outputs", "references"],
            "html": len(entries),
            "classified": len(entries),
            "categories": {"JX": len(entries)} if entries else {},
            "errorCount": 0,
            "warningCount": 0,
            "entries": entries,
        }

    def rx_manifest(self):
        return {
            "schemaVersion": self.mods.rx.SCHEMA_VERSION,
            "filter": "",
            "strict": True,
            "supplementCap": self.mods.rx.SUPPLEMENT_CAP,
            "fail": False,
            "counts": {
                "jx": 0,
                "present": 0,
                "referenced": 0,
                "uncovered": 0,
                "unreachable": 0,
                "safetynet": 0,
                "dangling": 0,
                "ok": 0,
                "ari_missing": 0,
            },
            "subjects": [],
            "skippedSubjects": [],
        }

    def worklist_item(self):
        return {
            "target": "刑JX001",
            "severity": "WARN",
            "kind": "FILE",
            "category": "ARIADNE",
            "path": "outputs/ux/001_ARIADNE/001_刑法/刑JX001_ARIADNE.html",
            "message": "data-rx 重複 1 件: 刑RX001_1",
            "action": "ARIADNE 想起カードの data-rx 割当を確認",
            "validators": ["python scripts\\check-lexia-preflight.py --allow-untracked-sync-artifacts"],
        }

    def worklist_manifest(self, items=None):
        items = items if items is not None else []
        return {
            "schemaVersion": self.mods.worklist.SCHEMA_VERSION,
            "roots": ["outputs", "references"],
            "filters": {"target": [], "includeFailed": True},
            "targets": len({item["target"] for item in items}),
            "counts": {
                "ERROR": sum(1 for item in items if item["severity"] == "ERROR"),
                "WARN": sum(1 for item in items if item["severity"] == "WARN"),
                "TODO": sum(1 for item in items if item["severity"] == "TODO"),
            },
            "categories": {"ARIADNE": len(items)} if items else {},
            "kinds": {"FILE": len(items)} if items else {},
            "items": items,
        }

    def stability_manifest(self):
        return {
            "schemaVersion": self.checker.STABILITY_SCHEMA_VERSION,
            "roots": ["outputs", "references"],
            "settleSeconds": 2.0,
            "attempt": 2,
            "attempts": 3,
            "stable": True,
            "beforeCount": 3,
            "afterCount": 3,
            "errorCount": 0,
            "changedCount": 0,
            "addedCount": 0,
            "removedCount": 0,
            "errors": [],
            "changed": [],
            "added": [],
            "removed": [],
        }

    def change_summary_manifest(self):
        return {
            "schemaVersion": self.checker.CHANGE_SUMMARY_SCHEMA_VERSION,
            "untrackedFiles": "all",
            "total": 2,
            "failPresets": [],
            "failGroups": [],
            "failCount": 0,
            "failItems": [],
            "groups": [
                {
                    "group": "ROOT_TOOLING",
                    "count": 1,
                    "items": [{"status": " M", "path": "scripts/check.py"}],
                },
                {
                    "group": "GENERATED_SYNC_HTML",
                    "count": 1,
                    "items": [{"status": "??", "path": "outputs/ux/a.html"}],
                },
            ],
        }

    def manifest_diff(self):
        return {
            "schemaVersion": self.checker.MANIFEST_DIFF_SCHEMA_VERSION,
            "before": "deploy/old/lexia-sync-manifest.json",
            "after": "deploy/new/lexia-sync-manifest.json",
            "counts": {
                "beforeEntries": 1,
                "afterEntries": 1,
                "unchanged": 1,
                "added": 0,
                "removed": 0,
                "generatedOnly": 0,
                "contentChanged": 0,
                "sizeOnly": 0,
                "metadataOnly": 0,
                "changedTotal": 0,
            },
            "added": [],
            "removed": [],
            "generatedOnly": [],
            "contentChanged": [],
            "sizeOnly": [],
            "metadataOnly": [],
        }

    def generated_validators_manifest(self):
        return {
            "schemaVersion": self.checker.GENERATED_VALIDATORS_SCHEMA_VERSION,
            "root": "outputs/ux",
            "targets": ["ariadne", "rx", "tree"],
            "planned": {"ariadne": 1, "rx": 1, "tree": 1},
            "summary": {
                "ariadne": {"items": 1, "failures": 0, "errors": 0, "warnings": 1},
                "rx": {"items": 1, "failures": 0, "errors": 0, "warnings": 0},
                "tree": {"items": 1, "failures": 0, "errors": 0, "warnings": 0},
            },
            "warnings": [
                {
                    "kind": "ariadne",
                    "label": "outputs/ux/001_ARIADNE/001_刑法/刑JX032_ARIADNE.html",
                    "command": "python scripts/validate-ariadne.py outputs/ux/001_ARIADNE/001_刑法/刑JX032_ARIADNE.html",
                    "returnCode": 0,
                    "errors": 0,
                    "warnings": 1,
                    "warningLines": ["[WARN] A25"],
                }
            ],
            "failures": [],
        }

    def write_bundle(self, worklist=None, stability=False, change_summary=False, manifest_diff=False, generated_validators=False) -> None:
        worklist = worklist if worklist is not None else self.worklist_manifest()
        self.write_json(self.checker.SYNC_MANIFEST, self.sync_manifest())
        self.write_json(self.checker.RX_MANIFEST, self.rx_manifest())
        self.write_json(self.checker.WORKLIST_MANIFEST, worklist)
        if stability:
            self.write_json(self.checker.STABILITY_MANIFEST, self.stability_manifest())
        if change_summary:
            self.write_json(self.checker.CHANGE_SUMMARY_MANIFEST, self.change_summary_manifest())
        if manifest_diff:
            self.write_json(self.checker.MANIFEST_DIFF, self.manifest_diff())
        if generated_validators:
            self.write_json(self.checker.GENERATED_VALIDATORS_MANIFEST, self.generated_validators_manifest())
        (self.bundle / self.checker.WORKLIST_MARKDOWN).write_text(
            "# Lexia Content Worklist\n\n"
            f"- targets: {worklist['targets']}\n"
            "- ERROR: 0\n",
            encoding="utf-8",
        )
        (self.bundle / self.checker.PROMPTS_DIR).mkdir()

    def test_valid_empty_bundle_passes(self) -> None:
        self.write_bundle()
        errors = self.checker.validate_bundle(self.bundle)
        self.assertEqual([], errors)

    def test_valid_prompt_bundle_passes(self) -> None:
        worklist = self.worklist_manifest([self.worklist_item()])
        self.write_bundle(worklist)
        prompt = self.bundle / self.checker.PROMPTS_DIR / "刑JX001_content_prompt.md"
        prompt.write_text("# 刑JX001 内容改善セッション\n\nbody\n", encoding="utf-8")
        errors = self.checker.validate_bundle(self.bundle)
        self.assertEqual([], errors)

    def test_index_payload_summarizes_bundle_without_timestamp(self) -> None:
        worklist = self.worklist_manifest([self.worklist_item()])
        self.write_bundle(worklist)
        prompt = self.bundle / self.checker.PROMPTS_DIR / "刑JX001_content_prompt.md"
        prompt.write_text("# 刑JX001 内容改善セッション\n\nbody\n", encoding="utf-8")
        payload = self.checker.build_index_payload(self.bundle)
        self.assertEqual(self.checker.INDEX_SCHEMA_VERSION, payload["schemaVersion"])
        self.assertNotIn("generatedAt", payload)
        self.assertIn(self.checker.SYNC_MANIFEST, payload["files"])
        self.assertEqual(0, payload["sync"]["errorCount"])
        self.assertFalse(payload["sync"]["hasTextLength"])
        self.assertFalse(payload["sync"]["hasStableSha256"])
        self.assertEqual([], payload["sync"]["lowestTextEntries"])
        self.assertEqual(0, payload["rx"]["dangling"])
        self.assertEqual(1, payload["worklist"]["targets"])
        self.assertEqual(["刑JX001_content_prompt.md"], payload["worklist"]["promptFiles"])
        self.assertTrue(payload["gates"]["syncContract"])
        self.assertTrue(payload["gates"]["rxReachability"])
        self.assertFalse(payload["gates"]["contentWorklist"])
        self.assertTrue(payload["gates"]["changeSummary"])
        self.assertFalse(payload["gates"]["generatedValidators"])
        self.assertFalse(payload["gates"]["ready"])
        self.assertEqual({"ERROR": 0, "WARN": 1, "TODO": 0}, payload["gates"]["details"]["contentWorklist"])
        self.assertFalse(payload["generatedValidators"]["checked"])
        self.assertEqual({"checked": False, "failureCount": 0}, payload["gates"]["details"]["generatedValidators"])

    def test_index_payload_summarizes_sync_manifest_quality(self) -> None:
        self.write_bundle()
        entries = [
            self.sync_entry("outputs/001_JX/001_刑法/刑JX002.html", "刑JX002", 1200, 6000),
            self.sync_entry("outputs/001_JX/001_刑法/刑JX001.html", "刑JX001", 800, 8000),
        ]
        self.write_json(self.checker.SYNC_MANIFEST, self.sync_manifest(entries))
        payload = self.checker.build_index_payload(self.bundle)
        self.assertTrue(payload["sync"]["hasTextLength"])
        self.assertTrue(payload["sync"]["hasStableSha256"])
        self.assertEqual(
            [
                {
                    "sourcePath": "outputs/001_JX/001_刑法/刑JX001.html",
                    "category": "JX",
                    "code": "刑JX001",
                    "textLength": 800,
                    "bytes": 8000,
                    "density": 0.1,
                },
                {
                    "sourcePath": "outputs/001_JX/001_刑法/刑JX002.html",
                    "category": "JX",
                    "code": "刑JX002",
                    "textLength": 1200,
                    "bytes": 6000,
                    "density": 0.2,
                },
            ],
            payload["sync"]["lowestTextEntries"],
        )

    def test_index_payload_summarizes_stability_manifest(self) -> None:
        self.write_bundle(stability=True)
        payload = self.checker.build_index_payload(self.bundle)
        self.assertIn(self.checker.STABILITY_MANIFEST, payload["files"])
        self.assertTrue(payload["stability"]["stable"])
        self.assertEqual(2, payload["stability"]["attempt"])
        self.assertEqual(3, payload["stability"]["attempts"])
        self.assertEqual(3, payload["stability"]["beforeCount"])
        self.assertEqual(3, payload["stability"]["afterCount"])

    def test_index_payload_summarizes_change_summary_manifest(self) -> None:
        self.write_bundle(change_summary=True)
        payload = self.checker.build_index_payload(self.bundle)
        self.assertIn(self.checker.CHANGE_SUMMARY_MANIFEST, payload["files"])
        self.assertEqual("all", payload["changes"]["untrackedFiles"])
        self.assertEqual([], payload["changes"]["failPresets"])
        self.assertEqual([], payload["changes"]["failGroups"])
        self.assertEqual(0, payload["changes"]["failCount"])
        self.assertEqual(2, payload["changes"]["total"])
        self.assertEqual([], payload["changes"]["failItems"])
        self.assertEqual(1, payload["changes"]["groups"]["ROOT_TOOLING"])
        self.assertEqual(1, payload["changes"]["groups"]["GENERATED_SYNC_HTML"])
        self.assertEqual({"failCount": 0}, payload["gates"]["details"]["changeSummary"])
        self.assertTrue(payload["gates"]["changeSummary"])
        self.assertTrue(payload["gates"]["contentWorklist"])
        self.assertFalse(payload["gates"]["generatedValidators"])
        self.assertFalse(payload["gates"]["ready"])

    def test_change_summary_tooling_only_preset_is_valid(self) -> None:
        self.write_bundle(change_summary=True)
        manifest = self.change_summary_manifest()
        manifest["failPresets"] = ["tooling-only"]
        self.write_json(self.checker.CHANGE_SUMMARY_MANIFEST, manifest)
        errors = self.checker.validate_bundle(self.bundle)
        self.assertEqual([], errors)

    def test_index_payload_summarizes_manifest_diff(self) -> None:
        self.write_bundle(manifest_diff=True)
        payload = self.checker.build_index_payload(self.bundle)
        self.assertIn(self.checker.MANIFEST_DIFF, payload["files"])
        self.assertEqual(self.checker.MANIFEST_DIFF_SCHEMA_VERSION, payload["manifestDiff"]["schemaVersion"])
        self.assertEqual(0, payload["manifestDiff"]["counts"]["contentChanged"])
        self.assertEqual(1, payload["manifestDiff"]["counts"]["unchanged"])

    def test_index_payload_summarizes_generated_validators(self) -> None:
        self.write_bundle(generated_validators=True)
        payload = self.checker.build_index_payload(self.bundle)
        self.assertIn(self.checker.GENERATED_VALIDATORS_MANIFEST, payload["files"])
        self.assertEqual(self.checker.GENERATED_VALIDATORS_SCHEMA_VERSION, payload["generatedValidators"]["schemaVersion"])
        self.assertTrue(payload["generatedValidators"]["checked"])
        self.assertEqual(["ariadne", "rx", "tree"], payload["generatedValidators"]["targets"])
        self.assertEqual(1, payload["generatedValidators"]["warningCount"])
        self.assertEqual(1, payload["generatedValidators"]["warningItemCount"])
        self.assertEqual(0, payload["generatedValidators"]["failureCount"])
        self.assertEqual(1, payload["gates"]["generatedValidatorWarnings"])
        self.assertTrue(payload["gates"]["generatedValidators"])
        self.assertTrue(payload["gates"]["ready"])
        self.assertEqual({"checked": True, "failureCount": 0}, payload["gates"]["details"]["generatedValidators"])
        self.assertEqual(
            [
                {
                    "kind": "ariadne",
                    "label": "outputs/ux/001_ARIADNE/001_刑法/刑JX032_ARIADNE.html",
                    "warnings": 1,
                }
            ],
            payload["generatedValidators"]["warningItems"],
        )

    def test_invalid_generated_validators_manifest_is_error(self) -> None:
        self.write_bundle(generated_validators=True)
        broken = self.generated_validators_manifest()
        broken["schemaVersion"] = "bad"
        broken["targets"] = ["unknown"]
        broken["summary"]["ariadne"]["items"] = 99
        broken["warnings"][0]["label"] = ""
        self.write_json(self.checker.GENERATED_VALIDATORS_MANIFEST, broken)
        errors = self.checker.validate_bundle(self.bundle)
        self.assertTrue(any("schemaVersion mismatch" in error for error in errors), errors)
        self.assertTrue(any("targets: expected non-empty known target list" in error for error in errors), errors)
        self.assertTrue(any("label: expected non-empty string" in error for error in errors), errors)

    def test_generated_validators_verify_current_is_error(self) -> None:
        self.write_bundle(generated_validators=True)

        class FakeGeneratedValidators:
            @staticmethod
            def validate_payload(_payload):
                return []

            @staticmethod
            def validate_against_current(_payload):
                return ["current summary mismatch"]

        class FakeMods:
            generated_validators = FakeGeneratedValidators()

        errors = self.checker.validate_generated_validators_manifest(
            FakeMods(),
            self.bundle / self.checker.GENERATED_VALIDATORS_MANIFEST,
            verify_current=True,
        )
        self.assertTrue(any("current summary mismatch" in error for error in errors), errors)

    def test_invalid_manifest_diff_is_error(self) -> None:
        self.write_bundle(manifest_diff=True)
        broken = self.manifest_diff()
        broken["schemaVersion"] = "bad"
        broken["counts"]["contentChanged"] = -1
        broken["added"] = "bad"
        self.write_json(self.checker.MANIFEST_DIFF, broken)
        errors = self.checker.validate_bundle(self.bundle)
        self.assertTrue(any("schemaVersion must be" in error for error in errors), errors)
        self.assertTrue(any("counts.contentChanged" in error for error in errors), errors)
        self.assertTrue(any("added must be an array" in error for error in errors), errors)

    def test_manifest_diff_counts_must_match_arrays(self) -> None:
        self.write_bundle(manifest_diff=True)
        broken = self.manifest_diff()
        broken["counts"]["added"] = 1
        broken["added"] = []
        broken["counts"]["changedTotal"] = 99
        self.write_json(self.checker.MANIFEST_DIFF, broken)
        errors = self.checker.validate_bundle(self.bundle)
        self.assertTrue(any("counts.added must match added length" in error for error in errors), errors)
        self.assertTrue(any("counts.changedTotal must equal diff group sum" in error for error in errors), errors)

    def test_index_payload_summarizes_change_summary_fail_items(self) -> None:
        summary = self.change_summary_manifest()
        summary["failGroups"] = ["GENERATED_SYNC_HTML"]
        summary["failCount"] = 1
        summary["failItems"] = [
            {"group": "GENERATED_SYNC_HTML", "status": "??", "path": "outputs/ux/a.html"},
        ]
        self.write_bundle(change_summary=True)
        self.write_json(self.checker.CHANGE_SUMMARY_MANIFEST, summary)
        payload = self.checker.build_index_payload(self.bundle)
        self.assertEqual(summary["failItems"], payload["changes"]["failItems"])
        self.assertFalse(payload["gates"]["changeSummary"])
        self.assertFalse(payload["gates"]["ready"])
        self.assertEqual({"failCount": 1}, payload["gates"]["details"]["changeSummary"])

    def test_change_fail_summary_reports_blocking_items(self) -> None:
        summary = self.change_summary_manifest()
        summary["failPresets"] = ["tooling-only"]
        summary["failGroups"] = ["GENERATED_SYNC_HTML"]
        summary["failCount"] = 2
        summary["failItems"] = [
            {"group": "GENERATED_SYNC_HTML", "status": "??", "path": "outputs/ux/a.html"},
            {"group": "GENERATED_SYNC_HTML", "status": "??", "path": "outputs/ux/b.html"},
        ]
        self.write_bundle(change_summary=True)
        self.write_json(self.checker.CHANGE_SUMMARY_MANIFEST, summary)
        payload = self.checker.change_fail_summary(self.bundle, limit=1)
        self.assertIsNotNone(payload)
        assert payload is not None
        self.assertEqual(2, payload["failCount"])
        self.assertEqual(["tooling-only"], payload["failPresets"])
        self.assertEqual([{"group": "GENERATED_SYNC_HTML", "path": "outputs/ux/a.html"}], payload["failItems"])

    def test_not_ready_gates_reports_blocking_gate_names(self) -> None:
        worklist = self.worklist_manifest([self.worklist_item()])
        self.write_bundle(worklist, change_summary=True)
        summary = self.change_summary_manifest()
        summary["failGroups"] = ["GENERATED_SYNC_HTML"]
        summary["failCount"] = 1
        summary["failItems"] = [
            {"group": "GENERATED_SYNC_HTML", "status": "??", "path": "outputs/ux/a.html"},
        ]
        self.write_json(self.checker.CHANGE_SUMMARY_MANIFEST, summary)
        payload = self.checker.not_ready_gates(self.bundle)
        self.assertFalse(payload["ready"])
        self.assertEqual(["contentWorklist", "changeSummary", "generatedValidators"], payload["blocking"])
        self.assertEqual(
            [
                "contentWorklist: ERROR=0 WARN=1 TODO=0",
                "changeSummary: failCount=1",
                "generatedValidators: checked=false failureCount=0",
            ],
            payload["details"],
        )

    def test_cli_can_fail_on_change_fail_items(self) -> None:
        summary = self.change_summary_manifest()
        summary["failGroups"] = ["GENERATED_SYNC_HTML"]
        summary["failCount"] = 1
        summary["failItems"] = [
            {"group": "GENERATED_SYNC_HTML", "status": "??", "path": "outputs/ux/a.html"},
        ]
        self.write_bundle(change_summary=True)
        self.write_json(self.checker.CHANGE_SUMMARY_MANIFEST, summary)
        original_argv = sys.argv
        out = io.StringIO()
        try:
            sys.argv = [str(SCRIPT), str(self.bundle), "--fail-on-change-fail-items"]
            with redirect_stdout(out):
                rc = self.checker.main()
        finally:
            sys.argv = original_argv
        self.assertEqual(1, rc)
        self.assertIn("NOTICE change summary has blocking items", out.getvalue())
        self.assertIn("ERROR=1", out.getvalue())

    def test_cli_can_fail_on_not_ready_gates(self) -> None:
        worklist = self.worklist_manifest([self.worklist_item()])
        self.write_bundle(worklist)
        prompt = self.bundle / self.checker.PROMPTS_DIR / "刑JX001_content_prompt.md"
        prompt.write_text("# 刑JX001 内容改善セッション\n\nbody\n", encoding="utf-8")
        original_argv = sys.argv
        out = io.StringIO()
        try:
            sys.argv = [str(SCRIPT), str(self.bundle), "--fail-on-not-ready"]
            with redirect_stdout(out):
                rc = self.checker.main()
        finally:
            sys.argv = original_argv
        self.assertEqual(1, rc)
        self.assertIn("NOTICE bundle gates are not ready: contentWorklist", out.getvalue())
        self.assertIn("contentWorklist: ERROR=0 WARN=1 TODO=0", out.getvalue())
        self.assertIn("generatedValidators: checked=false failureCount=0", out.getvalue())
        self.assertIn("ERROR=1", out.getvalue())

    def test_invalid_stability_manifest_is_error(self) -> None:
        self.write_bundle(stability=True)
        broken = self.stability_manifest()
        broken["stable"] = False
        broken["changedCount"] = 1
        broken["changed"] = ["outputs/a.html"]
        self.write_json(self.checker.STABILITY_MANIFEST, broken)
        errors = self.checker.validate_bundle(self.bundle)
        self.assertTrue(any("stable must be true" in error for error in errors), errors)
        self.assertTrue(any("changedCount must be 0" in error for error in errors), errors)

    def test_invalid_stability_attempts_are_error(self) -> None:
        self.write_bundle(stability=True)
        broken = self.stability_manifest()
        broken["attempt"] = 4
        broken["attempts"] = 3
        self.write_json(self.checker.STABILITY_MANIFEST, broken)
        errors = self.checker.validate_bundle(self.bundle)
        self.assertTrue(any("attempt must be <= attempts" in error for error in errors), errors)

    def test_stability_counts_must_match_detail_arrays(self) -> None:
        self.write_bundle(stability=True)
        broken = self.stability_manifest()
        broken["changed"] = ["outputs/a.html"]
        self.write_json(self.checker.STABILITY_MANIFEST, broken)
        errors = self.checker.validate_bundle(self.bundle)
        self.assertTrue(any("changedCount must match changed length" in error for error in errors), errors)

    def test_invalid_change_summary_manifest_is_error(self) -> None:
        self.write_bundle(change_summary=True)
        broken = self.change_summary_manifest()
        broken["total"] = 99
        broken["failPresets"] = ["unknown"]
        broken["failGroups"] = ["GENERATED_SYNC_HTML"]
        broken["failCount"] = 9
        broken["groups"][0]["count"] = 42
        broken["groups"][0]["group"] = "UNKNOWN"
        self.write_json(self.checker.CHANGE_SUMMARY_MANIFEST, broken)
        errors = self.checker.validate_bundle(self.bundle)
        self.assertTrue(any("group is unknown" in error for error in errors), errors)
        self.assertTrue(any("failPresets must be an array of known presets" in error for error in errors), errors)
        self.assertTrue(any("count must match items length" in error for error in errors), errors)
        self.assertTrue(any("failCount must match selected failGroups" in error for error in errors), errors)
        self.assertTrue(any("total must match grouped item count" in error for error in errors), errors)

    def test_invalid_change_summary_fail_items_are_error(self) -> None:
        self.write_bundle(change_summary=True)
        broken = self.change_summary_manifest()
        broken["failGroups"] = ["GENERATED_SYNC_HTML"]
        broken["failCount"] = 1
        broken["failItems"] = [
            {"group": "WORK", "status": "??", "path": "work/tmp.py"},
            {"group": "GENERATED_SYNC_HTML", "status": "?", "path": ""},
        ]
        self.write_json(self.checker.CHANGE_SUMMARY_MANIFEST, broken)
        errors = self.checker.validate_bundle(self.bundle)
        self.assertTrue(any("group must be one of failGroups" in error for error in errors), errors)
        self.assertTrue(any("status must be a two-character string" in error for error in errors), errors)
        self.assertTrue(any("path must be a non-empty string" in error for error in errors), errors)
        self.assertTrue(any("failItems length must match failCount" in error for error in errors), errors)

    def test_write_bundle_index_skips_identical_content(self) -> None:
        self.write_bundle()
        path = self.checker.write_bundle_index(self.bundle)
        first = path.read_text(encoding="utf-8")
        path_again = self.checker.write_bundle_index(self.bundle)
        self.assertEqual(path, path_again)
        self.assertEqual(first, path.read_text(encoding="utf-8"))

    def test_validate_index_passes_after_write(self) -> None:
        self.write_bundle()
        self.checker.write_bundle_index(self.bundle)
        self.assertEqual([], self.checker.validate_index(self.bundle))

    def test_validate_index_detects_stale_index(self) -> None:
        self.write_bundle()
        self.checker.write_bundle_index(self.bundle)
        (self.bundle / self.checker.WORKLIST_MARKDOWN).write_text(
            "# Lexia Content Worklist\n\n- targets: 0\n- touched: yes\n",
            encoding="utf-8",
        )
        errors = self.checker.validate_index(self.bundle)
        self.assertTrue(any("stale index" in error for error in errors), errors)

    def test_missing_and_stale_prompts_are_detected(self) -> None:
        worklist = self.worklist_manifest([self.worklist_item()])
        self.write_bundle(worklist)
        (self.bundle / self.checker.PROMPTS_DIR / "stale_content_prompt.md").write_text("old", encoding="utf-8")
        errors = self.checker.validate_bundle(self.bundle)
        self.assertTrue(any("missing prompt files" in error for error in errors), errors)
        self.assertTrue(any("stale prompt files" in error for error in errors), errors)

    def test_markdown_target_count_is_checked(self) -> None:
        self.write_bundle()
        (self.bundle / self.checker.WORKLIST_MARKDOWN).write_text("# Lexia Content Worklist\n\n- targets: 99\n", encoding="utf-8")
        errors = self.checker.validate_bundle(self.bundle)
        self.assertTrue(any("missing target count line" in error for error in errors), errors)

    def test_prompt_filename_for_target_matches_worklist_generator(self) -> None:
        self.assertEqual("刑JX001_content_prompt.md", self.checker.prompt_filename_for_target("刑JX001"))
        self.assertEqual("A_B_content_prompt.md", self.checker.prompt_filename_for_target("A/B"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
