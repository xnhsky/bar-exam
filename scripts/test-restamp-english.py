#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""restamp-english.py の軽量 self-test。"""
from __future__ import annotations

import importlib.util
import types
import sys
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().with_name("restamp-english.py")


def load_module():
    spec = importlib.util.spec_from_file_location("restamp_english", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class RestampEnglishTest(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = load_module()

    def test_determine_dt_preserves_single_quoted_genmeta(self) -> None:
        html = "<p class='footer-date lexia-genmeta' data-generated='2026-06-28T10:11+09:00'>Generated</p>"
        dt = self.mod.determine_dt("outputs/001_JX/001_刑法/刑JX001.html", html, {})
        self.assertEqual(datetime(2026, 6, 28, 10, 11, tzinfo=self.mod.JST), dt)

    def test_determine_dt_reads_single_quoted_native_footer_date(self) -> None:
        html = "<p class='small footer-date muted'>作成日：2026-01-02 ／ old</p>"
        dt = self.mod.determine_dt("outputs/001_JX/001_刑法/刑JX001.html", html, {})
        self.assertEqual(datetime(2026, 1, 2, 12, 0, tzinfo=self.mod.JST), dt)

    def test_tx_add_map_takes_priority_over_existing_footer(self) -> None:
        add_dt = datetime(2026, 3, 4, 5, 6, tzinfo=self.mod.JST)
        html = "<p class='footer-date lexia-genmeta' data-generated='2026-06-28T10:11+09:00'>Generated</p>"
        dt = self.mod.determine_dt("outputs/000_TX/001_刑法/刑TX001.html", html, {"outputs/000_TX/001_刑法/刑TX001.html": add_dt})
        self.assertEqual(add_dt, dt)

    def test_build_add_date_map_reads_git_log_as_utf8(self) -> None:
        stdout = "@2026-06-28T10:11:00+09:00\noutputs/001_JX/001_刑法/刑JX001.html\n"

        def fake_run(_cmd, **kwargs):
            self.assertEqual("utf-8", kwargs.get("encoding"))
            self.assertEqual("replace", kwargs.get("errors"))
            return types.SimpleNamespace(stdout=stdout)

        with patch.object(self.mod.subprocess, "run", side_effect=fake_run):
            add_map = self.mod.build_add_date_map()
        self.assertEqual(datetime(2026, 6, 28, 10, 11, tzinfo=self.mod.JST), add_map["outputs/001_JX/001_刑法/刑JX001.html"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
