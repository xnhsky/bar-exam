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
| **4-8** | 8 templates の sync-required body_pre_toc (393 bytes / 12 lines) を `{{BODY_PRE_TOC}}` slot 化。**案 (δ) refined: Python .format() 名前付き placeholder** で動的値埋込 (旧 6 slot {{JP_PREFIX}} 等は据え置き、本 slot は経路の重複)。**パターン C の 4 例目**（universal const を .format() 拡張、broken intermediate state なし）。8 templates 各 -377 bytes、累計 -3,016 bytes | `ff09a5b` (BACKLOG) / `7331edb` (render) / `783c8bb` (templates) | ✅ 維持（300 のみ DIFF） |
| **4-9** | 8 templates の diff-allowed pre_part_a 領域 (4 lines / 180-223 bytes、8 variants 完全 1:1 対応) を `{{PRE_PART_A}}` に集約 slot 化。**A + C 組合せ 2 例目** (Phase 4-6 TOC 同形、PRE_PART_A_FORM_NAMES_BY_TYPE 辞書 8 entry + HTML コメント枠 const)。未対応 instruction_type で RuntimeError raise。fillin8 form 名内コロン全角 (U+FF1A) を template byte-identical 保証。pre_part_a variants 8→1 集約、各 -180〜-223 bytes、累計 -約 1,526 bytes | `0a4eb04` (BACKLOG) / `5b61da4` (render) / `ec8f7ab` (templates) | ✅ 維持（300 のみ DIFF） |

CP gate 正準 baseline: `_phase3_2_pre_patch_baseline.json` (`docs/cp-gate.md` §1)

---

## §1. Phase 4-10: head 領域 slot 化（Phase 4-8 body_pre_toc 同形・C refined 3 例目）

### 1-1. 領域の特性

`head` は DOCTYPE 〜 `<style>` 直前の **sync-required 領域**（867 bytes / 9 lines、
8 templates 完全 byte-identical / hash=`ccd63a7fba54`）。Phase 4-8 body_pre_toc と
同様、内部に 4 個の **動的 slot** を含む点で完全静的 universal const とは異なる:

```html
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{JP_PREFIX}}{{PROBLEM_ID}} - {{CRIME}}（{{SOURCE_ID}}）</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=...&display=swap" rel="stylesheet">
```

含む動的 slot 4 個（重複除いて）: `JP_PREFIX` / `PROBLEM_ID` / `CRIME` / `SOURCE_ID`、
すべて `<title>` 行に集中。`OVERRIDE_PATTERN` 等は不在 → **P1/P2/P3 間で head 出力差異
なし**。

### 1-2. 着手前調査の確定事項

| 観点 | 結果 |
|---|---|
| P1/P2/P3 間の head 差分 | **なし**（OVERRIDE_PATTERN slot 不在）|
| title slot 化方針 | head 集約 slot に **内包**（別 slot 化不要）|
| doc-header の所在 | head 外（body_pre_toc 内、**Phase 4-8 で集約済**）|
| パターン分類判定 | head 内に 4 動的 slot 含む → **C refined** 採択（純粋形 NG） |

### 1-3. Phase 4-8 body_pre_toc との対比

| 観点 | Phase 4-8 body_pre_toc | Phase 4-10 head |
|---|---|---|
| sync 状態 | 8 templates 完全 byte-identical | 同左 |
| 内部動的 slot 数 | 6 個 | **4 個** |
| パターン分類 | C refined (.format()) | C refined (.format()) ← **3 例目** |
| 旧 slot 据え置き | 全 6 個 (footer-spec 等で他参照) | 全 4 個 (footer-spec / body_pre_toc で他参照) |
| broken state | なし | なし |
| 規模 | 393 bytes | 867 bytes (約 2.2 倍) |
| 設計コスト | 中（パターン確立）| **極低**（Phase 4-8 を機械的踏襲）|

→ Phase 4-10 head は **Phase 4-8 body_pre_toc のロジックをほぼコピペで適用**。

### 1-4. 命名規約

| 項目 | 名称 |
|---|---|
| slot 名 | `{{HEAD}}` |
| const 名 | `HEAD_TEMPLATE` (Python format placeholder `{jp_prefix}` 等を含む) |
| 関数名 | `render_head(problem: dict) -> str` |
| upgrade スクリプト | `scripts/upgrade_templates_head_slot.py` |

---

## §2. 設計（C refined・Phase 4-8 同形・確定版）

### 2-1. 採択方針

| 項目 | 設計 |
|---|---|
| schema 変更 | **なし** |
| JSON 改修 | **なし**（既存 4 slot 値を流用） |
| 新 slot | `{{HEAD}}` を 8 templates の head 領域全体に置換 |
| render.py 改修 | `HEAD_TEMPLATE` const (Python format placeholder) + `render_head(problem)` 関数 + `slots["HEAD"]` 配線 |
| 旧 4 slot の去就 | **据え置き**（body_pre_toc / footer-spec 等で他参照あり、削除不可）。HEAD は経路の重複 |
| escape 処理 | 旧仕様踏襲（escape なし、Phase 4-7/4-8 と同一）|
| 14 protected への影響 | byte-identical 維持期待 |
| 300 への影響 | 同上 |

### 2-2. render.py 追加内容

```python
HEAD_TEMPLATE: str = (
    '<!DOCTYPE html>\n'
    '<html lang="ja">\n'
    '<head>\n'
    '<meta charset="UTF-8">\n'
    '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
    '<title>{jp_prefix}{problem_id} - {crime}（{source_id}）</title>\n'
    '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
    '<link href="https://fonts.googleapis.com/css2?family=...省略...&display=swap" rel="stylesheet">'
)


def render_head(problem: dict) -> str:
    """{{HEAD}} slot 値を返す（Python .format() で動的値埋込）。"""
    subject = problem.get("subject", "KEI")
    jp_prefix = SUBJECT_TO_JP[subject] + "TX"
    return HEAD_TEMPLATE.format(
        jp_prefix=jp_prefix,
        problem_id=str(problem.get("id", "")),
        crime=str(problem.get("crime", "")),
        source_id=str(problem.get("source", "")),
    )
```

`build_slot_dict()` に `slots["HEAD"] = render_head(problem)` を 1 行追加。

### 2-3. upgrade スクリプト

8 templates 同一 OLD (head 領域全体、867 bytes) → 共通 NEW = `{{HEAD}}`。
Phase 4-8 body_pre_toc と同形の単一 OLD 方式。

### 2-4. byte-identical 維持リスク

**極めて低い**:
- 8 templates 完全 byte-identical 確認済
- 動的 slot 4 個はすべて他で参照あり据え置き
- Phase 4-8 body_pre_toc で .format() 拡張パターン実証済
- font URL の `family=` クエリ等に `{` `}` リテラル不在を確認 → `.format()` 安全

### 2-5. broken intermediate state なし

旧 4 slot を削除しないため、Commit 2 完了直後でも render は通常動作。

---

## §3. 3 commit 実装計画

各 commit 後 STOP for review。各 commit で CP gate + check_template_sync + validate-tx（全 15 件）を実行。

| # | commit subject | 影響範囲 | broken state |
|---|---|---|---|
| 1 | `docs: BACKLOG.md §0 Phase 4-9 完了追記 + §1 Phase 4-10 head スコープ` | docs only | なし |
| 2 | `feat(phase4-10 render): HEAD_TEMPLATE + render_head() + slot 供給配線` | scripts/render.py | なし |
| 3 | `feat(phase4-10 templates): 8 templates の head を {{HEAD}} に置換` | upgrade script + 8 templates + outputs (byte-identical 期待) | なし |

### Phase 4-10 完了条件

- 全 15 件 `validate-tx.py` で ERROR 0 / WARNING 0 を**維持**
- CP gate PASS=14 / DIFF=1（300 のみ DIFF、Phase 4-9 完了状態と同じ）
- check_template_sync sync-required 7 領域 PASS（head は slot 化で新 hash になるが 8 templates 同期維持）
- 8 templates の head (9 行) が `{{HEAD}}` 単行に縮減（累計 -約 6,800 bytes）

---

## §4. Phase 4-11 以降の候補（参考、未着手）

| 候補 | 領域 | 主要懸念 | 優先度 |
|---|---|---|---|
| **basis 領域** (diff-allowed 6 variants) | basis diff-allowed 領域 (avg 335 bytes / 6 lines、A-3 sec-nav back-link 差) | Phase 4-6 TOC / 4-9 pre_part_a と同形の A+C 組合せ **3 例目**。Phase 3-3 で basis card 構造化済との関連整理が必要 | **中（最有力）** |
| `part_a` 領域 (diff-allowed 8 variants) | avg 1,515 bytes / 21 lines | instruction_type 別の問題情報差。A+C か D 寄りかは事前調査必要 | 中 |
| `a2` 領域 (diff-allowed 8 variants) | avg 1,643 bytes / 60 lines | A-2 解答エリア構造差、D 構造化レンダリング寄り | 中 |
| `part_b` 領域 (diff-allowed 6 variants) | avg 5,530 bytes / 174 lines | 最大規模 diff-allowed、A + D 組合せ可能性 | 低（設計セッション要）|
| `css` 領域（巨大）| sync (60,743 bytes / 1,997 lines) | spec §Annex A canonical CSS と同期、構造化困難 | 低（要設計検討）|
| `js` 領域 | sync (17,552 bytes / 405 lines) | spec §Annex C canonical JS と同期、構造化困難 | 低（要設計検討）|
| Phase 5+ JX シリーズ着手 | JX 系（事例式）| spec/jx-v3.2-master.md 由来の構造化 (A〜H 8 サブセクション + 第 3〜5 部)、1 問 1〜2 時間規模 | 別シリーズ・別 Phase（Phase 4 完了後）|

Phase 4-10 完了後、優先度順にスコープ化する。**Phase 4-11 は basis 領域が最有力候補**
（A+C 組合せ 3 例目で「再利用の定型性」を完全実証、Phase 4-6 TOC / 4-9 pre_part_a の
dispatch ロジックを機械的踏襲、規模最小）。

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
