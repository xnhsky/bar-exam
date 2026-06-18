---
description: 新規 TX ファイルを問題 PDF から生成
---

新規 TX ファイル（HTML カード）を生成する。

引数：問題 PDF のパス（例：`inputs/tx-pdfs/K302-problem.pdf`）

## 必須手順

1. **PDF 読解**：問題番号・科目・年度・全選択肢・正解・正答率・出題テーマを抽出
2. **パターン判定**：正答率 ≥60%→P1／40-60%→P2／<40%→P3
3. **冒頭応答必須**：「正答率__%→パターン_『___』適用」を最初に出力
4. **規律確認**：以下を順に view
   - `spec/legacy/tx-v8.11.6-core.md`
5. **canonical コード取得**：以下を順に view
   - `spec/legacy/tx-v8.11.6-annex-A.css`
   - `spec/legacy/tx-v8.11.6-annex-B.html`
   - `spec/legacy/tx-v8.11.6-annex-C.js`
   - P2 の場合のみ `spec/legacy/tx-v8.11.6-annex-A-bis-2.css`
   - P3 の場合のみ `spec/legacy/tx-v8.11.6-annex-A-bis-3.css`
6. **canonical 実装例の確認**：`canonical/KTX301.html`（必要な部分のみ view_range で）
7. **新ファイル組み立て**：
   - annex-A.css 全文を `<style>` 内に逐語コピー
   - P2/P3 の場合は対応する annex-A-bis の `:root{}` ブロックを `<style>` 末尾に追記
   - annex-B.html の skeleton にコンテンツを流し込み
   - annex-C.js 全文を `</body>` 直前の `<script>` 内に逐語コピー
8. **コンテンツ規律遵守**：
   - A-2 解説文は `data-explanation` 属性にプレーンテキストで格納
   - 条文・判例 body のラベル始まり段落は必ず `<p class="hanging"><span class="hang-body">` ラップ
   - PART D ARENA を 12 問・○:×=6:6 で構築
   - 全 section-title に sec-icon 配置
9. **出力先**：科目に応じて `outputs/{科目}/` 配下に保存
   - 刑法 → `outputs/000_TX/001_刑法/K{NNN}.html`
   - 憲法 → `outputs/000_TX/007_憲法/KEN{NNN}.html`
   - 民法 → `outputs/000_TX/003_民法/MIN{NNN}.html`
   - 他科目も同様
10. **検証実行**：`bash python scripts/validate.py <出力ファイル>` を実行
11. **配信判定**：ERROR 0 件確認後に `present_files` で完了報告

## 鉄則

- canonical コードは**バイトレベルで逐語コピー**。書き直し禁止。
- コンテンツ部分のみ差替え。class 名・id 命名・タグ順序を変えない。
- 「保守的書き換え」を絶対にしない。

$ARGUMENTS
