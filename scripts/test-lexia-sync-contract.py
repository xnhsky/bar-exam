#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check-lexia-sync-contract.py の軽量 self-test。

外部 test runner なしで実行できるよう、標準 unittest と一時ディレクトリだけを使う。
Lexia 同期で壊れやすい分類・欠落・data-rx dangling の代表ケースを固定する。
"""
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path


SCRIPT = Path(__file__).resolve().with_name("check-lexia-sync-contract.py")


def load_contract_module():
    spec = importlib.util.spec_from_file_location("check_lexia_sync_contract", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def html(title: str, body: str = "") -> str:
    filler = " ".join(["本文"] * 4000)
    return f"""<!doctype html>
<html lang="ja">
<head><meta charset="utf-8"><title>{title}</title></head>
<body>
<main>{filler}</main>
{body}
<footer class="lexia-genmeta" data-generated="2026-06-28T00:00:00+09:00">Generated: 2026-06-28 00:00</footer>
</body>
</html>
"""


class LexiaSyncContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = load_contract_module()
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.old_root = self.mod.ROOT
        self.mod.ROOT = self.root

    def tearDown(self) -> None:
        self.mod.ROOT = self.old_root
        self.tmp.cleanup()

    def write(self, rel: str, text: str) -> Path:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def test_classifies_core_lexia_categories(self) -> None:
        cases = {
            "outputs/000_TX/001_刑法/刑TX001.html": ("TX_OFFICIAL", "刑TX001", "刑法"),
            "outputs/ux/000_TX/001_刑法/刑TX001_lex.html": ("TX_LEXIA", "刑TX001_lex", "刑法"),
            "outputs/001_JX/001_刑法/刑JX001.html": ("JX", "刑JX001", "刑法"),
            "outputs/ux/001_ARIADNE/001_刑法/刑JX001_ARIADNE.html": ("ARIADNE", "刑JX001_ARIADNE", "刑法"),
            "outputs/ux/003_TREE/001_刑法/刑JX001_TREE.html": ("TREE", "刑JX001_TREE", "刑法"),
            "outputs/ux/002_RX/001_刑法/刑JX001/刑RX001_1.html": ("RX", "刑RX001_1", "刑法"),
            "outputs/005_KJX/001_刑法/刑KJX001.html": ("KJX", "刑KJX001", "刑法"),
        }
        for rel, expected in cases.items():
            with self.subTest(rel=rel):
                path = self.write(rel, html(Path(rel).stem))
                meta, warnings = self.mod.classify(path)
                self.assertEqual([], warnings)
                self.assertIsNotNone(meta)
                self.assertEqual(expected[0], meta["category"])
                self.assertEqual(expected[1], meta["code"])
                self.assertEqual(expected[2], meta["subject"])

    def test_code_key_supports_kjx(self) -> None:
        self.assertEqual(("刑", "KJX", 1, None), self.mod.code_key("刑KJX001"))

    def test_ariadne_dangling_data_rx_is_error(self) -> None:
        path = self.write(
            "outputs/ux/001_ARIADNE/001_刑法/刑JX001_ARIADNE.html",
            html("刑JX001 ARIADNE", '<div class="self-check-quiz" data-recall="1" data-rx="刑RX001_1"></div>'),
        )
        _entry, errors, _warnings = self.mod.audit_entry(path)
        self.assertTrue(any("data-rx 参照先 RX 不在" in e for e in errors), errors)

    def test_ariadne_existing_data_rx_passes(self) -> None:
        self.write("outputs/ux/002_RX/001_刑法/刑JX001/刑RX001_1.html", html("刑RX001_1"))
        path = self.write(
            "outputs/ux/001_ARIADNE/001_刑法/刑JX001_ARIADNE.html",
            html("刑JX001 ARIADNE", '<div class="self-check-quiz" data-recall="1" data-rx="刑RX001_1"></div>'),
        )
        _entry, errors, _warnings = self.mod.audit_entry(path)
        self.assertFalse(any("data-rx 参照先 RX 不在" in e for e in errors), errors)

    def test_ariadne_single_quoted_attrs_are_parsed(self) -> None:
        self.write("outputs/ux/002_RX/001_刑法/刑JX001/刑RX001_1.html", html("刑RX001_1"))
        path = self.write(
            "outputs/ux/001_ARIADNE/001_刑法/刑JX001_ARIADNE.html",
            html(
                "刑JX001 ARIADNE",
                """
                <a class='go-athena' data-athena-code='刑JX001'>ATHENA</a>
                <div class='quiz self-check-quiz' data-recall='1' data-rx='刑RX001_1'></div>
                """,
            ),
        )
        _entry, errors, _warnings = self.mod.audit_entry(path)
        self.assertFalse(any("data-athena-code" in e for e in errors), errors)
        self.assertFalse(any("data-rx 参照先 RX 不在" in e for e in errors), errors)

    def test_ariadne_duplicate_data_rx_is_warning(self) -> None:
        self.write("outputs/ux/002_RX/001_刑法/刑JX001/刑RX001_1.html", html("刑RX001_1"))
        path = self.write(
            "outputs/ux/001_ARIADNE/001_刑法/刑JX001_ARIADNE.html",
            html(
                "刑JX001 ARIADNE",
                """
                <a class="go-athena" data-athena-code="刑JX001">ATHENA</a>
                <div class="self-check-quiz" data-recall="1" data-rx="刑RX001_1"></div>
                <div class="self-check-quiz" data-recall="1" data-rx="刑RX001_1"></div>
                """,
            ),
        )
        _entry, errors, warnings = self.mod.audit_entry(path)
        self.assertFalse(errors, errors)
        self.assertTrue(any("data-rx 重複" in w for w in warnings), warnings)

    def test_intentional_none_data_rx_is_not_warning(self) -> None:
        self.mod.ARIADNE_RX_MAP = {"刑JX001_ARIADNE.html": [None, "刑RX001_1"]}
        self.write("outputs/ux/002_RX/001_刑法/刑JX001/刑RX001_1.html", html("刑RX001_1"))
        path = self.write(
            "outputs/ux/001_ARIADNE/001_刑法/刑JX001_ARIADNE.html",
            html(
                "刑JX001 ARIADNE",
                """
                <div class="self-check-quiz" data-recall="1"></div>
                <div class="self-check-quiz" data-recall="1" data-rx="刑RX001_1"></div>
                """,
            ),
        )
        _entry, _errors, warnings = self.mod.audit_entry(path)
        self.assertFalse(any("data-rx 欠落" in w for w in warnings), warnings)

    def test_find_untracked_sync_files_uses_repo_relative_paths(self) -> None:
        tracked = {"outputs/001_JX/001_刑法/刑JX001.html"}
        paths = [
            self.root / "outputs/001_JX/001_刑法/刑JX001.html",
            self.root / "outputs/ux/001_ARIADNE/001_刑法/刑JX001_ARIADNE.html",
        ]
        self.assertEqual(
            ["outputs/ux/001_ARIADNE/001_刑法/刑JX001_ARIADNE.html"],
            self.mod.find_untracked_sync_files(paths, tracked),
        )
        self.assertEqual([], self.mod.find_untracked_sync_files(paths, None))

    def test_git_stage_parser_excludes_intent_to_add_empty_blob(self) -> None:
        output = (
            b"100644 e69de29bb2d1d6434b8b29ae775ad8c2e48c5391 0\toutputs/new.html\0"
            b"100644 0123456789abcdef0123456789abcdef01234567 0\toutputs/tracked.html\0"
        )
        self.assertEqual({"outputs/tracked.html"}, self.mod.parse_git_stage_paths(output))

    def test_display_path_handles_repo_external_json_targets(self) -> None:
        inside = self.root / "deploy" / "audit.json"
        outside = self.root.parent / "audit.json"
        self.assertEqual("deploy/audit.json", self.mod.display_path(inside))
        self.assertEqual(str(outside.resolve()), self.mod.display_path(outside))

    def test_generated_footer_requires_iso_tz_and_matching_display(self) -> None:
        valid = '<p class="footer-date lexia-genmeta" data-generated="2026-06-28T10:11+09:00">Generated: 2026-06-28 10:11 / JX</p>'
        problems, generated = self.mod.genmeta_status(valid)
        self.assertEqual([], problems)
        self.assertEqual("2026-06-28T10:11+09:00", generated)

        single_quoted = "<p class='footer-date lexia-genmeta' data-generated='2026-06-28T10:11+09:00'>Generated: 2026-06-28 10:11 / JX</p>"
        problems, generated = self.mod.genmeta_status(single_quoted)
        self.assertEqual([], problems)
        self.assertEqual("2026-06-28T10:11+09:00", generated)

        bad_format = '<p class="footer-date lexia-genmeta" data-generated="2026/06/28 10:11">Generated: 2026-06-28 10:11 / JX</p>'
        problems, _generated = self.mod.genmeta_status(bad_format)
        self.assertTrue(any("ISO8601+TZ" in p for p in problems), problems)

        mismatch = '<p class="footer-date lexia-genmeta" data-generated="2026-06-28T10:11+09:00">Generated: 2026-06-28 10:12 / JX</p>'
        problems, _generated = self.mod.genmeta_status(mismatch)
        self.assertTrue(any("表示日時" in p for p in problems), problems)

        duplicate_generated = (
            '<p class="footer-date lexia-genmeta" data-generated="2026-06-28T10:11+09:00" '
            'data-generated="2026-06-28T10:12+09:00">Generated: 2026-06-28 10:11 / JX</p>'
        )
        problems, _generated = self.mod.genmeta_status(duplicate_generated)
        self.assertTrue(any("data-generated が複数" in p for p in problems), problems)

    def test_stable_hash_ignores_generated_timestamp_only(self) -> None:
        first = html("刑JX001").replace("2026-06-28T00:00:00+09:00", "2026-06-28T10:11+09:00").replace(
            "2026-06-28 00:00", "2026-06-28 10:11"
        )
        second = html("刑JX001").replace("2026-06-28T00:00:00+09:00", "2026-06-29T12:34+09:00").replace(
            "2026-06-28 00:00", "2026-06-29 12:34"
        )
        changed = second.replace("刑JX001", "刑JX002", 1)
        self.assertEqual(self.mod.stable_content_sha256(first), self.mod.stable_content_sha256(second))
        self.assertNotEqual(self.mod.stable_content_sha256(first), self.mod.stable_content_sha256(changed))

    def test_json_manifest_is_schema_versioned_and_stable(self) -> None:
        entries = [
            self.mod.Entry(
                sourcePath="outputs/b.html",
                fileName="b.html",
                code="刑JX002",
                baseCode="刑JX002",
                title="刑JX002",
                subject="刑法",
                subjectDir="001_刑法",
                category="JX",
                bytes=20,
                textLength=12,
                stableSha256="b" * 64,
                generated="2026-06-28T00:00+09:00",
            ),
            self.mod.Entry(
                sourcePath="outputs/a.html",
                fileName="a.html",
                code="刑JX001",
                baseCode="刑JX001",
                title="刑JX001",
                subject="刑法",
                subjectDir="001_刑法",
                category="JX",
                bytes=10,
                textLength=10,
                stableSha256="a" * 64,
                generated="2026-06-28T00:00+09:00",
            ),
        ]
        payload = self.mod.build_manifest_payload(
            roots=["outputs", "references"],
            files_count=2,
            entries=entries,
            category_counts=Counter({"JX": 2}),
            error_count=0,
            warning_count=0,
        )
        self.assertEqual(self.mod.SCHEMA_VERSION, payload["schemaVersion"])
        self.assertNotIn("generatedAt", payload)
        self.assertEqual(["outputs/a.html", "outputs/b.html"], [e["sourcePath"] for e in payload["entries"]])
        self.assertEqual(list(self.mod.ENTRY_JSON_FIELDS), list(payload["entries"][0].keys()))
        self.assertEqual(10, payload["entries"][0]["textLength"])
        self.assertEqual("a" * 64, payload["entries"][0]["stableSha256"])
        dumped = json.dumps(payload, ensure_ascii=False, indent=2)
        dumped_again = json.dumps(
            self.mod.build_manifest_payload(
                roots=["outputs", "references"],
                files_count=2,
                entries=entries,
                category_counts=Counter({"JX": 2}),
                error_count=0,
                warning_count=0,
            ),
            ensure_ascii=False,
            indent=2,
        )
        self.assertEqual(dumped, dumped_again)

    def test_low_text_entries_are_stably_sorted(self) -> None:
        entries = [
            self.mod.Entry(
                sourcePath="outputs/c.html",
                fileName="c.html",
                code="刑JX003",
                baseCode="刑JX003",
                title="刑JX003",
                subject="刑法",
                subjectDir="001_刑法",
                category="JX",
                bytes=1000,
                textLength=100,
                stableSha256="c" * 64,
                generated="2026-06-28T00:00+09:00",
            ),
            self.mod.Entry(
                sourcePath="outputs/a.html",
                fileName="a.html",
                code="刑JX001",
                baseCode="刑JX001",
                title="刑JX001",
                subject="刑法",
                subjectDir="001_刑法",
                category="JX",
                bytes=10000,
                textLength=100,
                stableSha256="a" * 64,
                generated="2026-06-28T00:00+09:00",
            ),
            self.mod.Entry(
                sourcePath="outputs/b.html",
                fileName="b.html",
                code="刑JX002",
                baseCode="刑JX002",
                title="刑JX002",
                subject="刑法",
                subjectDir="001_刑法",
                category="JX",
                bytes=1000,
                textLength=50,
                stableSha256="b" * 64,
                generated="2026-06-28T00:00+09:00",
            ),
        ]
        self.assertEqual(
            ["outputs/b.html", "outputs/a.html"],
            [entry.sourcePath for entry in self.mod.low_text_entries(entries, 2)],
        )

    def test_write_text_if_changed_skips_identical_content(self) -> None:
        path = self.root / "audit.json"
        self.assertTrue(self.mod.write_text_if_changed(path, "one\n"))
        self.assertFalse(self.mod.write_text_if_changed(path, "one\n"))
        self.assertTrue(self.mod.write_text_if_changed(path, "two\n"))
        self.assertEqual("two\n", path.read_text(encoding="utf-8"))

    def test_audit_roots_counts_global_missing_sidecar_warnings(self) -> None:
        self.write("outputs/001_JX/001_刑法/刑JX001.html", html("刑JX001"))
        result = self.mod.audit_roots(["outputs"], allow_untracked_sync_artifacts=True)
        self.assertEqual(1, len(result.entries))
        self.assertEqual(0, result.error_count)
        self.assertEqual(2, result.warning_count)
        self.assertTrue(any("JX 対応 ARIADNE 欠落" in msg for msg in result.global_warnings), result.global_warnings)
        self.assertTrue(any("JX 対応 TREE 欠落" in msg for msg in result.global_warnings), result.global_warnings)


if __name__ == "__main__":
    unittest.main(verbosity=2)
