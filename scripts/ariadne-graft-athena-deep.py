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
/* ==== ATHENA-GRAFT : アテナ(JX)から移植した 論点/条文/判例/学説 の scoped 描画 ==== */
.athena-graft{margin:6px 0 2px}
.athena-graft .graft-h{font-family:var(--f-soft); color:#fff; font-weight:800; font-size:.86rem; letter-spacing:.04em; background:linear-gradient(135deg,var(--a-head),var(--a-foot)); border-radius:9px 9px 0 0; padding:9px 14px; margin:18px 0 0; display:flex; align-items:center; gap:8px}
.athena-graft .graft-note{font-family:var(--f-soft); font-size:.76rem; color:var(--ink-soft); background:var(--sheet); border:1px solid var(--line-2); border-top:none; border-radius:0 0 9px 9px; padding:6px 14px 7px; margin:0 0 8px}
.athena-graft .card,.athena-graft .ref-entry{background:#fff; border:1px solid var(--line-2); border-radius:11px; padding:14px 17px; margin:11px 0; box-shadow:0 2px 7px rgba(70,58,80,.05); line-height:1.9; font-family:var(--f-body); font-size:.9rem; color:var(--ink)}
.athena-graft .ref-entry{border-left:4px solid var(--a-mid)}
.athena-graft section[id^="ref-stat"]{border-left-color:#6b7280}
.athena-graft section[id^="ref-case"]{border-left-color:var(--ai)}
.athena-graft section[id^="ref-doctrine"]{border-left-color:var(--li)}
.athena-graft section[id^="ref-term"]{border-left-color:var(--gd)}
.athena-graft h3{font-family:var(--f-disp); font-size:1.04rem; color:var(--a-head); margin:0 0 8px}
.athena-graft h4{font-family:var(--f-disp); font-size:.98rem; color:var(--ink); margin:0 0 7px; display:flex; align-items:center; gap:8px; flex-wrap:wrap; border:none; padding:0}
.athena-graft h5{font-family:var(--f-soft); font-size:.82rem; font-weight:800; color:var(--li-deep); margin:13px 0 3px; padding-left:9px; border-left:3px solid var(--li-line)}
.athena-graft p{margin:.4em 0; text-indent:0}
.athena-graft blockquote.statute,.athena-graft blockquote.case{margin:8px 0; padding:11px 15px; border-radius:9px; font-family:var(--f-disp); line-height:1.95}
.athena-graft blockquote.statute{background:#f3f4f6; border-left:4px solid #6b7280}
.athena-graft blockquote.case{background:var(--ai-soft); border-left:4px solid var(--ai)}
.athena-graft blockquote p{margin:0; text-indent:0}
.athena-graft table{width:100%; border-collapse:collapse; margin:8px 0; font-size:.85rem; font-family:var(--f-body)}
.athena-graft th,.athena-graft td{border:1px solid var(--line-2); padding:6px 9px; text-align:left; vertical-align:top}
.athena-graft th{background:var(--li-soft); color:var(--li-deep); font-family:var(--f-soft); font-weight:700; white-space:nowrap}
.athena-graft .key-box{background:var(--gd-soft); border:1px solid var(--gd-line); border-radius:10px; padding:11px 14px 11px 16px; margin:10px 0}
.athena-graft .key-box ol{margin:0; padding-left:1.3em}
.athena-graft .key-box li{margin:.25em 0; font-size:.88rem}
.athena-graft .rank-A,.athena-graft .rank-B,.athena-graft .rank-C{font-weight:800; padding:0 4px; border-radius:3px; font-family:var(--f-soft); font-size:.92em}
.athena-graft .rank-A{color:#8a1f1f; background:#f6d5d5}
.athena-graft .rank-B{color:#7a5810; background:#fbeec9}
.athena-graft .rank-C{color:#445; background:#e3e7ec}
.athena-graft .tan{display:inline-block; font-family:var(--f-soft); font-weight:800; font-size:.68rem; padding:1px 7px; border-radius:4px; letter-spacing:.04em; vertical-align:1px; margin-left:4px}
.athena-graft .tan-super{background:#8a1f1f; color:#fff}
.athena-graft .tan-high{background:#c2982f; color:#fff}
.athena-graft .tan-std{background:#79a6a6; color:#fff}
.athena-graft .hl-super{background:linear-gradient(transparent 58%,var(--hl-gold) 58%); font-weight:700; padding:0 2px}
.athena-graft .hl-high{background:linear-gradient(transparent 60%,var(--hl-green) 60%); font-weight:700; padding:0 2px}
.athena-graft .hl-std{background:linear-gradient(transparent 66%,var(--hl-blue) 66%); padding:0 2px}
.athena-graft a.xref{color:var(--a-head); font-weight:700; text-decoration:none; border-bottom:1.5px solid var(--li-line)}
.athena-graft a.xref:hover{background:var(--li-soft)}
.athena-graft .xref-dead{color:var(--ink); font-weight:600}
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

    def sect(title, sub, items):
        if not items: return ""
        body = issue if items == "ISSUE" else "\n".join(items)
        return (f'      <div class="graft-h">{title}</div>\n'
                f'      <div class="graft-note">{sub}</div>\n{body}\n')

    graft = ['    <div class="athena-graft">']
    if issue:
        graft.append(f'      <div class="graft-h">🧭 論点（アテナの自動抽出・配点付き）</div>\n'
                     f'      <div class="graft-note">本問の論点・適用条文・配点をアテナ正典からそのまま移植。</div>\n{issue}')
    graft.append(sect("📜 条文 完全プロファイル", "全文／体系的位置／要件効果／立法趣旨・保護法益／関連条文網／答案での使い方（アテナ正典から移植）", stats))
    graft.append(sect("⚖ 判例 完全プロファイル", "事案／判旨／補足／射程／後続判例／答案での使い方（アテナ正典から移植）", cases))
    graft.append(sect("📖 学説一覧", "各説の論拠・帰結・批判（アテナ正典から移植）", docs))
    graft.append(sect("📕 用語集", "本問の重要概念の定義・趣旨（アテナ正典から移植）", terms))
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
