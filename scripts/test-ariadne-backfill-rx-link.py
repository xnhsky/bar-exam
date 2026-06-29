#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ariadne-backfill-rx-link.py の軽量 self-test。"""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().with_name("ariadne-backfill-rx-link.py")


def load_module():
    spec = importlib.util.spec_from_file_location("ariadne_backfill_rx_link", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class AriadneBackfillRxLinkTest(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = load_module()

    def test_is_recall_tag_accepts_single_quoted_multi_class(self) -> None:
        tag = "<div class='card self-check-quiz' data-recall='1'>"
        self.assertTrue(self.mod.is_recall_tag(tag))
        self.assertFalse(self.mod.is_recall_tag("<div class='card self-check-quiz'>"))
        self.assertFalse(self.mod.is_recall_tag("<div class='card not-self-check-quiz' data-recall='1'>"))

    def test_stamp_data_rx_inserts_after_data_recall_with_quote_variants(self) -> None:
        stamped, changed = self.mod.stamp_data_rx(
            "<div class='self-check-quiz' data-recall='1' data-kind='x'>",
            "刑RX001_1",
        )
        self.assertTrue(changed)
        self.assertIn("data-recall='1' data-rx=\"刑RX001_1\" data-kind='x'", stamped)

    def test_stamp_data_rx_skips_existing_data_rx(self) -> None:
        tag = "<div class='self-check-quiz' data-recall='1' data-rx='刑RX001_1'>"
        stamped, changed = self.mod.stamp_data_rx(tag, "刑RX001_2")
        self.assertFalse(changed)
        self.assertEqual(tag, stamped)

    def test_open_replacement_only_counts_recall_cards(self) -> None:
        html = (
            "<div class='self-check-quiz' data-recall='1'></div>"
            "<div class='self-check-quiz'></div>"
            "<div class='other' data-recall='1'></div>"
        )
        tags = self.mod.recall_tags_in_html(html)
        self.assertEqual(["<div class='self-check-quiz' data-recall='1'>"], tags)

    def test_unmapped_rx_status_counts_missing_direct_links(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "刑JX999_ARIADNE.html"
            path.write_text(
                "<div class='self-check-quiz' data-recall='1' data-rx='刑RX999_1'></div>"
                "<div class='self-check-quiz' data-recall='1'></div>",
                encoding="utf-8",
            )
            self.assertEqual((2, 1), self.mod.unmapped_rx_status(str(path)))

            path.write_text(
                "<div class='self-check-quiz' data-recall='1' data-rx='刑RX999_1'></div>",
                encoding="utf-8",
            )
            self.assertEqual((1, 0), self.mod.unmapped_rx_status(str(path)))


if __name__ == "__main__":
    unittest.main(verbosity=2)
