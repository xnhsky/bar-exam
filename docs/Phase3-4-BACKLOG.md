# Phase 3/4+ slot 化 BACKLOG

> `templates/KTX_template*.html` のリテラル HTML を JSON-schema-driven な slot に
> 段階的に置換していく作業の継続管理ドキュメント。Phase 4-2 完了時点の状態と、
> Phase 4-3 以降の予定を本ファイルで一元管理する。

---

## §0. 完了済み phase 一覧

| Phase | 内容 | commit | byte-identical 14 件 |
|---|---|---|---|
| **2** | PART C 7 sections (C-1〜C-7) を `{{C1_SYSTEMATIC}}`〜`{{C7_MEMORY}}` に slot 化 | `47c1f1d` | ✅ 維持 |
| **3-1〜3-5** | PART B basis cards (statute / case) を `{{BASIS_CARDS}}` に slot 化 + 構造化レンダリング。300.json を 1st demo | `1f54a17` | ✅ 維持（300 のみ意図的 DIFF） |
| **4-1** | PART A 【見解】(sc5 単独) を `{{VIEWS_BLOCK}}` に slot 化 | `88b0486` | ✅ 維持 |
| **4-2** | footer-spec feature-tag 列 (8 templates 共通) を `{{FOOTER_FEATURE_TAGS}}` に slot 化 | `88b0486` | ✅ 維持 |

CP gate 正準 baseline: `_phase3_2_pre_patch_baseline.json` (`docs/cp-gate.md` §1)

---

## §1. Phase 4-3: final-answer DOM block インテグレーション

### 1-1. スコープ

`spec/tx-v8.11.7-core.md §22-bis / §22-ter` で規定される `<div class="final-answer" hidden>`
DOM block を 14 outputs に反映する。現状すべての outputs で **DOM block 自体が
存在しない**（CSS と JS のみ）。canonical KTX301.html line 3036 が唯一の参考実装。

**最終形（C-7 末尾配置・§22-bis 単一解答型）:**
```html
    <!-- §22-bis: C-7 末尾配置 final-answer -->
    <div class="final-answer" hidden>
      <h3>🎯 正解</h3>
      <span class="answer-num">3</span>
      <p class="fa-summary"><strong>[一文要約]</strong>　[詳細]</p>
      <p>[追加説明＋ref-stat/ref-case リンク]</p>   <!-- extra_html、optional -->
    </div>
```

**§22-ter 多解答型（multi-select-5 専用）:**
```html
    <div class="answer-num answer-num-multi">
      <div class="ans-cell ans-correct"><span class="ans-stmt">1</span><span class="ans-val">1</span></div>
      <div class="ans-cell ans-correct"><span class="ans-stmt">4</span><span class="ans-val">1</span></div>
    </div>
```
正解と判定された記述のみ表示（AP-38）。ox-grid 系は AP-40 で single 形式に統一。

### 1-2. 関連仕様（spec/tx-v8.11.7-core.md）

| § | 内容 | 違反検出 |
|---|---|---|
| §22-bis | 単一解答型 4 行構成 | — |
| §22-ter | 多解答型 cell 構造、正解のみ表示 | AP-38 / S75 |
| §22-quater-1 | `hidden` 属性必須 | AP-30 / S68 |
| §22-quater-2 | `fa-summary` 内「正解はN」リテラル禁止 | AP-32 / S70 |
| §22-quater-3 | CSS 8 規則必須（既存・触れない）| AP-31 / S69 |
| AP-40 | ox-grid は single 形式統一 | S76 |

### 1-3. 採択した設計（前セッション議論より）

- **schema: 案 A thin**（既存 `problem.answer` + `problem.instruction_type` から派生、JSON 追加は `summary_html` + 任意 `extra_html` のみ）
- **配置: β（render.py 内嵌）**（template は変更せず、`render_c7_memory()` の出力末尾・back-to-top 直前に inject）
- **extra_html は独立 optional フィールド**（`summary_html` と分離、§22-bis 4 行目専用）
- **他 14 件は final_answer 未指定で byte-identical 維持**、300 のみ追加（demo case）

---

## §2. schema 拡張（案 A 確定版）

`schema/problem.schema.json` に追加する property:

```json
"final_answer": {
  "type": ["object", "null"],
  "additionalProperties": false,
  "description": "C-7 末尾配置 final-answer block (§22-bis 単一 / §22-ter 多解答)。null/未指定の場合は block ごと出力されない（既存 14 件 byte-identical 維持）。mode (single/multi) と answer-num 中身は problem.instruction_type + problem.answer から render.py 内で派生。multi-select-5 のみ §22-ter、それ以外は §22-bis（ox-grid 系も AP-40 で single）。",
  "required": ["summary_html"],
  "properties": {
    "summary_html": {
      "type": "string",
      "minLength": 1,
      "description": "<p class=\"fa-summary\"> の本文 HTML。先頭 <strong> 一文要約 + 詳細。「正解はN」リテラル禁止 (AP-32)"
    },
    "extra_html": {
      "type": "string",
      "description": "§22-bis 形式の 4 行目（追加説明 paragraph）の HTML。判例引用・体系整理等。§22-ter（multi-select-5）でも出力するが用途は同上。省略可"
    }
  }
}
```

`$defs` に追加する type なし（thin schema）。

### 派生ルール（render.py 実装方針）

```
if not problem.final_answer:                       → "" (block 不在、byte-identical 維持)
elif problem.instruction_type == "multi-select-5": → §22-ter 形式 (cells = [{stmt: n, val: "1"} for n in problem.answer])
else:                                              → §22-bis 形式 (answer-num = _format_answer(problem.answer))
```

---

## §3. 4 commit 実装計画

各 commit 後 STOP for review。各 commit で CP gate + check_template_sync + validate-tx (代表 4 件) を実行。

| # | commit subject | 影響範囲 | 期待 CP gate | sync 維持 | validate-tx |
|---|---|---|---|---|---|
| 1 | `docs: Phase 3/4+ BACKLOG.md` | docs only | PASS=14 / DIFF=1 (300) | ✅ | ✅ |
| 2 | `feat(phase4-3 schema): final_answer + extra_html optional` | schema/problem.schema.json | PASS=14 / DIFF=1 (300) | ✅ | ✅ |
| 3 | `feat(phase4-3 data): 300.json に final_answer demo` | problems/300.json | PASS=14 / DIFF=1 (300) | ✅ | ✅ |
| 4 | `feat(phase4-3 render): render_c7_memory() に final-answer 埋込` | scripts/render.py + outputs/tx/刑TX/刑TX300.html | PASS=14 / DIFF=1 (300 中身が更新) | ✅ | ✅ |

### 各 commit の検証コマンド

```bash
# CP gate
python scripts/_cp_gate_check.py

# template sync (Phase 4-3 では template を触らないので必ず PASS)
python scripts/check_template_sync.py

# validate-tx 代表 4 件
for f in 刑TX/刑TX326 憲TX/憲TX001 行政TX/行政TX001 刑訴TX/刑訴TX001; do
  python scripts/validate-tx.py "outputs/tx/$f.html"
done
```

### 期待値

- Commit 1-3: outputs 再 render 不要（schema/doc/JSON のみ変更）。CP gate は前 commit と同値
- Commit 4: 300 の outputs/tx/刑TX/刑TX300.html を再 render（final-answer DOM 追加で hash 変化）。
  baseline `_phase3_2_pre_patch_baseline.json` の 300 hash は維持されず DIFF 継続（許容範囲）。
  **他 14 件は再 render しても byte-identical（final_answer 未指定経路）**。
- `check_template_sync.py`: 全 commit で sync-required 7 領域 PASS（template 不変）
- `validate-tx.py`: 全 commit で ERROR 0 / WARNING 0。Commit 4 適用後の 300 では §22-bis canonical hit で
  S68 (hidden 必須) が初めて実質チェックされ、`hidden` 付与済みなら PASS

---

## §4. Phase 4-4 以降の候補（参考、未着手）

`templates/KTX_template*.html` で残るリテラル HTML / sync-required 領域内のハードコード：

| 候補 | 領域 | 主要懸念 | 優先度 |
|---|---|---|---|
| PART D drill-block 12 件 (`drill-block` literal) | part_c_d sync 領域内 | drill_blocks JSON は既存、template の `<div class="drill-block">` 構造を slot 化 | 中 |
| TOC 行（`<div class="toc-row">`）| toc diff-allowed 領域 (6 variants) | instruction_type 別の TOC ラベル差を render.py 側で生成 | 低 |
| marker-legend ブロック | marker_legend sync 領域 | リテラル固定だが、spec bump 時に同期手修正が必要 | 低 |
| body_pre_toc（`<div class="doc-header">` 等）| body_pre_toc sync 領域 | 静的、変更頻度低 | 低 |
| PART A 見出しコメント（pre_part_a diff-allowed 8 variants）| pre_part_a | コメント文言の集約 | 低 |

Phase 4-3 完了後、優先度順にスコープ化する。

---

## §5. 検証スクリプトと baseline

| スクリプト | 目的 | Phase 4-3 期待値 |
|---|---|---|
| `scripts/_cp_gate_check.py` | 全 15 件再 render → baseline と sha256 比較 | PASS=14 / DIFF=1 (300) |
| `scripts/check_template_sync.py` | 8 templates の sync-required 7 領域一致確認 | 全 commit で PASS |
| `scripts/validate-tx.py` | S1〜S82 構造/feature-tag/content independence 検証 | ERROR 0 / WARNING 0 |

baseline は `_phase3_2_pre_patch_baseline.json` 据え置き（byte-identical 維持型 patch のため、`docs/cp-gate.md` §4 「baseline 更新ルール」 で更新不要に該当）。
