#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""lexia-content-worklist.py の軽量 self-test。"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


WORKLIST_SCRIPT = Path(__file__).resolve().with_name("lexia-content-worklist.py")
CONTRACT_SCRIPT = Path(__file__).resolve().with_name("check-lexia-sync-contract.py")


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class LexiaContentWorklistTest(unittest.TestCase):
    def setUp(self) -> None:
        self.worklist = load_module("lexia_content_worklist", WORKLIST_SCRIPT)
        self.contract = load_module("check_lexia_sync_contract", CONTRACT_SCRIPT)

    def test_rx_file_maps_to_parent_jx_target(self) -> None:
        target = self.worklist.target_from_path_or_message(
            self.contract,
            "outputs/ux/002_RX/001_刑法/刑JX057/刑RX057_1.html",
        )
        self.assertEqual("刑JX057", target)

    def test_kjx_file_maps_to_kjx_target(self) -> None:
        target = self.worklist.target_from_path_or_message(
            self.contract,
            "outputs/005_KJX/001_刑法/刑KJX001.html",
        )
        self.assertEqual("刑KJX001", target)

    def test_quarantined_jx_gets_generated_artifact_validators(self) -> None:
        validators = self.worklist.inferred_validators_for_target(
            self.contract,
            "刑JX020",
            "outputs/001_JX/001_刑法/_failed/刑JX020_bad-topic_20260628.html",
        )
        self.assertIn(r"python scripts\validate-jx.py outputs\001_JX\001_刑法\刑JX020.html", validators)
        self.assertIn(r"python scripts\validate-ariadne.py outputs\ux\001_ARIADNE\001_刑法\刑JX020_ARIADNE.html", validators)
        self.assertIn(r"python scripts\validate-tree.py outputs\ux\003_TREE\001_刑法\刑JX020_TREE.html", validators)
        self.assertEqual(self.worklist.CONTENT_PREFLIGHT_CMD, validators[-1])

    def test_quarantined_tx_gets_official_and_lexia_validators(self) -> None:
        validators = self.worklist.inferred_validators_for_target(
            self.contract,
            "刑TX045",
            "outputs/000_TX/001_刑法/_failed/刑TX045_failed_20260524-004650.html",
        )
        self.assertIn(r"python scripts\validate-tx.py outputs\000_TX\001_刑法\刑TX045.html", validators)
        self.assertIn(r"python scripts\validate-tx-core.py outputs\ux\000_TX\001_刑法\刑TX045_lex.html", validators)
        self.assertEqual(self.worklist.CONTENT_PREFLIGHT_CMD, validators[-1])

    def test_collect_failed_items_scans_only_quarantine_html(self) -> None:
        old_root = self.worklist.ROOT
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            failed = root / "outputs" / "000_TX" / "001_刑法" / "_failed" / "刑TX045_failed.html"
            failed.parent.mkdir(parents=True)
            failed.write_text("<html></html>", encoding="utf-8")
            ok = root / "outputs" / "000_TX" / "001_刑法" / "刑TX045.html"
            ok.write_text("<html></html>", encoding="utf-8")
            notes = failed.with_suffix(".txt")
            notes.write_text("ignore", encoding="utf-8")
            try:
                self.worklist.ROOT = root
                items = self.worklist.collect_failed_items(self.contract)
            finally:
                self.worklist.ROOT = old_root

        self.assertEqual(1, len(items))
        item = items[0]
        self.assertEqual("刑TX045", item.target)
        self.assertEqual("TODO", item.severity)
        self.assertEqual("QUARANTINED", item.kind)
        self.assertEqual("outputs/000_TX/001_刑法/_failed/刑TX045_failed.html", item.path)
        self.assertIn(r"python scripts\validate-tx.py outputs\000_TX\001_刑法\刑TX045.html", item.validators)

    def test_prompt_contains_scope_and_preflight_last(self) -> None:
        items = [
            self.worklist.WorkItem(
                target="刑JX019",
                severity="WARN",
                kind="MISSING",
                category="JX",
                path="outputs/001_JX/001_刑法/刑JX019.html",
                message="JX 対応 ARIADNE 欠落",
                action="対応 ARIADNE を生成/復元し、data-athena-code と data-rx を確認",
                validators=[
                    r"python scripts\validate-jx.py outputs\001_JX\001_刑法\刑JX019.html",
                    r"python scripts\validate-ariadne.py outputs\ux\001_ARIADNE\001_刑法\刑JX019_ARIADNE.html",
                    self.worklist.CONTENT_PREFLIGHT_CMD,
                ],
            ),
        ]
        prompt = self.worklist.render_prompt(self.contract, "刑JX019", items)
        self.assertIn(r"outputs/ux/001_ARIADNE/001_刑法/刑JX019_ARIADNE.html", prompt)
        self.assertIn("scripts/ は原則触らない", prompt)
        self.assertLess(
            prompt.index(r"python scripts\validate-ariadne.py"),
            prompt.index(self.worklist.CONTENT_PREFLIGHT_CMD),
        )

    def test_filter_targets_keeps_only_requested_target(self) -> None:
        items = [
            self.worklist.WorkItem("刑JX019", "WARN", "MISSING", "JX", "", "JX 対応 TREE 欠落", "a", []),
            self.worklist.WorkItem("刑JX020", "TODO", "QUARANTINED", "FAILED", "", "隔離済み HTML が残っている", "b", []),
        ]
        filtered = self.worklist.filter_targets(items, ["刑JX020"])
        self.assertEqual(["刑JX020"], [item.target for item in filtered])

    def test_failing_items_respects_severity_threshold(self) -> None:
        items = [
            self.worklist.WorkItem("刑JX001", "ERROR", "FILE", "JX", "", "error", "a", []),
            self.worklist.WorkItem("刑JX002", "WARN", "MISSING", "JX", "", "warn", "b", []),
            self.worklist.WorkItem("刑JX003", "TODO", "QUARANTINED", "FAILED", "", "todo", "c", []),
        ]
        self.assertEqual(["ERROR"], [i.severity for i in self.worklist.failing_items(items, "error")])
        self.assertEqual(["ERROR", "WARN"], [i.severity for i in self.worklist.failing_items(items, "warn")])
        self.assertEqual(["ERROR", "WARN", "TODO"], [i.severity for i in self.worklist.failing_items(items, "any")])

    def test_duplicate_data_rx_action_points_to_rx_assignment(self) -> None:
        action = self.worklist.action_for("FILE", "data-rx 重複 1 件: 刑RX001_1")
        self.assertIn("data-rx 割当", action)

    def test_markdown_is_stable_by_default(self) -> None:
        items = [
            self.worklist.WorkItem("刑JX001", "WARN", "MISSING", "JX", "", "warn", "a", []),
        ]
        md = self.worklist.render_markdown(self.contract, items)
        self.assertNotIn("- generated:", md)
        stamped = self.worklist.render_markdown(self.contract, items, generated_at="2026-06-28T00:00:00+09:00")
        self.assertIn("- generated: 2026-06-28T00:00:00+09:00", stamped)

    def test_write_text_if_changed_skips_identical_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "worklist.md"
            self.assertTrue(self.worklist.write_text_if_changed(path, "one\n"))
            self.assertFalse(self.worklist.write_text_if_changed(path, "one\n"))
            self.assertTrue(self.worklist.write_text_if_changed(path, "two\n"))
            self.assertEqual("two\n", path.read_text(encoding="utf-8"))

    def test_json_manifest_is_schema_versioned_and_stable(self) -> None:
        items = [
            self.worklist.WorkItem("刑JX002", "TODO", "QUARANTINED", "FAILED", "b.html", "todo", "b", []),
            self.worklist.WorkItem("刑JX001", "WARN", "FILE", "ARIADNE", "a.html", "warn", "a", ["v"]),
        ]
        items = sorted(items, key=lambda item: self.worklist.priority_key(self.contract, item))
        payload = self.worklist.build_worklist_payload(self.contract, ["outputs", "references"], items)
        self.assertEqual(self.worklist.SCHEMA_VERSION, payload["schemaVersion"])
        self.assertEqual(["schemaVersion", "roots", "filters", "targets", "counts", "categories", "kinds", "items"], list(payload.keys()))
        self.assertEqual({"target": [], "includeFailed": True}, payload["filters"])
        self.assertEqual({"ERROR": 0, "WARN": 1, "TODO": 1}, payload["counts"])
        self.assertEqual(["target", "severity", "kind", "category", "path", "message", "action", "validators"], list(payload["items"][0].keys()))
        self.assertNotIn("generatedAt", payload)
        dumped = json.dumps(payload, ensure_ascii=False, indent=2)
        self.assertEqual(dumped, json.dumps(self.worklist.build_worklist_payload(self.contract, ["outputs", "references"], items), ensure_ascii=False, indent=2))

    def test_json_manifest_records_filters(self) -> None:
        items = [self.worklist.WorkItem("刑JX001", "WARN", "FILE", "ARIADNE", "", "warn", "a", [])]
        payload = self.worklist.build_worklist_payload(
            self.contract,
            ["outputs"],
            items,
            target_filter=["刑JX001", "刑JX001", ""],
            include_failed=False,
        )
        self.assertEqual({"target": ["刑JX001"], "includeFailed": False}, payload["filters"])

    def test_json_format_requires_json_path(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(WORKLIST_SCRIPT), "--json-format", "manifest", "--quiet"],
            cwd=WORKLIST_SCRIPT.parents[1],
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
        )
        self.assertEqual(2, completed.returncode)
        self.assertIn("--json-format", completed.stderr)

    def test_write_prompts_creates_one_file_per_target(self) -> None:
        items = [
            self.worklist.WorkItem(
                target="刑JX020",
                severity="TODO",
                kind="QUARANTINED",
                category="FAILED",
                path="outputs/001_JX/001_刑法/_failed/刑JX020_bad-topic_20260628.html",
                message="隔離済み HTML が残っている",
                action="隔離理由を確認し、正規出力は生成パイプラインから再生成",
                validators=[self.worklist.CONTENT_PREFLIGHT_CMD],
            )
        ]
        with tempfile.TemporaryDirectory() as tmp:
            stale = Path(tmp) / "刑JX999_content_prompt.md"
            stale.write_text("stale", encoding="utf-8")
            unrelated = Path(tmp) / "notes.md"
            unrelated.write_text("keep", encoding="utf-8")
            written = self.worklist.write_prompts(self.contract, items, Path(tmp))
            self.assertEqual(1, len(written))
            self.assertEqual("刑JX020_content_prompt.md", written[0].name)
            self.assertIn("刑JX020 内容改善セッション", written[0].read_text(encoding="utf-8"))
            self.assertFalse(stale.exists())
            self.assertTrue(unrelated.exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
