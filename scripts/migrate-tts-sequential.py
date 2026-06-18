#!/usr/bin/env python3
"""
migrate-tts-sequential.py - 既存 TTS 台本のサブパート命名をフラット連番へ移行

旧: {問題ID}-{メインパート1-7}{サブa-d}.txt   例 刑JX029-1a.txt / 刑JX029-2b.txt
新: {問題ID}-{連番}.txt                        例 刑JX029-1.txt  / 刑JX029-4.txt

同時に、台本の話す中身（橋渡し文・相互参照）の旧サブパート識別子
「1a」「2b」等を新しい連番読み上げ形「{問題番号}の{連番}」（例「29の2」）へ置換する。

Usage:
  python scripts/migrate-tts-sequential.py outputs/002_TTS            # dry-run（全フォルダ）
  python scripts/migrate-tts-sequential.py outputs/002_TTS --apply    # 実行（git mv + 内容書換）
  python scripts/migrate-tts-sequential.py outputs/002_TTS/001_刑法/刑JX029 --apply  # 単一フォルダ

--apply 時は git mv でリネーム（履歴保持）し、内容を上書きする。
旧トークンが当該フォルダに実在しない参照は WARN を出して未置換のまま残す。
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

OLD_PAT = re.compile(r"^(?P<id>.+?)-(?P<main>[1-7])(?P<sub>[a-d])\.txt$")
TOKEN_RE = re.compile(r"([1-7])([a-d])")
SUBS = "abcd"


def subject_num(pid: str) -> str:
    """刑JX029 -> '29' / 刑JX001 -> '1'"""
    m = re.search(r"(\d+)$", pid)
    return str(int(m.group(1))) if m else pid


def collect(folder: Path):
    """sorted [(main, subidx, path, id)]  旧命名のみ"""
    out = []
    for p in folder.glob("*.txt"):
        m = OLD_PAT.match(p.name)
        if m:
            out.append((int(m.group("main")), SUBS.index(m.group("sub")), p, m.group("id")))
    out.sort(key=lambda t: (t[0], t[1]))
    return out


def migrate_folder(folder: Path, apply: bool) -> bool:
    files = collect(folder)
    if not files:
        return True
    pid = files[0][3]
    num = subject_num(pid)

    # 旧トークン "2a" -> 新読み上げ "29の3" / (main,subidx) -> 連番
    token_map: dict[str, str] = {}
    rename_plan: list[tuple[Path, Path, int]] = []
    for seq, (main, subidx, p, _) in enumerate(files, start=1):
        token_map[f"{main}{SUBS[subidx]}"] = f"{num}の{seq}"
        rename_plan.append((p, folder / f"{pid}-{seq}.txt", seq))

    unmapped: set[str] = set()

    def repl(mo: re.Match) -> str:
        tok = mo.group(0)
        if tok in token_map:
            return token_map[tok]
        unmapped.add(tok)
        return tok

    print(f"\n=== {folder.name}  ({len(files)} files, 問題番号={num}) ===")
    for (src, dst, seq), (main, subidx, _, _) in zip(rename_plan, files):
        old_tok = f"{main}{SUBS[subidx]}"
        print(f"  {src.name:24s} -> {dst.name:20s}  ('{old_tok}' -> '{num}の{seq}')")

    if apply:
        for (src, dst, seq) in rename_plan:
            text = src.read_text(encoding="utf-8-sig")
            new_text = TOKEN_RE.sub(repl, text)
            # git mv（履歴保持）→ 内容上書き
            subprocess.run(["git", "mv", str(src), str(dst)], check=True)
            dst.write_text(new_text, encoding="utf-8")
        if unmapped:
            print(f"  [WARN] 当該フォルダに実在しない参照を未置換で残した: {sorted(unmapped)}")
    else:
        # dry-run でも未置換参照を検出
        for (main, subidx, p, _) in files:
            TOKEN_RE.sub(repl, p.read_text(encoding="utf-8-sig"))
        if unmapped:
            print(f"  [WARN] 当該フォルダに実在しない参照: {sorted(unmapped)}")

    return not unmapped


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    apply = "--apply" in sys.argv
    if not args:
        print("Usage: python scripts/migrate-tts-sequential.py <dir> [--apply]", file=sys.stderr)
        return 2
    root = Path(args[0])
    if not root.is_dir():
        print(f"ERROR: {root} is not a directory", file=sys.stderr)
        return 2

    # root 自体が問題フォルダ（*.txt を直接含む）か、tts ルートか
    if list(root.glob("*.txt")):
        folders = [root]
    else:
        folders = [d for d in sorted(root.iterdir()) if d.is_dir()]

    print(f"MODE: {'APPLY' if apply else 'DRY-RUN'}")
    ok = True
    for f in folders:
        ok &= migrate_folder(f, apply)
    print(f"\n{'=== APPLIED ===' if apply else '=== DRY-RUN (no changes) ==='}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
