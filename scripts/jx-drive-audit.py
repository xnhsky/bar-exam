#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
jx-drive-audit.py — JX 成果物の git↔Drive 配置ドリフト監査

目的:
    JX HTML は「git コミット（§9 永続化）」と「Drive 配置（jx-deploy.ps1 ⑥）」の
    2 系統で保全する。バッチが DRY-RUN だったり配置⑥前に中断すると、
    「git にはあるが Drive に無い」不一致が無検出で残る（2026-06-11 の刑JX034-036 事故）。
    本スクリプトは両系統を突き合わせ、ドリフトを一覧して exit 1 を返す検知係。

検査対象:
    outputs/jx/{接頭辞}JX/*.html （= ローカル成果物。git 管理）
        ↕
    H:\\マイドライブ\\CATALINA＿G共有\\■予備試験進行中\\2 JX_論 文\\{NNN_科目}\\*.html

使い方:
    python scripts/jx-drive-audit.py            # 全7科目を監査
    python scripts/jx-drive-audit.py --subject 刑
    python scripts/jx-drive-audit.py --fix-cmd  # 漏れを埋める jx-deploy コマンドも表示

Drive 未マウント時は監査不能として exit 2（CI で握りつぶさないため明示終了）。
"""
import argparse
import sys
from pathlib import Path

# Windows コンソール(cp932)でも絵文字・記号を出せるよう UTF-8 を強制
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

# 科目接頭辞 → (outputs サブフォルダ名, Drive 科目フォルダ名)
SUBJECTS = {
    '刑':   ('刑JX',   '001_刑法'),
    '刑訴': ('刑訴JX', '002_刑事訴訟法'),
    '民':   ('民JX',   '003_民法'),
    '商':   ('商JX',   '004_商法'),
    '民訴': ('民訴JX', '005_民事訴訟法'),
    '行政': ('行政JX', '006_行政法'),
    '憲':   ('憲JX',   '007_憲法'),
}

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUTS_JX = REPO_ROOT / 'outputs' / 'jx'
DRIVE_ROOT_CAND = Path(r'H:\マイドライブ\CATALINA＿G共有\■予備試験進行中\2 JX_論 文')


def html_ids(folder: Path, prefix: str):
    """folder 直下の {prefix}NNN.html のファイル名集合（拡張子付き）を返す。"""
    if not folder.is_dir():
        return set()
    return {p.name for p in folder.glob(f'{prefix}*.html')}


def main():
    ap = argparse.ArgumentParser(description='JX git↔Drive 配置ドリフト監査')
    ap.add_argument('--subject', choices=list(SUBJECTS), help='1 科目に限定（既定: 全7科目）')
    ap.add_argument('--fix-cmd', action='store_true', help='漏れを埋める jx-deploy コマンドを表示')
    args = ap.parse_args()

    if not DRIVE_ROOT_CAND.is_dir():
        print(f'[ABORT] Drive 未マウント: {DRIVE_ROOT_CAND}', file=sys.stderr)
        print('  → H: をマウントしてから再実行（監査不能のため exit 2）', file=sys.stderr)
        return 2

    targets = [args.subject] if args.subject else list(SUBJECTS)
    total_missing_drive = 0
    total_missing_local = 0
    fix_cmds = []

    print('=' * 64)
    print('JX git↔Drive 配置ドリフト監査')
    print('=' * 64)

    for subj in targets:
        prefix, drive_folder = SUBJECTS[subj]
        local = html_ids(OUTPUTS_JX / prefix, prefix)
        drive = html_ids(DRIVE_ROOT_CAND / drive_folder, prefix)

        missing_on_drive = sorted(local - drive)   # git にあるが Drive に無い（要配置）
        missing_in_local = sorted(drive - local)   # Drive にあるが git に無い（取りこぼし/要回収）

        status = 'OK' if not missing_on_drive and not missing_in_local else 'DRIFT'
        mark = '✅' if status == 'OK' else '❌'
        print(f'\n{mark} [{subj}] {prefix}  local={len(local)}  drive={len(drive)}  → {status}')

        if missing_on_drive:
            total_missing_drive += len(missing_on_drive)
            print(f'   ⛔ Drive 未配置 ({len(missing_on_drive)}): ' + ', '.join(missing_on_drive))
            for fn in missing_on_drive:
                pid = fn[:-5]  # strip .html
                fix_cmds.append(
                    f'pwsh -NoProfile -File scripts\\jx-deploy.ps1 -Subject {subj} -ProblemId {pid}'
                )
        if missing_in_local:
            total_missing_local += len(missing_in_local)
            print(f'   ⚠ Drive のみ（local/git 欠落 {len(missing_in_local)}）: ' + ', '.join(missing_in_local))

    print('\n' + '=' * 64)
    if total_missing_drive == 0 and total_missing_local == 0:
        print('✅ ドリフトなし — 全 JX HTML が git・Drive 両系統で一致')
        return 0

    print(f'❌ ドリフト検出: Drive未配置 {total_missing_drive} 件 / local欠落 {total_missing_local} 件')
    if args.fix_cmd and fix_cmds:
        print('\n--- Drive 未配置を埋めるコマンド ---')
        for c in fix_cmds:
            print('  ' + c)
    elif total_missing_drive:
        print('  Drive 未配置の補完: python scripts/jx-drive-audit.py --fix-cmd で配置コマンドを表示')
    return 1


if __name__ == '__main__':
    sys.exit(main())
