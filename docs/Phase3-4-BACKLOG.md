# Phase 3/4+ slot 化 BACKLOG

> `templates/KTX_template*.html` のリテラル HTML を JSON-schema-driven な slot に
> 段階的に置換していく作業の継続管理ドキュメント。各 Phase 完了時に §0 へ追記し、
> §1 を次 Phase スコープで上書きする運用。

---

## §0. 完了済み phase 一覧

| Phase | 内容 | commit | byte-identical 14 件 |
|---|---|---|---|
| **2** | PART C 7 sections (C-1〜C-7) を `{{C1_SYSTEMATIC}}`〜`{{C7_MEMORY}}` に slot 化 | `47c1f1d` | ✅ 維持 |
| **3-1〜3-5** | PART B basis cards (statute / case) を `{{BASIS_CARDS}}` に slot 化 + 構造化レンダリング。300.json を 1st demo | `1f54a17` | ✅ 維持（300 のみ意図的 DIFF） |
| **4-1** | PART A 【見解】(sc5 単独) を `{{VIEWS_BLOCK}}` に slot 化 | `88b0486` | ✅ 維持 |
| **4-2** | footer-spec feature-tag 列 (8 templates 共通) を `{{FOOTER_FEATURE_TAGS}}` に slot 化 | `88b0486` | ✅ 維持 |
| **4-3** | C-7 末尾 final-answer DOM block (§22-bis 単一 / §22-ter 多解答) を render.py 内嵌型で実装。300.json に 1st demo (詐欺罪・single-choice-5)。thin schema (final_answer.summary_html + 任意 extra_html)、β 配置 (template 不変)、hidden 属性必須を render 側で強制 | `0f7e673` (BACKLOG) / `abd2a28` (schema) / `f327664` (data) / `dee2bc0` (render) | ✅ 維持（300 のみ DIFF） |
| **4-4** | basis card rb-chip back-link target id を inject_ref_ids() 後処理で auto-注入 (canonical 規約 `ref-X-NNN`)。300.json basis 規約整理 (`-1-` qualifier 削除) + 最判平8.4.26 anchor 化 + 8th basis card 追加で完全 resolve。全 15 件 ERROR 0 / WARNING 0 達成 | `41f0edf` (BACKLOG) / `b2bb088` (render) / `49dea8d` (data) | ✅ 維持（300 のみ DIFF） |
| **4-5** | 8 templates の sync-required marker-legend block (11 行・709 bytes) を `{{MARKER_LEGEND}}` に集約 slot 化。universal content (subject / instruction_type 無関係) のため schema/JSON 改修なし、引数なし render_marker_legend() 関数で完結。--dry-run 8/8 OK で universality 実証 → extra_legend_items hook 不要が確定 | `6b64e17` (BACKLOG) / `9caa756` (render) / `3cc412c` (templates) | ✅ 維持（300 のみ DIFF） |
| **4-6** | 8 templates の diff-allowed `toc` 領域 (6 variants → 1 集約) を `{{TOC_ROW}}` に集約 slot 化。thin schema 派生 (problem.instruction_type → TOC_CHOICE_LABELS_BY_TYPE) で choice ラベル系列を生成、universal 部分 (TOC_HEAD / TOC_TAIL) は const。未対応 instruction_type で RuntimeError raise (silent fallback 不採用) | `7555a40` (BACKLOG) / `1afefca` (render) / `e93c3cb` (templates) | ✅ 維持（300 のみ DIFF） |
| **4-7** | 8 templates の PART D drill 12 件固定 slot 方式 (旧 60 個 DRILL_NN_* slot) を `{{DRILL_BLOCKS}}` 1 slot + 構造化レンダリング (render_drill_blocks) に移行。**パターン D 確立** (Phase 3-3 basis structured rendering の再利用)、A/B/C/D の **4 パターン体系完成**。escape 旧仕様踏襲 (720 field-values 検証で 0 件確認)、num JSON 信頼、旧 60 slot 完全削除。8 templates 各 -8,850 bytes (本セッション最大規模、累計 -70 KB) | `5f4856a` (BACKLOG) / `39cf18b` (render) / `28e6e28` (templates) | ✅ 維持（300 のみ DIFF） |

CP gate 正準 baseline: `_phase3_2_pre_patch_baseline.json` (`docs/cp-gate.md` §1)

---

## §1. Phase 4-8: body_pre_toc slot 化（universal const + Python .format() 名前付き placeholder）

### 1-1. 領域の特性

`body_pre_toc` は `</style>` 〜 TOC bar 直前の **sync-required 領域**（393 bytes / 11 lines、
8 templates 完全 byte-identical / hash=`1fb1fe871c7e`）。Phase 4-5 marker-legend と同様
universal な構造を持つが、内部に 6 個の **動的 slot** を含む点で異なる:

```html
</head>
<body id="top">
<div class="container">

  <!-- HEADER -->
  <header class="header">
    <div class="doc-header">{{JP_PREFIX}}{{PROBLEM_ID}}</div>
    <h1>No.{{PROBLEM_ID}} ── {{CRIME}}（{{SOURCE_ID}}）</h1>
    <div class="exam-meta">
      <span><strong>正答率:</strong>{{CORRECT_RATE}}</span>
      <span><strong>パターン:</strong>{{OVERRIDE_PATTERN}}</span>
    </div>
```

含む動的 slot は 6 個（重複除いて）: `JP_PREFIX` / `PROBLEM_ID` / `CRIME` / `SOURCE_ID` /
`CORRECT_RATE` / `OVERRIDE_PATTERN`。これら旧 slot は footer-spec 等で他にも参照される
ため、Phase 4-8 で **削除しない**（temp 据え置き、BODY_PRE_TOC は経路の重複となる）。

### 1-2. 設計選択肢の比較と採択（案 δ refined）

| 観点 | (δ) const + render slot 順序依存 | (δ) refined: .format() + 名前付き placeholder | (α) 引数あり関数 |
|---|---|---|---|
| Phase 4-5 同形度 | 完全同形 | ほぼ同形（template が Python format） | 異なる |
| insertion order 依存 | あり（コメント mitigation） | **なし**（.format() で一括解決）| なし |
| 実装複雑度 | 低 | 低 | 中 |
| 保守性 | 中（暗黙の依存）| **高**（名前参照、明示的）| 高 |
| 将来 placeholder 追加時の保守性 | 中（順序に注意必要）| **高**（辞書 1 行追加）| 中 |
| パターン分類 | C（universal const）| C（universal template + .format）| A（thin schema 派生）|

**採択: (δ) refined — Python `.format(**problem_dict)` 名前付き placeholder 方式**

採択理由（ユーザ §8 回答）:
- Phase 4-5 同形を保ちつつ、insertion order 依存を **`.format()` 名前参照で実質非依存化**
- 引数あり関数 (α) は将来 placeholder 追加時の関数シグネチャ拡張負担が懸念
- `.format(**problem_dict)` で辞書 unpack 渡しなら placeholder 追加が辞書 1 行で済む

### 1-3. byte-identical 維持の前提

- 8 templates の body_pre_toc 領域は **完全 byte-identical**（hash=`1fb1fe871c7e`、Commit 2
  着手前に再確認予定）
- 旧 6 個の slot (`{{JP_PREFIX}}` 等) と新 BODY_PRE_TOC slot 値（`.format()` 解決済）が
  同じ HTML 文字列を生成 → 全 15 件 byte-identical 維持期待
- escape 旧仕様踏襲（escape なし、Phase 4-7 と同一方針）。Phase 4-7 の 720 field-values
  検証で実証済の問題著者の運用ルール（attribute-safe な内容を手動メンテ）に依存

### 1-4. 命名規約

| 項目 | 名称 |
|---|---|
| slot 名 | `{{BODY_PRE_TOC}}` |
| const 名 | `BODY_PRE_TOC_TEMPLATE` (Python format placeholder `{jp_prefix}` 等を含む) |
| 関数名 | `render_body_pre_toc(problem: dict) -> str` |
| upgrade スクリプト | `scripts/upgrade_templates_body_pre_toc_slot.py` |

---

## §2. 設計（案 δ refined・確定版）

### 2-1. 採択方針

| 項目 | 設計 |
|---|---|
| schema 変更 | **なし** |
| JSON 改修 | **なし**（既存 6 slot 値を流用） |
| 新 slot | `{{BODY_PRE_TOC}}` を 8 templates の body_pre_toc 領域全体に置換 |
| render.py 改修 | `BODY_PRE_TOC_TEMPLATE` const (Python format placeholder) + `render_body_pre_toc(problem)` 関数 + `slots["BODY_PRE_TOC"]` 配線 |
| 旧 6 slot の去就 | **据え置き**（footer-spec 等で他参照あり、削除不可）。BODY_PRE_TOC は経路の重複となるが許容 |
| escape 処理 | 旧仕様踏襲（escape なし、Phase 4-7 と同一方針） |
| 14 protected への影響 | byte-identical 維持期待（旧 6 slot 経由 == 新 BODY_PRE_TOC 経由が同 HTML 生成） |
| 300 への影響 | 同上 |

### 2-2. render.py 追加内容

```python
# Phase 4-8: body_pre_toc slot 化
# 8 templates の sync-required 領域 body_pre_toc block (393 bytes / 11 lines、
# universal な HTML 構造 + 6 個の動的値) を集約 slot 化。Phase 4-5 marker-legend と
# 同形の universal const パターンを、Python .format() 名前付き placeholder で動的値
# を埋め込む形に拡張。

BODY_PRE_TOC_TEMPLATE: str = (
    '</head>\n'
    '<body id="top">\n'
    '<div class="container">\n'
    '\n'
    '  <!-- HEADER -->\n'
    '  <header class="header">\n'
    '    <div class="doc-header">{jp_prefix}{problem_id}</div>\n'
    '    <h1>No.{problem_id} ── {crime}（{source_id}）</h1>\n'
    '    <div class="exam-meta">\n'
    '      <span><strong>正答率:</strong>{correct_rate}</span>\n'
    '      <span><strong>パターン:</strong>{override_pattern}</span>\n'
    '    </div>'
)


def render_body_pre_toc(problem: dict) -> str:
    """{{BODY_PRE_TOC}} slot 値を返す（Python .format() で動的値を埋込）。

    旧 6 slot ({{JP_PREFIX}} 等) と同じ値を Python format placeholder 経由で埋込み、
    slot 機構を経由しない完成 HTML を返す。insertion order 非依存。
    escape 旧仕様踏襲（escape なし）。
    """
    subject = problem.get("subject", "KEI")
    jp_prefix = SUBJECT_TO_JP[subject] + "TX"
    return BODY_PRE_TOC_TEMPLATE.format(
        jp_prefix=jp_prefix,
        problem_id=str(problem.get("id", "")),
        crime=str(problem.get("crime", "")),
        source_id=str(problem.get("source", "")),
        correct_rate=str(problem.get("correct_rate", "")),
        override_pattern=str(problem.get("override_pattern", "P1")),
    )
```

`build_slot_dict()` に slot 供給を追加（旧 6 slot は据え置き）:
```python
# Phase 4-8: body_pre_toc 集約 slot
slots["BODY_PRE_TOC"] = render_body_pre_toc(problem)
```

### 2-3. upgrade スクリプト

8 templates の body_pre_toc 領域全体（11 行・393 bytes・hash 完全一致）を
`{{BODY_PRE_TOC}}` 1 行に置換。8 templates すべてに同一 OLD（byte-identical のため）→
単一 OLD で 8 templates 同パッチ可能（Phase 4-5 marker-legend / Phase 4-7 drill と同形）。

```python
OLD = (
    '</head>\n'
    '<body id="top">\n'
    '<div class="container">\n'
    '\n'
    '  <!-- HEADER -->\n'
    '  <header class="header">\n'
    '    <div class="doc-header">{{JP_PREFIX}}{{PROBLEM_ID}}</div>\n'
    '    <h1>No.{{PROBLEM_ID}} ── {{CRIME}}（{{SOURCE_ID}}）</h1>\n'
    '    <div class="exam-meta">\n'
    '      <span><strong>正答率:</strong>{{CORRECT_RATE}}</span>\n'
    '      <span><strong>パターン:</strong>{{OVERRIDE_PATTERN}}</span>\n'
    '    </div>'
)
NEW = '{{BODY_PRE_TOC}}'
```

### 2-4. check_template_sync 境界検出

body_pre_toc 領域は `style_close + 1` 〜 `toc_open` で挟まれている。slot 化後 toc_open は
引き続き `{{TOC_ROW}}` 単一行（Phase 4-6 既対応）、style_close は `</style>` で不変。
したがって境界検出は **更新不要**。

ただし slot 化後の body_pre_toc 領域は `{{BODY_PRE_TOC}}` 1 行となり、現在の sync 領域
hash が変わるが、8 templates 同パッチなので同期維持（[1 variants] のまま）。

### 2-5. 検証戦略

- Commit 2 着手前: body_pre_toc 領域の 8 templates 完全 byte-identical を **再度** grep で
  確認（前 commit 466bc8a 後の現状で hash 一致を verify）
- Commit 2 (render 改修) 後: template 未変更のため CP gate 不変（slot 未使用、再 render
  しても出力 byte-identical）。**代替検証**: `render_body_pre_toc(problem)` 単体出力 ==
  現 outputs の対応領域、を 15 件 byte-identical 比較
- Commit 3 (template + apply) 後: 全 15 件再 render → 全 15 件 byte-identical 維持確認、
  CP gate / check_template_sync / validate-tx 全 PASS

### 2-6. broken intermediate state は発生しない

Phase 4-7 と異なり、旧 6 slot は削除しないため、Commit 2 完了直後の中間状態でも render
は通常通り動作する（旧 slot で template 直接 substitute、新 BODY_PRE_TOC slot 値は
template に `{{BODY_PRE_TOC}}` placeholder が無いので未使用）。Phase 4-7 のような broken
intermediate state mitigation 不要。

---

## §3. 3 commit 実装計画

各 commit 後 STOP for review。各 commit で CP gate + check_template_sync + validate-tx（全 15 件）を実行。

| # | commit subject | 影響範囲 | CP gate | sync | validate-tx |
|---|---|---|---|---|---|
| 1 | `docs: BACKLOG.md §1 Phase 4-8 body_pre_toc スコープ展開` (§0 は前 commit 466bc8a で Phase 4-7 追記済) | docs only | PASS=14 / DIFF=1 維持 | ✅ | 全 15 件 ERROR 0 / WARNING 0 維持 |
| **(中間検証)** | body_pre_toc 領域 8 templates 完全 byte-identical 再確認 | 検証のみ、コミットなし | — | — | 検証結果を STOP for review |
| 2 | `feat(phase4-8 render): BODY_PRE_TOC_TEMPLATE + render_body_pre_toc() + slot 供給配線` | scripts/render.py | PASS=14 / DIFF=1 維持（template 未変更、新 slot 未使用、render 出力不変）| ✅ | 全 15 件維持 |
| 3 | `feat(phase4-8 templates): 8 templates の body_pre_toc を {{BODY_PRE_TOC}} に置換` | upgrade script + 8 templates + outputs (全 15 件 byte-identical 期待) | PASS=14 / DIFF=1 維持 | ✅ | 全 15 件維持 |

### Phase 4-8 完了条件

- 全 15 件 `validate-tx.py` で ERROR 0 / WARNING 0 を**維持**
- CP gate PASS=14 / DIFF=1（300 のみ DIFF、Phase 4-7 完了状態と同じ）
- check_template_sync sync-required 7 領域 PASS（body_pre_toc 領域は slot 化で hash 変わるが 8 templates 同期維持）
- 8 templates の body_pre_toc (11 行) が `{{BODY_PRE_TOC}}` 単行に縮減（累計 -約 3,120 bytes、Phase 4-7 drill -70 KB と比較して極小）

---


## §4. Phase 4-9 以降の候補（参考、未着手）

| 候補 | 領域 | 主要懸念 | 優先度 |
|---|---|---|---|
| **PART A 見出しコメント**（pre_part_a diff-allowed 8 variants）| pre_part_a diff-allowed 領域 (8 variants) | コメント文言の集約、Phase 4-6 TOC と同形（per-instruction-type 派生、パターン A + C 組合せ）| **中（最有力）** |
| `head` 領域（DOCTYPE 〜 `<style>` 直前）| head sync 領域（867 bytes / 8 lines） | 静的、変更頻度低、Phase 4-5 marker-legend と同形 universal | 低 |
| `css` 領域（巨大）| css sync 領域（60,743 bytes / 1,996 lines） | spec の §Annex A canonical CSS と同期、構造化困難 | 低（要設計検討） |
| `js` 領域 | js sync 領域（17,552 bytes / 404 lines） | spec の §Annex C canonical JS と同期、構造化困難 | 低（要設計検討） |
| Phase 5+ JX シリーズ着手 | JX 系（事例式） | spec/jx-v3.2-master.md 由来の構造化 (A〜H 8 サブセクション + 第 3〜5 部)、1 問 1〜2 時間規模 | 別シリーズ・別 Phase（Phase 4 完了後） |

Phase 4-8 完了後、優先度順にスコープ化する。**Phase 4-9 は pre_part_a が最有力候補**
（Phase 4-6 TOC と同形 A+C 組合せ、8 variants の dispatch パターン応用、技術的に既習）。

---

## §5. 検証スクリプトと baseline

| スクリプト | 目的 | Phase 4-N 期待値 |
|---|---|---|
| `scripts/_cp_gate_check.py` | 全 15 件再 render → baseline と sha256 比較 | PASS=14 / DIFF=1 (300) |
| `scripts/check_template_sync.py` | 8 templates の sync-required 7 領域一致確認 | 全 commit で PASS |
| `scripts/validate-tx.py` | S1〜S82 構造/feature-tag/content independence 検証 | 全 15 件 ERROR 0 / WARNING 0 |

baseline は `_phase3_2_pre_patch_baseline.json` 据え置き（byte-identical 維持型 patch のため、`docs/cp-gate.md` §4 「baseline 更新ルール」 で更新不要に該当）。

---

## §6. 将来課題（未着手・参考）

### 6-1. 法条文の項・号 qualifier 付き ref-id 規約 `ref-law-X-Y-NNN`

Phase 4-4 では canonical KTX301 規約に揃え `ref-law-XXX-NNN`（項・号 qualifier なし）を採用。
ただし以下の限界がある:

- 同一条文の複数項（例: 246条1項 / 246条2項）を区別したい問題で、`ref-law-246-NNN` 単一系列は
  項を跨ぐ通し番号となり、basis chip 著者が記述ごとに該当項を特定する手数が増える
- 検索性・semantic 性で `ref-law-246-1-NNN` / `ref-law-246-2-NNN` の方が優れる

**着手判断条件**: 同一条文の複数項を同時参照する問題が出現したとき。それまでは canonical
規約で十分。実装時は `inject_ref_ids()` 内で anchor 表示テキストから「N項」「N号」を正規表現で
抽出し、id 構成に加える。

### 6-2. ref-case の冒頭以外への id 付与

現状 inject_ref_ids() は **document order の出現順**で NNN を付与する。記述N解説の文中で
ある case が複数回 inline 引用される場合、basis chip が "解説" / "あてはめ" / "考え方" 等の
複数ラベルで NNN を狙うが、NNN と段落 (h3, prof-summary, prof-note) との対応は chip 著者の
手作業で当てる必要がある。

**改善案**（着手条件: 大量の chip mis-targeting が発見されたとき）: render.py 側で
inline anchor の所属段落 (`<p class="prof-summary">` 内 / `<p class="prof-note">` 内 等) を
判定し、id に段落クラス情報を含める。但しこれは canonical 規約からの逸脱になるため、規約改定
の合意必要。

### 6-3. ref-id 全件の双方向検証

Phase 4-4 完了後、`validate-tx.py` の S8 は href→id 方向（chip が target を持つか）のみ検証する。
逆方向（id を target とする chip が存在するか）の検証は未実装。未使用 id があっても害はないが、
仕様の clean 性追求のため将来追加候補。

### 6-5. TOC choice ラベル series の拡張余地

Phase 4-6 で採用した `TOC_CHOICE_LABELS_BY_TYPE` は現状 4 series × 最大 3 N 値 = 6 cells 占用。
24 cells のうち 18 cells が拡張余地（例: ロ〜ホ系 / 漢数字 / N=6+ 等）。現状仕様外、設計に含めず
（YAGNI 重視）。新 instruction_type 追加時は辞書 1 行追加で対応可能。

### 6-6. drill-block field の HTML escape 規約

Phase 4-7 で旧仕様踏襲（escape なし）を採用。現運用では drill 各 field の HTML 内容が
attribute 安全な範囲に収まっているため byte-identical を優先。

**着手判断条件**: drill explanation 等に `<` `"` `&` 等の attribute-unsafe 文字が含まれる
問題が出現し、HTML 構文崩壊が顕在化したとき。実装時は `data-explanation` 等の attribute
内に出力する slot に対して個別に `html.escape(v, quote=True)` を適用、quiz-answer の text
content 出力は escape なし維持。**byte-diff が出るため新 baseline 切り替えが必要**になる
点に注意。
