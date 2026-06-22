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
/* ==== ATHENA-GRAFT : TX(GENESIS) 参考条文判例の作りを正典に再現（scoped・役割別フォント） ====
   ■ TX 由来の構築：白の basis-card／型別の左罫＋ヘッダ淡色帯／kd-label 役割色の小見出し／
     条文引用パネル／判旨ティールバッジ／freq-badge 重要度／TX テーブル。
   ■ フォント役割：明朝(f-disp)=題名・条文/判旨｜丸ゴ(f-soft)=見出し・ラベル・表頭・バッジ｜
                  角ゴ(f-body)=本文・解説・表本文｜等幅(f-code)=コード的ラベル */
.athena-graft{margin:10px 0 2px}

/* セクション見出し（TX セクション見出し風・左アクセント） */
.athena-graft .graft-h{font-family:var(--f-soft); font-weight:800; font-size:.96rem; letter-spacing:.04em; color:var(--a-head); background:linear-gradient(90deg,rgba(0,0,0,.035),transparent); border-left:4px solid var(--a-head); border-radius:4px; padding:7px 0 7px 12px; margin:26px 0 0; display:flex; align-items:center; gap:9px}
.athena-graft .graft-note{font-family:var(--f-body); font-size:.75rem; color:var(--ink-soft); margin:3px 0 12px 16px; line-height:1.7}

/* プロファイルカード ＝ TX .basis-card（白・角丸・型別左罫・ヘッダ帯） */
.athena-graft .card,.athena-graft .ref-entry{background:#fff; border:1px solid var(--line-2); border-radius:10px; padding:0 19px 16px; margin:14px 0; overflow:hidden; box-shadow:0 2px 8px rgba(70,58,80,.06); font-family:var(--f-body); font-size:.9rem; line-height:1.92; color:#2f2935}
.athena-graft .ref-entry{border-left:5px solid #6b7280}
.athena-graft section[id^="ref-case"]{border-left-color:var(--a-mid)}
.athena-graft section[id^="ref-doctrine"]{border-left-color:#8E6E9A}
.athena-graft section[id^="ref-term"]{border-left-color:#5b6470}

/* カードヘッダ ＝ TX .basis-card-header（型別淡色帯・明朝） */
.athena-graft .ref-entry > h4{font-family:var(--f-disp); font-weight:700; font-size:1.05em; color:#2c2632; letter-spacing:.03em; margin:0 -19px 14px; padding:12px 19px; background:#f3f4f6; border-bottom:1.5px solid var(--line-2); display:flex; align-items:center; gap:9px; flex-wrap:wrap}
.athena-graft section[id^="ref-case"] > h4{background:#ffeef1}
.athena-graft section[id^="ref-doctrine"] > h4{background:#f1ecf6}
.athena-graft section[id^="ref-term"] > h4{background:#eef0f2}

/* 論点カード（issue）＝ TX card 風 */
.athena-graft .card{padding:14px 18px 16px; border-left:5px solid var(--a-head)}
.athena-graft .card h3{font-family:var(--f-disp); font-size:1.1rem; color:var(--a-head); margin:0 0 10px; padding-bottom:7px; border-bottom:1.5px solid var(--line-2); letter-spacing:.03em}
.athena-graft .card > h4{font-family:var(--f-disp); font-size:1rem; color:var(--a-head); margin:14px 0 7px; padding-left:11px; border-left:4px solid var(--a-head)}

/* 小見出し h5 ＝ TX .kd-label（役割色・インラインタグ）｜丸ゴシック */
.athena-graft h5{display:inline-block; font-family:var(--f-soft); font-size:.78rem; font-weight:700; letter-spacing:.05em; margin:14px 0 5px; padding:1px 11px; border:1px solid var(--line-2); border-left:3px solid #5b6470; border-radius:3px; background:#eef0f2; color:#3c4450}
.athena-graft h5.r-hogo{background:rgba(94,140,140,.14); border-left-color:#5E8C8C; color:#37625f}
.athena-graft h5.r-shushi{background:rgba(142,110,154,.16); border-left-color:#8E6E9A; color:#5f4a69}
.athena-graft h5.r-shatei{background:rgba(79,138,91,.15); border-left-color:#4F8A5B; color:#2f6b3c}
.athena-graft h5.r-youken{background:#eef0f2; border-left-color:#5b6470; color:#3c4450}
.athena-graft h5.r-ate{background:rgba(194,152,47,.16); border-left-color:#c2982f; color:#856219}
.athena-graft h5.r-chui{background:rgba(160,80,122,.13); border-left-color:#A0507A; color:#8a3d63}
.athena-graft p{margin:.4em 0; text-indent:0}

/* 条文文言（statute）＝ TX 条文引用風（白パネル・左罫・明朝） */
.athena-graft blockquote.statute{margin:8px 0 12px; padding:12px 16px; border-radius:8px; font-family:var(--f-disp); font-size:.95rem; line-height:1.95; color:#2f2935; background:#f7f8fa; border:1px solid var(--line-2); border-left:4px solid #6b7280}
.athena-graft blockquote.statute p{margin:0; text-indent:0}

/* 判旨（case）＝ TX .judgment-text（【判旨】ティールバッジ・明朝） */
.athena-graft blockquote.case{position:relative; margin:18px 0 12px; padding:14px 16px 12px; border-radius:8px; font-family:var(--f-disp); font-weight:600; font-size:.95rem; line-height:1.95; color:#2f2935; background:#fff; border:1px solid var(--a-mid); border-top:2px solid var(--ai)}
.athena-graft blockquote.case::before{content:"判旨"; position:absolute; top:-11px; left:14px; font-family:var(--f-soft); font-size:.68rem; font-weight:800; letter-spacing:.08em; color:#fff; background:linear-gradient(135deg,var(--ai),var(--ai-deep)); padding:2px 10px; border-radius:4px; box-shadow:0 1px 3px rgba(0,0,0,.18)}
.athena-graft blockquote.case p{margin:0; text-indent:0}

/* テーブル ＝ TX 風（淡ヘッダ・けい線・角丸クリップ）｜表頭=丸ゴ／本文=角ゴ */
.athena-graft table{width:100%; border-collapse:separate; border-spacing:0; margin:9px 0 5px; font-size:.84rem; font-family:var(--f-body); background:#fff; border:1px solid var(--line-2); border-radius:8px; overflow:hidden}
.athena-graft td{padding:7px 11px; vertical-align:top; border-bottom:1px solid var(--line-2)}
.athena-graft th{padding:7px 11px; vertical-align:top; border-bottom:1.5px solid var(--line-2); background:#f3f4f6; color:#2c2632; font-family:var(--f-soft); font-weight:700; white-space:nowrap; text-align:left}
.athena-graft tr:last-child td{border-bottom:none}

/* 核心論点ボックス ＝ TX .note 風 */
.athena-graft .key-box{background:#e7f1ff; border:1px solid rgba(21,101,192,.30); border-radius:8px; padding:13px 16px 12px; margin:12px 0}
.athena-graft .key-box::before{content:"\2139 \6838\5fc3\8ad6\70b9\ff08\914d\70b9\306e\9ad8\3044\9806\ff09"; display:block; font-family:var(--f-soft); font-weight:700; font-size:.74rem; letter-spacing:.04em; color:#1a4f8a; margin-bottom:6px}
.athena-graft .key-box ol{margin:0; padding-left:1.35em}
.athena-graft .key-box li{margin:.28em 0; font-size:.88rem; line-height:1.8}

/* 重要度 ＝ TX .freq-badge（rank/tan を 高/中/低 に写像）｜丸ゴ */
.athena-graft .rank-A,.athena-graft .rank-B,.athena-graft .rank-C,.athena-graft .tan{display:inline-block; font-family:var(--f-soft); font-weight:700; font-size:.74em; padding:2px 9px; border-radius:4px; letter-spacing:.06em; vertical-align:1px}
.athena-graft .rank-A{color:#fff; background:#c0506a}
.athena-graft .rank-B{color:#5a3d00; background:#f3d99a}
.athena-graft .rank-C{color:#33404d; background:#dfe3e8}
.athena-graft .tan{color:#fff; margin-left:4px}
.athena-graft .tan-super{background:#b53a52}
.athena-graft .tan-high{background:#c2982f}
.athena-graft .tan-std{background:#79a6a6}
/* 本文蛍光（薄） */
.athena-graft .hl-super{background:linear-gradient(transparent 58%,var(--hl-gold) 58%); font-weight:700; padding:0 2px}
.athena-graft .hl-high{background:linear-gradient(transparent 60%,var(--hl-green) 60%); font-weight:700; padding:0 2px}
.athena-graft .hl-std{background:linear-gradient(transparent 66%,var(--hl-blue) 66%); padding:0 2px}
.athena-graft strong{color:#241f2a; font-weight:700}
.athena-graft a.xref{color:#1a2540; font-weight:700; text-decoration:none; background:rgba(20,40,90,.06); border-bottom:1.5px solid rgba(20,40,90,.4); padding:0 2px; border-radius:2px}
.athena-graft a.xref:hover{color:#fff; background:#1a2540}
.athena-graft .xref-dead{color:#2f2935; font-weight:600}
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
    issue = tag_h5_roles(strip_backrefs(issue)) if issue else ""
    stats = [tag_h5_roles(strip_backrefs(e)) for e in stats]
    cases = [tag_h5_roles(strip_backrefs(e)) for e in cases]
    docs  = [tag_h5_roles(strip_backrefs(e)) for e in docs]
    terms = [tag_h5_roles(strip_backrefs(e)) for e in terms]

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
