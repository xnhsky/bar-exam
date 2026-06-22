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
/* ==== ATHENA-GRAFT : アテナ移植を高級誌面に作り込む（scoped・マイルドライナー自由構成＋役割別フォント） ====
   ■ 色＝マイルドライナーから系統割付（自由構成）：論点=Violet／条文=Blue／判例=Pink／学説=Green／用語=Yellow
   ■ フォント＝役割別：明朝(f-disp)＝題名・法文/判旨｜丸ゴ(f-soft)＝章扉・ラベル・小見出し・表頭｜
                      角ゴ(f-body)＝本文・解説・表本文｜等幅(f-code)＝コード的ラベル(§法文/⚖判旨/短答) */
.athena-graft{margin:10px 0 2px; --gc:#f6f4ef; --gcb:var(--line-2); --gcd:var(--a-head); --gcm:var(--a-mid)}
/* 系統トークン（カード内で継承） */
.athena-graft .card{--gc:var(--ml-violet); --gcb:var(--ml-violet-b); --gcd:var(--ml-violet-d); --gcm:var(--ml-violet-m)}
.athena-graft section[id^="ref-stat"]{--gc:var(--ml-blue); --gcb:var(--ml-blue-b); --gcd:var(--ml-blue-d); --gcm:var(--ml-blue-m)}
.athena-graft section[id^="ref-case"]{--gc:var(--ml-pink); --gcb:var(--ml-pink-b); --gcd:var(--ml-pink-d); --gcm:var(--ml-pink-m)}
.athena-graft section[id^="ref-doctrine"]{--gc:var(--ml-green); --gcb:var(--ml-green-b); --gcd:var(--ml-green-d); --gcm:var(--ml-green-m)}
.athena-graft section[id^="ref-term"]{--gc:var(--ml-yellow); --gcb:var(--ml-yellow-b); --gcd:var(--ml-yellow-d); --gcm:var(--ml-yellow-m)}

/* 章扉バンド（系統色の帯＝多色誌面）｜フォント＝丸ゴシック(ラベル役割) */
.athena-graft .graft-h{position:relative; font-family:var(--f-soft); color:#fff; font-weight:800; font-size:1rem; letter-spacing:.07em; background:linear-gradient(135deg,var(--bg1,var(--a-head)),var(--bg2,var(--a-foot))); border-radius:13px 13px 0 0; padding:13px 17px 12px 21px; margin:26px 0 0; display:flex; align-items:center; gap:10px; box-shadow:0 4px 13px rgba(70,58,80,.17), inset 0 1px 0 rgba(255,255,255,.22)}
.athena-graft .graft-h::before{content:""; position:absolute; left:9px; top:50%; transform:translateY(-50%); width:4px; height:1.15em; border-radius:3px; background:rgba(255,255,255,.78)}
.athena-graft .gh-issue{--bg1:#6A4D86; --bg2:#46315c}
.athena-graft .gh-stat {--bg1:#2F6A8C; --bg2:#1d465e}
.athena-graft .gh-case {--bg1:#A84E74; --bg2:#76304f}
.athena-graft .gh-doc  {--bg1:#4E7536; --bg2:#344f22}
.athena-graft .gh-term {--bg1:#8a7320; --bg2:#574610}
/* 章扉キャプション｜フォント＝角ゴシック(読む文) */
.athena-graft .graft-note{font-family:var(--f-body); font-size:.745rem; color:var(--ink-soft); background:#fff; border:1px solid var(--line-2); border-top:none; border-radius:0 0 13px 13px; padding:8px 17px 9px; margin:0 0 12px; box-shadow:0 3px 9px rgba(70,58,80,.06); line-height:1.7}

/* プロファイルカード（系統色の薄面＋立体＋左スパイン）｜本文フォント＝角ゴシック */
.athena-graft .card,.athena-graft .ref-entry{position:relative; background:var(--gc); border:1px solid var(--gcb); border-left:5px solid var(--gcd); border-radius:14px; padding:16px 19px 17px; margin:14px 0; line-height:1.92; font-family:var(--f-body); font-size:.9rem; color:#322c38; box-shadow:0 4px 13px rgba(70,58,80,.08), inset 0 1px 0 rgba(255,255,255,.55)}
.athena-graft .ref-entry::after{content:""; position:absolute; inset:0; border-radius:14px; pointer-events:none; box-shadow:inset 0 0 0 1px rgba(255,255,255,.35)}

/* タイトル類｜フォント＝明朝(格式・法律文) */
.athena-graft h3{font-family:var(--f-disp); font-size:1.12rem; color:var(--gcd); margin:0 0 5px; letter-spacing:.04em}
.athena-graft .ref-entry > h4{font-family:var(--f-disp); font-size:1.05rem; font-weight:800; color:#2c2632; margin:-1px 0 11px; padding:0 0 9px; border-bottom:1.5px solid var(--gcb); display:flex; align-items:center; gap:9px; flex-wrap:wrap; letter-spacing:.02em; line-height:1.5}
.athena-graft .card > h4{font-family:var(--f-disp); font-size:1rem; color:var(--gcd); margin:15px 0 7px; padding:3px 0 3px 12px; border-left:4px solid var(--gcd); letter-spacing:.02em}

/* 小見出し h5 ＝アイブロウ｜フォント＝丸ゴシック(ラベル) */
.athena-graft h5{font-family:var(--f-soft); font-size:.745rem; font-weight:800; letter-spacing:.09em; color:var(--gcd); margin:15px 0 4px; padding-left:17px; position:relative}
.athena-graft h5::before{content:""; position:absolute; left:1px; top:.16em; width:9px; height:9px; border-radius:2px; background:var(--gcd); transform:rotate(45deg); box-shadow:0 1px 2px rgba(0,0,0,.18)}
.athena-graft p{margin:.42em 0; text-indent:0}

/* 法文／判旨＝白の引用紙パネル｜フォント＝明朝(法律文)・ラベルは等幅 */
.athena-graft blockquote.statute,.athena-graft blockquote.case{position:relative; margin:13px 0 12px; padding:15px 17px 13px; border-radius:11px; font-family:var(--f-disp); font-size:.96rem; line-height:1.98; color:#2f2935; background:linear-gradient(180deg,#ffffff,rgba(255,255,255,.86)); border:1px solid var(--gcb); border-left:4px solid var(--gcd); box-shadow:inset 0 1px 0 rgba(255,255,255,.8), 0 2px 7px rgba(70,58,80,.06)}
.athena-graft blockquote.statute::before{content:"§ 法文"; position:absolute; top:-9px; left:14px; font-family:var(--f-code); font-size:.62rem; font-weight:700; letter-spacing:.1em; color:#fff; background:var(--gcd); padding:2px 8px; border-radius:5px; box-shadow:0 1px 3px rgba(0,0,0,.18)}
.athena-graft blockquote.case::before{content:"⚖ 判旨"; position:absolute; top:-9px; left:14px; font-family:var(--f-code); font-size:.62rem; font-weight:700; letter-spacing:.08em; color:#fff; background:var(--gcd); padding:2px 8px; border-radius:5px; box-shadow:0 1px 3px rgba(0,0,0,.18)}
.athena-graft blockquote p{margin:0; text-indent:0}

/* 誌面テーブル（系統色ヘッダ帯＋ゼブラ）｜表頭=丸ゴシック／本文=角ゴシック */
.athena-graft table{width:100%; border-collapse:separate; border-spacing:0; margin:10px 0 5px; font-size:.84rem; font-family:var(--f-body); background:#fff; border:1px solid var(--gcb); border-radius:10px; overflow:hidden; box-shadow:0 2px 7px rgba(70,58,80,.06)}
.athena-graft td{padding:8px 12px; text-align:left; vertical-align:top; border-bottom:1px solid var(--gcb)}
.athena-graft th{padding:8px 12px; text-align:left; vertical-align:top; border-bottom:1px solid var(--gcb); background:linear-gradient(135deg,var(--gcd),var(--gcm)); color:#fff; font-family:var(--f-soft); font-weight:700; letter-spacing:.03em; white-space:nowrap; box-shadow:inset 0 1px 0 rgba(255,255,255,.2)}
.athena-graft tr:nth-child(even) td{background:rgba(0,0,0,.022)}
.athena-graft tr:last-child td{border-bottom:none}

/* 論点カードの核心ボックス（金の囲み）｜ラベル=丸ゴシック */
.athena-graft .key-box{position:relative; background:linear-gradient(180deg,var(--gd-soft),#fff); border:1px solid var(--gd-line); border-left:4px solid var(--gd); border-radius:12px; padding:14px 16px 13px; margin:12px 0; box-shadow:0 3px 9px rgba(160,120,30,.10)}
.athena-graft .key-box::before{content:"★ 核心論点（配点の高い順）"; display:block; font-family:var(--f-soft); font-weight:800; font-size:.74rem; letter-spacing:.05em; color:var(--gd-deep); margin-bottom:6px}
.athena-graft .key-box ol{margin:0; padding-left:1.4em}
.athena-graft .key-box li{margin:.3em 0; font-size:.88rem; line-height:1.8}

/* 重要度バッジ（艶あり立体ピル）｜丸ゴシック */
.athena-graft .rank-A,.athena-graft .rank-B,.athena-graft .rank-C{display:inline-block; font-family:var(--f-soft); font-weight:800; font-size:.82em; padding:1px 9px; border-radius:7px; letter-spacing:.03em; box-shadow:0 1px 2px rgba(0,0,0,.16), inset 0 1px 0 rgba(255,255,255,.4); vertical-align:1px}
.athena-graft .rank-A{color:#fff; background:linear-gradient(135deg,#c45069,#8a1f3a)}
.athena-graft .rank-B{color:#fff; background:linear-gradient(135deg,#d6a83f,#9c7016)}
.athena-graft .rank-C{color:#fff; background:linear-gradient(135deg,#8a93a0,#5b6470)}
.athena-graft .tan{display:inline-block; font-family:var(--f-code); font-weight:700; font-size:.64rem; padding:2px 8px; border-radius:6px; letter-spacing:.04em; vertical-align:1px; color:#fff; box-shadow:0 1px 2px rgba(0,0,0,.16), inset 0 1px 0 rgba(255,255,255,.35)}
.athena-graft .tan-super{background:linear-gradient(135deg,#b53a52,#8a1f1f)}
.athena-graft .tan-high{background:linear-gradient(135deg,#d6a83f,#a8761c)}
.athena-graft .tan-std{background:linear-gradient(135deg,#7faaaa,#557d7d)}
/* 本文蛍光（マイルドライナー下線） */
.athena-graft .hl-super{background:linear-gradient(transparent 58%,var(--hl-gold) 58%); font-weight:700; padding:0 2px}
.athena-graft .hl-high{background:linear-gradient(transparent 60%,var(--hl-green) 60%); font-weight:700; padding:0 2px}
.athena-graft .hl-std{background:linear-gradient(transparent 66%,var(--hl-blue) 66%); padding:0 2px}
.athena-graft strong{color:#241f2a; font-weight:800}
.athena-graft a.xref{color:var(--gcd); font-weight:700; text-decoration:none; border-bottom:1.5px solid var(--gcb); padding:0 1px}
.athena-graft a.xref:hover{background:rgba(255,255,255,.6)}
.athena-graft .xref-dead{color:#322c38; font-weight:600}
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


def strip_backrefs(block):
    block = re.sub(r'<div class="back-refs">.*?</div>', '', block, flags=re.S)
    block = re.sub(r'<a [^>]*class="back-to-toc"[^>]*>.*?</a>', '', block, flags=re.S)
    return block


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
    issue = strip_backrefs(issue) if issue else ""
    stats = [strip_backrefs(e) for e in stats]
    cases = [strip_backrefs(e) for e in cases]
    docs  = [strip_backrefs(e) for e in docs]
    terms = [strip_backrefs(e) for e in terms]

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
