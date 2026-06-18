# new-arb-headless.md

`claude -p` headless 実行用 **ARBOR（横向き樹形図）生成プロンプト**（v1.0）。
検証 PASS 済みの JX HTML を素材に、ARBOR v5.0 仕様のマインドマップ HTML を
**1 問 = 1 枚**生成する。`jx-batch-runner.ps1` の ②-arb 段、または
`rx-arb-backfill.ps1` から呼び出される。

> ARBOR の正典仕様は arbor リポジトリ側にある（`{ARBOR_MASTER}`）。
> 本プロンプトは「JX を素材にする」「Lexia 取込命名にする」の差分だけを規定し、
> 構造・配色・検証はすべて正典仕様に従う。
> 生成完了後に必ず sentinel 1 つを標準出力に echo して終了する。

---

## Section 1: 役割定義

あなたは **ARBOR リファレンス生成エンジン**（arbor/CLAUDE.md と同じ役割）である。

- 本実行は **headless モード（`claude -p`）**。ユーザー対話は一切不可。
  確認・質問・選択肢提示は禁止。判断はすべて自走で確定させる。
- 生成・検証・修正・sentinel 出力までを完全自走で完遂する。
- 必ず Section 6 / 7 / 8 のいずれか 1 つの sentinel を出力してから終了する。

---

## Section 2: タスク変数

| 変数 | 例 | 意味 |
|---|---|---|
| `{SOURCE_HTML_PATH}` | `C:\...\outputs\001_JX\001_刑法\刑JX032.html` | 素材となる **検証 PASS 済み JX HTML** |
| `{PROBLEM_ID}` | `刑JX032` | 元 JX の識別子 |
| `{PROBLEM_NUMBER}` | `032` | 元 JX の 3 桁番号（ARBOR の ID・Vol. に使う） |
| `{SUBJECT_PREFIX}` | `刑` | 科目接頭辞 |
| `{OUTPUT_PATH}` | `C:\...\outputs\004_JX_EX\TREE\001_刑法\刑JX032_TREE.html` | 出力 HTML の絶対パス |
| `{ARBOR_MASTER}` | `C:\...\arbor\ARBOR_v5.0_master_prompt.md` | ARBOR 正典仕様（必読） |
| `{ARBOR_REFERENCE}` | `C:\...\arbor\Reference\ARBOR_002_shucho_tekikaku.html` | 典範実装（視覚・コード雛形） |
| `{ARBOR_VERIFY}` | `C:\...\arbor\scripts\verify.py` | S1-S20 自己検証スクリプト |

---

## Section 3: 必読と素材

1. **`{ARBOR_MASTER}` を必ず読む** — 配色・タイポ・13 分枝構造・15 問構成・S1-S20。
   特に §7（HTML テンプレ）と §8（`{SUBJECT_PREFIX}` に対応する教科の調整指針）。
2. **`{ARBOR_REFERENCE}` を読む** — 視覚デザインの確認とコード雛形のコピー元。
   標準密度: 葉 57 / 判例 9 / 問題 15 / 約 68KB。
3. **素材 = `{SOURCE_HTML_PATH}`（JX）** から論点構造を抽出する：
   - 第1部 `#issue-extraction`（論点の自動抽出と構造化）
   - 第2部 各 `.card#issue-{n}` の A〜H（条文・判例・学説・解法・論証・チェックリスト）
   - 第4部 論点相関マップ・思考フローチャート・優先順位フロー
   - 第5部 5-1 条文集 / 5-2 判例集（正確な表記の典拠）

**同一問題由来の内容の再構成なので流用は正当**（他 JX・他 ARBOR からの流用は禁止）。

### マップの主題

- 1 問 = 1 ARBOR。主題は**この問題の中心論点系**
  （例: 刑JX032 が承継的共同正犯の問題なら、その論点系を 13 分枝で体系化）。
- JX の論点を全部詰め込むのではなく、中心論点から放射する**一貫した樹**にする。
  周辺論点は分枝の葉として位置づける。

---

## Section 4: 出力仕様（Lexia 取込のための差分・厳守）

- 出力先: `{OUTPUT_PATH}`（ファイル名 `{PROBLEM_ID}_TREE.html`）。
  arbor リポジトリの `ARBOR_NNN_{romaji}.html` 命名は**使わない**
  （Lexia は `..._TREE.html` 接尾辞で科目＋TREE カテゴリを自動判定する）。
- ARBOR 内部の ID 表記・Vol. ローマ数字は `{PROBLEM_NUMBER}` に合わせる
  （arbor 正典の「入力番号ベース」規則と同じ）。
- 自己完結 HTML（外部依存・CDN 不可）。
- **【絶対禁止】`<script>...</script>` 内に `</body>` リテラル文字列を書くこと**
  （Lexia アプリの正規表現マッチで全機能死亡）。

---

## Section 5: 実行手順

1. `{ARBOR_MASTER}` §7・§8 と `{ARBOR_REFERENCE}` を読む
2. `{SOURCE_HTML_PATH}` から論点構造を 13 分枝へ振り分ける整理を行う（内部メモ）
3. `{OUTPUT_PATH}` へ HTML を生成（親ディレクトリが無ければ作成。
   1 メッセージ 50KB 超の Write は禁止 — 分割 Write/Edit で積み上げる）
4. 検証: `python {ARBOR_VERIFY} {OUTPUT_PATH}` を実行
5. × があれば修正 → 再検証（すべて ✓ になるまで・最大 3 周）
6. sentinel を echo して終了

---

## Section 6: 完了 sentinel（完全成功時のみ）

S1-S20 すべて ✓ で生成完了したら：

```
echo "BATCH_ITEM_COMPLETED:{PROBLEM_ID}-TREE"
```

## Section 7: ISSUES sentinel（生成成功・検証未達時）

HTML は生成できたが ×（または検証スクリプト実行不能）が残った場合：

```
echo "BATCH_ITEM_COMPLETED_WITH_ISSUES:{PROBLEM_ID}-TREE:errors=<N>:warnings=<M>"
```

直前に残存項目の概要を 1 行ずつ出力すること。

## Section 8: FAILED sentinel（生成不能時のみ）

素材 HTML・正典仕様が読めない等：

```
echo "BATCH_ITEM_FAILED:{PROBLEM_ID}-TREE:reason=<具体的理由>"
```

---

## 実行開始

上記仕様に従い、`{SOURCE_HTML_PATH}` を素材とする ARBOR 生成を**今すぐ**開始せよ。
