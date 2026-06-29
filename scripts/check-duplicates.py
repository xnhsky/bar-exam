#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
バッチ重複・タイトル整合チェッカ

出力フォルダ群を横断走査し、ファイル単位バリデータ (validate-tx.py 等) では
拾えない「ファイル間」の不整合を検出する。

検出ルール:
  D80  ID-MISMATCH       : <title> / .doc-header / .footer-problem 内の問題コードが
                           ファイル名のコードと不一致
                           (例: 刑TX338.html の <title>、刑TX055.html の footer が
                            「刑TX311」のまま = TX311 からのコピペ残り)
                           ※ JX1/JX001、RX001-1/RX001_01 のような表記差は
                             数値比較で吸収し誤検出しない
                           ※ validate-jx.py は footer/header の ID を検査しないため、
                             この D80 が JX/RX/GX/PX も含め横断的にカバーする
  D81  DUP-TITLE         : 2 件以上のファイルが同一の <title> を持つ
                           (別問題が同一タイトル = Lexia の重複誤検出の源流)
  D82  DUP-BODY          : 2 件以上のファイルが本文一致
                           (lexia-genmeta の生成日時だけは正規化)
                           (同一問題が別名で重複保存 = 例 刑JX001/刑JX002)

いずれかを検出すると exit code 1 を返すので、night-batch / deploy 前の
ゲートとしても使える (例: `python scripts/check-duplicates.py && pwsh scripts/jx-deploy.ps1`)。

DUP-TITLE / DUP-BODY は「同一ツリー内」での重複のみを問題にする。
deploy/ は outputs/ のミラー (タイトルは同一・本文は変換済) なので、
ルートを複数渡した場合は各ルートを独立に検査する (ミラー間の一致は誤検出しない)。

使い方:
    python scripts/check-duplicates.py                 # 既定で outputs/ を走査
    python scripts/check-duplicates.py outputs/000_TX outputs/001_JX
    python scripts/check-duplicates.py outputs deploy   # 各ルートを独立に検査
"""

import sys
import re
import hashlib
from pathlib import Path
from collections import defaultdict

# Windows cp932 で絵文字出力時の UnicodeEncodeError 対策 (validate-tx.py と同方針)
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.S | re.I)
ROOT = Path(__file__).resolve().parents[1]
# 既知カテゴリ + 番号のみを問題コードとして扱う (試験年度 H29 等を誤って拾わないため)。
# KJX は JX より先に置く。そうしないと 刑KJX001 を 刑JX001 と誤読する。
CODE_RE = re.compile(
    r"(?<![A-Z])"
    r"(刑訴|民訴|行政|刑|憲|民|商)?"
    r"(KJX|TX|JX|GX|PX|RX|TREE|MTD)"
    r"0*([0-9]{1,4})"
    r"(?:[_-]0*([0-9]+))?"
    r"(?![0-9A-Z])",
    re.I,
)
CLASS_ATTR_RE = re.compile(
    r"<[a-zA-Z][\w:-]*\b[^>]*\bclass\s*=\s*(['\"])(.*?)\1[^>]*>",
    re.S | re.I,
)
TAG_RE = re.compile(r"<[^>]+>")
GENMETA_RE = re.compile(
    r"<([a-zA-Z][\w-]*)\b[^>]*\bclass\s*=\s*(['\"])[^'\"]*\blexia-genmeta\b[^'\"]*\2[^>]*>.*?</\1>",
    re.S | re.I,
)
DATA_GENERATED_RE = re.compile(r"\bdata-generated\s*=\s*(['\"])(.*?)\1", re.I)
GENERATED_DISPLAY_RE = re.compile(r"Generated:\s*\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}")


def code_key(s):
    """文字列から (科目prefix, カテゴリ大文字, 番号int, 枝番int|None) を抽出。"""
    if not s:
        return None
    m = CODE_RE.search(s)
    if not m:
        return None
    return (m.group(1) or "", m.group(2).upper(), int(m.group(3)), int(m.group(4)) if m.group(4) else None)


def same_code_key(a, b):
    """0 埋め・RX 枝番 separator 差を吸収し、科目 prefix は両方ある時だけ厳密比較。"""
    if a is None or b is None:
        return False
    ap, ak, an, abranch = a
    bp, bk, bn, bbranch = b
    if ak != bk or an != bn or abranch != bbranch:
        return False
    if ap and bp and ap != bp:
        return False
    return True


def format_code_key(key):
    if key is None:
        return "?"
    prefix, kind, num, branch = key
    text = f"{prefix}{kind}{num}"
    if branch is not None:
        text += f"_{branch}"
    return text


# 公式 TX（outputs/000_TX/...）と Lexia 用 TX（outputs/ux/000_TX/...）は
# 「同一問題の 2 表示版（公式＝番号5択 / Lexia＝記述単位 ox-grid）」＝意図的ミラー。
# 同一 <title> になるのは正常なので DUP-TITLE から除外する（科目/ファイル名が一致する組）。
def _mirror_sig(f):
    s = f.as_posix()
    for pref in ("/ux/000_TX/", "/000_TX/"):   # ux 版を先に判定（部分一致対策）
        i = s.find(pref)
        if i >= 0:
            tail = s[i + len(pref):]            # 例: 001_刑法/刑TX350.html
            # Lexia 用は識別のため末尾 _lex を付ける（刑TX350_lex.html）。
            # 公式（刑TX350.html）とミラー判定するため _lex を正規化して落とす。
            tail = re.sub(r"_lex(?=\.html?$)", "", tail, flags=re.I)
            return tail
    return None


def is_official_lexia_mirror(fs):
    sigs = set()
    for f in fs:
        sig = _mirror_sig(f)
        if sig is None:
            return False
        sigs.add(sig)
    return len(sigs) == 1


# class="marker" 直後の窓からコードを拾う (BeautifulSoup 非依存・軽量)。
# footer-spec の version feature-tag (例 "TX v9.2.0") は CODE_RE が数字直結のみ
# 拾うため誤検出しない。検査対象は ID が出る doc-header / footer-problem に限定。
MARKER_WINDOW = 300


def class_tag_index(html, class_name):
    for m in CLASS_ATTR_RE.finditer(html):
        classes = re.split(r"\s+", m.group(2).strip())
        if class_name in classes:
            return m.start()
    return -1


def code_near_class(html, class_name):
    idx = class_tag_index(html, class_name)
    if idx < 0:
        return None
    seg = TAG_RE.sub(" ", html[idx: idx + MARKER_WINDOW])
    return code_key(seg)


def normalize_genmeta_for_body_hash(html):
    def normalize_block(match):
        block = DATA_GENERATED_RE.sub(lambda m: f"data-generated={m.group(1)}<generated>{m.group(1)}", match.group(0))
        return GENERATED_DISPLAY_RE.sub("Generated: <generated>", block)

    return GENMETA_RE.sub(normalize_block, html)


def stable_body_digest(html):
    return hashlib.md5(normalize_genmeta_for_body_hash(html).encode("utf-8", "ignore")).hexdigest()


# _failed / __pycache__ 等の隔離・生成物フォルダは検査対象外
SKIP_DIR_PARTS = {"_failed", "__pycache__", "_experimental", "_migration"}


def collect_files(root):
    p = Path(root)
    if not p.is_absolute():
        p = ROOT / p
    if p.is_file() and p.suffix.lower() in (".html", ".htm"):
        return [p]
    if p.is_dir():
        found = list(p.rglob("*.html")) + list(p.rglob("*.htm"))
        found = [f for f in found if not (SKIP_DIR_PARTS & set(f.parts))]
        return sorted(set(found))
    return []


def check_root(root):
    """1 ルートを独立に検査し、検出件数を返す。"""
    files = collect_files(root)
    if not files:
        print(f"--- {root}: 対象 HTML が見つかりません ---\n")
        return 0

    title_of = {}
    title_groups = defaultdict(list)  # title -> [path,...]
    body_groups = defaultdict(list)   # md5  -> [path,...]
    mismatches = []                   # [(path, [(location, code), ...]), ...]

    for f in files:
        try:
            data = f.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            print(f"  読込失敗: {f} ({e})")
            continue
        m = TITLE_RE.search(data)
        title = re.sub(r"\s+", " ", m.group(1)).strip() if m else ""
        title_of[f] = title
        if title:
            title_groups[title].append(f)
        body_groups[stable_body_digest(data)].append(f)

        # D80: ファイル名コードと title / doc-header / footer-problem の各コードを照合
        fc = code_key(f.name)
        if fc:
            locs = {
                "title": code_key(title),
                "doc-header": code_near_class(data, "doc-header"),
                "footer": code_near_class(data, "footer-problem"),
            }
            bad = [(name, c) for name, c in locs.items() if c is not None and not same_code_key(fc, c)]
            if bad:
                mismatches.append((f, fc, bad))

    errors = 0
    print(f"=== ルート: {root}  ({len(files)} ファイル) ===\n")

    print("[D80] ID-MISMATCH (title/doc-header/footer の問題コードがファイル名と不一致)")
    if not mismatches:
        print("  なし ✅")
    else:
        for f, fc, bad in mismatches:
            locs_str = ", ".join(f"{name}={format_code_key(c)}" for name, c in bad)
            print(f"  ❌ {f}")
            print(f"       file={format_code_key(fc)}  /  不一致: {locs_str}")
        errors += len(mismatches)

    print("\n[D81] DUP-TITLE (同一 <title> を持つ別ファイル)")
    dup_titles = {t: fs for t, fs in title_groups.items()
                  if len(set(fs)) >= 2 and not is_official_lexia_mirror(set(fs))}
    if not dup_titles:
        print("  なし ✅")
    else:
        for t, fs in dup_titles.items():
            print(f"  ❌ <title>='{t}'")
            for f in sorted(set(fs)):
                print(f"       {f}")
        errors += sum(len(set(fs)) for fs in dup_titles.values())

    print("\n[D82] DUP-BODY (生成日時を除いた本文一致の別ファイル)")
    dup_bodies = {h: fs for h, fs in body_groups.items() if len(set(fs)) >= 2}
    if not dup_bodies:
        print("  なし ✅")
    else:
        for h, fs in dup_bodies.items():
            print(f"  ❌ md5={h[:12]}…")
            for f in sorted(set(fs)):
                print(f"       {f}")
        errors += sum(len(set(fs)) for fs in dup_bodies.values())

    print()
    return errors


def main(argv):
    roots = argv[1:] or ["outputs"]
    total = 0
    for root in roots:
        total += check_root(root)

    print("=" * 56)
    if total:
        print(f"❌ 全ルート計 {total} 件を検出。配布前に修正してください。")
        return 1
    print("✅ ファイル間の重複・タイトル不整合は見つかりませんでした。")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
