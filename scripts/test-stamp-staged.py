#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Lightweight self-test for stamp-staged.py."""
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().with_name("stamp-staged.py")


def load_module():
    spec = importlib.util.spec_from_file_location("stamp_staged", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class StampStagedTest(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = load_module()

    def test_parse_intent_to_add_stage_filters_empty_blob_and_lexia_html(self) -> None:
        out = (
            "100644 e69de29bb2d1d6434b8b29ae775ad8c2e48c5391 0\toutputs/ux/001_ARIADNE/001_刑法/刑JX019_ARIADNE.html\0"
            "100644 0123456789abcdef0123456789abcdef01234567 0\toutputs/ux/001_ARIADNE/001_刑法/刑JX020_ARIADNE.html\0"
            "100644 e69de29bb2d1d6434b8b29ae775ad8c2e48c5391 0\tdocs/not-sync.html\0"
            "100644 e69de29bb2d1d6434b8b29ae775ad8c2e48c5391 0\toutputs/ux/notes.txt\0"
        )
        self.assertEqual(
            ["outputs/ux/001_ARIADNE/001_刑法/刑JX019_ARIADNE.html"],
            self.mod.parse_intent_to_add_stage(out),
        )

    def test_merge_staged_paths_dedupes_preserving_order(self) -> None:
        cached = ["outputs/001_JX/001_刑法/刑JX001.html"]
        intent = [
            "outputs/001_JX/001_刑法/刑JX001.html",
            "outputs/ux/003_TREE/001_刑法/刑JX001_TREE.html",
        ]
        self.assertEqual(
            [
                "outputs/001_JX/001_刑法/刑JX001.html",
                "outputs/ux/003_TREE/001_刑法/刑JX001_TREE.html",
            ],
            self.mod.merge_staged_paths(cached, intent),
        )

    def test_imported_genmeta_checker_requires_real_stamp(self) -> None:
        self.assertFalse(self.mod.has_genmeta_stamp('<script>const x = "lexia-genmeta";</script>'))
        self.assertTrue(self.mod.has_genmeta_stamp('<p class="footer-date lexia-genmeta">Generated: x</p>'))


if __name__ == "__main__":
    unittest.main(verbosity=2)
