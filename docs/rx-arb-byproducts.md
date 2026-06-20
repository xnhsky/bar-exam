# RX / TREE 副産物パイプライン（2026-06-11 導入）

検証 PASS 済みの JX HTML を素材に、Lexia アプリ用の 2 種の副産物を自動生成する。

| 副産物 | 内容 | 出力先 | Lexia での扱い |
|---|---|---|---|
| **RX** | 論証カード（1論点1HTML・規範トグル＋○×クイズ付き） | `outputs/004_JX_EX/RX/{00N_科目}/{科目}JX{NNN}/{科目}RX{NNN}_{n}.html`（問題ごとサブフォルダ・2026-06-20 恒久化） | TX/JX と同格の SRS カード（今日のキュー・逆算・弱点注入の対象） |
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

## リモート生成（Claude Code on the web）での副産物（2026-06-20 導入）

PowerShell バッチが使えないリモート環境では、`/new-jx`（`.claude/commands/new-jx.md`）の
**Phase 9** が副産物を生成する。バッチランナーが別 `claude -p` セッションを立てるのと同様に、
**`Agent` サブエージェントを RX → TREE → ARIADNE の順に 1 つずつ起動**し、それぞれに対応する
`prompts/new-*-headless.md` 全文と repo 相対パス（置換済み）を渡す。非致命（失敗しても JX 本体の
完了・push は妨げない）。永続化は `scripts/jx-push.sh` が既定で `outputs/004_JX_EX` も stage する。

| 副産物 | リモートでの依存 | 可否 |
|---|---|---|
| **RX** | 素材 JX＋`scripts/validate-rx.py`（repo 内で完結） | ✅ |
| **ARIADNE** | 素材 JX＋`canonical/ARIADNE.html`＋`scripts/validate-ariadne.py`（repo 内で完結） | ✅ |
| **TREE** | 外部 arbor リポジトリに依存していたが、**`canonical/ARBOR.html`（gold TREE の正典複製）＋`scripts/validate-tree.py`（T1〜T9 軽量ゲート）で vendored 化** | ✅ |

**TREE の vendored モード**：外部 `arbor` リポジトリ（`ARBOR_v5.0_master_prompt.md`／verify.py）は
リモートに存在しない。そこで gold TREE 出力を **`canonical/ARBOR.html`** として repo に vendor し、
`prompts/new-arb-headless.md` に「`{ARBOR_MASTER}` を Read できなければ canonical/ARBOR.html を
唯一の構造参照にし、`scripts/validate-tree.py` で検証する」リモートモードを追記した。
フル S1〜S20 verify はローカル専用のまま。リモートは canonical と同じ密度（**13 分枝・葉 57・
問題 15・約 68KB**）に揃えることで品質を担保する。canonical/ARBOR.html の本文・論点はコピーせず
**構造シェルのみ参照**（content independence）。

```bash
# TREE 軽量検証（リモート・vendored モード）
python scripts/validate-tree.py outputs/004_JX_EX/TREE/001_刑法/刑JX042_TREE.html
```

## 既存 JX のバックフィル（ローカル・3種すべて対応）

`rx-arb-backfill.ps1` は **RX / TREE / ARIADNE の3種すべて**の欠落を後追い生成する
（2026-06-20 に ARIADNE 段と vendored TREE フォールバックを追加）。各 JX について未生成の
副産物だけを生成するので、何度流しても重複生成しない（冪等）。

```powershell
pwsh -NoProfile -File scripts/rx-arb-backfill.ps1 -Subject 刑 -DryRun        # 欠落の確認のみ（生成なし）
pwsh -NoProfile -File scripts/rx-arb-backfill.ps1 -Subject 刑 -MaxProblems 3 # 若番から3問ぶんの欠落を埋める
pwsh -NoProfile -File scripts/rx-arb-backfill.ps1 -Subject 刑 -FromNumber 30 -ToNumber 40  # 番号範囲指定
pwsh -NoProfile -File scripts/rx-arb-backfill.ps1 -Subject 刑 -SkipRx -SkipArb            # ARIADNE だけ埋める
```

- **TREE は外部 arbor 不在なら vendored モード**（`canonical/ARBOR.html` + `validate-tree.py`）へ
  自動フォールバックするので、arbor を持たない PC でも TREE を埋められる。
- 抑止スイッチ：`-SkipRx` / `-SkipArb` / `-SkipAriadne`。
- 生成後の永続化は通常の git commit か `jx-finalize.ps1 -Subject 刑 -Ids ... -NoCleanup`。
  バックフィルは入力 PDF を消さない（cleanup は新規生成パイプライン側の責務）。

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
{2 JX_論 文}\B_RX\00N_科目\{科目}JX{NNN}\{科目}RX{NNN}_{n}.html  ← RX 論証カード（問題ごとサブフォルダ・2026-06-20）
{2 JX_論 文}\C_TREE\00N_科目\{科目}JX{NNN}_TREE.html    ← TREE 樹形図（旧 C_ARBOR・2026-06-18 改名）
{2 JX_論 文}\D_ARIADNE\00N_科目\{科目}JX{NNN}_ARIADNE.html ← ARIADNE 解法ナビ＋周回
```

- 科目フォルダ（001_刑法〜007_憲法）は `jx-deploy.ps1 -InitAll` で作成済み（再実行可）
- バッチランナーの ⑥ は jx-deploy を呼ぶので、新規 JX は副産物も自動で Drive バックアップされる
- バックフィルで作った RX/TREE は `jx-deploy.ps1 -Subject 刑` （科目一括）で後追い配置できる
