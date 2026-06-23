#!/usr/bin/env python3
"""ARIADNE 統合ポリッシュ・オーケストレータ（2026-06-23・恒久対策）。
今セッションで分割された全磨き込みを1コマンドで冪等適用する。新規/旧型/ドリフト
いずれの ARIADNE も spec 品質へ正規化する単一窓口。生成パイプライン（rx-arb-backfill）
や autofill スイープから呼ぶことで「手動で都度直す」をなくす。

各サブスクリプトは冪等（再実行=0変更）。引数でファイル指定可、無指定で全 ARIADNE＋canonical。
注意：模範答案の『役割色塗り(r-issue等)』は法的分類が要るため本機では行わない
（新規は生成プロンプト §10 が付与、旧型は一度だけ人手/エージェントで実施済み）。
本機が揃えるのは構造・配色・配点バー・バッジ中央化・字下げ/階層/ぶら下がり。"""
import subprocess, sys, glob, os

# 適用順（すべて冪等・LF保存済み）
STEPS = [
    'ariadne-bsec.py',          # 骨子 第N箱
    'ariadne-matrix.py',        # 骨子マトリクス金バー/見出し
    'ariadne-stepnum.py',       # 行頭ステップ番号box
    'ariadne-weightbar3.py',    # 配点バー（ラベル内蔵+safe center+ellipsis）
    'ariadne-weightbar-name.py',# 配点バー 名称欠落（数字のみ）を凡例から補完（A28・恒久対策）
    'ariadne-badge-center.py',  # バッジ letter-spacing 中央化
    'ariadne-indent-normalize.py', # 字下げ遺伝リセット＋トラッキング相殺
    'ariadne-hanging.py',       # 模範答案 role .pn/.pb ぶら下がり（CSS土台）
    'ariadne-modelanswer.py',   # 模範答案 ぶら下がり＋階層インデント＋1字下げ統一
    'ariadne-pb-indent.py',     # 全 .pb（役割カード含む）本文先頭1字下げ＋display:block
]
HERE = os.path.dirname(os.path.abspath(__file__))

def _safe(x):
    """Windows cp932 コンソールでも落ちないよう ASCII 化（mojibake より crash 回避優先）"""
    return str(x).encode('ascii', 'replace').decode('ascii')

def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
    args = sys.argv[1:]
    print(_safe(f"[polish] {len(STEPS)} steps over {'specified files' if args else 'all ARIADNE+canonical'}"))
    for s in STEPS:
        path = os.path.join(HERE, s)
        if not os.path.exists(path):
            print(f"  - skip (missing): {s}"); continue
        r = subprocess.run([sys.executable, path, *args], capture_output=True, text=True, encoding='utf-8', errors='replace')
        tail = (r.stdout or '').strip().splitlines()
        msg = tail[-1] if tail else f"exit={r.returncode}"
        flag = '' if r.returncode == 0 else '  <<ERROR'
        print(_safe(f"  - {s:28} {msg}{flag}"))
        if r.returncode != 0 and r.stderr:
            print('    ', _safe(r.stderr.strip().splitlines()[-1]))
    print("[polish] done (re-run = 0 changes across all steps = spec-consistent)")

if __name__ == '__main__':
    main()
