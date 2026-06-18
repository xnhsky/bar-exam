#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Claude Code jsonl 履歴から 刑TX303.html の gold standard (252,977 bytes 想定) を復元する。

戦略：
  1. session jsonl を 1 行ずつパース
  2. 刑TX303.html を対象とする Write / Edit ツール呼び出しを時系列で抽出
  3. Write があれば content を初期状態とする
  4. Edit を時系列順に old → new で適用
  5. 最後にファイルに書き出す

入力: /c/Users/xnrg2.DESKTOP-5664QR6/.claude/projects/C--Users-xnrg2-DESKTOP-5664QR6-bar-exam/7588c63d-ab16-400f-9d7a-e5d7d06f8426.jsonl
出力: /tmp/303-recovered.html
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

JSONL = Path(r"C:\Users\xnrg2.DESKTOP-5664QR6\.claude\projects\C--Users-xnrg2-DESKTOP-5664QR6-bar-exam\7588c63d-ab16-400f-9d7a-e5d7d06f8426.jsonl")
TARGET = "刑TX303.html"
OUTPUT = Path("303-recovered.html")

# 同セッションで実際に Write が走った時点の baseline を取得するため、
# 同時刻付近の Read tool_result からも初期状態を吸い上げられるようにする。
BASE_FILE = Path("outputs/000_TX/001_刑法/刑TX303-eta-wip.html")  # 既知の WIP 状態（210 KB）


def parse_session():
    edits: list[dict] = []
    writes: list[dict] = []
    reads: list[dict] = []  # Read tool_result (for fallback initial state)
    with JSONL.open(encoding="utf-8") as fh:
        for line in fh:
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            msg = obj.get("message", {})
            content = msg.get("content")
            if not isinstance(content, list):
                continue
            ts = obj.get("timestamp", "")
            for item in content:
                if item.get("type") != "tool_use":
                    continue
                name = item.get("name")
                inp = item.get("input", {})
                fp = inp.get("file_path", "")
                if TARGET not in fp:
                    continue
                if name == "Write":
                    writes.append({
                        "ts": ts,
                        "content": inp.get("content", ""),
                    })
                elif name == "Edit":
                    edits.append({
                        "ts": ts,
                        "old": inp.get("old_string", ""),
                        "new": inp.get("new_string", ""),
                        "replace_all": inp.get("replace_all", False),
                    })
                elif name == "Read":
                    reads.append({
                        "ts": ts,
                        "offset": inp.get("offset"),
                        "limit": inp.get("limit"),
                    })
    edits.sort(key=lambda e: e["ts"])
    writes.sort(key=lambda w: w["ts"])
    return edits, writes, reads


def main():
    edits, writes, reads = parse_session()
    print(f"Found: {len(writes)} Write, {len(edits)} Edit, {len(reads)} Read tool calls", file=sys.stderr)

    # 初期状態：Write があればそれ、なければ eta-wip ベース
    if writes:
        text = writes[-1]["content"]  # 最新の Write を起点
        print(f"  Using LATEST Write ({writes[-1]['ts']}, {len(text)} chars) as initial state", file=sys.stderr)
        # この Write 以降の Edit のみ適用
        last_write_ts = writes[-1]["ts"]
        applicable_edits = [e for e in edits if e["ts"] > last_write_ts]
    else:
        if not BASE_FILE.exists():
            print(f"FAIL: no Write found and base file {BASE_FILE} missing", file=sys.stderr)
            sys.exit(1)
        text = BASE_FILE.read_text(encoding="utf-8")
        print(f"  Using {BASE_FILE} ({len(text)} chars) as initial state", file=sys.stderr)
        applicable_edits = edits

    print(f"  Applying {len(applicable_edits)} Edit ops in chronological order", file=sys.stderr)

    success = 0
    skipped = 0
    for i, e in enumerate(applicable_edits, 1):
        old = e["old"]
        new = e["new"]
        if not old:
            continue
        count = text.count(old)
        if count == 0:
            skipped += 1
            print(f"  Edit {i} [{e['ts']}]: old_string not found (skipped)", file=sys.stderr)
            continue
        if e["replace_all"]:
            text = text.replace(old, new)
        else:
            if count > 1:
                print(f"  Edit {i} [{e['ts']}]: old_string appears {count}x, replacing FIRST only", file=sys.stderr)
            text = text.replace(old, new, 1)
        success += 1

    print(f"\nResult: {success}/{len(applicable_edits)} Edits applied, {skipped} skipped", file=sys.stderr)
    print(f"Output size: {len(text):,} chars", file=sys.stderr)

    OUTPUT.write_text(text, encoding="utf-8", newline="")
    print(f"Wrote: {OUTPUT}", file=sys.stderr)


if __name__ == "__main__":
    main()
