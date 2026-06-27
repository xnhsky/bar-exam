# 保留中の対策タスク（撤去・ERROR化・バックログの発火条件）

> 「コーパス安定後に」「全問展開後に」など**発火条件が曖昧で抜けやすい対策系タスク**を
> 一元管理する。各項目は **完了条件（DoD）と発火トリガー**を明記する。新しい暫定機構・
> WARNING 検査・暫定マップを足したら、撤去/ERROR化の条件を必ずここへ追記すること。
>
> 初版 2026-06-27（復習プール記号フリー化＋意味ラベルの恒久対策に伴う棚卸し）。

---

## 0. 全体の依存関係（先に読む）

```
[バックログ消化] ──┬─→ [WARNING→ERROR 化]（#3）
  #1 G32(~170)     │
  #2 G31(88)・A(339)│
                   └─→ [Lexia FA_LABEL_SEED 撤去]（#4）
```

撤去・ERROR化は**バックログ（#1・#2）を消さないと既存ファイルが全滅 or 取込が壊れる**。
よって順序は固定：**#1/#2 を消化 → #3 ERROR化 → #4 撤去**。

---

## 1. 【バックログ・新規】G32 GIST/POINT 記号フリー化

- **何**：2026-06-27 新設の `validate-tx-core.py` G32 が、Lexia 復習プールに併載される
  GIST（`.syn-lead`）・POINT（`.choice-points li`）の記号残り（①〜/(a)〜/A説 等）を WARNING 化。
- **規模**：刑法 _lex 362問のサンプル 30問中 14問該当＝**推定 ~170問**。大半は組合せ問題の
  GIST が `①a＋⑥l` 式で書かれているもの。
- **修正方針**：spec 第3-bis項どおり、組合せ GIST は「限定説と認識必要説の組合せ」と
  **学説の実体名**で書き直す。POINT の記号・他記述参照も実体に置換。
- **DoD**：刑法 _lex 全 362件で **G32=0**。
- **発火**：制限復活後にバッチで worklist 出力→1問1エージェントで書き直し（gold＝刑TX351 流儀）。

## 2. 【バックログ・既知】G31（ox-stmt/論点コア）記号フリー化 ＋ 意味ラベル A 展開

- **B（G31）**：ox-stmt・verdict 論点コア列の記号フリー化。残り **88問**（P1 65＋P2 23）。
  P2 リスト：58,65,76,94,98,118,119,130,134,142,144,145,146,149,157,158,233,257,262,288,344,381,418。
  **DoD**：刑法 _lex 全 362件で G31=0（座談会例外 刑TX090 を除く）。
- **A（意味ラベル）**：物語段落への `data-fa-label` 付与。現状 bar-exam HTML には未付与で、
  Lexia 側 `FA_LABEL_SEED` が **23問だけ**暫定種まき（刑TX351・355〜376）。残り **~339問**。
  **新規生成は自動付与**（tx-inject-narrative.py／tx-build-typeA.py が data-fa-label を出力・
  new-tx Phase 4i）なので、既存問の**再生成 or ラベル後追い注入**が対象。
  **DoD**：刑法 _lex 全 362件の `.fa-narrative > p` に `data-fa-label` が付く。

## 3. 【ERROR化・最も忘れやすい】WARNING 検査の昇格

「当面 WARNING・コーパス安定後に ERROR 化」と各 spec に書かれた検査群。**#1・#2 の DoD 達成が前提**。

| 対象 | 検査 | 場所 | 昇格条件 |
|---|---|---|---|
| TX | **G31**（ox-stmt/論点コア自己完結） | `validate-tx-core.py` `g30_pool_self_contained` | #2 B 完了（G31=0） |
| TX | **G32**（GIST/POINT 自己完結） | `validate-tx-core.py` `g32_pool_gist_point_self_contained` | #1 完了（G32=0） |
| JX | **JC1〜JD1**（v4 LOOP-FOLD） | `validate-jx.py` | 新v系生成が安定（spec jx-v4.0.0 第8項）。**既存 v3.2 は WARNING 据置のままフラグ設計**で温存 |
| ARIADNE | **A22**（パズルエンジン）・**A26**（go-athena ボタン） | `validate-ariadne.py` | ariadne 安定後（spec jx-ariadne-v0.1） |

- **昇格のやり方**：`self.warn(...)` → `self.err(...)` に変える前に、**全コーパスで該当 0 を実測**。
  JX は「新v系のみ ERROR」のフラグ設計を崩さない（既存 v3.2 全滅を防ぐ）。

## 4. 【撤去】Lexia `FA_LABEL_SEED` 暫定マップ

- **何**：`lexia/src/App.jsx` の `FA_LABEL_SEED`（コード→段落ラベル）。bar-exam HTML が
  `data-fa-label` を持たない間、iframe 表示とプール STORY の両方へ食い出しタブを出すための暫定。
- **前提は整った**：2026-06-27 に bar-exam 生成側が `data-fa-label` を吐けるようになった
  （seedNarrativeLabels／extractStmtMeta は既に**baked ラベルを優先**し seed にフォールバック）。
- **DoD・発火**：**#2 A（339問）を全展開→Lexia へ再取込**し、全 _lex が baked ラベルを持った時点で
  `FA_LABEL_SEED`・`seedNarrativeLabels`・extractStmtMeta 内のフォールバック分岐を削除。
- **撤去漏れの害**：機能影響は無い（baked 優先なので無害）が、コード負債として残り続ける。

## 5. 【スコープ・対策不要の確認】他6科目

- **_lex は刑法のみ 362問**。憲/民/商/民訴/刑訴/行政 は未生成。
- 生成時に新パイプラインが**自動で記号フリー（G31/G32）＋意味ラベル（A）**を満たすので、
  他科目には #1〜#4 のような後追いバックログは**発生しない見込み**。
- **確認だけ残す**：他科目を初めて生成したら、その回の _lex で G31/G32=0・data-fa-label 付与を
  バッチ末尾で実測し、ここに「○科目 確認済み」と追記する。

## 6. 【各PC手動・低リスク】フック/常駐の install

- pre-commit フック（作成日時スタンプの保険・CLAUDE.md §9）と autofill 常駐タスク（§4-6）は
  各PCで一度 install が必要だが、`jx-batch-runner.ps1`／`rx-arb-autofill.ps1` が**冪等で自動 install**。
- **実運用上の発火**：各ローカルPCで一度バッチ or 常駐タスクを回せば自動で入る。手動 install
  （`bash scripts/install-hooks.sh`）は保険。リモート（Linux）は schtasks 無しで不要。
