#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""HTML から drill_blocks を逆抽出して JSON 配列を stdout に出力

Phase 13C-5: AI 生成 HTML（_experimental/*.html 等）から drill_blocks 12 件を
逆抽出し、problems/{ID}.json に手動マージできる形式で出力する。

render.py 側の drill rendering 仕様（render.py L1238-1275）と整合する schema：
  [{"num": "01", "tag": "...", "question": "...", "correct": "○", "explanation": "..."}, ...]

使い方:
    python scripts/extract_drill_blocks.py <HTMLファイル>
例:
    python scripts/extract_drill_blocks.py _experimental/刑TX305.html > extracted.json
"""

import sys
import json
import re
from pathlib import Path
from bs4 import BeautifulSoup

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")  # Windows cp932 回避


def extract(html_path):
    soup = BeautifulSoup(Path(html_path).read_text(encoding="utf-8"), "html.parser")
    drills = []
    for block in soup.find_all("div", class_="drill-block"):
        num_text = block.find("span", class_="drill-num").get_text()
        # "DRILL\xa001" → "01" (\xa0 は &nbsp; decode 後)
        num = re.sub(r"^DRILL\xa0", "", num_text).strip()
        tag = block.find("span", class_="drill-tag").get_text(strip=True)
        quiz = block.find("div", class_="self-check-quiz")
        drills.append({
            "num": num,
            "tag": tag,
            "question": block.find("div", class_="quiz-question").get_text(strip=True),
            "correct": quiz["data-correct-value"],
            "explanation": quiz["data-explanation"],
        })
    return drills


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("使い方: python scripts/extract_drill_blocks.py <HTMLファイル>", file=sys.stderr)
        sys.exit(1)
    result = extract(sys.argv[1])
    assert len(result) == 12, f"drill_blocks 12 件期待・実検出 {len(result)} 件"
    print(json.dumps(result, ensure_ascii=False, indent=2))
