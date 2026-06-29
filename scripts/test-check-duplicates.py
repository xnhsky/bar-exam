#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check-duplicates.py の軽量 self-test。"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().with_name("check-duplicates.py")


def load_module():
    spec = importlib.util.spec_from_file_location("check_duplicates", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def html(title: str, body: str = "", footer_code: str | None = None) -> str:
    footer = ""
    if footer_code:
        footer = f"<p class='footer-problem extra'><strong>{footer_code}</strong></p>"
    return f"""<!doctype html>
<html lang="ja">
<head><meta charset="utf-8"><title>{title}</title></head>
<body>
<main>{body or "本文"}</main>
<div class='unit doc-header'>{title}</div>
{footer}
<p class="footer-date lexia-genmeta" data-generated="2026-06-28T00:00+09:00">Generated: 2026-06-28 00:00</p>
</body>
</html>
"""


class CheckDuplicatesTest(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = load_module()
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

    def check_root(self) -> tuple[int, str]:
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            errors = self.mod.check_root(str(self.root))
        return errors, out.getvalue()

    def test_code_key_distinguishes_kjx_from_jx(self) -> None:
        self.assertEqual(("刑", "KJX", 1, None), self.mod.code_key("刑KJX001.html"))
        self.assertNotEqual(self.mod.code_key("刑KJX001.html"), self.mod.code_key("刑JX001.html"))

    def test_collect_files_resolves_relative_roots_from_repo_root(self) -> None:
        path = self.write("outputs/001_JX/001_刑法/刑JX001.html", html("刑JX001"))
        self.assertEqual([path], self.mod.collect_files("outputs"))

    def test_code_key_normalizes_rx_branch_separator_and_zero_padding(self) -> None:
        self.assertTrue(
            self.mod.same_code_key(
                self.mod.code_key("刑RX001_1.html"),
                self.mod.code_key("RX001-01"),
            )
        )
        self.assertFalse(
            self.mod.same_code_key(
                self.mod.code_key("刑RX001_1.html"),
                self.mod.code_key("刑RX001_2"),
            )
        )

    def test_code_key_detects_subject_mismatch_when_both_sides_have_prefix(self) -> None:
        self.assertFalse(
            self.mod.same_code_key(
                self.mod.code_key("刑TX001.html"),
                self.mod.code_key("民TX001"),
            )
        )

    def test_code_near_class_accepts_multi_class_and_single_quotes(self) -> None:
        sample = "<div class='alpha doc-header beta'><span>刑TX001</span></div>"
        self.assertEqual(("刑", "TX", 1, None), self.mod.code_near_class(sample, "doc-header"))

    def test_kjx_file_with_jx_header_is_mismatch(self) -> None:
        self.write("刑KJX001.html", html("刑JX001", footer_code="刑JX001"))
        errors, output = self.check_root()
        self.assertGreaterEqual(errors, 1, output)
        self.assertIn("ID-MISMATCH", output)
        self.assertIn("file=刑KJX1", output)

    def test_rx_branch_mismatch_is_mismatch(self) -> None:
        self.write("刑RX001_1.html", html("RX recall", footer_code="刑RX001-2"))
        errors, output = self.check_root()
        self.assertGreaterEqual(errors, 1, output)
        self.assertIn("footer=刑RX1_2", output)

    def test_stable_body_digest_ignores_lexia_genmeta_timestamp_only(self) -> None:
        one = html("刑TX001").replace("2026-06-28T00:00+09:00", "2026-06-28T00:00+09:00")
        two = html("刑TX001").replace("2026-06-28T00:00+09:00", "2026-06-29T12:34+09:00").replace(
            "Generated: 2026-06-28 00:00",
            "Generated: 2026-06-29 12:34",
        )
        self.assertEqual(self.mod.stable_body_digest(one), self.mod.stable_body_digest(two))


if __name__ == "__main__":
    unittest.main()
