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

CP gate 正準 baseline: `_phase3_2_pre_patch_baseline.json` (`docs/cp-gate.md` §1)

---

## §1. Phase 4-5: marker-legend slot 化

### 1-1. 問題の所在

8 templates の `marker-legend` block（sync-required 領域、SHA256 全 8 一致）は現状リテラル
HTML として埋め込まれており、spec 改訂で凡例文言が変わるたびに 8 templates 同期修正が必要。
Phase 4-2 footer-spec と同型の「sync-required 領域に集約 slot を 1 つ置き render.py で供給」
パターンを適用し、template 8 本の重複を排除する。

### 1-2. 現状

`marker-legend` 領域（709 bytes / 10 lines、8 templates 完全同期、hash=`db531d3cae`）:

```html
  <div class="marker-legend" aria-label="マーカー凡例">
    <span class="lg-title">凡例</span>
    <span class="lg-item"><span class="lg-sample lg-ron">論</span>論文関連</span>
    <span class="lg-divider">|</span>
    <span class="lg-item"><span class="exam-mark freq-high">高</span>短答頻出</span>
    <span class="lg-item"><span class="exam-mark freq-mid">中</span>標準</span>
    <span class="lg-item"><span class="exam-mark freq-low">低</span>関連</span>
    <span class="lg-divider">|</span>
    <span class="lg-item"><span class="statute-emphasis freq-high">条</span>条文</span>
    <span class="lg-item"><span class="case-emphasis freq-high">判</span>判例</span>
  </div>
```

universal content（subject / instruction_type 無関係）。`problem.json` に対応フィールドなし。

### 1-3. Phase 4-2 footer-spec パターンとの一致点

| 項目 | footer-spec (Phase 4-2) | marker-legend (Phase 4-5) |
|---|---|---|
| 領域種別 | sync-required (1 hash) | sync-required (1 hash) |
| 規模 | 326 bytes / 10 lines | 709 bytes / 10 lines |
| 対象 templates | 8 同期 | 8 同期 |
| 既存 schema 変更 | なし | なし |
| JSON フィールド | なし (universal) | なし (universal) |
| render.py 構造 | constant + 関数 | constant + 関数 |

Phase 4-2 が「v8.11.x の feature-tag 追加・version bump で 8 templates 手修正不要」の利点を
得たのと同様、Phase 4-5 では「marker 体系（論／高中低／条／判）の spec 変更を render.py 1 箇所で
追従可能」となる。

---

## §2. 設計（schema 変更なし・thin slot）

### 2-1. 採択方針

| 項目 | 設計 |
|---|---|
| schema 変更 | **なし**（universal content、JSON フィールド不要） |
| 新 slot | `{{MARKER_LEGEND}}` を 8 templates に追加（既存 marker-legend `<div>` 全体を置換） |
| render.py 改修 | `MARKER_LEGEND_DEFAULT: str` 定数 + `render_marker_legend() -> str` 関数（引数なし固定、将来 hook の必要性は Phase 4-5 完了後に判断） |
| JSON 改修 | **なし** |
| 14 protected への影響 | byte-identical 維持（slot 値 = 既存リテラル文字列） |
| 300 への影響 | byte-identical 維持（300 にも同じ marker-legend が描画される） |
| CP gate 期待 | PASS=14 / DIFF=1（変化なし） |

### 2-2. render.py 追加内容

```python
# Phase 4-5 marker-legend slot 化
MARKER_LEGEND_DEFAULT: str = (
    '  <div class="marker-legend" aria-label="マーカー凡例">\n'
    '    <span class="lg-title">凡例</span>\n'
    '    <span class="lg-item"><span class="lg-sample lg-ron">論</span>論文関連</span>\n'
    '    <span class="lg-divider">|</span>\n'
    '    <span class="lg-item"><span class="exam-mark freq-high">高</span>短答頻出</span>\n'
    '    <span class="lg-item"><span class="exam-mark freq-mid">中</span>標準</span>\n'
    '    <span class="lg-item"><span class="exam-mark freq-low">低</span>関連</span>\n'
    '    <span class="lg-divider">|</span>\n'
    '    <span class="lg-item"><span class="statute-emphasis freq-high">条</span>条文</span>\n'
    '    <span class="lg-item"><span class="case-emphasis freq-high">判</span>判例</span>\n'
    '  </div>'
)


def render_marker_legend() -> str:
    """{{MARKER_LEGEND}} slot 値を返す。

    引数なし固定。spec bump で legend 内容が変わる際は MARKER_LEGEND_DEFAULT のみ
    修正することで 8 templates を一括追従可能。per-problem 拡張 hook
    (extra_legend_items 等) は Phase 4-5 完了後に必要性を判断（現状 universal で十分）。
    """
    return MARKER_LEGEND_DEFAULT
```

`build_slot_dict()` に 1 行追加:
```python
slots["MARKER_LEGEND"] = render_marker_legend()
```

### 2-3. upgrade スクリプト仕様

`scripts/upgrade_templates_marker_legend_slot.py`（Phase 4-2 footer-spec パッチを踏襲）:

```python
OLD = (
    '  <div class="marker-legend" aria-label="マーカー凡例">\n'
    # ... 全 11 行
    '  </div>'
)
NEW = '{{MARKER_LEGEND}}'
```

8 templates 同パッチ、各 `(709 - 22) = 687` bytes（NEW = `{{MARKER_LEGEND}}` 16 chars 相当の
UTF-8 + Japanese multibyte 分の差）の削減。

### 2-4. 検証戦略

slot 値 = 既存リテラルなので **template patch 適用 → 再 render → 14 protected + 300 ともに
完全 byte-identical**。CP gate / check_template_sync / validate-tx すべて Phase 4-4 完了時点の
状態を維持。

---

## §3. 3 commit 実装計画

各 commit 後 STOP for review。各 commit で CP gate + check_template_sync + validate-tx（全 15 件）を実行。

| # | commit subject | 影響範囲 | CP gate | sync | validate-tx |
|---|---|---|---|---|---|
| 1 | `docs: BACKLOG.md §0 Phase 4-4 完了追記 + §1 Phase 4-5 marker-legend スコープ` | docs only | PASS=14 / DIFF=1 維持 | ✅ | 全 15 件 ERROR 0 / WARNING 0 維持 |
| 2 | `feat(phase4-5 render): MARKER_LEGEND_DEFAULT + render_marker_legend() + slot 供給配線` | scripts/render.py | PASS=14 / DIFF=1 維持（template 未変更、slot 未使用なので state 不変） | ✅ | 全 15 件 ERROR 0 / WARNING 0 維持 |
| 3 | `feat(phase4-5 templates): 8 templates の marker-legend を {{MARKER_LEGEND}} に置換` | scripts/upgrade_templates_marker_legend_slot.py + 8 templates + outputs (全 15 件 byte-identical) | PASS=14 / DIFF=1 維持 | ✅ | 全 15 件 ERROR 0 / WARNING 0 維持 |

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

### Phase 4-5 完了条件

- 全 15 件 `validate-tx.py` で ERROR 0 / WARNING 0 を**維持**
- CP gate PASS=14 / DIFF=1（300 のみ DIFF、Phase 4-4 完了状態と同じ）
- check_template_sync sync-required 7 領域 PASS
- 8 templates の marker-legend 領域が `{{MARKER_LEGEND}}\n` 1 行に縮減（hash は新領域 hash で同期維持）

---

## §4. Phase 4-6 以降の候補（参考、未着手）

| 候補 | 領域 | 主要懸念 | 優先度 |
|---|---|---|---|
| **TOC 行**（`<div class="toc-row">`）| toc diff-allowed 領域 (6 variants) | instruction_type 別の TOC ラベル差（ア〜オ／1〜5／A〜E 等）を render.py 側で生成。Phase 4-5 完了後の **次 Phase 候補 (Phase 4-6) として最有力** | **高（Phase 4-6 最有力）** |
| PART D drill-block 12 件 (`drill-block` literal) | part_c_d sync 領域内（PART C は Phase 2 で slot 化済、PART D drill が残存） | drill_blocks JSON は既存、template の `<div class="drill-block">` 構造 (各 ~12 行 × 12 件) を slot 化。最大規模・最高複雑度 | 中 |
| body_pre_toc（`<div class="doc-header">` 等）| body_pre_toc sync 領域（393 bytes / 11 lines） | 静的、変更頻度低 | 低 |
| PART A 見出しコメント（pre_part_a diff-allowed 8 variants）| pre_part_a | コメント文言の集約 | 低 |
| `head` 領域（DOCTYPE 〜 `<style>` 直前）| head sync 領域（867 bytes / 8 lines） | 静的、変更頻度低 | 低 |
| `css` 領域（巨大）| css sync 領域（60,743 bytes / 1,996 lines） | spec の §Annex A canonical CSS と同期、構造化困難 | 低（要設計検討）|
| `js` 領域 | js sync 領域（17,552 bytes / 404 lines） | spec の §Annex C canonical JS と同期、構造化困難 | 低（要設計検討）|

Phase 4-5 完了後、優先度順にスコープ化する。**Phase 4-6 は TOC が最有力候補**（規模小・variant 処理が
slot 化技術の応用練習として有意義）。

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

### 6-4. marker-legend の per-problem 拡張 hook (extra_legend_items)

Phase 4-5 では `render_marker_legend()` を引数なし固定で開始する（universal content の想定）。
ただし、特殊な記号系 (e.g., 「論」マーカーが特定論点でのみ意味を持つ場合) の問題別 legend
拡張が将来要求される可能性がある。Phase 4-2 footer-spec の `extra_tags` と同形の hook を
追加する案。

**着手判断条件**: Phase 4-5 完了後、universality 仮定が外れる問題が登場したとき。それまでは
不要。
