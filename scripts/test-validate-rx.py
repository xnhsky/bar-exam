#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Lightweight self-test for validate-rx.py."""
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().with_name("validate-rx.py")


class ValidateRxTest(unittest.TestCase):
    def test_accepts_single_quotes_and_multiclass_quiz_markup(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp)
            html = """<!doctype html>
<html>
<head><title>刑RX001_1</title></head>
<body>
<main style="max-width:920px">
  <div class='card self-check-quiz' data-correct-value='○' data-explanation='first'>
    <span class='label quiz-question'>論点を一文で答える。</span>
  </div>
  <div data-explanation="second" data-correct-value="×" class="self-check-quiz card">
    <span class="quiz-question label">反対構成を切る理由を答える。</span>
  </div>
  <section style="background:#fff7a8">norm</section>
</main>
<!-- padding so R9 does not report body loss -->
""" + ("x" * 4300) + """
</body>
</html>
"""
            (out_dir / "刑RX001_1.html").write_text(html, encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(out_dir), "刑RX001"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertNotIn("[ERROR]", result.stdout)
        self.assertIn("ERROR=0", result.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
