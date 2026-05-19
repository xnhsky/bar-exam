# Session 2026-05-19 — Phase 4-3 / 4-4 / 4-5 / 4-6 / 4-7 完走 + 4 パターン体系完成

> 本セッションで bar-exam TX 系 slot 化整備が Phase 4-2 完了状態から Phase 4-7 完了
> 状態まで前進した。Phase 4-3〜4-5 で 3 つの設計パターン (A/B/C) を確立、Phase 4-6 で
> その「3 パターン再利用」を実証、Phase 4-7 で **4 つ目のパターン D (構造化レンダリング)
> の再利用** を実証することで **4 パターン体系 (A/B/C/D) が完成**した。本セッションの
> 最大戦果。最終検証状態・次セッション着手候補・保留事項を一元記録する。

---

## §1. 本セッション完了 Phase と commit 履歴

### Phase 4-3: C-7 末尾 final-answer DOM block インテグレーション

`spec/tx-v8.11.7-core.md §22-bis / §22-ter` 規定の `<div class="final-answer" hidden>`
DOM block を、現状 14 outputs で **DOM 完全不在**（CSS と JS のみ）の状態から、
canonical KTX301.html 由来の構造で `render_c7_memory()` 内嵌型 (β 配置) として実装。

設計判断:
- **thin schema**（案 A）: `final_answer.summary_html` + 任意 `extra_html` のみ JSON 新規。
  `mode` (single/multi)・`answer_value`・`cells` は `instruction_type` + `answer` から render.py で派生
- **β 配置**: template 不変、`render_c7_memory()` 第 2 引数で final-answer HTML を受け取り
  memory-list 終了と back-to-top の間に inject
- **`hidden` 属性必須**を render.py 側で強制（§22-quater-1 / AP-30 / S68）
- **`extra_html` は独立 optional フィールド**（`summary_html` と分離、§22-bis 4 行目専用）
- 300.json に 1st demo（詐欺罪・single-choice-5・answer=5）

| commit | 内容 |
|---|---|
| `0f7e673` | docs: Phase 3/4+ slot 化 BACKLOG を追加 |
| `abd2a28` | feat(phase4-3 schema): final_answer + extra_html optional property を追加 |
| `f327664` | feat(phase4-3 data): 300.json に final_answer demo を追記 |
| `dee2bc0` | feat(phase4-3 render): render_c7_memory() に final-answer 埋込 |

### Phase 4-4: basis card rb-chip back-link 解決（S8 WARNING 撤去）

Phase 3-3 で導入された basis card `back_links[{href, label}]` 配列の rb-chip back-link
チップが、対応する `id="ref-X-NNN"` target を持たず 300 で S8 WARNING を発生させていた
（18 個の unresolved anchor）。

設計判断:
- **schema 変更なし**（既存 `basis.cards.back_links` を流用）
- `inject_ref_ids(html)` **後処理を `main()` 内に chain**: `rendered = render(...); rendered = inject_ref_ids(rendered)`
- **canonical KTX301 規約 `ref-{target}-{NNN}`** を採用（項 qualifier なし）。複数項参照
  対応の `ref-law-X-Y-NNN` 規約は将来課題 (BACKLOG §6-1)
- 14 protected ファイルは inline ref-X anchor **0 件** → 注入対象なしで byte-identical 自動維持
- 300.json basis 規約整理（`-1-` qualifier 削除、5 chips）+ 記述4 prof-note の「(最判平8.4.26)」
  anchor 化 + **scope 拡張で 8th basis card (case-saiko-h8-4-26) を追加**することで href
  target を完結
- **全 15 件 ERROR 0 / WARNING 0 達成**

判例関連性: 最判平8.4.26 は誤振込でも預金契約が有効に成立し受取人に形式的払戻請求権が
発生することを示した **民事先例**であり、記述4（誤振込払戻詐欺・最決平15.3.12）の民事的
背景を確定する。両判例の対比により **民事的有効性と刑事可罰性の独立判断** という核心法理
が際立つ重要対。

| commit | 内容 |
|---|---|
| `41f0edf` | docs: BACKLOG.md §0 Phase 4-3 完了追記 + §1 Phase 4-4 スコープ展開 |
| `b2bb088` | feat(phase4-4 render): inject_ref_ids() 後処理を main() に配線 |
| `49dea8d` | feat(phase4-4 data): 300.json basis 規約整理 + 最判平8.4.26 完全 anchor 化 |

### Phase 4-5: marker-legend slot 化

8 templates の sync-required 領域 marker-legend block（11 行・709 bytes・hash 全 8 同期）を
集約 slot 化。Phase 4-2 footer-spec パターンの最純粋形。

設計判断:
- **schema 変更なし・JSON 改修なし**（universal content）
- render.py に `MARKER_LEGEND_DEFAULT` 定数 + `render_marker_legend()` 関数（**引数なし固定**）
- `extra_legend_items` hook は **Phase 4-5 完了後に必要性判断**として §6-4 保留 → `--dry-run` で
  8/8 OK 確認により **universality 実証、hook 不要が確定**
- `check_template_sync.py` の境界検出を `{{MARKER_LEGEND}}` 単一行に対応（pre-slot
  `<div class="marker-legend">` へのレガシーフォールバックも温存）
- 8 templates 各 -692 bytes 削減（累計 5,536 bytes 削減）

| commit | 内容 |
|---|---|
| `6b64e17` | docs: BACKLOG.md §0 Phase 4-4 完了追記 + §1 Phase 4-5 marker-legend スコープ |
| `9caa756` | feat(phase4-5 render): MARKER_LEGEND_DEFAULT + render_marker_legend() + slot 供給配線 |
| `3cc412c` | feat(phase4-5 templates): 8 templates の marker-legend を {{MARKER_LEGEND}} に置換 |

### Phase 4-6: TOC slot 化（thin schema 派生による diff-allowed 領域の集約）

8 templates の diff-allowed `toc` 領域（6 variants / 363-436 bytes / 10-12 lines）を
**instruction_type 派生** で集約 slot 化。Phase 4-3 final_answer の thin schema 派生
パターンを diff-allowed 領域に適用した初例。

設計判断:
- **schema 変更なし・JSON 改修なし**（既存 `problem.instruction_type` から派生）
- render.py に `TOC_CHOICE_LABELS_BY_TYPE` 辞書（8 keys → labels list）+ `TOC_HEAD`/`TOC_TAIL`
  const + `render_toc(instruction_type)` 関数
- **未対応 instruction_type は `RuntimeError`** raise（silent fallback 不採用、新 type
  追加時の失敗を早期検出。`valid: [...]` を error message に含めヒント機能あり）
- upgrade スクリプト方式: **β variant 別 OLD dispatch**（`TEMPLATE_TO_TYPE` 表 +
  `LABELS_BY_TYPE` 表で各 template 用の OLD を構築）
- `check_template_sync.py` の境界検出を `{{TOC_ROW}}` 単一行に対応（Phase 4-5
  marker_legend と同形のフォールバック温存）
- 8 templates 各 -352〜-425 bytes 削減（variant 別、件数 3/4/5 × series 違い）

成果:
- **diff-allowed `toc` の variants 数: 6 → 1 に集約**（8 templates 全て `{{TOC_ROW}}` 単行）
- spec の navigation 改訂時、`TOC_CHOICE_LABELS_BY_TYPE` 辞書 1 箇所修正で 8 templates
  一括追従可能（手数 6→1）

| commit | 内容 |
|---|---|
| `7555a40` | docs: BACKLOG.md §0 Phase 4-5 完了追記 + §1 Phase 4-6 TOC スコープ + §6-4 削除 |
| `1afefca` | feat(phase4-6 render): TOC_CHOICE_LABELS_BY_TYPE + TOC_HEAD/TAIL + render_toc() + slot 供給配線 |
| `e93c3cb` | feat(phase4-6 templates): 8 templates の toc-row を {{TOC_ROW}} に置換 |

### Phase 4-7: PART D drill 構造化レンダリング（12 件固定方式 → 可変件数）

**重要 reframe**: 事前想定「PART D drill は未 slot 化」と異なり、着手前調査で「既に
Phase 2 以前から 12 件固定 slot 方式 (60 個の DRILL_NN_* slot) で構造化済」が判明。
Phase 4-7 の意義を **「12 件固定方式 → 構造化レンダリング (可変件数) への移行」** に
reframe。Phase 3-3 basis structured rendering と同種パターン (パターン D の再演)。

設計判断:
- **schema 変更なし**（既存 `drill_blocks` 配列フィールド流用）
- **escape 旧仕様踏襲**（escape なし）— byte-identical 優先、Commit 2 着手前 grep 検証で
  全 720 field-values (15 problems × 12 drills × 4 fields) で escape 対象文字 0 件確認済
- **num は JSON drill["num"] そのまま使用**（著者意図の番号付け尊重）
- **旧 60 個の `DRILL_NN_*` slot 完全削除**（backward compat 残置せず、Phase 4-3/4-5/4-6 と一貫）
- **broken intermediate state**: Commit 2 (render 改修) 完了直後は template に旧
  `{{DRILL_NN_*}}` 60 個残存で render 不可。Commit 2/3 連続実行で mitigation
- **代替検証手法**: Commit 2 着手中に `render_drill_blocks()` 出力 == 現 outputs の drill
  section を全 15 件で byte-identical 比較（render() 経由不要の関数単体検証）

成果:
- 8 templates × 約 96 行 drill literal を `{{DRILL_BLOCKS}}` 単行に集約（**本セッション
  最大規模、累計 -70,800 bytes ≒ -70 KB**）
- 旧 60 slot 固定方式 → 1 slot 構造化レンダリング
- drill 件数の可変化（現在 12 件均一、将来 6/8/15/20 等可能）
- パターン D（構造化レンダリング）が **Phase 3-3 basis から再利用された 2 例目**となり、
  パターン体系の完成度が向上

| commit | 内容 |
|---|---|
| `5f4856a` | docs: BACKLOG.md §0 Phase 4-6 完了追記 + §1 Phase 4-7 drill_blocks 構造化レンダリング スコープ |
| `39cf18b` | feat(phase4-7 render): render_drill_blocks() 構造化レンダリング + DRILL_BLOCKS slot 配線 + 旧 DRILL_NN_* slot 60 個廃止 |
| `28e6e28` | feat(phase4-7 templates): 8 templates の PART D drill 12 件を {{DRILL_BLOCKS}} に置換 |

### 本セッション通算 commit カウント

| 区分 | commits |
|---|---|
| CP gate infrastructure | `47cf0d0` |
| Phase 4-1 + 4-2 統合 | `88b0486` |
| Phase 4-3 (4 commits) | `0f7e673` / `abd2a28` / `f327664` / `dee2bc0` |
| Phase 4-4 (3 commits) | `41f0edf` / `b2bb088` / `49dea8d` |
| Phase 4-5 (3 commits) | `6b64e17` / `9caa756` / `3cc412c` |
| 中間サマリ（Phase 4-3〜4-5 完走時点）| `fc74f3e` |
| Phase 4-6 (3 commits) | `7555a40` / `1afefca` / `e93c3cb` |
| 中間サマリ最終版（Phase 4-3〜4-6 + push 持ち越し） | `8d669b4` |
| Phase 4-7 (3 commits) | `5f4856a` / `39cf18b` / `28e6e28` |
| **本セッション最終サマリ commit**（本ファイル更新 + BACKLOG §0 P4-7 追記）| （今回追加、20 commit 目で session 締め） |

累積 commits（Phase 4-3〜4-7 + 中間/最終サマリ 2 件）= **17**、本サマリ更新込みで **18**。
本セッション通算 = **21**（CP infra + Phase 4-1+4-2 + Phase 4-3〜4-7 + 中間サマリ 2 件）、
本サマリ更新込みで **22**。

remote `xnhsky/bar-exam` master への push 状況: 16 commits → 19 commits (Phase 4-7 完了
時点で push 済)、本サマリ commit で 20 commits 到達後さらに push 予定。

> 補足: Phase 2 PART C (`47c1f1d`) と Phase 3 basis (`1f54a17`) もこのセッション中に
> commit したが、内容自体は事前にローカル作業済の slot 化機能を 4-commit 構造で
> 整理整頓したもの。新規設計判断を含むのは Phase 4-3 以降のため、上記カウントから除外。

---

## §2. 本セッションで完成した 4 パターン体系（A/B/C/D）+ 再利用の実証

### パターン A: Thin schema + render 派生（Phase 4-3 final_answer、Phase 4-6 TOC で再利用）

**定義**: JSON 新規フィールドを最小化し、既存フィールドから render.py 内で派生計算する slot 化アプローチ。

**実装例**（Phase 4-3 final_answer）:
```python
def render_final_answer(problem: dict) -> str:
    fa = problem.get("final_answer")
    if not fa:
        return ""  # 未指定 → block ごと不出力 (byte-identical 維持)

    instr_type = problem.get("instruction_type", "")  # 既存
    answer_raw = problem.get("answer", "")             # 既存

    if instr_type == "multi-select-5" and isinstance(answer_raw, list):
        # §22-ter 派生
        ...
    else:
        # §22-bis 派生（answer_value = _format_answer(answer_raw)）
        ...
```

**Phase 4-6 での再利用**: TOC で `instruction_type` から `TOC_CHOICE_LABELS_BY_TYPE` 辞書を
参照し choice ラベルを派生（純粋形、JSON 介在なし、`final_answer` field すら不要）。

**適用条件**:
- 表示形式が既存フィールドから一意に導出可能（mode 自動判定、ラベル系列選択など）
- JSON 著作負担を minimum に保ちたい
- データの二重管理リスクを避けたい

**利点**:
- 既存 JSON の保守負担増加なし
- 派生ロジックが render.py 1 箇所に集約 → 仕様変更時の追従が容易
- thin schema により JSON validator のチェック範囲が明確

**トレードオフ**: 派生ルールが render.py に隠れるため、JSON だけ見ても最終 HTML が予測しづらい。
→ BACKLOG §2 で派生ルールを明示することで軽減。

### パターン B: Post-processing 注入（Phase 4-4 inject_ref_ids、本セッションでは Phase 4-6 で不使用）

**定義**: `render()` 出力済 HTML に対する後処理として、attribute / id を programmatic に注入。

**実装例**:
```python
REF_ANCHOR_PATTERN = re.compile(r'<a class="(ref-case|ref-stat)" href="#([^"]+)">')

def inject_ref_ids(html: str) -> str:
    counters: dict[str, int] = {}
    def repl(m):
        cls, target = m.group(1), m.group(2)
        counters[target] = counters.get(target, 0) + 1
        n = counters[target]
        return f'<a class="{cls}" id="ref-{target}-{n:03d}" href="#{target}">'
    return REF_ANCHOR_PATTERN.sub(repl, html)

# main() で chain:
rendered = render(template, slots)
rendered = inject_ref_ids(rendered)
```

**適用条件**:
- 構造化レンダリングでは表現しづらい横断的 attribute 注入（document order に依存）
- 既存 id 付き要素はマッチ回避で idempotent 維持可能
- 14 protected ファイルが当該 pattern を持たないこと確認済 → byte-identical 維持

**利点**:
- JSON / template に冗長な id 記述不要
- render.py の責務分離（構造化 → 後処理 → I/O）
- regex 単純で副作用追跡が容易

**トレードオフ**: `render.py` の `render()` が main() からのみ呼ばれる前提（テスト経路で
直接呼ぶ際は明示的に inject_ref_ids() を chain する必要）→ BACKLOG §2 「呼出経路前提」で
明文化。

### パターン C: Universal content の minimal slot 化（Phase 4-5 marker-legend、Phase 4-6 で部分採用）

**定義**: subject / instruction_type 無関係の固定 HTML を集約 slot 化、render.py constant
+ 引数なし関数のみで完結。

**実装例**:
```python
MARKER_LEGEND_DEFAULT: str = (
    '  <div class="marker-legend" aria-label="マーカー凡例">\n'
    ...
    '  </div>'
)

def render_marker_legend() -> str:
    return MARKER_LEGEND_DEFAULT
```

**Phase 4-6 での部分採用**: TOC の `TOC_HEAD` / `TOC_TAIL` 部分（先頭 3 行 + 末尾 5 行の
universal 部分）に const パターンを適用。choice 部分のみパターン A で派生。

**適用条件**:
- 8 templates 完全同期（hash 1 種）
- problem に依存しない固定値
- `--dry-run` で 8/8 OK 確認により universality 実証可能

**利点**:
- 設計 surface 最小、レビュー負担最小
- schema/JSON 改修ゼロ
- byte-identical 維持自明（slot 値 = 既存リテラル）
- spec 改訂時の追従が 1 箇所修正で完了（8 templates 手数 → 1）

**トレードオフ**: 将来 per-problem 拡張が必要になった場合、関数シグネチャ拡張が必要
（hook 残置 vs 必要時拡張、後者を採用し YAGNI 重視）。Phase 4-2 footer-spec の
`extra_tags` hook と対比可能。

### パターン D: 構造化レンダリング（固定 N slot → 配列駆動）（Phase 3-3 basis で前段確立、Phase 4-7 drill_blocks で再利用・体系化）

**定義**: 固定 N 件の slot 方式 (`{{X_01_TAG}}` 〜 `{{X_NN_TAG}}` 等の連番 slot) を、
**配列駆動の集約 slot** (`{{X_BLOCKS}}` 1 つ) + render.py 側 ループによる構造化レンダリング
に置換するパターン。件数の可変化、template 重複削減、render.py への一元化を同時に達成。

**実装例**（Phase 4-7 render_drill_blocks）:
```python
def render_drill_blocks(drills: list | None) -> str:
    if not drills:
        return ""  # 未指定 → drill section ごと不出力
    blocks = []
    for d in drills:
        num = str(d.get("num", ""))
        tag = str(d.get("tag", ""))
        # ... 各 field を取得
        block = (
            '    <div class="drill-block">\n'
            '      <div class="drill-label">'
            '<span class="drill-num">DRILL&nbsp;' + num + '</span>'
            '<span class="drill-tag">' + tag + '</span></div>\n'
            # ...8 行構造を構築
            '    </div>'
        )
        blocks.append(block)
    return "\n\n".join(blocks)
```

**Phase 3-3 での前段確立**: `render_basis(data)` が `basis.cards[]` 配列から basis-card HTML を
構造化生成（statute / case 分岐含む）。当時はパターンとして明示的にコード化されていなかったが、
Phase 4-7 でその構造を **再利用** することでパターンとして確立。

**適用条件**:
- 旧 template が固定 N 件の連番 slot (例: `{{X_01}}` ... `{{X_12}}`) を持つ
- 件数の可変化が将来的に有意義（または現状で件数の柔軟性が欲しい）
- JSON 側に既に配列フィールドが存在する（reuse 容易）
- escape 方針が確定している（旧仕様踏襲 / 新規 escape 適用 のいずれか）

**利点**:
- template の HTML 重複を最大限削減（Phase 4-7 では **-70 KB** / 8 templates）
- 件数の可変化（将来拡張）
- 旧 N 件 × M field = N×M 個の slot 供給ロジックが 1 関数に集約

**トレードオフ**:
- byte-identical 維持のため render 出力が旧 slot 方式と完全一致する必要 → **事前検証必須**
  （Phase 4-7 では Commit 2 着手中に全 15 件 byte-identical 検証を実施）
- broken intermediate state: 旧 slot 供給削除と template 更新の中間で render() が失敗 →
  **連続 commit / 即座の Commit 3 着手で mitigation**
- escape 設計の決定が新規論点になりうる → BACKLOG §6-N に将来課題として残置

### Phase 4-6 で確立した 4 つ目のメタ認知: **パターン再利用 + 境界更新の定型化**

Phase 4-6 は **新規パターンを導入せず**、Phase 4-3 (A) と Phase 4-5 (C) の組合せ + Phase 4-5
で確立した `check_template_sync` 境界更新を機械的に適用した。これにより以下が実証された:

#### 再利用例

| 設計要素 | 借用元 | 適用 |
|---|---|---|
| `TOC_CHOICE_LABELS_BY_TYPE` (instruction_type → labels) | Phase 4-3 final_answer の `multi-select-5` 派生分岐 | 8 type × labels[] の辞書化に拡張 |
| `TOC_HEAD` / `TOC_TAIL` const | Phase 4-5 `MARKER_LEGEND_DEFAULT` | universal 部分の固定 string 化 |
| `RuntimeError` on unknown type | Phase 4-2 footer-spec の `SUBJECT_TO_JP` 不一致 | silent fallback 不採用方針 |
| `check_template_sync` 境界更新 (`{{TOC_ROW}}` 単一行検出 + legacy fallback) | Phase 4-5 marker_legend と同パターン | 機械的コピペ |
| upgrade スクリプト構造 (TEMPLATE_TO_X 表 + OLD/NEW dispatch) | Phase 4-2 footer / 4-5 marker | β variant 別 dispatch に拡張 |

#### 設計コストの推移

| Phase | 新規設計判断 | 既存パターン再利用 |
|---|---|---|
| 4-3 (final_answer) | パターン A 確立 + β 配置設計 + thin/explicit/hybrid 比較 | — |
| 4-4 (inject_ref_ids) | パターン B 確立 + canonical 規約選択 + 8th card scope 拡張 | — |
| 4-5 (marker-legend) | パターン C 確立 + universality 実証 protocol | パターン A の対極として理論化 |
| **4-6 (TOC)** | **設計判断ほぼなし**（既存パターン組合せ） | **A + C + 境界更新の機械適用** |
| **4-7 (drill_blocks)** | **設計判断ほぼなし**（パターン D 再利用、escape 旧仕様踏襲） | **D（Phase 3-3 basis 由来）+ broken intermediate state mitigation** |

→ パターンが確立した後の Phase は **「新規設計 → パターン適用」へとシフト**。
Phase 4-7 で **パターン D の再利用** が実証され、A/B/C/D の 4 パターン体系が完成した。
Phase 4-8 以降も同様の再利用が期待できる。

### 4 パターン体系の選択指針（完成版・Phase 4-7 確定）

| ニーズ | 推奨パターン | 実例 |
|---|---|---|
| 既存 JSON フィールドから表示が一意導出可、新表現追加 | **A**（thin schema 派生） | 4-3 final_answer / 4-6 TOC |
| 既存 HTML 構造への横断的属性注入、document order 依存 | **B**（post-processing） | 4-4 inject_ref_ids |
| 8 templates 完全同期、problem 非依存の固定 HTML | **C**（universal const） | 4-2 footer-spec / 4-5 marker-legend |
| **旧 N 件固定 slot 方式の集約 + 配列駆動レンダリング** | **D**（構造化レンダリング） | **3-3 basis / 4-7 drill_blocks** |
| diff-allowed 領域の variant を既存フィールドから派生して集約 | **A + C 組合せ**（Phase 4-6 TOC のパターン）| 4-6 TOC |
| sync-required 領域内で per-problem 動的内容を含む | **A + β 配置**（Phase 4-3 final_answer のパターン）| 4-3 final_answer |
| spec 仕様の頻繁改訂対象、構造変化なし | **C**（footer-spec / marker-legend） | 4-2 / 4-5 |
| 構造化されているが N 固定で件数可変ニーズあり | **D**（render 関数化 + slot 集約） | 4-7 drill_blocks |

---

## §3. 検証最終状態

| 検証項目 | 結果 |
|---|---|
| **CP gate** (`scripts/_cp_gate_check.py`) | PASS=14 / DIFF=1 (300) / EXTRA=0 / MISS=0 |
| **check_template_sync** | sync-required 7 領域すべて 8 templates byte-identical（head / css / body_pre_toc / marker_legend / part_c_d / footer_spec / js）／ diff-allowed `toc` は variants 6→1 集約済 |
| **validate-tx 全 15 件** | ERROR 0 / WARNING 0（Phase 4-4 で達成、Phase 4-5/4-6/4-7 で維持） |
| **baseline** | `_phase3_2_pre_patch_baseline.json` 据え置き（Phase 4-3〜4-7 すべて byte-identical 維持型 patch のため、`docs/cp-gate.md` §4 規定により baseline 更新不要） |
| **remote 反映** | `https://github.com/xnhsky/bar-exam.git` master = local HEAD (`28e6e28`)、19 commits 反映済 |

300 のみ DIFF=1 は意図的（Phase 3-3 basis 構造化 + Phase 4-3 final_answer + Phase 4-4
anchor 注入 + 8th basis card 追加の累積結果、`docs/cp-gate.md` §1 「byte-identical
非保護」明示）。Phase 4-5/4-6/4-7 は 300 含め全 15 件 byte-identical で hash 不変。

---

## §4. 次セッション第 1 タスク候補

### 候補 A: remote 設定 + push（**最優先・本セッション持ち越し**）

**状態**: 本セッション中に **解決済**。Phase 4-3〜4-6 完了時点で 16 commits の初回 push が
GCM 経由ブラウザ認証で完了（remote `https://github.com/xnhsky/bar-exam.git` master）、
Phase 4-7 完了時点で追加 3 commits が GCM cached 認証で silent push 完了
（local HEAD = origin/master = `28e6e28`、累計 19 commits 反映）。本サマリ commit を
追加した後さらに 1 commit push 予定（最終 20 commits）。

→ **次セッションでは push は初手不要**。GCM cache 済のため通常の `git push` で透過的に
反映される。

### 候補 A': Phase 4-8 着手（body_pre_toc slot 化、最有力）

BACKLOG §4 で Phase 4-8 最有力候補として明示済。

- **領域**: body_pre_toc sync 領域（393 bytes / 11 lines、8 templates 完全同期）
- **設計**: Phase 4-5 marker-legend と同形の universal const + 引数なし関数パターン（C）
- **commit 計画**: 標準 3-commit（BACKLOG / render / templates）
- **規模**: 小（Phase 4-5 marker-legend の 約半分の bytes）、リスク最小

### 候補 B: pre_part_a 8 variants（中規模）

- **領域**: PART A 見出しコメント差（pre_part_a diff-allowed 8 variants）
- **設計**: Phase 4-6 TOC と同形（A + C 組合せ、per-instruction-type 派生）

### 候補 C: BACKLOG / SESSION-SUMMARY の継続整理

- BACKLOG §0 に Phase 4-7 完了行を追記（**本サマリ commit に統合済予定**）
- §6-N の整理（不要項目削除）

### 推奨順序

1. **A' (Phase 4-8 body_pre_toc)** を最初に消化（規模最小、パターン C の純粋形再演）
2. **B (Phase 4-9 pre_part_a)** 着手（パターン A+C 組合せ再演、Phase 4-6 と同形）
3. **C** は A' の commit 1 (BACKLOG update) に統合可

---

## §5. 保留事項

### 5-1. `ref-law-X-Y-NNN` 規約（BACKLOG §6-1）

- **状態**: 同一条文の複数項を区別する将来課題
- **着手判断条件**: 246条1項 + 246条2項 を同時参照する問題が出現したとき
- **実装方針**: `inject_ref_ids()` 内で anchor 表示テキストから「N項」「N号」を正規表現抽出し
  id に追加

### 5-2. ref-case 段落クラス情報 id 注入（BACKLOG §6-2）

- **状態**: chip mis-targeting が大量発生した場合の対応案
- **着手判断条件**: 複数 chip 著者の手作業 NNN 割当ミスが累積してきたとき
- **note**: canonical 規約からの逸脱になるため規約改定の合意が必要

### 5-3. ref-id 双方向検証（BACKLOG §6-3）

- **状態**: 未使用 id 検出機能（仕様 clean 性追求）
- **アクション**: `validate-tx.py` の S8 を双方向化、または別 sanity check スクリプト追加

### 5-4. TOC choice ラベル series の拡張余地（BACKLOG §6-5）

- **状態**: 現状 4 series × 最大 3 N 値 = 6 cells 占用 / 18 cells 拡張余地
- **着手判断条件**: 新 instruction_type 追加が必要なとき（辞書 1 行追加で対応可能）

### 5-5. Phase 5+ JX シリーズ着手

- **状態**: TX シリーズの slot 化を Phase 4-N で進行中、JX (事例式) シリーズの slot 化は
  未着手
- **note**: `spec/jx-v3.2-master.md` 由来の構造化（A〜H 8 サブセクション × 主要論点 +
  第 3〜5 部）が次ターゲット。1 問 1〜2 時間規模のため Phase 5 として大きく時間配分が必要

### 5-6. `problems/_300_v6_backup.json`

- **状態**: git 未追跡で意図的残置（Phase 3 既存判断 — `docs/cp-gate.md` §3 historical
  artifact 扱い）
- **アクション**: Phase 4 完了後の整理 commit で削除候補（緊急性なし）

### 5-7. Phase 4-N 旧 baseline 群

- **状態**: `_sha256_baseline.json` / `_html_baseline.json` / `_html_baseline_10.json` /
  `_template_baseline.json` / `_template_baseline_7.json` は git 未追跡で残置
- **アクション**: 同上、整理 commit で削除候補（`docs/cp-gate.md` §3 で historical artifact
  扱い明示済）

### 5-8. ~~remote 未確保~~（**本セッション中に解決済**）

- **状態**: 本セッション中に GCM 経由 push で解決。累積 19 commits を `xnhsky/bar-exam`
  master に反映済、本サマリ commit 後さらに 1 commit push で 20 commits 到達予定
- **次セッション**: GCM cached 認証で透過的に push 可能

---

## §6. セッション統計

| 項目 | 数値 |
|---|---|
| 本セッション通算 commits（CP infra + Phase 4-1〜4-7 + 中間/最終サマリ 2 件）| **21**（本サマリ commit 含めれば **22**） |
| Phase 4-3〜4-7 のみの commits | **17** |
| 14 protected ファイルの byte-identical 維持 | ✅ 全 commit |
| 300 (demo) の hash 変化 | Phase 4-3 / 4-4 で更新、Phase 4-5 / 4-6 / 4-7 で不変 |
| 全 15 件 validate-tx ERROR 0 / WARNING 0 達成タイミング | Phase 4-4 完了時点（以後 4-5/4-6/4-7 で維持） |
| templates 行数削減累計 | marker-legend 80 行 + toc 80-96 行 + drill 768 行 = 約 **930 行削減** |
| templates bytes 削減累計 | marker-legend 5,536 + toc 約 3,200 + drill **70,800** = 約 **79,500 bytes 削減 (≒ -80 KB)** |
| diff-allowed `toc` variants 集約 | 6 variants → 1 variants |
| 旧 DRILL_NN_* slot 廃止数 | **60 slot** (Phase 4-7) |
| 確立された設計パターン数 | **4**（A: thin schema 派生 / B: post-processing / C: universal const / D: 構造化レンダリング）+ メタ認知 1（再利用 + 境界更新の定型化） |
| 各パターンの再利用例 | A: 4-3 / 4-6 ・ B: 4-4 のみ ・ C: 4-2 / 4-5 / 4-6(部分) ・ D: 3-3 / 4-7 |
| remote push | `xnhsky/bar-exam` master = local HEAD (`28e6e28` + 本サマリ commit) |
| BACKLOG.md 行数推移 | 168（新規）→ 245（P4-4）→ 226（P4-5）→ 270（P4-6）→ 360 行（P4-7）|

---

**本セッション、Phase 4-3 / 4-4 / 4-5 / 4-6 / 4-7 の 5 Phase 完走。**
**設計パターンの確立（4-3〜4-5: 3 パターン）→ 再利用（4-6）→ 第 4 パターンの体系化と再利用（4-7）**
**という 4 パターン体系（A/B/C/D）の完成 + 各々の再利用例を 1 セッション内で達成した。**

remote `xnhsky/bar-exam` master に外部 backup 完了。

push は次セッション初手タスク（候補 A）として持ち越し。
