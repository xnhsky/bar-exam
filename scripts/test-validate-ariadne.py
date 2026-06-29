#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""validate-ariadne.py の軽量 self-test。"""
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().with_name("validate-ariadne.py")


def load_module():
    spec = importlib.util.spec_from_file_location("validate_ariadne", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ValidateAriadneTest(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = load_module()

    def test_extract_divs_accepts_single_quoted_multi_class(self) -> None:
        html = "<div class='panel self-check-quiz' data-recall='1'>問<div>内側</div></div>"
        blocks = self.mod.extract_divs(html, "self-check-quiz")
        self.assertEqual(1, len(blocks))
        self.assertIn("data-recall='1'", blocks[0][0])
        self.assertIn("内側", blocks[0][1])

    def test_go_athena_target_accepts_attribute_order_and_quote_variants(self) -> None:
        html = "<a data-athena-code='刑JX001' class='button go-athena'>ATHENA</a>"
        self.assertEqual("刑JX001", self.mod.go_athena_target(html))

        html = '<a class="go-athena button" data-athena-code="民JX002">ATHENA</a>'
        self.assertEqual("民JX002", self.mod.go_athena_target(html))

    def test_data_rx_helper_accepts_single_quotes(self) -> None:
        tag = "<div class='self-check-quiz' data-rx='刑RX001_1'></div>"
        self.assertEqual("刑RX001_1", self.mod.first_attr_value(self.mod.DATA_RX_RE, tag))

    def test_quiz_contract_helpers_accept_quote_variants(self) -> None:
        card_tag = "<div class='self-check-quiz' data-arena='1' data-correct-value='○' data-explanation='解説'>"
        inner = (
            "<p class='quiz-question'>問い</p>"
            "<button class='quiz-btn' data-value='○'>○</button>"
            '<button data-value="×" class="quiz-btn">×</button>'
        )
        self.assertEqual("1", self.mod.first_attr_value(self.mod.DATA_ARENA_RE, card_tag))
        self.assertEqual("○", self.mod.first_attr_value(self.mod.DATA_CORRECT_VALUE_RE, card_tag))
        self.assertTrue(self.mod.DATA_EXPLANATION_RE.search(card_tag))
        self.assertEqual("問い", self.mod.first_element_text_by_class(inner, "p", "quiz-question"))
        self.assertEqual(["○", "×"], self.mod.attr_values_on_classed_tags(inner, "quiz-btn", self.mod.DATA_VALUE_RE))

    def test_html_has_class_uses_class_tokens_not_substrings(self) -> None:
        self.assertFalse(self.mod.html_has_class("<div class='not-self-check-quiz'></div>", "self-check-quiz"))
        self.assertTrue(self.mod.html_has_class("<section class='box self-check-quiz'></section>", "self-check-quiz"))

    def test_late_section_helpers_accept_quote_and_class_variants(self) -> None:
        html = (
            "<details class='panel peek'><div class='body text'>教示本文</div></details>"
            "<p class='x do'>実行する</p>"
            "<div class='ttl current'>第1手</div>"
            "<section id='ref-stat-1'></section>"
            "<section id=\"ref-case-1\"></section>"
            "<p class='r-issue fact'>答案</p>"
            "<div class='bc-col extra'></div>"
        )
        self.assertEqual(["実行する"], self.mod.element_texts_by_class(html, "p", "do"))
        peek = self.mod.extract_tag_blocks_by_class(html, "details", "peek")
        self.assertEqual(1, len(peek))
        self.assertEqual("教示本文", self.mod.first_element_text_by_class(peek[0][1], "div", "body"))
        self.assertEqual("第1手", self.mod.first_element_text_by_class(html, "div", "ttl"))
        self.assertTrue(self.mod.html_has_id_prefix(html, "ref-stat"))
        self.assertEqual(1, self.mod.id_prefix_count(html, "ref-case"))
        self.assertEqual(1, self.mod.class_prefix_count(html, "p", ("r-issue", "r-norm", "r-apply", "r-concl")))
        self.assertEqual(1, self.mod.class_count(html, "bc-col"))

    def test_extract_tag_block_by_id_accepts_single_quotes(self) -> None:
        html = "<details id='deep-dive' class='panel'><p>深掘り</p></details>"
        self.assertIn("深掘り", self.mod.extract_tag_block_by_id(html, "details", "deep-dive"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
