#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Lightweight self-test for stamp_footer.py."""
from __future__ import annotations

import importlib.util
import sys
import unittest
from datetime import datetime
from pathlib import Path


SCRIPT = Path(__file__).resolve().with_name("stamp_footer.py")


def load_module():
    spec = importlib.util.spec_from_file_location("stamp_footer", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class StampFooterTest(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = load_module()
        self.dt = datetime(2026, 6, 28, 10, 11, tzinfo=self.mod.JST)

    def test_existing_genmeta_is_collapsed_to_one_stamp(self) -> None:
        html = """<!doctype html>
<html><body>
<p class="footer-date lexia-genmeta" data-generated="2026-01-01T00:00+09:00">Generated: 2026-01-01 00:00 / old</p>
<main>body</main>
<p class="footer-date lexia-genmeta" data-generated="2026-01-02T00:00+09:00">Generated: 2026-01-02 00:00 / old</p>
</body></html>
"""
        out = self.mod.stamp_html(html, self.dt, "JX v4.0.0 LOOP-FOLD")
        self.assertEqual(1, out.count("lexia-genmeta"))
        self.assertIn('data-generated="2026-06-28T10:11+09:00"', out)
        self.assertIn("Generated: 2026-06-28 10:11 / JX v4.0.0 LOOP-FOLD", out)

    def test_existing_single_quoted_genmeta_is_replaced_not_duplicated(self) -> None:
        html = """<!doctype html>
<html><body>
<p class='footer-date lexia-genmeta' data-generated='2026-01-01T00:00+09:00'>Generated: 2026-01-01 00:00 / old</p>
</body></html>
"""
        out = self.mod.stamp_html(html, self.dt, "ARIADNE v0.3")
        self.assertEqual(1, out.count("lexia-genmeta"))
        self.assertIn('data-generated="2026-06-28T10:11+09:00"', out)

    def test_has_genmeta_stamp_ignores_comments_and_script_literals(self) -> None:
        self.assertTrue(self.mod.has_genmeta_stamp('<p class="footer-date lexia-genmeta">Generated: x</p>'))
        self.assertTrue(self.mod.has_genmeta_stamp("<p class='footer-date lexia-genmeta'>Generated: x</p>"))
        self.assertFalse(self.mod.has_genmeta_stamp("<!-- lexia-genmeta -->"))
        self.assertFalse(self.mod.has_genmeta_stamp('<script>const c = "lexia-genmeta";</script>'))

    def test_legacy_japanese_footer_is_replaced(self) -> None:
        html = """<!doctype html>
<html><body>
<div class="footer-spec">
<p class="footer-date">作成日：2026-01-01</p>
</div>
</body></html>
"""
        out = self.mod.stamp_html(html, self.dt, "TX v11.1.0 LOOP-CORE")
        self.assertNotIn("作成日", out)
        self.assertEqual(1, out.count("lexia-genmeta"))
        self.assertIn("Generated: 2026-06-28 10:11 / TX v11.1.0 LOOP-CORE", out)

    def test_multiclass_footer_date_is_replaced_inside_footer_spec(self) -> None:
        html = """<!doctype html>
<html><body>
<div class="layout footer-spec compact">
<p class="small footer-date muted">作成日：2026-01-01 ／ old</p>
</div>
</body></html>
"""
        out = self.mod.stamp_html(html, self.dt, "TX v11.1.0 LOOP-CORE")
        self.assertNotIn("作成日", out)
        self.assertEqual(1, out.count("lexia-genmeta"))
        self.assertNotIn('style="text-align:center"', out)
        self.assertLess(out.index("lexia-genmeta"), out.index("</div>"))

    def test_single_quoted_footer_spec_and_native_date_are_handled(self) -> None:
        html = """<!doctype html>
<html><body>
<div class='layout footer-spec compact'>
<p class='small footer-date muted'>作成日：2026-01-01 ／ old</p>
</div>
</body></html>
"""
        out = self.mod.stamp_html(html, self.dt, "TX v11.1.0 LOOP-CORE")
        self.assertNotIn("作成日", out)
        self.assertEqual(1, out.count("lexia-genmeta"))
        self.assertNotIn('style="text-align:center"', out)
        self.assertLess(out.index("lexia-genmeta"), out.index("</div>"))

    def test_footer_spec_without_date_gets_inner_stamp(self) -> None:
        html = """<!doctype html>
<html><body>
<div class="layout footer-spec compact">
<p>source</p>
</div>
</body></html>
"""
        out = self.mod.stamp_html(html, self.dt, "TX v11.1.0 LOOP-CORE")
        self.assertEqual(1, out.count("lexia-genmeta"))
        self.assertNotIn('style="text-align:center"', out)
        self.assertLess(out.index("lexia-genmeta"), out.index("</div>"))

    def test_single_quoted_footer_spec_without_date_gets_inner_stamp(self) -> None:
        html = """<!doctype html>
<html><body>
<div class='layout footer-spec compact'>
<p>source</p>
</div>
</body></html>
"""
        out = self.mod.stamp_html(html, self.dt, "TX v11.1.0 LOOP-CORE")
        self.assertEqual(1, out.count("lexia-genmeta"))
        self.assertNotIn('style="text-align:center"', out)
        self.assertLess(out.index("lexia-genmeta"), out.index("</div>"))

    def test_no_footer_container_gets_centered_body_stamp(self) -> None:
        html = "<html><body><main>body</main></body></html>"
        out = self.mod.stamp_html(html, self.dt, "RX AXIOM v2.8")
        self.assertIn('style="text-align:center"', out)
        self.assertLess(out.index("lexia-genmeta"), out.index("</body>"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
