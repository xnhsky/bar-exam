#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JX 入力アラインメント・チェッカー（PDF ↔ 講義逐語のズレを事前検出）

背景：
  inputs/001_JX/{科目}/重問PDF/{n}.pdf と inputs/001_JX/{科目}/講義逐語/{科目名}_重問{nn}.txt は
  本来『同番号』で対応するはずだが、実際には番号がズレている系列がある
  （刑28/29/30 は重問PDFと逐語が -7 ズレ。内容照合で 21/22/23 が一致）。
  逐語は JX 生成の第一次情報源であるため、ズレたまま生成すると講師アドバイスが
  別問題のものになる事故が起きる。本スクリプトはこれを『事前に』検出・修正する。

仕組み：
  1) inputs/001_JX/transcript-map.json（マニフェスト）を読む。
  2) 対象 (科目, 番号) について、overrides があればそれを採用、無ければ『同番号』既定で解決。
  3) 解決した逐語ファイルの存在を確認。
  4) overrides に keywords があれば、逐語本文を走査し全 keyword の出現を確認
     （欠落＝中身が別問題＝ズレ疑い → ERROR）。
  5) 既定（同番号）で解決した問題は、検証されていない旨を WARNING で知らせる。

使い方：
  # 1 問だけ解決（生成前に逐語パスを取得する標準動線）
  python scripts/check-jx-alignment.py 刑 28
  python scripts/check-jx-alignment.py 刑 28 --quiet   # 解決パスだけ標準出力（ランナー用）

  # 科目一括スキャン（PDF があるのに逐語が無い／ズレ疑いを洗い出す）
  python scripts/check-jx-alignment.py 刑 --all

終了コード：
  0 = OK（解決＆keyword検証通過 / 一括スキャンで致命的問題なし）
  1 = 逐語ファイルが見つからない（致命）
  2 = keyword 不一致＝ズレ疑い（致命）
  3 = マニフェスト不正・引数不正
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "inputs" / "001_JX" / "transcript-map.json"

GREEN = "\033[32m"; YELLOW = "\033[33m"; RED = "\033[31m"; DIM = "\033[2m"; RST = "\033[0m"


def load_manifest():
    if not MANIFEST.exists():
        print(f"{RED}[FATAL]{RST} マニフェストが無い: {MANIFEST}")
        sys.exit(3)
    try:
        return json.loads(MANIFEST.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"{RED}[FATAL]{RST} マニフェスト JSON 不正: {e}")
        sys.exit(3)


def transcript_candidates(man, subj_cfg, n):
    """番号 n（int）に対する既定の逐語ファイル名候補（同番号）。"""
    nn = f"{n:02d}"
    subj_jp = subj_cfg["subject_jp"]
    out = []
    for tmpl in man.get("transcript_filename_templates", []):
        out.append(tmpl.format(subject_jp=subj_jp, nn=nn))
    return out


def resolve(man, subject, n):
    """戻り値: (transcript_path: Path|None, source: 'override'|'default', meta: dict)"""
    subjects = man.get("subjects", {})
    if subject not in subjects:
        print(f"{RED}[FATAL]{RST} 未知の科目: {subject}（マニフェストに無い）")
        sys.exit(3)
    cfg = subjects[subject]
    tdir = ROOT / cfg["transcript_dir"]
    ov = cfg.get("overrides", {})
    key = str(n)
    if key in ov:
        fname = ov[key]["transcript"]
        return tdir / fname, "override", ov[key]
    # default: same-number
    for cand in transcript_candidates(man, cfg, n):
        p = tdir / cand
        if p.exists():
            return p, "default", {}
    # none found
    return None, "default", {}


def check_keywords(path, keywords):
    """全 keyword が本文に含まれるか。戻り: (ok, missing[])"""
    text = path.read_text(encoding="utf-8", errors="ignore")
    missing = [kw for kw in keywords if kw not in text]
    return (len(missing) == 0), missing


def head_preview(path, n=6):
    """逐語冒頭の非空行を n 本返す（人間が『ざっと』ズレを見抜くため）。"""
    lines = []
    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        s = raw.strip()
        if s:
            lines.append(s[:60])
        if len(lines) >= n:
            break
    return lines


def check_one(man, subject, n, quiet=False):
    path, source, meta = resolve(man, subject, n)
    if path is None or not path.exists():
        if not quiet:
            print(f"{RED}[ERROR]{RST} 刑JX{n:03d} 相当の逐語が見つからない（科目={subject} 番号={n}）")
            print(f"        既定の同番号候補を探したが不在。overrides に明示してください。")
        return 1
    if quiet:
        # ランナー用：解決パスのみ
        print(str(path))
        return 0
    label = f"{subject} 第{n}問"
    if source == "override":
        ok = True
        kws = meta.get("keywords", [])
        if kws:
            ok, missing = check_keywords(path, kws)
        if ok:
            print(f"{GREEN}[OK]{RST} {label} → {path.name}（override・keyword検証通過: {kws}）")
            if meta.get("note"):
                print(f"     {DIM}{meta['note']}{RST}")
            print(f"     {DIM}冒頭プレビュー（ざっと内容照合用）：{RST}")
            for ln in head_preview(path):
                print(f"       {DIM}| {ln}{RST}")
            return 0
        else:
            print(f"{RED}[ERROR]{RST} {label} → {path.name}（override 指定だが keyword 欠落: {missing}）")
            print(f"        ズレ疑い。overrides の transcript 指定を見直してください。")
            return 2
    else:
        print(f"{YELLOW}[WARN]{RST} {label} → {path.name}（同番号・未検証）")
        print(f"     {DIM}冒頭プレビュー（ざっと内容照合用・PDFの論点と食い違わないか目視）：{RST}")
        for ln in head_preview(path):
            print(f"       {DIM}| {ln}{RST}")
        print(f"     ズレを感じたら overrides に正しい逐語を登録してください（1字1句の検証は不要）。")
        return 0


def scan_all(man, subject):
    cfg = man["subjects"][subject]
    pdf_dir = ROOT / cfg["pdf_dir"]
    if not pdf_dir.exists():
        print(f"{RED}[FATAL]{RST} PDF ディレクトリが無い: {pdf_dir}")
        return 3
    nums = []
    for p in pdf_dir.glob("*.pdf"):
        m = re.search(r"\d+", p.stem)
        if m:
            nums.append(int(m.group()))
    nums = sorted(set(nums))
    if not nums:
        print(f"{YELLOW}[WARN]{RST} {pdf_dir} に PDF が無い")
        return 0
    print(f"=== {subject} 一括スキャン（PDF {len(nums)} 問）===")
    worst = 0
    for n in nums:
        rc = check_one(man, subject, n, quiet=False)
        worst = max(worst, rc)
    print(f"--- 完了。最悪終了コード={worst}（0=OK,1=逐語欠落,2=ズレ疑い）---")
    return worst


def main():
    args = [a for a in sys.argv[1:]]
    quiet = "--quiet" in args
    do_all = "--all" in args
    args = [a for a in args if not a.startswith("--")]
    if len(args) < 1:
        print(__doc__)
        sys.exit(3)
    man = load_manifest()
    subject = args[0]
    if do_all:
        sys.exit(scan_all(man, subject))
    if len(args) < 2:
        print(f"{RED}[FATAL]{RST} 番号を指定してください（例: 刑 28）")
        sys.exit(3)
    try:
        n = int(re.search(r"\d+", args[1]).group())
    except (AttributeError, ValueError):
        print(f"{RED}[FATAL]{RST} 番号が数値でない: {args[1]}")
        sys.exit(3)
    sys.exit(check_one(man, subject, n, quiet=quiet))


if __name__ == "__main__":
    main()
