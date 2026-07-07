#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tx-classify-type.py ── TX `_lex` を「単純5択 vs 特殊型」に分類し版・PDF有無と突合する監査器。

なぜ要るか（2026-07-07）:
  特殊型（≠5記述・組合せ・穴埋め・見解A/B・事例Ⅰ/Ⅱ）を最新 v13.1.0 へ上げる作業の
  台帳を機械生成する。決定論ラッパー `tx-lex-v11-to-v13.py` は 5記述固定なので特殊型は
  「PDFからのR再生成」経路（tx-v13-runner.ps1 -Regen）へ回す必要があり、どれが特殊型で
  どれがローカルPDFを持つか（=いま再生成可能か）を一覧化しないと運用できない。

版判定の単一情報源:
  フッター feature-tag `TX v<major.minor.patch> LOOP-CARD`（無い旧世代は v11 系）を正典とする。
  最新版は下記 LATEST_VERSION 定数。版が上がったらここだけ直す（runner と規約を合わせる）。

特殊型シグナル（baseline 刑TX001＝単純5択で 0 ヒットを確認済み）:
  R rows!=5 : `class="ox-row` の数が 5 でない（8穴埋め等の構造的特殊）
  C 組合せ  : `ものの組合せ`
  F 穴埋め  : `穴埋め` または `に当てはまる`
  E 事例    : `事例Ⅰ`
  O 見解(弱): `見解Ａ` / `見解の対立` / `説によれば`（学説対比型・弱シグナル）
  ※ `空欄`/`見解`/`学説` 単体は全文に出る定型で判別に使わない。

使い方:
  python -X utf8 scripts/tx-classify-type.py                # 全体サマリ＋backlog（人間可読）
  python -X utf8 scripts/tx-classify-type.py --backlog      # backlog のファイル一覧のみ
  python -X utf8 scripts/tx-classify-type.py --json out.json # 機械可読 dump
  python -X utf8 scripts/tx-classify-type.py --regenerable  # backlog かつローカルPDFあり（R対象）だけ
  python -X utf8 scripts/tx-classify-type.py --file <lex>   # 1ファイルの判定を表示（分類の単発確認）
"""
from __future__ import annotations
import re, sys, json, argparse
from pathlib import Path

# 版：最新の正典タグ。版を上げたらここを直す（tx-v13-runner.ps1 の $LatestVerTag と一致させる）。
LATEST_VERSION = '13.1.0'

UX_ROOT = Path('outputs/ux/000_TX')
IN_ROOT = Path('inputs/000_TX')

VER_RE = re.compile(r'TX v(\d+\.\d+\.\d+)\s+LOOP-CARD')
OXROW_RE = re.compile(r'class="ox-row')
NUM_RE = re.compile(r'(\d+)_lex$')

# 特殊型シグナル（タグ, 説明, 判定関数）
def _rows(h):
    return len(OXROW_RE.findall(h))

SPECIAL_MARKERS = {
    'C': ('組合せ', lambda h: 'ものの組合せ' in h),
    'F': ('穴埋め', lambda h: ('穴埋め' in h) or ('に当てはまる' in h)),
    'E': ('事例', lambda h: '事例Ⅰ' in h),
    'O': ('見解(弱)', lambda h: ('見解Ａ' in h) or ('見解の対立' in h) or ('説によれば' in h)),
}


def classify(path: Path):
    h = path.read_text(encoding='utf-8', errors='replace')
    m = VER_RE.search(h)
    version = m.group(1) if m else '11.x'   # feature-tag 無し＝旧世代（v11 系）
    rows = _rows(h)
    tags = []
    if rows != 5:
        tags.append('R')
    for t, (_desc, fn) in SPECIAL_MARKERS.items():
        if fn(h):
            tags.append(t)
    tags = [t for t in ['R', 'C', 'F', 'E', 'O'] if t in tags]  # 安定順
    is_special = bool(tags)
    is_latest = (version == LATEST_VERSION)
    stem = path.stem  # 例 刑TX089_lex
    nm = NUM_RE.search(stem)
    num = int(nm.group(1)) if nm else None
    folder = path.parent.name  # 例 001_刑法
    pdf = (IN_ROOT / folder / f'{num}.pdf') if num is not None else None
    pdf_present = bool(pdf and pdf.exists())
    return {
        'file': str(path).replace('\\', '/'),
        'id': stem[:-4],           # 刑TX089
        'num': num,
        'folder': folder,
        'version': version,
        'ox_rows': rows,
        'special_tags': tags,      # 例 ['R','C','F']
        'is_special': is_special,
        'is_latest': is_latest,
        'pdf_present': pdf_present,
    }


def scan():
    files = sorted(UX_ROOT.glob('*/*_lex.html'))
    return [classify(p) for p in files]


def fmt_row(r):
    return '%-9s v%-7s rows=%-2d %-8s %s' % (
        r['id'], r['version'], r['ox_rows'],
        ''.join(r['special_tags']) or '-',
        'PDF' if r['pdf_present'] else 'DRIVE-ONLY')


def main():
    ap = argparse.ArgumentParser(description='TX _lex 特殊型分類＋backlog監査')
    ap.add_argument('--backlog', action='store_true', help='特殊型 かつ 非最新版 の一覧のみ')
    ap.add_argument('--regenerable', action='store_true', help='backlog かつ ローカルPDFあり のみ')
    ap.add_argument('--json', metavar='OUT', help='機械可読 dump を書き出す')
    ap.add_argument('--file', metavar='LEX', help='1ファイルだけ判定表示')
    a = ap.parse_args()

    if a.file:
        r = classify(Path(a.file))
        print(json.dumps(r, ensure_ascii=False, indent=2))
        return

    rows = scan()
    backlog = [r for r in rows if r['is_special'] and not r['is_latest']]
    regenerable = [r for r in backlog if r['pdf_present']]
    drive_only = [r for r in backlog if not r['pdf_present']]

    if a.json:
        Path(a.json).write_text(json.dumps({
            'latest_version': LATEST_VERSION,
            'total': len(rows), 'backlog': len(backlog),
            'regenerable': len(regenerable), 'drive_only': len(drive_only),
            'items': rows,
        }, ensure_ascii=False, indent=2), encoding='utf-8')
        print('[WROTE] %s  total=%d backlog=%d regenerable=%d drive_only=%d'
              % (a.json, len(rows), len(backlog), len(regenerable), len(drive_only)))
        return

    if a.regenerable:
        for r in regenerable:
            print(fmt_row(r))
        print('\n再生成可能（backlog かつ ローカルPDF）: %d 本' % len(regenerable))
        return
    if a.backlog:
        for r in backlog:
            print(fmt_row(r))
        print('\nbacklog（特殊型 かつ 非 v%s）: %d 本' % (LATEST_VERSION, len(backlog)))
        return

    # 既定：サマリ
    by_ver = {}
    for r in rows:
        by_ver[r['version']] = by_ver.get(r['version'], 0) + 1
    special = [r for r in rows if r['is_special']]
    print('=== TX _lex 監査（最新版 = v%s）===' % LATEST_VERSION)
    print('総数            : %d' % len(rows))
    print('版内訳          : ' + ' / '.join('v%s=%d' % (k, v) for k, v in sorted(by_ver.items())))
    print('特殊型（全体）  : %d' % len(special))
    print('  最新版        : %d' % len([r for r in special if r['is_latest']]))
    print('  backlog       : %d  （うち PDFあり=%d / Driveのみ=%d）'
          % (len(backlog), len(regenerable), len(drive_only)))
    # 特殊型バケツ内訳（重複あり）
    buckets = {'R': 0, 'C': 0, 'F': 0, 'E': 0, 'O': 0}
    for r in backlog:
        for t in r['special_tags']:
            buckets[t] += 1
    labels = {'R': 'rows≠5', 'C': '組合せ', 'F': '穴埋め', 'E': '事例', 'O': '見解(弱)'}
    print('backlogバケツ   : ' + ' / '.join('%s=%d' % (labels[k], buckets[k]) for k in ['R', 'C', 'F', 'E', 'O']))
    print('\n--backlog で一覧、--regenerable でR対象、--json で機械可読出力。')


if __name__ == '__main__':
    main()
