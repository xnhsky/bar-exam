# JX パイプライン補助システム（整合チェック・PDF削除・回収動線）

> 2026-06-06 新設。JX 生成の前後を固める 3 つの補助システム。
> ① 入力アラインメント・チェック ② 処理済 PDF の安全削除 ③ 成果物の回収動線。

---

## ① 入力アラインメント・チェック（PDF ↔ 講義逐語のズレ検出）

### なぜ必要か
`inputs/jx/{科目}/重問PDF/{n}.pdf` と `inputs/jx/{科目}/講義逐語/{科目名}_重問{nn}.txt` は
**本来同番号で対応するはずだが、実際にはズレている系列がある**。
**刑 28/29/30 は重問PDFと講義逐語が −7 ズレ**（内容照合で 21/22/23 が一致）。
逐語は JX 生成の第一次情報源（CLAUDE.md §4-3）なので、ズレたまま生成すると
**講師アドバイス（`.lecturer-advice`）が別問題のものになる事故**が起きる。

### 方針（軽量・ざっと検出）
**生成を始める段階で「ざっとズレに気づければ十分」**。1字1句の照合は不要。
チェッカーは逐語の**冒頭プレビュー**を表示するので、PDF の論点と食い違っていないかを
目視で素早く確認できる。明らかにズレていたら overrides を直す、という運用。

### 仕組み
- 正典マニフェスト：**`inputs/jx/transcript-map.json`**
  - 既定（default）は「同番号」対応。
  - ズレが判明した問題のみ `overrides` に逐語ファイル名を明示。
  - `keywords` ＝「その逐語に必ず出現するはずの論点語」（任意・確定済み問題のみ）。本文走査で欠落＝ズレ疑い。
- チェッカー：**`scripts/check-jx-alignment.py`**（解決した逐語の**冒頭6行をプレビュー表示**）

### 使い方
```bash
# 生成前に逐語パスを取得（標準動線・人間が確認）
python scripts/check-jx-alignment.py 刑 28
#   → [OK] 刑 第28問 → 刑法_重問21.txt（override・keyword検証通過）

# ランナー用：解決した逐語パスだけを標準出力
python scripts/check-jx-alignment.py 刑 28 --quiet
#   → inputs/jx/刑/講義逐語/刑法_重問21.txt

# 科目一括スキャン（PDF があるのに逐語が無い／ズレ疑いを洗い出す）
python scripts/check-jx-alignment.py 刑 --all
```
終了コード：`0`=OK / `1`=逐語欠落 / `2`=keyword 不一致（ズレ疑い） / `3`=引数・マニフェスト不正。

### 新しいズレを見つけたら
1. 内容照合で正しい逐語を特定。
2. `transcript-map.json` の該当科目 `overrides` に
   `"<番号>": {"transcript": "<逐語ファイル名>", "keywords": ["論点語", ...], "note": "..."}` を追記。
3. `python scripts/check-jx-alignment.py <科目> <番号>` で `[OK]` を確認。

> **生成フローへの組み込み**：新規 JX 生成（new-jx / JX-MAIN/SUB）では、
> PDF を読む前に必ず本チェッカーで逐語を解決する。`[ERROR]`（コード1・2）なら
> **生成を中断**し、マニフェストを修正してから着手する（無断推定禁止）。

---

## ② 処理済 PDF の安全削除（git 管理）

### 方針（CLAUDE.md §8：PDF は重要資産・原本は Drive 常在）
- 削除は **「処理済のみ」**。生成 HTML が存在し **かつ git に commit 済み**であることを
  確認してからでないと削除しない（作業消失の防止）。
- 削除は **`git rm`（履歴に残る＝復元可能）**。物理 `rm` はしない。
- 既定は **dry-run**。実削除は `--commit` を付けたときだけ。

### 使い方
```bash
scripts/jx-cleanup-pdf.sh 刑 28                 # dry-run（何が消えるか表示）
scripts/jx-cleanup-pdf.sh 刑 28 --commit        # 実際に git rm（commit は呼び出し側で）
scripts/jx-cleanup-pdf.sh 刑 28 29 30 --commit  # 複数まとめて
git commit -m "chore(jx): remove processed input PDFs (刑28-30)"
```
HTML が無い／未コミット／未コミット差分ありの場合は **`[HOLD]` で削除を拒否**（終了コード1）。

---

## ③ 成果物の回収動線（＝リモートコンテナから回収して git push）

### なぜ必要か
リモート実行（Claude Code on the web 等）は **ephemeral でコンテナが回収**される。
**回収の動線とは「コンテナ上で生成したファイルを回収して git push し、GitHub に残す」こと**
（CLAUDE.md §9：生成＝コミットで永続化）。push しないままコンテナが回収されると成果物は消える。

### 中核ツール：`scripts/jx-push.sh`（回収＝add→commit→push を1コマンド）
```bash
scripts/jx-push.sh "feat(jx): 刑JX028 を生成保存（J1〜J21 PASS）"
scripts/jx-push.sh "msg" outputs/jx/刑JX/刑JX028.html   # 対象を明示
scripts/jx-push.sh --dry "msg"                         # 確認のみ（add/commitしない）
```
- 既定対象は `outputs/jx` 配下の追加/変更/未追跡。
- `git push -u origin <現ブランチ>` を**ネットワークエラー時に指数バックオフ再試行**（2s,4s,8s,16s／最大4回）。
- push 後に回収マニフェスト（下記）を自動表示。

### 補助：`scripts/jx-retrieval-manifest.py`（何をどこから回収できるか一覧）
```bash
python scripts/jx-retrieval-manifest.py                       # 今回の成果物＋GitHub URL＋手順
python scripts/jx-retrieval-manifest.py --md > deploy/retrieval-latest.md
```
リモートのプロキシ remote（`http://local_proxy@.../git/owner/repo`）からも
GitHub URL（`https://github.com/xnhsky/bar-exam/...`）を復元する。

### push 後に他環境へ取り込むルート
- **A. git pull**（推奨）：`git fetch origin <branch>` → `git checkout <branch>`。
- **B. 直接 DL**：GitHub の Raw URL をブラウザ／`curl` で取得。
- **C. Drive ミラー**（任意・手動）：GitHub から DL → `マイドライブ / 2 JX_論文 / 00N_科目`。

---

## 標準フロー（新規 JX 1 問）への組み込み順

```
1. python scripts/check-jx-alignment.py <科目> <番号>      # ① 逐語の解決・ズレ検出（[OK] 必須）
2. （PDF＋解決した逐語を読んで JX を生成：new-jx）
3. python scripts/validate-jx.py <出力HTML>                # J1〜J20 ERROR 0 件
4. scripts/jx-push.sh "feat(jx): <ID> を生成保存"          # ③ 回収＝add→commit→push（§9 永続化）
5. scripts/jx-cleanup-pdf.sh <科目> <番号> --commit         # ② 処理済 PDF を git rm
   scripts/jx-push.sh "chore(jx): remove processed input PDFs"   # 削除も push して回収
```
