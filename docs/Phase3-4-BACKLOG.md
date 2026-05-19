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

CP gate 正準 baseline: `_phase3_2_pre_patch_baseline.json` (`docs/cp-gate.md` §1)

---

## §1. Phase 4-7: PART D drill 構造化レンダリング（12 件固定方式 → 可変件数）

### 1-1. 重要な発見と意義 reframe

**事前想定** (BACKLOG §4 や前セッション総括の文言):
「PART D drill は未 slot 化なので集約 slot 化する」

**実際の現状** (Phase 4-7 着手前調査で判明):
**PART D drill は既に Phase 2 以前から 12 件固定 slot 方式で構造化済**。

| 項目 | 結果 |
|---|---|
| PART D 全体の sync 状態 | 8 templates **完全 byte-identical**（hash=`672cca2605`、10,634 bytes / 135 lines） |
| drill-block の slot 化状況 | 既に固定 12 件方式（合計 60 個の `DRILL_NN_*` slot：12 件 × {TAG, QUESTION, CORRECT, EXPLANATION, O_CORRECT, X_CORRECT}） |
| drill_blocks JSON 構造 | 既存 `[{num, tag, question, correct, explanation}, ...]` |
| 全 15 件の drill 件数 | **全件 12 件**（完全均一） |
| render.py 配線 | `build_slot_dict` で `drills_by_num` 経由、12 件分の slot を fill |

→ Phase 4-7 の意義を **「12 件固定方式 → 構造化レンダリング (可変件数) への移行」** に reframe。
Phase 3-3 basis structured rendering と同種のパターン。

### 1-2. 現状の drill-block template 構造（既に slot 化済）

```html
<div class="drill-block">
  <div class="drill-label">
    <span class="drill-num">DRILL&nbsp;01</span>
    <span class="drill-tag">{{DRILL_01_TAG}}</span>
  </div>
  <div class="self-check-quiz" data-arena="1"
       data-correct-value="{{DRILL_01_CORRECT}}"
       data-explanation="{{DRILL_01_EXPLANATION}}">
    <div class="quiz-question">{{DRILL_01_QUESTION}}</div>
    <div class="quiz-buttons">
      <button class="quiz-btn" type="button"
              data-correct="{{DRILL_01_O_CORRECT}}" data-value="○">○</button>
      <button class="quiz-btn" type="button"
              data-correct="{{DRILL_01_X_CORRECT}}" data-value="×">×</button>
    </div>
    <div class="quiz-answer" hidden>
      <span class="quiz-result"></span>{{DRILL_01_EXPLANATION}}
    </div>
  </div>
</div>
```

これが 12 ブロック分（01〜12）、template に固定リテラルで存在。

### 1-3. universal vs per-problem 境界

per-problem 可変なのは **drill_blocks JSON の中身**（tag / question / correct / explanation）のみ。
HTML 構造の外殻、num 表記、`<button>` の○×ラベルは universal。

```
universal (template 固定):
  - <section class="section recall-arena" id="part-d">
  - <nav class="sec-nav"> / <h2 class="section-title">
  - <p class="arena-intro">
  - <div class="arena-counter">
  - <div class="drill-block"> × 12 (HTML 外殻、placeholder 含む)
  - <div class="arena-scorecard">
  - <div class="back-to-top">

per-problem 可変 (JSON drill_blocks 由来):
  - num (例 "01") → drill-num + slot key (例: DRILL_01)
  - tag (記述N / 論点)
  - question (Q. ...)
  - correct (○/×)
  - explanation (詳細解説)
  - O_CORRECT / X_CORRECT は correct から派生
```

固定 12 件・件数可変なし。

---

## §2. 設計（案 A 構造化レンダリング・確定版）

### 2-1. 採択方針

| 項目 | 設計 |
|---|---|
| schema 変更 | **なし**（既存 `drill_blocks` 配列フィールドを流用） |
| JSON 改修 | **なし**（既存 drill_blocks 流用、num 値も JSON 信頼） |
| 新 slot | `{{DRILL_BLOCKS}}` を 8 templates の PART D drill 12 件分の HTML 全体に置換 |
| render.py 改修 | `render_drill_blocks(drills: list)` 関数追加、`{{DRILL_BLOCKS}}` slot 供給配線 |
| **escape 処理** | **旧仕様踏襲（escape なし）** — byte-identical 維持優先、escape は意味変化を伴うため個別対処すべき問題で default にしない（ユーザ方針） |
| **num の扱い** | **JSON num 信頼** — 著者意図の番号付け（欠番・non-sequential）を破壊するリスク回避（ユーザ方針） |
| **旧 `DRILL_NN_*` slot 60 個** | **完全削除** — Phase 4-3/4-5/4-6 と一貫、backward compat 残置は保守性悪化（ユーザ方針） |
| 14 protected への影響 | byte-identical 維持期待（全 15 件 drill 12 件均一、構造化レンダリングが同 HTML を再生） |
| 300 への影響 | 同上 |

### 2-2. render.py 追加内容（概要）

```python
def render_drill_blocks(drills: list[dict] | None) -> str:
    """{{DRILL_BLOCKS}} slot 値を返す（構造化レンダリング）。

    drill 未指定 / 空 → ""（drill section ごと出力されないが、template の
    arena-counter / arena-scorecard / 周辺 HTML は残る。drill 0 件運用なら
    将来別の slot 化を検討）
    list → 各 drill を <div class="drill-block">...</div> に変換、改行で連結

    - escape 処理なし（旧 build_slot_dict 仕様踏襲、byte-identical 維持優先）
    - num は JSON drill["num"] をそのまま使用（"01" 等の 0 埋め文字列を期待）
    - correct ("○"/"×") から O_CORRECT / X_CORRECT ("true"/"false") を派生
    """
    if not drills:
        return ""
    blocks = []
    for d in drills:
        num = str(d.get("num", ""))
        tag = str(d.get("tag", ""))
        question = str(d.get("question", ""))
        correct = str(d.get("correct", ""))
        explanation = str(d.get("explanation", ""))
        o_correct = "true" if correct == "○" else "false"
        x_correct = "true" if correct == "×" else "false"
        blocks.append(
            f'    <div class="drill-block">\n'
            f'      <div class="drill-label">'
            f'<span class="drill-num">DRILL&nbsp;{num}</span>'
            f'<span class="drill-tag">{tag}</span></div>\n'
            f'      <div class="self-check-quiz" data-arena="1" '
            f'data-correct-value="{correct}" '
            f'data-explanation="{explanation}">\n'
            f'        <div class="quiz-question">{question}</div>\n'
            f'        <div class="quiz-buttons">'
            f'<button class="quiz-btn" type="button" '
            f'data-correct="{o_correct}" data-value="○">○</button>'
            f'<button class="quiz-btn" type="button" '
            f'data-correct="{x_correct}" data-value="×">×</button></div>\n'
            f'        <div class="quiz-answer" hidden>'
            f'<span class="quiz-result"></span>{explanation}</div>\n'
            f'      </div>\n'
            f'    </div>'
        )
    return "\n\n".join(blocks)
```

`build_slot_dict()` 改修:
- 旧 60 個の `DRILL_NN_*` slot 供給ループを **完全削除**
- `slots["DRILL_BLOCKS"] = render_drill_blocks(problem.get("drill_blocks", []))` を 1 行追加

### 2-3. upgrade スクリプト方式

8 templates の PART D drill 12 件分の literal HTML（約 96 行 × 8 = 768 行）を `{{DRILL_BLOCKS}}` 1 行に置換。
8 templates すべてに同一 OLD（PART D 全 byte-identical のため）→ 単一 OLD で 8 templates 同パッチ可能（Phase 4-2 footer-spec / Phase 4-5 marker-legend と同形）。

```python
OLD = (
    '    <div class="drill-block">\n'
    # 12 件分の drill block 全部 (約 96 行)
    ...
    '    </div>'  # 最後の drill-block 終了
)
NEW = '{{DRILL_BLOCKS}}'
```

### 2-4. check_template_sync 境界検出

PART D drill は part_c_d sync region 内部（個別 boundary 未定義）。slot 化後 part_c_d は更に collapsed されるが、`part_c_d` 領域の境界 (basis_close+1 〜 footer_open) は不変なので **check_template_sync 改修不要**（Phase 4-5 marker_legend / Phase 4-6 toc のような境界更新は不要）。

ただし `part_c_d` 領域の hash 自体は当然変化する（8 templates 全部同パッチなので 1 hash 維持される）。

### 2-5. byte-identical 維持リスクの精査

#### リスク 1: HTML attribute escape（事前検証必須）

現状 `data-explanation="{{DRILL_NN_EXPLANATION}}"` の slot 値は escape 未処理。explanation
が `<a class="ref-case" href="#x">最決</a>` や `"` を含む場合、属性切れリスク。

**ユーザ方針: 旧仕様踏襲（escape なし）** で byte-identical を確実にする。
ただし **Commit 2 着手前に escape 対象文字 (`<` `>` `&` `"` `'`) が drill 各 field
に含まれていないかを grep 検証**することで、本方針が実質的に安全であることを実証する。

検証手順:
```bash
# 全 15 件の problems/*.json で drill_blocks 内の各文字列 field を抽出し、
# escape 対象文字の出現を確認
python -c "
import json, os, glob, re
for f in sorted(glob.glob('problems/*.json')):
    name = os.path.basename(f)
    if name.startswith('_'): continue
    d = json.load(open(f, encoding='utf-8'))
    for i, dr in enumerate(d.get('drill_blocks', [])):
        for key in ('tag', 'question', 'correct', 'explanation'):
            v = dr.get(key, '')
            for ch in ('<', '>', '&', '\"', \"'\"):
                if ch in v:
                    print(f'{name} drill[{i}].{key}: contains {ch!r}')
"
```

検証結果に応じて:
- escape 対象文字 0 件 → 旧仕様踏襲で byte-identical 確実、Commit 2 を予定通り実施
- escape 対象文字あり → 該当箇所の影響を個別評価、必要なら設計再考（STOP for review）

#### リスク 2: drill_blocks num の 0 埋め

JSON 著者が `"num": "1"` (no zero-pad) や `"num": 1` (int) で書くと、現状 `build_slot_dict` の
`drills_by_num` は `n.isdigit()` で文字列のみ受理し、0 埋めしないキーは matching 失敗 →
silent fail で全 slot 空文字。

ユーザ方針「JSON num 信頼」: render_drill_blocks では `str(d.get("num", ""))` をそのまま
出力する。問題著者が "01" "02" を期待値として書く現運用に依存。15 件すべて検証で確認済。

### 2-6. 検証戦略

- Commit 2 着手前に **escape 検証 grep** を実施、結果を STOP for review で報告
- Commit 2 (render 改修) 後、template 未変更のため CP gate 不変（slot 未使用、{{DRILL_BLOCKS}} 注入なし）
  - ただし 60 個の旧 DRILL_NN_* slot を削除するため、template に残る `{{DRILL_NN_*}}` が
    **未置換 slot として render() で RuntimeError** を起こす ← この副作用に注意
  - 対策: Commit 2 と Commit 3 は **同時実施が安全**（render 改修と template 改修の中間状態で
    壊れる）。**ただし review 慎重重視のため commit 分割は維持**、Commit 2 と 3 の間で
    render を実行しないことで mitigation
- Commit 3 (template + apply) 後、全 15 件再 render → 14 protected + 300 すべて byte-identical
  維持を確認

### 2-7. 着手注意事項

⚠ **Commit 2 と Commit 3 の中間状態は render 不可**: render.py から旧 DRILL_NN_* 供給を
削除し、template にまだ {{DRILL_NN_*}} が残っている状態で render() を呼ぶと未置換 slot
RuntimeError。Commit 2 完了後 review → 即 Commit 3 着手の流れで中間状態を最小化。

---

## §3. 3 commit 実装計画

各 commit 後 STOP for review。各 commit で CP gate + check_template_sync + validate-tx（全 15 件）を実行。

| # | commit subject | 影響範囲 | CP gate | sync | validate-tx |
|---|---|---|---|---|---|
| 1 | `docs: BACKLOG.md §0 Phase 4-6 完了追記 + §1 Phase 4-7 drill_blocks 構造化レンダリング スコープ` | docs only | PASS=14 / DIFF=1 維持 | ✅ | 全 15 件 ERROR 0 / WARNING 0 維持 |
| **(中間検証)** | **escape 対象文字の grep 検証** (本 BACKLOG §2-5 手順) | 検証のみ、コミットなし | — | — | 検証結果を STOP for review |
| 2 | `feat(phase4-7 render): render_drill_blocks() + DRILL_BLOCKS slot 供給配線 + 旧 DRILL_NN_* slot 60 個廃止` | scripts/render.py +約 100 行 / -約 30 行 (build_slot_dict 内 drill loop) | **再 render 不可** (template に旧 slot 残存) | ✅ | (検証不能、Commit 3 と組合せ確認) |
| 3 | `feat(phase4-7 templates): 8 templates の PART D drill 12 件を {{DRILL_BLOCKS}} に置換 + apply` | upgrade script + 8 templates 各 -約 96 行 + outputs (全 15 件 byte-identical 期待) | PASS=14 / DIFF=1 維持 | ✅ | 全 15 件 ERROR 0 / WARNING 0 維持 |

### 各 commit 後の検証コマンド

```bash
python scripts/_cp_gate_check.py
python scripts/check_template_sync.py
for f in 刑TX/刑TX300 刑TX/刑TX303 刑TX/刑TX304 刑TX/刑TX305 \
         刑TX/刑TX326 刑TX/刑TX327 刑TX/刑TX328 刑TX/刑TX329 刑TX/刑TX330 \
         憲TX/憲TX001 民TX/民TX001 商TX/商TX001 \
         民訴TX/民訴TX001 刑訴TX/刑訴TX001 行政TX/行政TX001; do
  python scripts/validate-tx.py "outputs/tx/$f.html"
done
```

### Phase 4-7 完了条件

- 全 15 件 `validate-tx.py` で ERROR 0 / WARNING 0 を**維持**
- CP gate PASS=14 / DIFF=1（300 のみ DIFF、Phase 4-6 完了状態と同じ）
- check_template_sync sync-required 7 領域 PASS（part_c_d 領域は新 hash で 8 templates 同期）
- 8 templates の PART D drill 12 件 (約 96 行) が `{{DRILL_BLOCKS}}` 単行に縮減（template
  bytes 削減累計が本セッション最大規模、約 -60 KB / 8 templates）
- 旧 `DRILL_NN_*` slot 60 個 build_slot_dict から削除済

---

## §4. Phase 4-8 以降の候補（参考、未着手）

| 候補 | 領域 | 主要懸念 | 優先度 |
|---|---|---|---|
| **body_pre_toc**（`<div class="doc-header">` 等）| body_pre_toc sync 領域（393 bytes / 11 lines） | 静的、変更頻度低、universal slot 化（Phase 4-5 と同形）| **中（最有力）** |
| PART A 見出しコメント（pre_part_a diff-allowed 8 variants）| pre_part_a | コメント文言の集約、Phase 4-6 TOC と同形（per-instruction-type 派生）| 中 |
| `head` 領域（DOCTYPE 〜 `<style>` 直前）| head sync 領域（867 bytes / 8 lines） | 静的、変更頻度低 | 低 |
| `css` 領域（巨大）| css sync 領域（60,743 bytes / 1,996 lines） | spec の §Annex A canonical CSS と同期、構造化困難 | 低（要設計検討） |
| `js` 領域 | js sync 領域（17,552 bytes / 404 lines） | spec の §Annex C canonical JS と同期、構造化困難 | 低（要設計検討） |
| Phase 5+ JX シリーズ着手 | JX 系（事例式） | spec/jx-v3.2-master.md 由来の構造化 (A〜H 8 サブセクション + 第 3〜5 部)、1 問 1〜2 時間規模 | 別シリーズ・別 Phase（Phase 4 完了後） |

Phase 4-7 完了後、優先度順にスコープ化する。**Phase 4-8 は body_pre_toc が最有力候補**
（規模小・Phase 4-5 marker-legend と同形の universal const パターン応用、最小リスク）。

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
