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

CP gate 正準 baseline: `_phase3_2_pre_patch_baseline.json` (`docs/cp-gate.md` §1)

---

## §1. Phase 4-6: TOC slot 化 (thin schema 派生)

### 1-1. 問題の所在

8 templates の diff-allowed 領域 `toc` ブロック（`<div class="toc-row">...</div>`）は
**6 variants の重複**を抱えている。各 variant は同一 universal 部分（先頭 3 行 + 末尾 5 行）
を持ち、中央の choice anchor 群（3〜5 件）だけが `instruction_type` 別に異なる。
spec の navigation 改訂時に 6 variants を個別修正する手数がかかる。

### 1-2. 6 variants の構造解析

| variant | hash | templates | instruction_type | choice ラベル (件数) |
|---|---|---|---|---|
| 1 | `43f82e4e93` | `fillin` | `fill-in` | A/B/C/D/E (5) |
| 2 | `44ffa583fc` | `KTX_template` + `comb5` | `ox-grid-5` / `combination-5` | ア/イ/ウ/エ/オ (5) |
| 3 | `8c20f24070` | `ox4` | `ox-grid-4` | ア/イ/ウ/エ (4) |
| 4 | `c0c7a95d1e` | `msel5` + `sc5` | `multi-select-5` / `single-choice-5` | 1/2/3/4/5 (5) |
| 5 | `d377f13ad0` | `fillin8` | `fillin8` | 肢1/肢2/肢3/肢4/肢5 (5) |
| 6 | `d44489660e` | `ox3comb8` | `ox-grid-3-combination-8` | ア/イ/ウ (3) |

### 1-3. universal vs per-type 境界

```html
    <div class="toc-row">                       ← universal (TOC_HEAD)
      <a href="#part-a">問題文</a>                ← universal
      <a href="#answer-area">解答</a>             ← universal
[--- 以下 per-type 可変 ---]
      <a href="#choice-1">{LABEL_1}</a>
      ... (instruction_type 別の N choices)
[--- 以下 universal (TOC_TAIL) ---]
      <a href="#basis">共通根拠</a>
      <a href="#c-1">体系</a>
      <a href="#c-7">三層記憶</a>
      <a href="#part-d">⚔ARENA</a>
    </div>
```

可変領域は中央の **choice anchor 群（3〜5 行）のみ**。

---

## §2. 設計（thin schema 派生、Phase 4-3 final_answer パターン踏襲）

### 2-1. 採択方針

| 項目 | 設計 |
|---|---|
| schema 変更 | **なし** |
| JSON 改修 | **なし**（既存 `problem.instruction_type` から派生） |
| 新 slot | `{{TOC_ROW}}` を 8 templates の `<div class="toc-row">...</div>` 全体を置換 |
| render.py 改修 | `TOC_CHOICE_LABELS_BY_TYPE: dict` + `TOC_HEAD` + `TOC_TAIL` + `render_toc(instruction_type)` |
| 未知 instruction_type | `RuntimeError` raise（silent fallback 禁止、安全側設計） |
| diff-allowed 6 variants | slot 化後は 8 templates 全て `{{TOC_ROW}}` 単一行 → diff-allowed 変動なし（領域分類は不変） |
| 14 protected への影響 | byte-identical 維持期待（各問題の instruction_type に対応する variant が render される） |
| 300 への影響 | 同上 |

### 2-2. render.py 追加内容

```python
TOC_CHOICE_LABELS_BY_TYPE: dict[str, list[str]] = {
    "ox-grid-5":               ["ア", "イ", "ウ", "エ", "オ"],
    "ox-grid-4":               ["ア", "イ", "ウ", "エ"],
    "ox-grid-3-combination-8": ["ア", "イ", "ウ"],
    "multi-select-5":          ["1", "2", "3", "4", "5"],
    "single-choice-5":         ["1", "2", "3", "4", "5"],
    "combination-5":           ["ア", "イ", "ウ", "エ", "オ"],
    "fill-in":                 ["A", "B", "C", "D", "E"],
    "fillin8":                 ["肢1", "肢2", "肢3", "肢4", "肢5"],
}

TOC_HEAD: str = (
    '    <div class="toc-row">\n'
    '      <a href="#part-a">問題文</a>\n'
    '      <a href="#answer-area">解答</a>\n'
)
TOC_TAIL: str = (
    '      <a href="#basis">共通根拠</a>\n'
    '      <a href="#c-1">体系</a>\n'
    '      <a href="#c-7">三層記憶</a>\n'
    '      <a href="#part-d">⚔ARENA</a>\n'
    '    </div>'
)


def render_toc(instruction_type: str) -> str:
    """{{TOC_ROW}} slot 値を返す（instruction_type 派生）。未知 type で RuntimeError。"""
    if instruction_type not in TOC_CHOICE_LABELS_BY_TYPE:
        raise RuntimeError(
            f"unknown instruction_type {instruction_type!r} for TOC. "
            f"valid: {sorted(TOC_CHOICE_LABELS_BY_TYPE)}"
        )
    labels = TOC_CHOICE_LABELS_BY_TYPE[instruction_type]
    choice_lines = "".join(
        f'      <a href="#choice-{i}">{lab}</a>\n'
        for i, lab in enumerate(labels, start=1)
    )
    return TOC_HEAD + choice_lines + TOC_TAIL
```

`build_slot_dict()` に slot 供給を追加（`instruction_type` から派生）:
```python
instruction_type = problem.get("instruction_type", "")
slots["TOC_ROW"] = render_toc(instruction_type)
```

### 2-3. upgrade スクリプト方式（β variant 別 OLD dispatch）

8 templates ごとに当該 variant の OLD 文字列を持ち、template → variant 対応表で dispatch:

```python
TEMPLATE_TO_VARIANT: dict[str, str] = {
    "KTX_template.html":          "ox-grid-5",
    "KTX_template_ox4.html":      "ox-grid-4",
    "KTX_template_msel5.html":    "multi-select-5",
    "KTX_template_sc5.html":      "single-choice-5",
    "KTX_template_comb5.html":    "combination-5",
    "KTX_template_fillin.html":   "fill-in",
    "KTX_template_ox3comb8.html": "ox-grid-3-combination-8",
    "KTX_template_fillin8.html":  "fillin8",
}

OLD_BY_TYPE: dict[str, str] = {
    "ox-grid-5": <variant 2 の TOC 全文>,
    "ox-grid-4": <variant 3 の TOC 全文>,
    ...
}
```

各 template の OLD を完全一致で照合 → NEW = `{{TOC_ROW}}` に置換。--dry-run で 8/8 OK を期待。

### 2-4. check_template_sync 境界検出更新

Phase 4-5 marker_legend と同形:

```python
toc_slot_idx = _find_line_idx(lines, r"\{\{TOC_ROW\}\}")
if toc_slot_idx >= 0:
    toc_open = toc_slot_idx
    toc_close = toc_slot_idx
else:
    toc_open = _find_line_idx(lines, r'<div class="toc-row">')
    toc_close = _find_line_idx(lines, r"</div>", toc_open + 1) if toc_open >= 0 else -1
```

slot 化後 `toc` 領域は 8 templates 全て `{{TOC_ROW}}` 単行 → diff-allowed の variant 数は
6 → 1 に集約。sync-required / diff-allowed の領域分類自体は不変（toc は引き続き diff-allowed）。

### 2-5. 検証戦略

slot 値 = `instruction_type` 別の既存 variant 出力 → 全 15 件 byte-identical 維持を期待。
CP gate / check_template_sync / validate-tx すべて Phase 4-5 完了状態を維持。

---

## §3. 3 commit 実装計画

各 commit 後 STOP for review。各 commit で CP gate + check_template_sync + validate-tx（全 15 件）を実行。

| # | commit subject | 影響範囲 | CP gate | sync | validate-tx |
|---|---|---|---|---|---|
| 1 | `docs: BACKLOG.md §0 Phase 4-5 完了追記 + §1 Phase 4-6 TOC スコープ + §6-4 削除` | docs only | PASS=14 / DIFF=1 維持 | ✅ | 全 15 件 ERROR 0 / WARNING 0 維持 |
| 2 | `feat(phase4-6 render): TOC_CHOICE_LABELS_BY_TYPE + TOC_HEAD/TAIL + render_toc() + slot 供給配線` | scripts/render.py | PASS=14 / DIFF=1 維持（template 未変更、slot 未使用） | ✅ | 全 15 件維持 |
| 3 | `feat(phase4-6 templates): 8 templates の toc-row を {{TOC_ROW}} に置換 + check_template_sync 境界更新` | upgrade script + 8 templates + outputs + check_template_sync.py | PASS=14 / DIFF=1 維持 | ✅ | 全 15 件維持 |

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

### Phase 4-6 完了条件

- 全 15 件 `validate-tx.py` で ERROR 0 / WARNING 0 を**維持**
- CP gate PASS=14 / DIFF=1（300 のみ DIFF、Phase 4-5 完了状態と同じ）
- check_template_sync sync-required 7 領域 PASS（領域分類は不変、toc は diff-allowed のまま）
- diff-allowed `toc` の variants 数: 6 → 1 に集約
- 8 templates の `<div class="toc-row">...</div>`（11〜12 行）が `{{TOC_ROW}}` 単行に縮減

---

## §4. Phase 4-7 以降の候補（参考、未着手）

| 候補 | 領域 | 主要懸念 | 優先度 |
|---|---|---|---|
| **PART D drill-block 12 件** (`drill-block` literal) | part_c_d sync 領域内（PART C は Phase 2 で slot 化済、PART D drill が残存） | drill_blocks JSON は既存、template の `<div class="drill-block">` 構造 (各 ~12 行 × 12 件) を slot 化。最大規模・最高複雑度 | **高（Phase 4-7 最有力）** |
| body_pre_toc（`<div class="doc-header">` 等）| body_pre_toc sync 領域（393 bytes / 11 lines） | 静的、変更頻度低 | 低 |
| PART A 見出しコメント（pre_part_a diff-allowed 8 variants）| pre_part_a | コメント文言の集約 | 低 |
| `head` 領域（DOCTYPE 〜 `<style>` 直前）| head sync 領域（867 bytes / 8 lines） | 静的、変更頻度低 | 低 |
| `css` 領域（巨大）| css sync 領域（60,743 bytes / 1,996 lines） | spec の §Annex A canonical CSS と同期、構造化困難 | 低（要設計検討） |
| `js` 領域 | js sync 領域（17,552 bytes / 404 lines） | spec の §Annex C canonical JS と同期、構造化困難 | 低（要設計検討） |
| Phase 5+ JX シリーズ着手 | JX 系（事例式） | spec/jx-v3.2-master.md 由来の構造化 (A〜H 8 サブセクション + 第 3〜5 部)、1 問 1〜2 時間規模 | 別シリーズ・別 Phase（Phase 4 完了後） |

Phase 4-6 完了後、優先度順にスコープ化する。**Phase 4-7 は PART D drill が最有力**（drill_blocks JSON が既存・最大規模・slot 化の挑戦的対象）。

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

### 6-4. ~~marker-legend の per-problem 拡張 hook (extra_legend_items)~~（削除）

Phase 4-5 完了時の `--dry-run 8/8 OK` で 8 templates 完全同期が実証され、universality が
確定したため、本項は **不要として削除**（2026-05-19 Phase 4-6 commit 1）。

### 6-5. TOC choice ラベル series の拡張余地

Phase 4-6 で採用した `TOC_CHOICE_LABELS_BY_TYPE` は現状 4 series × 最大 3 N 値 = 6 cells 占用。
24 cells のうち 18 cells が拡張余地（例: ロ〜ホ系 / 漢数字 / N=6+ 等）。現状仕様外、設計に含めず
（YAGNI 重視）。新 instruction_type 追加時は辞書 1 行追加で対応可能。
