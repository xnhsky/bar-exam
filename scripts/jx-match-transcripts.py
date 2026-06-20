#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
jx-match-transcripts.py  ── 講義逐語 ↔ 重問PDF 内容照合の自動補助（2026-06-07）

なぜ必要か（CLAUDE.md §4「逐語取り込みプロトコル」）:
  講義動画の Whisper 逐語は「動画の通し番号」で命名されており、重問PDFの問題番号とは
  別系統（講座は教育順・PDFはテキスト順）。番号を結合キーにすると全面的に誤ペアリングする。
  正しい結合キーは「中身」だけ。本スクリプトは PDF を OCR し、逐語との文字n-gram TF-IDF
  コサイン類似度で各逐語を最も近いPDFへ割り当て、確信度で層別して「提案」を出す。

設計の要点（刑法の確定対応表で実証済み）:
  - 画像PDFを pymupdf でラスタライズ→tesseract(jpn) で OCR（結果はキャッシュ）。
  - ひらがな（話し言葉のフィラーでノイズ源）を除去し、漢字・カタカナ・英数字の
    文字 n-gram(既定 2-3) TF-IDF コサインで照合。刑法で top-1≈99% / top-3=100%。
  - 絶対コサインは確信度として弱い（真の一致でも 0.02〜0.46 と広い）。順位と競合余白で層別。
  - 競合割当：各PDFに最良逐語・各逐語に最良PDFを greedy 割当。あぶれた逐語＝総合問題/余り、
    逐語の付かないPDF＝逐語欠落、として明示（固定しきい値で N問目以降と決め打ちしない）。
  - **自動改名はしない**。CONFIDENT 層だけ --apply で改名でき、REVIEW/RESIDUAL は人手確認。
    生成時は別途「照合ガード」（冒頭で事案一致を自己照合）が最終安全網。

使い方:
  python scripts/jx-match-transcripts.py --subject 刑                # 提案を表示＋_match-proposal.md 出力
  python scripts/jx-match-transcripts.py --subject 刑 --validate     # 既存 重問逐語NN 命名で精度検証
  python scripts/jx-match-transcripts.py --subject 刑 --apply        # CONFIDENT 層のみ改名（dry-run解除）

依存: pymupdf, pytesseract, pillow, scikit-learn, および tesseract-ocr + jpn 言語データ。
"""
import re, os, sys, io, argparse, unicodedata, subprocess

SUBJ_DIRS = ["刑", "憲", "民", "商", "民訴", "刑訴", "行政"]
# 科目フォルダは 00N_科目 形式（2026-06-20 統一・outputs と対称）。--subject は短縮名を維持。
SUBJ_DIR_MAP = {"刑": "001_刑法", "刑訴": "002_刑事訴訟法", "民": "003_民法",
                "商": "004_商法", "民訴": "005_民事訴訟法", "行政": "006_行政法", "憲": "007_憲法"}

def clean(s: str) -> str:
    """照合用に正規化：ひらがな除去＋漢字/カタカナ/英数字のみ残す。"""
    s = unicodedata.normalize("NFKC", s)
    s = re.sub(r"[ぁ-ゟ]", "", s)                       # 話し言葉フィラー除去
    return re.sub(r"[^一-鿿ァ-ヶA-Za-z0-9]", "", s)

def lazy_imports():
    try:
        import fitz, pytesseract           # noqa
        from PIL import Image              # noqa
        from sklearn.feature_extraction.text import TfidfVectorizer  # noqa
        from sklearn.metrics.pairwise import cosine_similarity        # noqa
    except ImportError as e:
        sys.exit(f"[依存不足] {e}\n  pip install pymupdf pytesseract pillow scikit-learn\n"
                 f"  apt-get install -y tesseract-ocr tesseract-ocr-jpn")

def ocr_pdf(path: str, cache_dir: str, pages: int) -> str:
    import fitz, pytesseract
    from PIL import Image
    base = os.path.splitext(os.path.basename(path))[0]
    cf = os.path.join(cache_dir, base + ".txt")
    if os.path.exists(cf) and os.path.getsize(cf) > 0:
        return open(cf, encoding="utf-8").read()
    d = fitz.open(path); txt = ""
    for i in range(min(pages, d.page_count)):
        pix = d[i].get_pixmap(matrix=fitz.Matrix(3, 3))
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        txt += pytesseract.image_to_string(img, lang="jpn") + "\n"
    open(cf, "w", encoding="utf-8").write(txt)
    return txt

def first_int(name: str):
    m = re.search(r"\d+", name)
    return int(m.group()) if m else None

def load_pdfs(pdf_dir, cache_dir, pages):
    ids, texts = [], []
    for fn in sorted(os.listdir(pdf_dir)):
        if fn.lower().endswith(".pdf") and os.path.splitext(fn)[0].isdigit():
            ids.append(int(os.path.splitext(fn)[0]))
            texts.append(clean(ocr_pdf(os.path.join(pdf_dir, fn), cache_dir, pages)))
            print(f"\r  OCR {len(ids)} PDFs...", end="", file=sys.stderr)
    print("", file=sys.stderr)
    return ids, texts

def load_transcripts(tx_dirs):
    """逐語を読み込む。正規の 講義逐語/ サブフォルダを優先し、無ければフラットに後退。
       対応表・README・本スクリプトの提案出力など非逐語ファイルは除外する。"""
    DOC_PAT = re.compile(r"対応表|README|proposal|HANDOFF|_match|逐語-PDF")
    names, paths, texts = [], [], []
    chosen = None
    for d in tx_dirs:
        if os.path.isdir(d) and any(
            fn.lower().endswith((".txt", ".md")) and not DOC_PAT.search(fn) and not fn.startswith("_")
            for fn in os.listdir(d)):
            chosen = d
            break
    if chosen is None:
        return names, paths, texts
    for fn in sorted(os.listdir(chosen)):
        if not fn.lower().endswith((".txt", ".md")):
            continue
        if fn.startswith("_") or DOC_PAT.search(fn):
            continue
        p = os.path.join(chosen, fn)
        names.append(fn); paths.append(p)
        texts.append(clean(open(p, encoding="utf-8").read()))
    return names, paths, texts

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--subject", required=True, choices=SUBJ_DIRS)
    ap.add_argument("--root", default="inputs/jx")
    ap.add_argument("--pages", type=int, default=2, help="OCRするPDF先頭ページ数")
    ap.add_argument("--ngram", default="2,3", help="文字n-gram範囲 (例 3,3)")
    ap.add_argument("--margin", type=float, default=0.15,
                    help="CONFIDENT判定の相対余白（1位cos と 2位cos の比 1-top2/top1）")
    ap.add_argument("--validate", action="store_true", help="既存 重問逐語NN 命名で精度を検証")
    ap.add_argument("--apply", action="store_true", help="CONFIDENT層のみ git mv で改名（既定は dry-run）")
    ap.add_argument("--prefix", default=None,
                    help="改名時のファイル名ステム（既定: 科目フル名_重問逐語）。例 憲法_重問逐語")
    args = ap.parse_args()
    # 科目ディレクトリ→重問ステムの既定（他科目は実運用時に要確認）
    PREFIX_MAP = {"刑": "刑法", "憲": "憲法", "民": "民法", "商": "商法",
                  "民訴": "民訴", "刑訴": "刑訴", "行政": "行政法"}
    stem = args.prefix or (PREFIX_MAP.get(args.subject, args.subject) + "_重問逐語")
    lazy_imports()
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    base = os.path.join(args.root, SUBJ_DIR_MAP.get(args.subject, args.subject))
    pdf_dir = os.path.join(base, "重問PDF")
    tx_dirs = [os.path.join(base, "講義逐語"), base]   # サブフォルダ＋フラット
    cache_dir = os.path.join(base, "_ocr_cache")
    os.makedirs(cache_dir, exist_ok=True)
    if not os.path.isdir(pdf_dir):
        sys.exit(f"[なし] {pdf_dir} がありません")

    print(f"[1/3] OCR & 読み込み（{args.subject}）...", file=sys.stderr)
    pid, ptxt = load_pdfs(pdf_dir, cache_dir, args.pages)
    tname, tpath, ttxt = load_transcripts(tx_dirs)
    if not pid or not tname:
        sys.exit("[なし] PDF または 逐語が見つかりません")

    print(f"[2/3] 照合（PDF {len(pid)} × 逐語 {len(tname)}）...", file=sys.stderr)
    lo, hi = (int(x) for x in args.ngram.split(","))
    vec = TfidfVectorizer(analyzer="char", ngram_range=(lo, hi), min_df=1)
    X = vec.fit_transform(ptxt + ttxt)
    sim = cosine_similarity(X[len(ptxt):], X[:len(ptxt)])      # 逐語 × PDF

    if args.validate:
        top1 = top3 = n = 0
        for i, nm in enumerate(tname):
            m = re.search(r"重問逐語(\d+)", nm)
            if not m:
                continue
            n += 1; want = int(m.group(1))
            rank = [pid[j] for j in np.argsort(-sim[i])]
            top1 += rank[0] == want; top3 += want in rank[:3]
        if n:
            print(f"[検証] 重問逐語NN {n}本: top-1={top1}/{n}={top1/n:.0%}  top-3={top3}/{n}={top3/n:.0%}")
        return

    # 競合 greedy 割当：(cos, 逐語i, PDFj) 降順、両方空なら確定
    order = sorted(((sim[i, j], i, j) for i in range(len(tname)) for j in range(len(pid))),
                   key=lambda x: x[0], reverse=True)
    tx_to_pdf, pdf_taken = {}, {}
    for s, i, j in order:
        if i in tx_to_pdf or j in pdf_taken:
            continue
        tx_to_pdf[i] = (pid[j], s); pdf_taken[j] = i

    confident, review, residual = [], [], []
    for i, nm in enumerate(tname):
        rank_j = np.argsort(-sim[i])
        top1_pdf, top1_cos = pid[rank_j[0]], sim[i, rank_j[0]]
        top2_cos = sim[i, rank_j[1]] if len(rank_j) > 1 else 0.0
        relmargin = 1 - (top2_cos / top1_cos) if top1_cos > 0 else 0.0
        if i not in tx_to_pdf:
            residual.append((nm, top1_pdf, top1_cos))            # あぶれ＝総合問題/余り候補
            continue
        assigned_pdf, acos = tx_to_pdf[i]
        contested = assigned_pdf != top1_pdf
        if (not contested) and relmargin >= args.margin and top1_cos > 0:
            confident.append((nm, assigned_pdf, acos, relmargin))
        else:
            review.append((nm, assigned_pdf, acos, top1_pdf, top1_cos, relmargin, contested))
    missing_pdfs = [pid[j] for j in range(len(pid)) if j not in pdf_taken]

    # ---- レポート出力 ----
    out = os.path.join(base, "_match-proposal.md")
    L = []
    L.append(f"# {args.subject} 逐語↔PDF 照合提案（自動・要人手確認）\n")
    L.append(f"PDF {len(pid)} 本 / 逐語 {len(tname)} 本 / n-gram{args.ngram} / "
             f"CONFIDENT {len(confident)} ・ REVIEW {len(review)} ・ RESIDUAL {len(residual)} ・ 逐語欠落PDF {len(missing_pdfs)}\n")
    L.append("> **改名は自動で行わない。** CONFIDENT は `--apply` で改名可。REVIEW/RESIDUAL は"
             " PDF実物と中身を突き合わせて人手確定。生成時は冒頭で事案一致を自己照合（照合ガード）。\n")
    L.append("## CONFIDENT（高信頼・1位かつ余白十分）→ `{科目}_重問逐語NN.txt` 改名候補\n")
    L.append("| 逐語ファイル | →PDF | cos | 相対余白 |\n|--|--:|--:|--:|")
    for nm, p, c, rm in sorted(confident, key=lambda x: x[1]):
        L.append(f"| {nm} | {p:02d} | {c:.3f} | {rm:.2f} |")
    L.append("\n## REVIEW（要確認・競合または余白僅少）\n")
    L.append("| 逐語ファイル | 割当PDF | cos | 1位PDF | 1位cos | 余白 | 競合 |\n|--|--:|--:|--:|--:|--:|:--:|")
    for nm, ap_, ac, t1, t1c, rm, ct in sorted(review, key=lambda x: x[2]):
        L.append(f"| {nm} | {ap_:02d} | {ac:.3f} | {t1:02d} | {t1c:.3f} | {rm:.2f} | {'✗' if ct else ''} |")
    L.append("\n## RESIDUAL（どのPDFにも割り当たらない逐語＝総合問題/余りの候補）\n")
    L.append("| 逐語ファイル | 最近傍PDF | cos |\n|--|--:|--:|")
    for nm, p, c in sorted(residual, key=lambda x: x[2], reverse=True):
        L.append(f"| {nm} | {p:02d} | {c:.3f} |")
    L.append("\n## 逐語の付かないPDF（逐語欠落／総合問題で対象外の可能性）\n")
    L.append(", ".join(f"PDF{p:02d}" for p in sorted(missing_pdfs)) or "（なし）")
    open(out, "w", encoding="utf-8").write("\n".join(L) + "\n")

    print(f"[3/3] 提案を書き出し: {out}", file=sys.stderr)
    print(f"  CONFIDENT={len(confident)}  REVIEW={len(review)}  RESIDUAL={len(residual)}  逐語欠落PDF={len(missing_pdfs)}")
    print(f"  逐語欠落PDF: {sorted(missing_pdfs)}")
    print(f"  RESIDUAL: {[nm for nm,_,_ in residual]}")

    if args.apply:
        tx_dir = os.path.join(base, "講義逐語")
        n = 0
        for nm, p, c, rm in confident:
            src = None
            for d in tx_dirs:
                cand = os.path.join(d, nm)
                if os.path.exists(cand):
                    src = cand; break
            if not src:
                continue
            dst = os.path.join(tx_dir, f"{stem}{p:02d}.txt")
            if os.path.abspath(src) == os.path.abspath(dst):
                continue
            if os.path.exists(dst):
                print(f"  [skip] 衝突: {dst} 既存", file=sys.stderr); continue
            subprocess.run(["git", "mv", src, dst], check=False)
            n += 1
        print(f"  [apply] CONFIDENT {n} 件を改名（REVIEW/RESIDUAL は未改名・人手確認）")
    else:
        print("  （dry-run。改名するなら --apply。ただし REVIEW/RESIDUAL は必ず人手確認）")

if __name__ == "__main__":
    main()
