#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tx-lex-v11-to-v13.py ── 純 v11 LOOP-CORE _lex → v13.1.0 LOOP-CARD 決定論ラッパー。

刑TX386 で手作業込みで実施した v11→v13 の全工程を1本の CLI に固めたもの（全て決定論・
本文不変・冪等・CRLF 保持）。tx-lex-v13-recanon.py は入力に v12.2.1（inline-card シェル＋
inline エンジン）を要求するため、純 v11（ox-grid＋choice-section・inline カード無し）には
そのままでは使えない。本ラッパーが不足分（カードシェル注入・エンジン/CSS の gold 逐語移植・
DOM gap 補完）を前後に足して橋渡しする。参照元 gold＝刑TX359（canonical/GENESIS-CARD.html）。

工程（順序 LOCKED）:
  0. idempotency guard: 既に v13.1.0 実体（pbox-chip＋nb-badge＋tx-inline-card）なら NOCHANGE。
  1. prep : 各記述の問題文原文で inline-card シェル5＋空 ox-pool-explain＋tx-sysmap placeholder を注入。
           syn-lead(💡THE GIST) を slots['gist'] へ、syn-image を 🗝記憶のフック＋slots['hook'] へ移送。
           cross-column に col-warn TRAP（slots['trap']）を追加（recanon が各カードの ⚠️tx-v13-trap へ）。
  2. recanon(tx-lex-v13-recanon.build) : 統合解説昇格／📚BASIS集約／ref配線／体系マップSVG／横断／
           marking／Lexiaプール／旧部削除／gold-parity／polish。
  3. engine swap : recanon は配線しか足さないので gold の <script>2本を逐語移植（v13 インラインエンジン）。
  4. style swap  : recanon の v13b CSS delta は tx-inline-card/answer-table-panel/verdict-brief/story-panel を
           取りこぼす。gold <style> へ差し替え、AI選定パレット差分変数を末尾 :root で cascade 上書き保全。
  5. sysmap-pbox(subject自動 gizou/houka) ＋ 帰結箱除去 ＋ v131-author(kihan＋mark＋nb-badge＋viewBox532)。
  6. DOM gap 補完 : tx-sysmap-back×5 ／ #sn-combos ／ tx-inline-reveal-panel＋answer-area inline-prototype-mode
           ／ 孤立 "PART B ── …" part-title 除去。
  7. CRLF 変換で書き戻し。

入力:
  <v11_lex.html>  slots.json  data.json  [--out PATH] [--gold canonical/GENESIS-CARD.html]
  slots.json（体系マップ＋カード文・詳細は docs／--help）: subject, top_title, head_subtitle, aria,
     panels_caption, panels[5]{title,sub,color}, ox_line, cross{title,header[3],rows[[3]],kimete,throughline},
     mark{"1..5":[verdict,phrase,fix]}, gist{label:text}, hook{label:text}, trap{label:text}
     （任意）basis_refs{basis-card-id:[label,...]}＝v11 basis カードが「記述X」を本文に持たず
     recanon が配分できない時だけ、そのカードを割り当てる記述ラベルを明示（386は不要・387 law-148 で使用）。
  data.json（v131-author）: { label: {kihan, mark(印付き原文HTML・内側span は単引用)} }

検証は呼び出し側で validate-tx-core.py＋check-tx-lex-engine.py＋tx-lex-v13-stamp.py --apply を通すこと。
"""
from __future__ import annotations
import re, sys, json, argparse, importlib.util, tempfile, os
from pathlib import Path

GOLD = 'canonical/GENESIS-CARD.html'
SCRIPTS = Path(__file__).parent


class SpecialTypeError(RuntimeError):
    """5記述前提に乗らない特殊型を掛けられた時に投げる（クラッシュではなく誘導つき停止）。"""
    def __init__(self, path, reasons):
        self.path = path
        self.reasons = reasons
        super().__init__('SPECIAL_TYPE: %s は特殊型のため本ラッパー非対応（%s）'
                         % (path, ' / '.join(reasons)))


def load_mod(fname, modname):
    saved = sys.stdout
    spec = importlib.util.spec_from_file_location(modname, SCRIPTS / fname)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    # recanon 等が top-level で sys.stdout=TextIOWrapper(buffer) と再ラップする。そのまま
    # 復元すると捨てられる wrapper が GC 時に buffer を close して以後の print が壊れる。
    # detach() で buffer を切り離してから元の stdout へ戻す（"I/O operation on closed file" 対策）。
    if sys.stdout is not saved:
        try:
            sys.stdout.detach()
        except Exception:
            pass
        sys.stdout = saved
    return mod


def special_reasons(h):
    """このラッパーが扱えない特殊型かを判定して理由リストを返す（空＝単純5記述で処理可）。
    本ラッパーは 5記述・客体三分の体系マップ前提なので、記述数≠5／組合せ／穴埋めは構造的に非互換。
    そういう問題は PDF からの R 再生成（tx-v13-runner.ps1 -Regen）へ回すのが正しい（docs/tx-v13-migration-targets.md）。"""
    labels = re.findall(r'<div class="ox-row" data-stmt="([^"]*)"', h)
    if len(labels) < 5:
        labels = re.findall(r'<div class="problem-text"><span class="choice-num-inline">([^<]+)</span>', h)
    reasons = []
    if len(labels) != 5:
        reasons.append('記述数=%d（≠5・体系マップが5節客体モデルに乗らない）' % len(labels))
    if 'ものの組合せ' in h:
        reasons.append('組合せ型（ものの組合せ）')
    if ('穴埋め' in h) or ('に当てはまる' in h):
        reasons.append('穴埋め型')
    return reasons


def dedup_bref_ids(h):
    """同一カード内で同じ code（典型は case が2件）だと bref-{label}-{code} が id 重複する。
    2件目以降を bref-...-N へ一意化（case は ref-stat リンク先でないので安全）。"""
    seen = {}
    def rep(m):
        iid = m.group(1)
        seen[iid] = seen.get(iid, 0) + 1
        return ('id="%s"' % iid) if seen[iid] == 1 else ('id="%s-%d"' % (iid, seen[iid]))
    return re.sub(r'id="(bref-[^"]+)"', rep, h)


# ---------------------------------------------------------------- 1. prep
def prep(h, slots):
    """v11 に inline-card シェル／ox-pool-explain／tx-sysmap placeholder を注入し、
    syn-lead/syn-image を v13m へ移送、cross-column に col-warn TRAP を足す。"""
    labels = re.findall(r'<div class="ox-row" data-stmt="([^"]*)"', h)[:5]
    if len(labels) < 5:
        # ox-row が無い型は problem-text の choice-num-inline から
        labels = re.findall(r'<div class="problem-text"><span class="choice-num-inline">([^<]+)</span>', h)[:5]
    # ここに到達する時点で run() の特殊型ガードを通過済み（＝5記述のはず）。保険として明示メッセージで停止。
    assert len(labels) == 5, ('SPECIAL_TYPE: 記述数=%d ≠5。この決定論ラッパーは5記述専用。'
                              'tx-v13-runner.ps1 -Regen（PDF→v13）へ回すこと。labels=%r' % (len(labels), labels))

    # stmt-text 抽出（problem-text 原文）。<strong>/emphasis span 等のインライン markup は除去して
    # プレーン化する（recanon の apply_mark はフレーズ完全一致で syn-orig をマークするため、
    # markup がフレーズを分断すると marking が silent fail する＝387 ア〜エで実害）。
    stmt = {}
    for lab in labels:
        m = re.search(r'<div class="problem-text"><span class="choice-num-inline">%s</span>(.*?)</div>' % re.escape(lab), h, re.S)
        stmt[lab] = re.sub(r'<[^>]+>', '', m.group(1)).strip()

    # inline-card シェル＋sysmap placeholder（最後の problem-text 直後）
    if '<article class="tx-inline-card"' not in h:
        arts = []
        for lab in labels:
            arts.append(
                '<article class="tx-inline-card" data-stmt="%s" id="stmt-%s">'
                '<div class="tx-inline-head"><p class="tx-inline-stmt">'
                '<span class="choice-num-inline">%s</span>'
                '<span class="tx-inline-stmt-text">%s</span></p>'
                '<div aria-label="記述%sの正誤を選ぶ" class="tx-inline-actions">'
                '<button class="tx-inline-ox" data-stmt="%s" data-value="○" type="button">○</button>'
                '<button class="tx-inline-ox" data-stmt="%s" data-value="×" type="button">×</button>'
                '<span aria-live="polite" class="tx-inline-verdict"></span></div></div>'
                '<div class="tx-inline-explain" hidden></div></article>'
                % (lab, lab, lab, stmt[lab], lab, lab, lab))
        block = ('\n<div class="tx-sysmap" id="tx-sysmap"></div>\n'
                 '<div class="tx-inline-list">\n' + '\n'.join(arts) + '\n</div>\n')
        last = labels[-1]
        h = re.sub(r'(<div class="problem-text"><span class="choice-num-inline">%s</span>.*?</div>)' % re.escape(last),
                   lambda m: m.group(1) + block, h, count=1, flags=re.S)

    # ox-row に空 ox-pool-explain
    def add_pool(m):
        row = m.group(0)
        if 'ox-pool-explain' in row:
            return row
        return re.sub(r'(</span>)(\s*</div>\s*)$', r'\1\n          <div class="ox-pool-explain"></div>\2', row, count=1)
    h = re.sub(r'<div class="ox-row" data-stmt="[^"]*">.*?</div>\s*(?=<div class="ox-row"|</div>)', add_pool, h, flags=re.S)

    # syn-lead → gist / syn-image → 🗝記憶のフック（choice-N ↔ labels[N-1]）
    gist = slots.get('gist', {}); hook = slots.get('hook', {})
    for i, lab in enumerate(labels, start=1):
        sm = re.search(r'(<section class="choice-section \w+" id="choice-%d">.*?</section>)' % i, h, re.S)
        if not sm:
            continue
        sec = new = sm.group(1)
        if lab in gist:
            new = re.sub(r'(<p class="syn-lead"><span class="syn-tag">)(.*?)(</span>).*?(</p>)',
                         lambda m: m.group(1) + m.group(2) + m.group(3) + gist[lab] + m.group(4),
                         new, count=1, flags=re.S)
        if lab in hook:
            new = re.sub(r'<p class="syn-image"><span class="syn-tag">.*?</span>.*?</p>',
                         '<p class="syn-image"><span class="syn-tag">\U0001f5dd 記憶のフック</span>' + hook[lab] + '</p>',
                         new, count=1, flags=re.S)
        if new != sec:
            h = h.replace(sec, new, 1)

    # basis_refs 上書き：v11 basis カードが「記述X」を本文に持たず recanon が配分できない場合に
    # 隠しヒント span を header 直後へ注入して配分させる（recanon は refs 検出後に破棄・honbun 不変）。
    for cid, labs in slots.get('basis_refs', {}).items():
        pat = re.compile(r'(<div class="basis-card [^"]*" id="%s">\s*<div class="basis-card-header">.*?</div>)' % re.escape(cid), re.S)
        def _inj(m):
            if 'basis-ref-hint' in m.group(0):
                return m.group(0)
            hint = '<span class="basis-ref-hint" hidden>' + ' '.join('記述%s' % l for l in labs) + '</span>'
            return m.group(1) + hint
        h = pat.sub(_inj, h, count=1)

    # cross-column に col-warn TRAP（recanon が tx-v13-trap へ）。
    # v11 が既に別形式の col-warn TRAP（例 <strong>TRAP 1</strong>＝記述ラベル無し）を持つ場合でも、
    # recanon は「TRAP N（記述X）」形式しか解析しないので、その形式が未存在なら注入する（誤 skip 防止）。
    trap = slots.get('trap', {})
    if trap and not re.search(r'<strong>TRAP \d+（記述', h):
        th = '\n' + '\n'.join(
            '<p class="col-warn"><strong>TRAP %d（記述%s）</strong>%s</p>' % (i + 1, lab, trap[lab])
            for i, lab in enumerate(labels) if lab in trap) + '\n'
        # cross-column-sec は recanon が削除する。その </section> 直前へ確実に挿入
        # （recanon の col-warn 抽出は文書全体を走査するので位置は section 内であれば足りる）。
        cm = re.search(r'(<section class="section" id="cross-column-sec">.*?)(</section>)', h, re.S)
        if cm:
            h = h[:cm.start()] + cm.group(1) + th + cm.group(2) + h[cm.end():]
    return h


# ---------------------------------------------------------------- 3. engine swap
def engine_swap(h, gold):
    g = [m.group(0) for m in re.finditer(r'<script\b[^>]*>.*?</script>', gold, re.S)]
    hs = [(m.start(), m.end()) for m in re.finditer(r'<script\b[^>]*>.*?</script>', h, re.S)]
    if len(g) != 2 or len(hs) != 2:
        raise RuntimeError('script count mismatch gold=%d file=%d' % (len(g), len(hs)))
    h = h[:hs[1][0]] + g[1] + h[hs[1][1]:]
    h = h[:hs[0][0]] + g[0] + h[hs[0][1]:]
    for s in re.findall(r'<script\b[^>]*>.*?</script>', h, re.S):
        if '</' + 'body>' in s:
            raise RuntimeError('body-close literal in script')
    return h


# ---------------------------------------------------------------- 4. style swap + palette 保全
def _color_vars(style):
    d = {}
    for m in re.finditer(r'(--[a-z0-9-]+)\s*:\s*([^;]+);', style):
        k = m.group(1)
        if k.startswith('--font') or k.startswith('--fs'):
            continue
        d.setdefault(k, m.group(2).strip())
    return d


def style_swap(h, gold):
    h_full = h[h.find('<style'):h.rfind('</style>') + len('</style>')]
    g_full = gold[gold.find('<style'):gold.rfind('</style>') + len('</style>')]
    mv = _color_vars(h[h.find('<style'):h.rfind('</style>')])
    gv = _color_vars(gold[gold.find('<style'):gold.rfind('</style>')])
    diff = {k: v for k, v in mv.items() if gv.get(k) != v}
    ov = ('\n/* === AI選定パレット保全（末尾上書き＝cascade勝ち） === */\n:root{\n'
          + ''.join('  %s: %s;\n' % (k, v) for k, v in sorted(diff.items())) + '}\n')
    g_new = g_full[:-len('</style>')] + ov + '</style>'
    return h.replace(h_full, g_new, 1)


# ---------------------------------------------------------------- 5b. 帰結箱除去
def remove_kekka_box(h):
    return re.sub(r'<g transform="translate\(750,548\)"><rect x="-330".*?本問の帰結.*?</g>', '', h, flags=re.S, count=1)


# ---------------------------------------------------------------- 6. DOM gap 補完
REVEAL_PANEL = (
    '<div class="tx-inline-reveal-panel">\n'
    '<p>各記述の○×をこの場で選ぶと、裏側の Lexia 用 OX グリッドにも同じ回答が入ります。全記述を選ぶと採点できます。周回確認だけなら、全選択せずに解説だけ閲覧できます。</p>\n'
    '<button aria-expanded="false" class="tx-inline-browse-btn" type="button">解説だけ閲覧</button>\n'
    '<button class="tx-inline-reveal-btn" disabled="" type="button">解答を表示</button>\n'
    '<span class="tx-inline-result" hidden=""></span>\n</div>\n')


def dom_fill(h, backmod):
    # tx-sysmap-back ×5
    h, bstats = backmod.process_html(h)
    ins = bstats.get('inserted', 0)
    # #sn-combos（sn-body 先頭）
    if 'id="sn-combos"' not in h:
        h = h.replace('<div class="sn-body">', '<div class="sn-body">\n        <div class="sn-combos" id="sn-combos"></div>', 1)
    # reveal-panel＋inline-prototype-mode
    if 'class="tx-inline-reveal-panel"' not in re.sub(r'<style.*?</style>', '', h, flags=re.S):
        m = re.search(r'<div class="answer-area" id="answer-area"', h)
        if m:
            h = h[:m.start()] + REVEAL_PANEL + h[m.start():]
            h = h.replace('<div class="answer-area" id="answer-area"', '<div class="answer-area inline-prototype-mode" id="answer-area"', 1)
    # 孤立 PART B part-title 除去（「記述別解説」「肢別解説」等の表記ゆれを一般化して除去。
    # ただし「PART B+ ──」は G40 対象外なので巻き込まない＝"PART B ── " の空白付きだけを対象）
    h = re.sub(r'\s*<!--[^>]*?PART B ── (?:記述別解説|肢別解説).*?-->\s*', '\n', h, flags=re.S)
    h = re.sub(r'\s*<div class="part-title">PART B ── [^<]*</div>\s*', '\n', h, count=1)
    return h, ins


# ---------------------------------------------------------------- main
def is_v131(h):
    return ('class="pbox-chip"' in h and 'class="nb-badge"' in h and '<article class="tx-inline-card"' in h)


def run(path, slots, data, out=None, gold_path=GOLD, force=False):
    raw = Path(path).read_bytes()
    crlf = b'\r\n' in raw[:9000]
    h = raw.decode('utf-8').replace('\r\n', '\n')
    log = []
    if is_v131(h):
        log.append('NOCHANGE (already v13.1.0)')
        return h, log, crlf
    # 特殊型ガード：5記述前提が崩れる問題はここで明示停止し、正しい経路（PDF→R再生成）へ誘導する。
    reasons = special_reasons(h)
    if reasons and not force:
        raise SpecialTypeError(path, reasons)

    gold = Path(gold_path).read_text(encoding='utf-8')
    recanon = load_mod('tx-lex-v13-recanon.py', 'tx_lex_v13_recanon')
    pbox = load_mod('tx-lex-sysmap-pbox.py', 'tx_lex_sysmap_pbox')
    v131 = load_mod('tx-lex-v131-author.py', 'tx_lex_v131_author')
    backmod = load_mod('tx-lex-sysmap-back.py', 'tx_lex_sysmap_back')

    # 1. prep
    h = prep(h, slots); log.append('prep: cards+pool+placeholder+gist/hook/trap')

    # 2. recanon（一時ファイル経由）
    with tempfile.TemporaryDirectory() as td:
        ip = os.path.join(td, 'interm.html'); op = os.path.join(td, 'out.html')
        Path(ip).write_text(h, encoding='utf-8', newline='\n')
        recanon.build(ip, slots, out=op)
        h = Path(op).read_text(encoding='utf-8')
    log.append('recanon: v13-verdict=%d basis-item=%d bref=%d' % (h.count('tx-v13-verdict'), h.count('class="tx-basis-item '), h.count('id="bref-')))

    # 3. engine swap
    h = engine_swap(h, gold); log.append('engine swapped (gold <script>x2)')

    # 4. style swap + palette
    h = style_swap(h, gold); log.append('style swapped + palette preserved')

    # 5. pbox → 帰結箱除去 → v131-author
    h, st = pbox.process(h); log.append('pbox: %s' % st)
    h = remove_kekka_box(h); log.append('kekka-box removed')
    data = {str(k): v for k, v in data.items()}
    h, stats = v131.process(h, data); log.append('v131-author: nb-badge=%d brief-mark=%d' % (stats['nodes'], stats['rows']))

    # 6. DOM gap
    h, ins = dom_fill(h, backmod); log.append('dom-fill: sysmap-back+%d, sn-combos, reveal-panel, partB-title removed' % ins)

    # 7. bref id 一意化（同カード複数 case の重複 id 解消）
    h = dedup_bref_ids(h)

    return h, log, crlf


def main():
    ap = argparse.ArgumentParser(description='純 v11 _lex → v13.1.0 LOOP-CARD 決定論ラッパー')
    ap.add_argument('html')
    ap.add_argument('slots')
    ap.add_argument('data')
    ap.add_argument('--out', default=None)
    ap.add_argument('--gold', default=GOLD)
    ap.add_argument('--force', action='store_true',
                    help='特殊型ガードを無視して強行（体系マップ破綻の恐れ・非推奨）')
    a = ap.parse_args()
    slots = json.loads(Path(a.slots).read_text(encoding='utf-8'))
    data = json.loads(Path(a.data).read_text(encoding='utf-8'))
    try:
        h, log, crlf = run(a.html, slots, data, out=a.out, gold_path=a.gold, force=a.force)
    except SpecialTypeError as e:
        sys.stderr.write(
            '[SKIP-SPECIAL] %s\n'
            '  理由: %s\n'
            '  → この決定論ラッパーは5記述・客体三分モデル専用です。特殊型は PDF から\n'
            '     `pwsh scripts/tx-v13-runner.ps1 -Subject 刑 -Regen -FromNumber N -ToNumber N` で最新v13へ再生成し、\n'
            '     構造は近い合格実例（穴埋め=刑TX368 / 組合せ=刑TX089・174・218・256 / 見解=刑TX290）に倣ってください。\n'
            '     どうしても強行するなら --force（体系マップが破綻し得ます）。\n'
            % (a.html, ' / '.join(e.reasons)))
        sys.exit(3)
    outp = a.out or a.html
    # CRLF 保持（元が CRLF なら CRLF で書き戻す）
    data_out = (h.replace('\n', '\r\n') if crlf else h).encode('utf-8')
    Path(outp).write_bytes(data_out)
    for l in log:
        print('  ' + l)
    bare = data_out.count(b'\n') - data_out.count(b'\r\n')
    print('[WROTE] %s  bytes=%d  bareLF=%d' % (outp, len(data_out), bare))


if __name__ == '__main__':
    main()
