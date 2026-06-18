# RX / TREE 副産物パイプライン（2026-06-11 導入）

検証 PASS 済みの JX HTML を素材に、Lexia アプリ用の 2 種の副産物を自動生成する。

| 副産物 | 内容 | 出力先 | Lexia での扱い |
|---|---|---|---|
| **RX** | 論証カード（1論点1HTML・規範トグル＋○×クイズ付き） | `outputs/004_JX_EX/RX/{科目}RX/{科目}RX{NNN}_{n}.html` | TX/JX と同格の SRS カード（今日のキュー・逆算・弱点注入の対象） |
| **TREE** | ARBOR 横向き樹形図（1問1枚） | `outputs/004_JX_EX/TREE/{科目}TREE/{科目}JX{NNN}_TREE.html` | 参考教材（TREE カテゴリ・SRS 対象外） |

## 関連ファイル

| ファイル | 役割 |
|---|---|
| `prompts/new-rx-headless.md` | RX 生成プロンプト（Lexia 取込仕様を内包） |
| `prompts/new-arb-headless.md` | TREE 生成プロンプト（ARBOR 正典 `C:\...\arbor\ARBOR_v5.0_master_prompt.md` を参照） |
| `scripts/validate-rx.py` | RX 検証（R1〜R9・exit 0 = PASS） |
| `scripts/rx-arb-backfill.ps1` | **既存 JX** の欠落副産物を後追い生成 |
| `logs/rx-arb-summary.csv` | 副産物のコスト・結果ログ（jx-cost-summary.csv とは別管理） |

## 新規 JX での自動生成

`jx-batch-runner.ps1` に ②-rx / ②-arb 段が組み込み済み。**既定で ON**。

- 実行順: ① JX 生成 → ② validate-jx PASS → **②-rx RX → ②-arb TREE** → ③ TTS → …
- **非致命設計**: RX/TREE が失敗しても JX/TTS の進行・連続失敗判定・overall には影響しない
- 前提ファイル（プロンプト・validate-rx.py・ARBOR 正典）が無い場合は警告のみで自動スキップ
- スキップ指定: `-SkipRx` / `-SkipArb`、ARBOR リポジトリ位置の変更: `-ArborRoot <path>`

```powershell
# 通常運用（副産物込み）
pwsh -NoProfile -File scripts/jx-batch-runner.ps1 -Subject 刑 -MaxProblems 3
# 副産物なしの従来運用
pwsh -NoProfile -File scripts/jx-batch-runner.ps1 -Subject 刑 -SkipRx -SkipArb
```

## 既存 JX のバックフィル

```powershell
pwsh -NoProfile -File scripts/rx-arb-backfill.ps1 -Subject 刑 -DryRun   # 欠落の確認のみ
pwsh -NoProfile -File scripts/rx-arb-backfill.ps1 -Subject 刑 -MaxProblems 3
```

## sentinel（jx-batch-runner の Get-Sentinel と互換）

```
BATCH_ITEM_COMPLETED:{PROBLEM_ID}-RX
BATCH_ITEM_COMPLETED_WITH_ISSUES:{PROBLEM_ID}-RX:errors=N:warnings=M
BATCH_ITEM_FAILED:{PROBLEM_ID}-RX:reason=...
（TREE は -TREE サフィックス）
```

## Lexia への取込

`outputs/004_JX_EX/RX/` と `outputs/004_JX_EX/TREE/` の HTML をそのまま Lexia の一括取込（ZIP/ドラッグドロップ）へ。
ファイル名だけで科目・カテゴリが自動判定される（刑RX032_1 → 刑法/RX、刑JX032_TREE → 刑法/TREE）。

## 注意

- RX/TREE も `claude -p` を 1 回ずつ消費する（1 問あたり計 +2 セッション）。
  夜間バッチの所要時間・コスト見積りに織り込むこと。
- `<script>` 内 `</body>` リテラル禁止は RX/TREE にも適用（validate-rx R8 で機械検証）。
- ⑦永続化（jx-finalize）は **RX/TREE も同じコミットで GitHub バックアップする**
  （2026-06-11 対応済み。①バックアップの add 対象に outputs/004_JX_EX/RX・outputs/004_JX_EX/TREE の該当ファイルを含む）。
  バックフィルで後追い生成した分は `jx-finalize.ps1 -Subject 刑 -Ids 刑JX001,... -NoCleanup`
  か、通常の git commit で永続化できる。

## Drive バックアップ（⑥配置・2026-06-11 対応済み）

`jx-deploy.ps1` が RX/TREE も repo ミラー＋Drive の両方へ配置する：

```
{2 JX_論 文}\B_RX\00N_科目\{科目}RX{NNN}_{n}.html      ← RX 論証カード
{2 JX_論 文}\C_ARBOR\00N_科目\{科目}JX{NNN}_TREE.html   ← ARBOR 樹形図
```

- 科目フォルダ（001_刑法〜007_憲法）は `jx-deploy.ps1 -InitAll` で作成済み（再実行可）
- バッチランナーの ⑥ は jx-deploy を呼ぶので、新規 JX は副産物も自動で Drive バックアップされる
- バックフィルで作った RX/TREE は `jx-deploy.ps1 -Subject 刑` （科目一括）で後追い配置できる
