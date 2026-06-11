# -*- coding: utf-8 -*-
"""
JX台本(.txt)を、演技指導なし・本文そのままで、各科目フォルダへ振り分けて保存する。

変更点(前バージョンから):
  - 「明るく元気いっぱい…」等の演技指導(指示文)を付けない
  - 本文を「」で囲まない（指示文がないので囲みも不要）
  - 出力先を「奇偶フォルダ」ではなく「各科目フォルダ」に変更

使い方(Windows / python は python3 ではなく python):
    python place_jx_scripts.py "C:\\path\\to\\台本フォルダ"

奇数=Aoede / 偶数=Laomedeia の対応は、生成時にどちらのタブで読むかの目安として
一覧に表示する（ファイル自体には声情報は持たせない）。
"""
import os, re, sys

# === 設定（実フォルダに合わせて必ず確認・追記）==========================
# 保存先のベース。実フォルダ名と完全一致しているか要確認
#   ・全角アンダースコア "＿"(CATALINA＿G共有) と半角 "_" の違い
#   ・"2 JX_論文" などのスペース有無・全半角
BASE = r"H:\マイドライブ\CATALINA＿G共有\■予備試験進行中\2 JX_論 文\A_重問耳トレ"

# ファイル名の「JXより前の接頭辞」→ 科目フォルダ名 の対応表。
# 刑法だけ入れてある。他科目は実際の接頭辞とフォルダ名(番号含む)に合わせて追記。
SUBJECT_MAP = {
    "刑":   "1 刑法",
    "刑訴": "2 刑事訴訟法",
    "民":   "3 民法",
    "商":   "4 商法",
    "民訴": "5 民事訴訟法",
    "行":   "6 行政法",
    "憲":   "7 憲法",
}
# ↑ フォルダ名(番号順)は実物で確認済み。左の接頭辞(刑訴/民/商/民訴/行/憲)は
#   xnhのファイル命名と一致しているか、各科目を初めて流す前に dryrun で要確認。

VOICE_ODD  = "Aoede"        # 奇数番号の問題
VOICE_EVEN = "Laomedeia"    # 偶数番号の問題
LIMIT = 5000               # TTS 1ジョブの目安上限(文字)
# ======================================================================

def subject_prefix(name: str):
    """ファイル名の JX より前を接頭辞として取り出す。刑JX025→刑 / 刑訴JX...→刑訴"""
    return name.split("JX")[0] if "JX" in name else None

def problem_no(name: str):
    m = re.search(r"JX0*(\d+)", name)
    return int(m.group(1)) if m else None

def main(src: str, dryrun: bool = False):
    if not os.path.isdir(BASE):
        print("【中止】BASE フォルダが見つかりません:")
        print(f"  {BASE}")
        print("実フォルダ名（スペース・全半角・＿/_ の違い）と一致しているか確認してください。")
        print("確実なのは、ls が通ったパスをそのまま BASE にコピーすることです。")
        return
    if dryrun:
        print("=== DRYRUN（書き込みなし・振り分け先の確認のみ）===")
    for f in sorted(os.listdir(src)):
        if not f.lower().endswith(".txt"):
            continue
        with open(os.path.join(src, f), encoding="utf-8") as fh:
            body = fh.read().strip()

        pref = subject_prefix(f)
        if pref not in SUBJECT_MAP:
            print(f"{f}  →  接頭辞『{pref}』が未登録のためスキップ（SUBJECT_MAP に追記してください）")
            continue

        subject_dir = os.path.join(BASE, SUBJECT_MAP[pref])
        if not os.path.isdir(subject_dir):
            print(f"{f}  →  科目フォルダが見つからずスキップ: {SUBJECT_MAP[pref]}（フォルダ名を要確認）")
            continue

        if not dryrun:
            with open(os.path.join(subject_dir, f), "w", encoding="utf-8") as fh:
                fh.write(body)   # 演技指導なし・本文そのまま

        n = problem_no(f)
        head = "[DRYRUN] " if dryrun else ""
        if n is None:
            print(f"{head}{f}  →  {SUBJECT_MAP[pref]} に保存（番号不明）  {len(body)}字")
            continue
        odd = (n % 2 == 1)
        voice = VOICE_ODD if odd else VOICE_EVEN
        flag = "  ★上限超過(分割推奨)" if len(body) > LIMIT else ""
        print(f"{head}{f}  →  {SUBJECT_MAP[pref]}  /  問題{n}（{'奇数' if odd else '偶数'}）= {voice}タブ  {len(body)}字{flag}")

if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    dry  = any(a in ("--dryrun", "-n") for a in sys.argv[1:])
    main(args[0] if args else ".", dryrun=dry)
