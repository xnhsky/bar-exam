#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check-lexia-sync-contract.py の軽量 self-test。

外部 test runner なしで実行できるよう、標準 unittest と一時ディレクトリだけを使う。
Lexia 同期で壊れやすい分類・欠落・data-rx dangling の代表ケースを固定する。
"""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
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
    filler = " ".join(["本文"] * 1300)
    return f"""<!doctype html>
<html lang="ja">
<head><meta charset="utf-8"><title>{title}</title></head>
<body>
<main>{filler}</main>
{body}
<footer class="lexia-genmeta" data-generated="2026-06-28T00:00:00+09:00">Generated: 2026-06-28</footer>
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


if __name__ == "__main__":
    unittest.main(verbosity=2)
