# 引継ぎ：ARIADNE 刑法を validate ERROR 0 へ（リモート CC 用）

> 2026-07-02 作成。ローカル(xnrg2 PC)から**リモート Claude Code** へ引継ぎ。master @ `c365570c` に push 済み。
> **まず `git pull origin master` してから着手**。作業は master（または PR ブランチ）で。

## ゴール
`python scripts/check-ariadne-canonical.py` が **ERROR 0** になること（＝ ARIADNE 刑法の A33/A32 残エラー解消）。

## いまの状態（済み・pushed）
- **骨子 simple-bone 正典化(v1.2.1)**：`canonical/ARIADNE.html`・`ARIADNE.placeholder.html`・`spec/jx-ariadne-v1.2.0-core.md §17`・`prompts/new-ariadne-headless.md`・`docs/canonical-lineage.md`。骨子は刑JX001型の simple `.bone`（1項目1行）。matrix-bone は旧型(A34 WARN)。
- **検証ゲート強化**：`scripts/validate-ariadne.py` に A34(matrix WARN)・**A35(深掘りテンプレ流用=別問題の人物記号混入→ERROR)**・A36(版drift)・A37(未定義box)・A38(draft逐語)・A39(bc-inst 2カラム)。
- **自動化**：pre-commit ゲート `scripts/validate-staged.py`(block既定・報告は `LEXIA_VALIDATE=report`)＋settings.json Stopフック＋機械修正 `scripts/ariadne-conform-fix.py`＋手順書 `docs/ariadne-rollout-playbook.md`。
- **移行済み**：刑JX009-020（骨子simple化＋適合修正、**018は深掘り層を別問題流用から本問=事後的奪取意思/盗品保管継続犯/違法性の錯誤/257条で全面再鋳造**）。P3で版スタンプ→v1.2.0統一＋warn-box→key-box（60件）。A33を部分執筆。

## 残タスク（これを消せば ERROR 0）
`python scripts/validate-ariadne.py <file>` で各ファイルの該当カード番号が出る（下記は 2026-07-02 実測）。

### 1. A33（周回ドリル解説の手掛かり不足）＝11ファイル
対象と該当 `周回ドリルN`：
- 刑JX018=3／刑JX032=4,14／刑JX036=8,10／刑JX039=3,5,17／刑JX044=8／刑JX050=10／刑JX052=8／刑JX054=3／刑JX055=8／刑JX057=13／刑JX064=8

**直し方**：該当 `.self-check-quiz` の `.quiz-answer` を書き直す。
- **理由(から/ため)＋要件/規範＋結論(成立/不成立)** の少なくとも2つを明示（validator の判定語＝`validate-ariadne.py` の A33 regex。配点/実益/検討/罪名等も可）。18字以上。
- 中身は**そのファイル自身の検証済み本文**（`.model-answer`・`.box-norm`・深掘り `.basis-card`/学説）に厳密準拠。無い判例・規範・条文を創作しない（spec §11）。
- **直上の教示(`.do`/`.peek`)の言い換えにしない**（§4-bis）＝どこでも効く規範・定義・要件・区別の想起にする。
- `data-correct-value`・設問文・骨子・パズルエンジン・配色・フォントは**変更しない**。書き換えるのは薄い `.quiz-answer` 本文だけ。
- 1件直す→`validate-ariadne.py <file>`→A33 PASS を確認、を回す。

### 2. A32（骨子コンテナ未閉）＝刑JX073・刑JX074（073はA33ドリル1も）
**真因**：JX073/074 は骨子コンテナの閉じ region が CRLF（`</details>\r\n\r\n  </div>...`）。`validate-ariadne.py` の A32(~L380)は **LF固定文字列で照合**し、ファイルを改行保持で読むため CRLF だと不一致→誤検出（canonical/JX009=純LF, JX071/072=本文CRLF+閉じLF は通る）。CRLF は私のローカル Edit ツール(Windows)が混ぜたもの。
**恒久修正（推奨）**：`validate-ariadne.py` を**改行非依存**にする＝ファイルを `html` に読み込んだ直後（各チェック前）に **`html = html.replace('\r\n', '\n')`** を1行追加。これで JX073/074＋今後の全 Windows 生成 ARIADNE の A32 誤検出が消える。`</body>` リテラル検査等は `\r` 非依存で無害。
（即効の代替：該当2ファイルを LF 正規化。ただし再発するので validator 修正が上策。）
刑JX073 の A33 ドリル1 は上記 A33 レシピで。

### 3. 刑TX355_lex.html（別件・ARIADNE ではない TX）
`python scripts/validate-tx-core.py outputs/ux/000_TX/001_刑法/刑TX355_lex.html` で FAIL。ARIADNE 移行とは無関係の TX 課題。出た G-error に従って修正（優先度低・別扱いでも可）。

## 仕上げ手順
1. **A32 恒久修正**（validate-ariadne.py に改行正規化1行）→ canonical と JX073/074 が A32 PASS することを確認。
2. **A33** 11ファイル＋073ドリル1 を validator ループで執筆。
3. **刑TX355_lex** を別途（任意）。
4. `python scripts/check-ariadne-canonical.py` → **ERROR 0** 確認。
5. commit＋push。**commit ゲートは修正済みで正常動作**（clean なら通る／WIP を通すなら `LEXIA_VALIDATE=report git commit …`）。

## 注意・gold 参照
- gold＝`刑JX001_ARIADNE.html`(設計)／`刑JX009_ARIADNE.html`(骨子 before→after)／`刑JX018_ARIADNE.html`(深掘り再鋳造の見本)。
- **A35 が他ファイルで ERROR を出したら**、それは 018 型の別問題流用＝元JX から本問論点で深掘り再鋳造（創作禁止）。
- PLACEHOLDER-LOCK：骨子・エンジン・配色・フォント・CSS は触らない。編集は問題固有スロットのみ。
- 詳細レシピは `docs/ariadne-rollout-playbook.md`、正典書式は `spec/jx-ariadne-v1.2.0-core.md §17`。
- WIP コミット `f1fb15cd` は `--no-verify` でスタンプ未実行のものが混じる可能性。最終 commit（フック経由）で genmeta が刻まれる。

## この引継ぎの範囲外（後日・別タスク）
範囲外の matrix-bone 残（刑JX007・008・021・022・023・024・071・072）の simple-bone 化と、他科目(002-007)への展開は `docs/ariadne-rollout-playbook.md §5` の反復ループで別途。
