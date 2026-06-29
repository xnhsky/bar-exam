# bar-exam

司法試験・予備試験対策の HTML 教材自動生成プロジェクト。

## 概要

問題 PDF を Claude Code に投入すると、仕様書に従って自己完結型の HTML 教材を生成する。短答式（**TX**）と論文・事例式（**JX**）の 2 シリーズ × 7 科目をカバー。

## クイックスタート

### 1. 環境準備

```bash
# Python パッケージ
pip install beautifulsoup4
```

### 2. PDF 配置

```
inputs/
├── 000_TX/001_刑法/         # 短答式 PDF をここに置く
└── jx-pdfs/         # 論文・事例式 PDF をここに置く
```

PDF のファイル名は数字を含むこと（例：`299.pdf`、`K310-problem.pdf`）。数字部分が出力ファイル名のシリアル番号になる。

### 3. 生成

Claude Code で：

```
/new-tx inputs/000_TX/001_刑法/299.pdf
/new-jx inputs/jx-pdfs/15.pdf
```

出力は `outputs/000_TX/{科目TX}/` または `outputs/001_JX/{科目JX}/` に保存される。

### 4. 検証

```bash
python scripts/validate-tx.py outputs/000_TX/001_刑法/刑TX299.html
python scripts/validate-jx.py outputs/001_JX/003_民法/民JX015.html
```

Lexia 同期前の横断確認:

```bash
python scripts/check-lexia-preflight.py --root-only
python scripts/check-lexia-preflight.py --tooling-only
python scripts/check-lexia-preflight.py --allow-untracked-sync-artifacts
python scripts/check-lexia-sync-contract.py --summary --thin-report 20 --allow-untracked-sync-artifacts
```

`--root-only` は監査スクリプト/README など root 改善だけを切り出す時、`--tooling-only` は
root tooling と生成 validator 改善を同じ作業単位で見る時に使う。最終同期前は
`python scripts/check-lexia-preflight.py --final --bundle-dir deploy/lexia-preflight` を使う。

同期マニフェストは `fileName` / `code` / `title` / `subject` / `category` / `sourcePath` / `generated` に加え、HTML サイズの `bytes`、タグ除去後の `textLength`、生成日時フッターだけを無視した `stableSha256` を記録する。`textLength` は見た目の HTML サイズだけでは拾いにくい本文不足の検出に、`stableSha256` は「生成日時だけ変わって毎回更新扱いになる」原因の切り分けに使う。

## ディレクトリ構成

```
bar-exam/
├── CLAUDE.md                     # AI 向け指示書（必読）
├── README.md                     # 本ファイル
├── .claude/
│   ├── settings.local.json       # Claude Code 権限設定
│   └── commands/                 # カスタムスラッシュコマンド
│       ├── new-tx.md
│       ├── new-jx.md
│       ├── upgrade-tx.md
│       └── validate.md
├── spec/                         # 仕様書（読み取り専用扱い）
│   ├── tx-v9.0.0-genkei-core.md   # TX 仕様書 GENKEI（自己完結・5475 行）
│   └── jx-v3.2-master.md         # JX 仕様書（byte-level 正典・1320 行）
├── canonical/
│   └── KTX301.html               # 構造参考（本文複製禁止）
├── inputs/
│   ├── 000_TX/001_刑法/                  # TX 入力 PDF
│   ├── tx-legacy/                # 既存 TX HTML（アップグレード用）
│   ├── jx-pdfs/                  # JX 入力 PDF
│   └── jx-legacy/                # 既存 JX HTML（アップグレード用）
├── outputs/
│   ├── tx/
│   │   ├── 001_刑法/
│   │   ├── 007_憲法/
│   │   ├── 003_民法/
│   │   ├── 004_商法/
│   │   ├── 005_民事訴訟法/
│   │   ├── 002_刑事訴訟法/
│   │   └── 006_行政法/
│   └── jx/
│       ├── 001_刑法/
│       ├── 007_憲法/
│       ├── 003_民法/
│       ├── 004_商法/
│       ├── 005_民事訴訟法/
│       ├── 002_刑事訴訟法/
│       └── 006_行政法/
└── scripts/
    ├── validate-tx.py            # TX 構造＋コンテンツ独立性検証
    └── validate-jx.py            # JX 構造検証
```

## シリーズの違い

| 項目 | TX（短答式） | JX（論文・事例式） |
|---|---|---|
| **問題形式** | 5択・○×・組合せ等 | 事例問題（論文型） |
| **仕様書** | tx-v9.0.0-genkei-core.md | jx-v3.2-master.md |
| **設計思想** | GENKEI（原型骨格 + 刑TX300 由来 byte-lock CSS/JS） | 三層ペルソナ（法学教育者・認知心理エディトリアル・色彩設計） |
| **PART 構成** | A（問題＋解答）／B（肢別解説）／A-3（共通根拠）／C（体系・記憶）／D（ARENA） | 第 0〜5 部構成（凡例／本論 A〜H／採点講評／体系化／完全プロファイル） |
| **タイポ** | 12 役割書体 | 11 役割書体 |
| **1 問の処理時間** | 数分〜30 分 | 1〜2 時間 |
| **HTML 1 問のサイズ** | 約 110〜130 KB | 数百 KB〜1 MB 規模 |
| **検証** | S1〜S82 | J1〜J20 |

## ファイル命名規則（共通）

```
{日本語科目接頭辞}{TX|JX}{3桁0埋め数字}.html
```

| 科目 | TX | JX |
|---|---|---|
| 刑法 | 刑TX001.html | 刑JX001.html |
| 憲法 | 憲TX015.html | 憲JX015.html |
| 民法 | 民TX120.html | 民JX120.html |
| 商法 | 商TX045.html | 商JX045.html |
| 民訴 | 民訴TX078.html | 民訴JX078.html |
| 刑訴 | 刑訴TX033.html | 刑訴JX033.html |
| 行政法 | 行政TX092.html | 行政JX092.html |

PDF ファイル名の最初の連続数字 → 3 桁ゼロ埋め → 上記形式のファイル名。詳細は `CLAUDE.md` §2 参照。

## v8.11.7 で取り込まれた一連の対策

このプロジェクトの最大の課題は「Claude Code に仕様書を投入すると、§Annex B body skeleton 内に逐語埋込されている KTX301 の問題固有テキスト（詐欺罪論点・特定判例引用）が、別問題の生成時にそのまま流用される」事故（**canonical text leakage**）でした。

v8.11.7 は、v8.11.1 で確立した本クリーン版（jp-prefix-naming + content-independence）に、旧プロジェクトで段階的に開発された v8.11.2〜v8.11.6-hotfix1 の機能を一括統合したバージョンです。**1 つの仕様書ファイルで全ての規律を網羅**しているため、複数バージョン仕様書の混在運用は不要になりました。

### v8.11.1 由来（本クリーン版基盤）

1. **§0-quad コンテンツ独立性プロトコル 7 ステップ**：構造シェルと本文テキストを厳密分離し、本文は「§Annex B を一切参照せず問題 PDF だけから新規執筆」させる
2. **§0-quad-2 禁止文言ブラックリスト 18 項目**：KTX301 由来の特定文言（「畏怖の一材料」「最判昭28.5.8」等）を機械検出
3. **§1-bis 日本語接頭辞 + TX 命名規則**：刑TX／憲TX／民TX／商TX／民訴TX／刑訴TX／行政TX の正式化
4. **AP-42 / S78 / S79 / S80 / S81 / S82**：上記の機械検出（v8.11.7 で renumber）

### v8.11.2 由来：A-2 2 段階開示プロトコル

5. Stage 1（選択 → ハイライトのみ）と Stage 2（reveal → 正誤判定）を厳格分離
6. `<button class="reveal-answer-btn">` 必須、`<p class="answer-instruction">` canonical 文言固定
7. **AP-33 / AP-34 / S71 / S72**

### v8.11.3 由来：3 Type 対応

8. `data-answer-type` で single / multi / ox-grid を自動分岐
9. selection-counter UI（multi）／answer-ox-grid UI（ox-grid）
10. **AP-35 / S73**

### v8.11.4 由来：spoiler-leak-eradication

11. PART A 内「N（XX）正解」リテラル排除／`data-explanation` 先頭の正解値リテラル排除／FA は正解の数字のみ表示
12. **AP-36 / AP-37 / AP-38 / S74 / S75**

### v8.11.5 由来：spoiler-strong-elimination + ox-grid-fa-unification

13. PART A 内 `<strong>N（XX）</strong>` 太字削除／ox-grid 型 FA を `<span class="answer-num">11112</span>` 形式に統一
14. **AP-39 / AP-40 / S76**

### v8.11.6-hotfix1 由来：host-injection-safe

15. `<script>` 内に `</body>` リテラル禁止（Lexia 等の host アプリ正規表現バグ対策）
16. **AP-41 / S77**

---

詳しくは `spec/legacy/tx-v9.0.0-genkei-core.md` の冒頭 GENKEI 設計哲学・§33 footer-spec canonical（v9.0.0 GENKEI 版）・§37 仕様書終了の v9.0.0 経路総括を参照。v8.11.x 系の差分史は §0-prime（v8.11.1 → v8.11.7 統合差分）と §34-bis〜§34-novies に保持。

## トラブルシューティング

### 「数字が抽出できない」と Claude Code に言われた
PDF ファイル名に数字が含まれていない可能性。ファイル名をリネーム（例：`299_problem.pdf`）してから再実行。

### canonical/KTX301.html を消してもいい？
構造の完成形を確認したい時の参考実装。仕様書 v8.11.1 は自己完結（§Annex A/B/C 全文埋込）なので、KTX301.html がなくても生成可能。ただし「実物の見た目」を確認したい場合は手元に置いておくと便利。

### v3.2 と TX v8.11.7 の用語が違う
TX と JX は別シリーズで独立した仕様体系。それぞれの仕様書の用語に従う：
- TX：PART A/B/C/D、sub-card 4 種、ARENA など
- JX：第 0〜5 部、A〜H サブ構造、三層ペルソナ など

### Lexia でクイズが動かない
TX/JX 共通の致命的バグ。`<script>...</script>` 内のどこかに `</body>` というリテラル文字列を書いていないか確認（コメント・文字列・テンプレートリテラル全部）。代替表記：`</` + `body>` のように分割。

## ライセンス

個人学習用途。
