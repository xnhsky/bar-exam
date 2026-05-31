#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase Y-4-bis-impl Commit 2: 303.json に v9.4.0 5 fields を追加。

既存 27 keys（Y-4 で補完済）に以下を追加:
  - spec_version: "v9.2.0" → "v9.4.0"
  - exam_badges[]: 4 件
  - theme_tags[]: N 件
  - difficulty: ★★☆
  - choices[*].summary_html: 5 件
  - choices[*].basis_link_card: 5 件

mindmap_section は任意（303 では mindmap_tree + mindmap_radial で十分なため省略）。
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JSON_PATH = ROOT / "problems" / "303.json"

with JSON_PATH.open(encoding="utf-8") as f:
    p = json.load(f)

# --------------------------------------------------------------
# Step 1: spec_version を v9.4.0 に更新
# --------------------------------------------------------------
p["spec_version"] = "v9.4.0"

# --------------------------------------------------------------
# Step 2: exam_badges
# --------------------------------------------------------------
# 自動導出 (subject KEI / exam 司法試験 / year H26 / source 共通H26-20) で
# render.py が "📚 刑法 / 📝 司法試験 / 📅 H26 / 🔢 共通H26-20" を生成。
# 明示指定で詳細制御も可能。本 303 では default 動作を活用するため未指定。
# 必要なら：p["exam_badges"] = ["📚 刑法", "📝 司法試験", "📅 H26", "🔢 共通H26-20"]

# --------------------------------------------------------------
# Step 3: theme_tags
# --------------------------------------------------------------
p["theme_tags"] = [
    "詐欺罪",
    "横領罪",
    "盗品等罪",
    "不動産二重売買",
    "不可罰的事後行為",
    "幇助の時的限界",
    "不法原因給付",
    "刑法独自占有説",
]

# --------------------------------------------------------------
# Step 4: difficulty （correct_rate=50 → ★★☆ 自動派生・明示指定で固定）
# --------------------------------------------------------------
p["difficulty"] = "★★☆"

# --------------------------------------------------------------
# Step 5: choices[*].summary_html
# --------------------------------------------------------------
summaries = {
    "ア": "不動産詐欺の既遂時期について<a class=\"ref-case\" href=\"#case-dairen-t11-12-15\">大連判大11.12.15</a>は<span class=\"case-emphasis freq-high\">占有移転時又は所有権移転登記完了時のいずれか早い時点</span>で既遂とする。本記述は本問事案にこの判例規範をあてはめており正しい。",
    "イ": "甲がAを欺いて本件不動産を取得した時点で<span class=\"case-emphasis freq-high\">詐欺既遂罪</span>が成立済み。その後の乙への移転登記は事前犯罪行為により違法評価が尽くされる<strong>不可罰的事後行為</strong>であり、横領罪は別罪として成立しない。",
    "ウ": "<span class=\"case-emphasis freq-high\">刑法62条1項</span>の幇助は正犯の実行行為以前又はこれと同時に行われるものに限られる。乙が売買交渉を始めた時点では甲の詐欺罪の実行行為は既に終了しており、乙に詐欺既遂罪の幇助犯は成立しない。",
    "エ": "盗品等有償譲受け罪（<a class=\"ref-stat\" href=\"#law-256\">256条2項</a>）は、財産罪により領得された物の有償譲受けが、譲受人の<strong>盗品性の認識</strong>と相俟って成立する。乙は甲の詐欺取得を認識しつつ有償譲り受けた事実に該当して正しい。",
    "オ": "<a class=\"ref-case\" href=\"#case-saiko-s23-6-5\">最判昭23.6.5（百選Ⅱ63事件）</a>の<span class=\"case-emphasis freq-high\">刑法独自占有説</span>により、刑法上の占有・他人性は民法上の所有権帰属と独立に判断される。丙が乙から受領した3000万円は刑法上「自己の占有する他人の物」に当たり、馬券購入は不法領得意思に基づく横領行為に該当して<strong>横領罪成立</strong>。本記述は「成立しない」とするため誤り。",
}

for c in p["choices"]:
    lbl = c.get("label")
    if lbl in summaries:
        c["summary_html"] = summaries[lbl]

# --------------------------------------------------------------
# Step 6: choices[*].basis_link_card
# --------------------------------------------------------------
basis_links = {
    "ア": {
        "label": "📎 参照する条文・判例",
        "items": [
            {"href": "case-dairen-t11-12-15", "label": "大連判大11.12.15（不動産詐欺既遂時期）", "kind": "case"},
            {"href": "law-246", "label": "刑法246条（詐欺罪）", "kind": "statute"},
        ],
    },
    "イ": {
        "label": "📎 参照する条文・判例",
        "items": [
            {"href": "law-246", "label": "刑法246条（詐欺罪・本記述で既遂済）", "kind": "statute"},
            {"href": "law-252", "label": "刑法252条1項（横領罪・本記述では成立せず）", "kind": "statute"},
        ],
    },
    "ウ": {
        "label": "📎 参照する条文・判例",
        "items": [
            {"href": "law-62", "label": "刑法62条1項（幇助の時的限界）", "kind": "statute"},
            {"href": "law-246", "label": "刑法246条（詐欺罪正犯）", "kind": "statute"},
        ],
    },
    "エ": {
        "label": "📎 参照する条文・判例",
        "items": [
            {"href": "law-256", "label": "刑法256条1項・2項（盗品等罪）", "kind": "statute"},
            {"href": "law-246", "label": "刑法246条（本犯としての詐欺罪）", "kind": "statute"},
        ],
    },
    "オ": {
        "label": "📎 参照する条文・判例",
        "items": [
            {"href": "case-saiko-s23-6-5", "label": "最判昭23.6.5（百選Ⅱ63・刑法独自占有説）", "kind": "case"},
            {"href": "case-saiko-s39-1-24", "label": "最判昭39.1.24（共有関係・補強判例）", "kind": "case"},
            {"href": "case-saiko-s45-10-21", "label": "最大判昭45.10.21（民法708条反射効・民事）", "kind": "case"},
            {"href": "law-252", "label": "刑法252条1項（横領罪）", "kind": "statute"},
            {"href": "law-mn-708", "label": "民法708条（不法原因給付）", "kind": "statute"},
        ],
    },
}

for c in p["choices"]:
    lbl = c.get("label")
    if lbl in basis_links:
        c["basis_link_card"] = basis_links[lbl]

# --------------------------------------------------------------
# Step 7: 書き戻し
# --------------------------------------------------------------
JSON_PATH.write_text(
    json.dumps(p, ensure_ascii=False, indent=2),
    encoding="utf-8",
)

print(f"[OK] 303.json v9.4.0 補完完了: top-level keys = {len(p)}")
print(f"     spec_version: {p['spec_version']}")
print(f"     theme_tags: {len(p['theme_tags'])} 件")
print(f"     choices[*].summary_html: {sum(1 for c in p['choices'] if c.get('summary_html'))} 件")
print(f"     choices[*].basis_link_card: {sum(1 for c in p['choices'] if c.get('basis_link_card'))} 件")
