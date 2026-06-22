#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ariadne-graft-athena-deep.py — ARIADNE 深掘り層へ「論点・条文・判例・学説」をアテナ(JX)から移植（verbatim graft・spec §11）

狙い：ARIADNE 深掘り層の 論点/条文/判例/学説 を、私が蒸留し直す（創作・ドリフトのリスク）のではなく、
検証済み正典 ATHENA(JX) の **完全プロファイルをそのまま移植**して法的正確性を担保し、文字どおりアテナ級にする。

移植するもの（ATHENA から balanced 単位で抽出）：
  - 論点抽出 `<div class="card" id="issue-extraction">…</div>`
  - 条文 完全プロファイル `<section class="ref-entry" id="ref-stat-…">…</section>` ×N
  - 判例 完全プロファイル `<section class="ref-entry" id="ref-case-…">…</section>` ×N
  - 学説一覧     `<section class="ref-entry" id="ref-doctrine-…">…</section>` ×N
  （用語 ref-term は対象外＝ARIADNE コア層に1行定義があるため）

サニタイズ：
  - `.back-refs`（本編アンカーへの逆リンク＝ARIADNE に無い）を除去
  - graft 後の最終 id 集合に解決しない `<a href="#…">` は `<span>` へ unwrap（dead link 化を防ぐ）
  - graft 内の相互リンク（条文↔判例 等）は live なので維持（ARIADNE 末尾 JS が details 内でもジャンプ）

ARIADNE 側の 規範(box-norm) と「アテナで詳しく」ボタンは温存し、論点/条文/判例/学説 だけ graft で差し替える。
scoped CSS（.athena-graft）を1度だけ注入（ATHENA のクラスを ARIADNE 内で安全に描画）。

使い方:
  python scripts/ariadne-graft-athena-deep.py 刑JX001            # 1問 graft（dry-run 表示なし＝直接書込）
  python scripts/ariadne-graft-athena-deep.py 刑JX001 --check    # 書かずに統計のみ
"""
import argparse, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARIADNE_DIR = ROOT / "outputs" / "ux" / "000_ARIADNE"
JX_DIR = ROOT / "outputs" / "001_JX"
XREF_ANCHOR = ".xref{color:var(--a-head); font-weight:700}"
GRAFT_MARK = "ATHENA-GRAFT"

GRAFT_CSS = """
/* ==== ATHENA-GRAFT : 刑TX328 の本物の型（basis-card）に条文判例学説用語を流し込む（見た目そのまま・scoped） ====
   ＝画像模倣ではなく TX328 の HTML 型（.basis-card / -header / -body）を直接使い、テキストを流し込む。
   フォント＝TX328 同一（本文 Yu Mincho 明朝・見出し Shippori・判旨 Zen Old Mincho・条文 Noto Serif・
   ラベル Zen Kaku・表頭/バッジ Zen Maru）。文字色 #2E4953／accent #4E8597／判旨 #D78A8A。 */
.athena-graft{margin:10px 0 2px; color:#2E4953}

/* セクション章扉 */
.athena-graft .graft-h{font-family:"Zen Maru Gothic","Hiragino Maru Gothic ProN","Yu Gothic Medium",sans-serif; font-weight:800; font-size:.96rem; letter-spacing:.04em; color:#4E8597; background:linear-gradient(90deg,rgba(78,133,151,.10),transparent); border-left:4px solid #4E8597; border-radius:4px; padding:7px 0 7px 12px; margin:26px 0 0; display:flex; align-items:center; gap:9px}
.athena-graft .graft-note{font-family:"Zen Kaku Gothic Antique","Yu Gothic","Hiragino Sans",sans-serif; font-size:.75rem; color:#5b6f78; margin:3px 0 12px 16px; line-height:1.7}

/* ===== TX328 .basis-card 本物の型 ===== */
.athena-graft .basis-card{background:#fff; border:1px solid #D6C9DC; border-radius:6px; padding:0; margin:14px 0; overflow:hidden; box-shadow:0 2px 8px rgba(46,73,83,.07)}
.athena-graft .basis-card.statute-card{background:#eef6f6; border-left:5px solid #7fb1ad}
.athena-graft .basis-card.case-card{background:#fdf1f1; border-left:5px solid #ee9a9a}
.athena-graft .basis-card.doctrine-card{border-left:5px solid #D6C9DC}
.athena-graft .basis-card.term-card{border-left:5px solid #D6C9DC}
.athena-graft .basis-card-header{background:#F5EFF6; padding:12px 22px; font-family:"Shippori Mincho B1","Yu Mincho","Hiragino Mincho ProN","Noto Serif JP",serif; font-weight:700; font-size:1.08em; color:#4A3D54; border-bottom:1px solid #D6C9DC; letter-spacing:.04em; display:flex; align-items:center; gap:9px; flex-wrap:wrap}
.athena-graft .basis-card.case-card .basis-card-header{background:#fdc9c9; color:#7a2e2e; border-bottom-color:#f3b3b3}
.athena-graft .basis-card-body{padding:18px 22px 16px; font-family:"Yu Mincho","游明朝","Hiragino Mincho ProN","Noto Serif JP",serif; font-weight:600; font-size:.92rem; line-height:1.95; color:#2E4953}
.athena-graft .basis-card-body p{margin:0 0 .8em; text-indent:1em}
.athena-graft .basis-card-body p:last-child{margin-bottom:0}
/* ★重要度バッジ＝TX328 §19 のマイルドゴールド（地#feea84・文字/★ #6e5410・金枠#e0c75a）で統一 */
.athena-graft .freq-badge,.athena-graft .freq-badge.freq-high,.athena-graft .freq-badge.freq-mid,.athena-graft .freq-badge.freq-low{display:inline-block; margin-left:auto; font-family:"Zen Maru Gothic","Hiragino Maru Gothic ProN","Yu Gothic Medium",sans-serif; font-size:.72rem; padding:2px 9px; border-radius:4px; font-weight:700; letter-spacing:.06em; white-space:nowrap; background:#feea84; color:#6e5410; border:1px solid #e0c75a}

/* 論点カード（issue） */
.athena-graft .card{background:#fff; border:1px solid #D6C9DC; border-left:5px solid #4E8597; border-radius:6px; padding:14px 20px 16px; margin:14px 0; box-shadow:0 2px 8px rgba(46,73,83,.07); font-family:"Yu Mincho","游明朝","Hiragino Mincho ProN","Noto Serif JP",serif; font-weight:600; font-size:.92rem; line-height:1.95; color:#2E4953}
.athena-graft .card h3{font-family:"Shippori Mincho B1","Yu Mincho","Hiragino Mincho ProN","Noto Serif JP",serif; font-size:1.12rem; color:#2E4953; margin:0 0 10px; padding-bottom:7px; border-bottom:1.5px solid #D6C9DC; letter-spacing:.03em}
.athena-graft .card > h4{font-family:"Shippori Mincho B1","Yu Mincho","Hiragino Mincho ProN","Noto Serif JP",serif; font-size:1.02rem; color:#4E8597; margin:14px 0 7px; padding-left:11px; border-left:4px solid #4E8597}

/* 小見出し h5 ＝ TX328 .kd-label（Zen Kaku・役割色） */
.athena-graft h5{display:inline-block; font-family:"Zen Kaku Gothic Antique","Yu Gothic","Hiragino Sans",sans-serif; font-size:.84em; font-weight:700; letter-spacing:.06em; margin:14px 0 6px; padding:1px 10px; border:1px solid #D6C9DC; border-left:3px solid #4E8597; border-radius:3px; background:#EDE2EF; color:#4A3D54}
.athena-graft h5.r-hogo{background:rgba(94,140,140,.14); border-left-color:#5E8C8C; color:#37625f}
.athena-graft h5.r-shushi{background:rgba(142,110,154,.16); border-left-color:#8E6E9A; color:#5f4a69}
.athena-graft h5.r-shatei{background:rgba(79,138,91,.15); border-left-color:#4F8A5B; color:#2f6b3c}
.athena-graft h5.r-youken{background:#EDE2EF; border-left-color:#4A3D54; color:#4A3D54}
.athena-graft h5.r-ate{background:rgba(194,152,47,.16); border-left-color:#c2982f; color:#856219}
.athena-graft h5.r-chui{background:rgba(160,80,122,.13); border-left-color:#A0507A; color:#8a3d63}

/* 条文文言（statute）＝ Noto Serif */
.athena-graft blockquote.statute{margin:8px 0 12px; padding:12px 16px; border-radius:6px; font-family:"Noto Serif JP","Yu Mincho","Hiragino Mincho ProN",serif; font-size:.95rem; line-height:1.95; color:#2E4953; background:#fbfdfd; border:1px solid #cfe6e2; border-left:4px solid #6b7280}
.athena-graft blockquote.statute p{margin:0; text-indent:0}

/* 判旨（case）＝ TX328 .judgment-text（Zen Old Mincho・⚖判旨 pinkバッジ=--mid #D78A8A・等幅） */
.athena-graft blockquote.case{position:relative; margin:20px 0 12px; padding:14px 16px 12px; border-radius:6px; font-family:"Zen Old Mincho","Yu Mincho","Hiragino Mincho ProN","Noto Serif JP",serif; font-weight:700; font-size:.95rem; line-height:1.95; color:#2E4953; background:#fff; border:1px solid #ee9a9a; border-top:2px solid #D78A8A}
.athena-graft blockquote.case::before{content:"⚖ 判旨"; position:absolute; top:-12px; left:16px; font-family:"Source Code Pro","Consolas","Menlo",monospace; font-size:.72rem; font-weight:700; letter-spacing:.04em; color:#fff; background:#D78A8A; padding:4px 13px; border-radius:3px; box-shadow:0 1px 3px rgba(0,0,0,.16)}
.athena-graft blockquote.case p{margin:0; text-indent:0}

/* テーブル ＝ TX328（th=accent teal #4E8597・td罫 #88AEBA・ゼブラ #F0E8ED） */
.athena-graft table{width:100%; border-collapse:collapse; margin:9px 0 5px; font-size:.9rem; font-family:"Yu Mincho","游明朝","Hiragino Mincho ProN","Noto Serif JP",serif; background:#fff}
.athena-graft th,.athena-graft td{border:1px solid #88AEBA; padding:10px 12px; vertical-align:top; text-align:left; line-height:1.7}
.athena-graft th{background:#d6e8e7; color:#1f4d4a; font-family:"Zen Maru Gothic","Hiragino Maru Gothic ProN","Yu Gothic Medium",sans-serif; font-weight:700; letter-spacing:.04em; white-space:nowrap}
.athena-graft tr:nth-child(even) td{background:#F0E8ED}
.athena-graft td[rowspan],.athena-graft th[rowspan]{vertical-align:middle; text-align:center}

/* 核心論点ボックス ＝ TX328 .note（青・ℹ NOTE・Zen Kaku） */
.athena-graft .key-box{position:relative; background:#e7f1ff; border:1px solid rgba(21,101,192,.30); border-radius:8px; padding:14px 16px 12px; margin:12px 0; font-family:"Zen Kaku Gothic Antique","Yu Gothic","Hiragino Sans",sans-serif; font-weight:500}
.athena-graft .key-box::before{content:"🔑 KEY"; display:block; font-family:"Source Code Pro","Consolas","Menlo",monospace; font-weight:700; font-size:.72rem; letter-spacing:.1em; color:#0d47a1; margin-bottom:7px}
.athena-graft .key-box ol{margin:0; padding-left:1.4em}
.athena-graft .key-box li{margin:.3em 0; line-height:1.8}

/* インライン重要度（本文中の rank-* / tan-*）＝ freq-badge 階調 */
.athena-graft .rank-A,.athena-graft .rank-B,.athena-graft .rank-C,.athena-graft .tan{display:inline-block; font-family:"Zen Maru Gothic","Hiragino Maru Gothic ProN","Yu Gothic Medium",sans-serif; font-weight:700; font-size:.78em; padding:1px 8px; border-radius:4px; letter-spacing:.06em; vertical-align:1px}
.athena-graft .rank-A,.athena-graft .tan-super{color:#fff; background:#4E8597}
.athena-graft .rank-B,.athena-graft .tan-high{color:#2E4953; background:#88AEBA}
.athena-graft .rank-C,.athena-graft .tan-std{color:#2E4953; background:#DCE8E8}
.athena-graft .tan{margin-left:4px}
/* 本文強調 */
.athena-graft .hl-super{background:linear-gradient(transparent 58%,#cfe7ec 58%); font-weight:700; padding:0 2px}
.athena-graft .hl-high{background:linear-gradient(transparent 60%,#d8e8c8 60%); font-weight:700; padding:0 2px}
.athena-graft .hl-std{background:linear-gradient(transparent 66%,#e9dfe9 66%); padding:0 2px}
.athena-graft strong{color:#1f3640; font-weight:700}
.athena-graft a.xref,.athena-graft a.ref-stat{color:#1a2540; font-weight:700; text-decoration:none; background:rgba(20,40,90,.06); border-bottom:1.5px solid rgba(20,40,90,.4); padding:0 2px; border-radius:2px}
.athena-graft a.ref-case{color:#2a1018; font-weight:700; text-decoration:none; background:rgba(120,30,50,.07); border-bottom:1.5px solid rgba(120,30,50,.5); padding:0 2px; border-radius:2px}
.athena-graft a.xref:hover,.athena-graft a.ref-stat:hover{color:#fff; background:#1a2540}
.athena-graft .xref-dead{color:#2E4953; font-weight:600}
.athena-graft .back-to-toc{display:none}
"""


def balanced_div(html, start_idx):
    """start_idx の <div ...> から対応する </div> までを返す（ネスト対応）。"""
    open_re = re.compile(r'<div\b', re.I); close_re = re.compile(r'</div>', re.I)
    i = start_idx; depth = 0
    while i < len(html):
        mo = open_re.search(html, i); mc = close_re.search(html, i)
        if mc is None: break
        if mo and mo.start() < mc.start():
            depth += 1; i = mo.end()
        else:
            depth -= 1; i = mc.end()
            if depth == 0:
                return html[start_idx:i]
    return None


def merge_empty_cells(html):
    """ATHENA の表は「効果」等を1行目だけ書き2行目以降を空セルにする（rowspan のつもり）。
    空 <td></td> を直上の同列セルへ rowspan 結合し、空白行に見える問題を解消する。
    既存 rowspan/colspan を含む表は触らない（誤結合防止）。"""
    def fix_table(mt):
        tbl = mt.group(0)
        if 'rowspan' in tbl or 'colspan' in tbl:
            return tbl
        rows = re.findall(r'<tr[^>]*>(.*?)</tr>', tbl, re.S)
        parsed = []
        for rrow in rows:
            cells = re.findall(r'<(t[hd])((?:\s[^>]*)?)>(.*?)</\1>', rrow, re.S)
            parsed.append([list(c) for c in cells])
        ncol = max((len(r) for r in parsed), default=0)
        if ncol == 0:
            return tbl
        delete = set(); span = {}
        for col in range(ncol):
            owner = None
            for row in range(len(parsed)):
                if col >= len(parsed[row]):
                    owner = None; continue
                inner = parsed[row][col][2]
                if inner.strip() == '':
                    if owner is not None:
                        span[owner] = span.get(owner, 1) + 1
                        delete.add((row, col))
                    # 直上に親が無い空セルはそのまま
                else:
                    owner = (row, col)
        if not delete:
            return tbl
        out = []
        for row in range(len(parsed)):
            cs = []
            for col in range(len(parsed[row])):
                if (row, col) in delete:
                    continue
                tag, attrs, inner = parsed[row][col]
                rs = span.get((row, col))
                if rs and rs > 1:
                    attrs = attrs + f' rowspan="{rs}"'
                cs.append(f'<{tag}{attrs}>{inner}</{tag}>')
            out.append('<tr>' + ''.join(cs) + '</tr>')
        return '<table>' + ''.join(out) + '</table>'
    return re.sub(r'<table[^>]*>.*?</table>', fix_table, html, flags=re.S)


def strip_backrefs(block):
    block = re.sub(r'<div class="back-refs">.*?</div>', '', block, flags=re.S)
    block = re.sub(r'<a [^>]*class="back-to-toc"[^>]*>.*?</a>', '', block, flags=re.S)
    return block


# TX .kd-label の役割色へ：ATHENA の h5 見出し文言から役割クラスを推定して付与
ROLE_MAP = [('保護法益', 'r-hogo'), ('立法趣旨', 'r-shushi'), ('制度趣旨', 'r-shushi'), ('趣旨', 'r-shushi'),
            ('射程', 'r-shatei'), ('要件', 'r-youken'), ('効果', 'r-youken'), ('体系的位置', 'r-youken'), ('性質', 'r-youken'),
            ('答案', 'r-ate'), ('使い方', 'r-ate'), ('具体化', 'r-ate'), ('分解', 'r-ate'),
            ('注意', 'r-chui'), ('批判', 'r-chui'), ('改正', 'r-chui'), ('関連', 'r-chui'), ('対立', 'r-chui')]

def tag_h5_roles(block):
    def repl(m):
        text = m.group(1)
        cls = 'r-youken'
        for kw, c in ROLE_MAP:
            if kw in text:
                cls = c; break
        return f'<h5 class="kd-label {cls}">{text}</h5>'
    return re.sub(r'<h5>(.*?)</h5>', repl, block, flags=re.S)


# ATHENA の ref-entry を TX328 の本物の型（basis-card / basis-card-header / basis-card-body）へ流し込む
TYPE_CLS = {'stat': 'statute-card', 'case': 'case-card', 'doctrine': 'doctrine-card', 'term': 'term-card'}
TYPE_ICON = {'stat': '📜', 'case': '⚖', 'doctrine': '📖', 'term': '📕'}
TAN_FREQ = {'tan-super': 'freq-high', 'tan-high': 'freq-mid', 'tan-std': 'freq-low'}

RANK_FREQ = {'rank-A': ('freq-high', '★★★'), 'rank-B': ('freq-mid', '★★'), 'rank-C': ('freq-low', '★')}

def to_basis_card(raw, kind):
    """ref-entry → TX328 の本物の型 <div class="basis-card {type}-card"><div class="basis-card-header">…</div><div class="basis-card-body">…</div></div>
    題名＝先頭の h4、無ければ先頭の h5（学説・用語は h5 が題名）。本文側の残り h5 だけ kd-label 化する。"""
    m_id = re.search(r'<section class="ref-entry" id="([^"]+)">', raw)
    cid = m_id.group(1) if m_id else ''
    inner = raw[m_id.end():] if m_id else raw
    inner = re.sub(r'</section>\s*$', '', inner).strip()
    # 題名要素：h4 優先、無ければ先頭 h5
    mt = re.search(r'<h4[^>]*>(.*?)</h4>', inner, re.S) or re.search(r'<h5[^>]*>(.*?)</h5>', inner, re.S)
    title_raw = mt.group(1) if mt else ''
    body = (inner[:mt.start()] + inner[mt.end():]) if mt else inner
    # 重要度 → freq-badge（短答★ tan、無ければ rank-A/B/C）
    freq_html = ''
    tan = re.search(r'<span class="tan ([^"]+)">(.*?)</span>', title_raw, re.S)
    if tan:
        freq_html = f'<span class="freq-badge {TAN_FREQ.get(tan.group(1).split()[0], "freq-mid")}">{tan.group(2).strip()}</span>'
    else:
        rk = re.search(r'class="(rank-[ABC])"', title_raw)
        if rk:
            fc, star = RANK_FREQ[rk.group(1)]
            freq_html = f'<span class="freq-badge {fc}">{star}</span>'
    title = re.sub(r'<span class="tan[^"]*">.*?</span>', '', title_raw, flags=re.S)
    title = re.sub(r'<[^>]+>', '', title).strip()
    body = merge_empty_cells(tag_h5_roles(body.strip()))
    header = f'<div class="basis-card-header">{TYPE_ICON[kind]} {title}{freq_html}</div>'
    return (f'<div class="basis-card {TYPE_CLS[kind]}" id="{cid}">\n'
            f'{header}\n<div class="basis-card-body">\n{body}\n</div>\n</div>')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("id", help="問題ID（例 刑JX001）")
    ap.add_argument("--check", action="store_true", help="書かずに統計のみ")
    args = ap.parse_args()
    code = args.id

    ar = list(ARIADNE_DIR.glob(f"*/{code}_ARIADNE.html"))
    jx = list(JX_DIR.glob(f"*/{code}.html"))
    if not ar: sys.exit(f"ARIADNE 出力が見つからない: {code}_ARIADNE.html")
    if not jx: sys.exit(f"ATHENA(JX) が見つからない: {code}.html（移植元が必要）")
    arp, jxp = ar[0], jx[0]
    a = jxp.read_text(encoding="utf-8")
    r = arp.read_text(encoding="utf-8")

    # --- 抽出（balanced 単位） ---
    mi = re.search(r'<div class="card" id="issue-extraction">', a)
    issue = balanced_div(a, mi.start()) if mi else None
    entries = re.findall(r'<section class="ref-entry" id="ref-(?:stat|case|doctrine|term)-[^"]+">.*?</section>', a, re.S)
    stats = [e for e in entries if 'id="ref-stat' in e]
    cases = [e for e in entries if 'id="ref-case' in e]
    docs  = [e for e in entries if 'id="ref-doctrine' in e]
    terms = [e for e in entries if 'id="ref-term' in e]
    print(f"[抽出] 論点:{1 if issue else 0} 条文:{len(stats)} 判例:{len(cases)} 学説:{len(docs)} 用語:{len(terms)}")
    if args.check:
        return

    # --- サニタイズ ---
    issue = merge_empty_cells(tag_h5_roles(strip_backrefs(issue))) if issue else ""
    stats = [to_basis_card(strip_backrefs(e), 'stat') for e in stats]
    cases = [to_basis_card(strip_backrefs(e), 'case') for e in cases]
    docs  = [to_basis_card(strip_backrefs(e), 'doctrine') for e in docs]
    terms = [to_basis_card(strip_backrefs(e), 'term') for e in terms]

    def sect(kind, title, sub, items):
        if not items: return ""
        body = "\n".join(items)
        return (f'      <div class="graft-h gh-{kind}">{title}</div>\n'
                f'      <div class="graft-note">{sub}</div>\n{body}\n')

    graft = ['    <div class="athena-graft">']
    if issue:
        graft.append(f'      <div class="graft-h gh-issue">🧭 論点（アテナの自動抽出・配点付き）</div>\n'
                     f'      <div class="graft-note">本問の論点・適用条文・配点をアテナ正典からそのまま移植。</div>\n{issue}')
    graft.append(sect("stat", "📜 条文 完全プロファイル", "全文／体系的位置／要件効果／立法趣旨・保護法益／関連条文網／答案での使い方（アテナ正典から移植）", stats))
    graft.append(sect("case", "⚖ 判例 完全プロファイル", "事案／判旨／補足／射程／後続判例／答案での使い方（アテナ正典から移植）", cases))
    graft.append(sect("doc", "📖 学説一覧", "各説の論拠・帰結・批判（アテナ正典から移植）", docs))
    graft.append(sect("term", "📕 用語集", "本問の重要概念の定義・趣旨（アテナ正典から移植）", terms))
    graft.append('    </div>')
    graft_html = "\n".join(x for x in graft if x.strip())

    # --- ARIADNE 深掘り層を再構成（規範 box-norm とジャンプボタンは温存・論点条文判例学説のみ graft へ） ---
    deep = re.search(r'(<details id="deep-dive">.*?<div class="deep-body">)(.*?)(</div>\s*</details>)', r, re.S)
    if not deep: sys.exit("ARIADNE 深掘り層が見つからない")
    head, body, tail = deep.group(1), deep.group(2), deep.group(3)
    # 規範（box-norm 群）を温存：最初の h4(規範) ～ 最初の graft対象 h4 直前 まで
    norm = re.search(r'(<h4>.*?§ 規範.*?</h4>(?:\s*<div class="box box-norm">.*?</div>)+)', body, re.S)
    norm_block = norm.group(1) if norm else ""
    lead = re.search(r'<div class="athena-lead">.*?</div>', body, re.S)
    lead_block = ('<div class="athena-lead">本層は<b>アテナ(JX正典)から移植</b>した論点・条文・判例・学説の完全プロファイル。'
                  '法的正確性はアテナと同一。規範は実戦用に要約、知識はアテナ密度のまま。さらに網羅事典は末尾「アテナで詳しく」へ。</div>'
                  ) if not lead else lead.group(0)
    btn = re.search(r'(<!-- B: .*?)?<a class="go-athena".*?</a>\s*<div class="deep-note">.*?</div>', body, re.S)
    btn_block = btn.group(0) if btn else ""

    new_body = "\n      " + "\n      ".join(filter(None, [lead_block, norm_block])) + "\n" + graft_html + "\n      " + btn_block + "\n    "

    # --- dead xref の unwrap（最終 id 集合に無いアンカーを span 化） ---
    pre = r[:deep.start()] + head + new_body + tail + r[deep.end():]
    final_ids = set(re.findall(r'id="([^"]+)"', pre))
    def fix_anchor(m):
        href = m.group('href')
        if href.startswith('#') and href[1:] not in final_ids:
            return f'<span class="xref-dead">{m.group("inner")}</span>'
        return m.group(0)
    # graft 範囲だけ置換（全文に副作用を出さない）
    new_block_full = head + new_body + tail
    new_block_fixed = re.sub(r'<a\b[^>]*href="(?P<href>#[^"]*)"[^>]*>(?P<inner>.*?)</a>', fix_anchor, new_block_full, flags=re.S)
    out = r[:deep.start()] + new_block_fixed + r[deep.end():]

    # --- scoped CSS 注入（1度だけ） ---
    if GRAFT_MARK not in out:
        out = out.replace(XREF_ANCHOR, XREF_ANCHOR + "\n" + GRAFT_CSS, 1)

    arp.write_text(out, encoding="utf-8")
    print(f"[書込] {arp}  ({len(out.encode())//1024}KB)")


if __name__ == "__main__":
    main()
