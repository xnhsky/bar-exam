#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""stamp-created-date.py の軽量 self-test。"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import sys
import tempfile
import types
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().with_name("stamp-created-date.py")


def load_module():
    spec = importlib.util.spec_from_file_location("stamp_created_date", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class StampCreatedDateTest(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = load_module()
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.old_repo = self.mod.REPO
        self.mod.REPO = self.root

    def tearDown(self) -> None:
        self.mod.REPO = self.old_repo
        self.tmp.cleanup()

    def write(self, rel: str, text: str) -> Path:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def test_git_output_is_read_as_utf8(self) -> None:
        def fake_run(_cmd, **kwargs):
            self.assertEqual("utf-8", kwargs.get("encoding"))
            self.assertEqual("replace", kwargs.get("errors"))
            return types.SimpleNamespace(stdout=" M outputs/001_JX/001_刑法/刑JX001.html\n")

        with patch.object(self.mod.subprocess, "run", side_effect=fake_run):
            self.assertIn("刑JX001", self.mod._git("status"))

    def test_main_ignores_script_literal_and_stamps_real_missing_genmeta(self) -> None:
        path = self.write(
            "outputs/001_JX/001_刑法/刑JX001.html",
            '<html><body><script>const marker = "lexia-genmeta";</script></body></html>',
        )
        calls = []

        def fake_stamp_file(file_path, _dt, version):
            calls.append((Path(file_path), version))
            return True

        with (
            patch.object(self.mod, "targets", return_value=[path]),
            patch.object(self.mod, "is_dirty", return_value=True),
            patch.object(self.mod, "first_commit_dt", return_value=None),
            patch.object(self.mod, "stamp_file", side_effect=fake_stamp_file),
            patch.object(self.mod, "infer_version", return_value="JX v4.0.0 LOOP-FOLD"),
            contextlib.redirect_stdout(io.StringIO()),
        ):
            self.assertEqual(0, self.mod.main())
        self.assertEqual([(path, "JX v4.0.0 LOOP-FOLD")], calls)

    def test_main_skips_real_genmeta_stamp(self) -> None:
        path = self.write(
            "outputs/001_JX/001_刑法/刑JX001.html",
            '<p class="footer-date lexia-genmeta" data-generated="2026-06-28T10:11+09:00">Generated: 2026-06-28 10:11</p>',
        )
        with (
            patch.object(self.mod, "targets", return_value=[path]),
            patch.object(self.mod, "stamp_file") as stamp_file,
            contextlib.redirect_stdout(io.StringIO()),
        ):
            self.assertEqual(0, self.mod.main())
        stamp_file.assert_not_called()

    def test_first_commit_dt_uses_oldest_log_line(self) -> None:
        out = "2026-06-29T10:00:00+09:00\n2026-06-28T09:30:00+09:00\n"
        with patch.object(self.mod, "_git", return_value=out):
            self.assertEqual(
                datetime(2026, 6, 28, 9, 30, tzinfo=self.mod.JST),
                self.mod.first_commit_dt("outputs/001_JX/001_刑法/刑JX001.html"),
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
