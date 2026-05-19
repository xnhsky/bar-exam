# Session 2026-05-19 — Phase 4-3 / 4-4 / 4-5 完走 + 設計パターン総括

> 本セッションで bar-exam TX 系 slot 化整備が Phase 4-2 完了状態から Phase 4-5 完了
> 状態まで前進した。累積 commits 12（本サマリ commit 含めれば 13）、Phase 4-3〜4-5
> で確立された 3 つの設計パターン、最終検証状態、次セッション着手候補、保留事項を
> 一元記録する。

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

判例関連性（commit 2 着手前に確定文書化）: 最判平8.4.26 は誤振込でも預金契約が有効に
成立し受取人に形式的払戻請求権が発生することを示した **民事先例**であり、記述4
（誤振込払戻詐欺・最決平15.3.12）の民事的背景を確定する。両判例の対比により
**民事的有効性と刑事可罰性の独立判断**という核心法理が際立つ重要対。

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

### 本セッション通算 commit カウント

| 区分 | commits |
|---|---|
| CP gate infrastructure | `47cf0d0` |
| Phase 4-1 + 4-2 統合 | `88b0486` |
| Phase 4-3 (4 commits) | `0f7e673` / `abd2a28` / `f327664` / `dee2bc0` |
| Phase 4-4 (3 commits) | `41f0edf` / `b2bb088` / `49dea8d` |
| Phase 4-5 (3 commits) | `6b64e17` / `9caa756` / `3cc412c` |
| **本サマリ commit** | (今回追加、Phase 4-3〜4-5 累積で 11 commits 目) |

累積 commits（Phase 4-3〜4-5 のみ）= 10、本サマリ込みで 11。
本セッション通算 = 12（CP infra + Phase 4-1+4-2 + Phase 4-3〜4-5）、本サマリ込みで 13。

> 補足: Phase 2 PART C (`47c1f1d`) と Phase 3 basis (`1f54a17`) もこのセッション中に
> commit したが、内容自体は事前にローカル作業済の slot 化機能（footer/views/partc/basis）を
> 4-commit 構造で整理整頓したもの。新規設計判断を含むのは Phase 4-3 以降のため、上記
> カウントから除外。

---

## §2. 本セッションで確立された 3 つの設計パターン

### パターン A: Thin schema + render 派生（Phase 4-3 final_answer）

**定義**: JSON 新規フィールドを最小化し、既存フィールドから render.py 内で派生計算する slot 化アプローチ。

**実装例**:
```python
def render_final_answer(problem: dict) -> str:
    fa = problem.get("final_answer")
    if not fa:
        return ""  # 未指定 → block ごと不出力 (byte-identical 維持)

    summary_html = fa.get("summary_html", "")
    extra_html = fa.get("extra_html", "")
    instr_type = problem.get("instruction_type", "")  # 既存
    answer_raw = problem.get("answer", "")             # 既存

    if instr_type == "multi-select-5" and isinstance(answer_raw, list):
        # §22-ter 派生
        ...
    else:
        # §22-bis 派生（answer_value = _format_answer(answer_raw)）
        ...
```

**適用条件**:
- 表示形式が既存フィールドから一意に導出可能（mode 自動判定など）
- JSON 著作負担を minimum に保ちたい
- データの二重管理リスクを避けたい

**利点**:
- 既存 JSON の保守負担増加なし
- 派生ロジックが render.py 1 箇所に集約 → 仕様変更時の追従が容易
- thin schema により JSON validator のチェック範囲が明確

**トレードオフ**: 派生ルールが render.py に隠れるため、JSON だけ見ても最終 HTML が予測しづらい。
→ BACKLOG §2 で派生ルールを明示することで軽減。

### パターン B: Post-processing 注入（Phase 4-4 inject_ref_ids）

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

### パターン C: Universal content の minimal slot 化（Phase 4-5 marker-legend）

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

# build_slot_dict():
slots["MARKER_LEGEND"] = render_marker_legend()
```

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

### 3 パターンの選択指針

| ニーズ | 推奨パターン |
|---|---|
| 既存 JSON フィールドから表示が一意導出可、新表現追加 | **A**（thin schema） |
| 既存 HTML 構造への横断的属性注入、document order 依存 | **B**（post-processing） |
| 8 templates 完全同期、problem 非依存の固定 HTML | **C**（universal slot） |
| sync-required 領域内で per-problem 動的内容を含む | A + B 組合せ（例: Phase 4-3 final_answer の C-7 内嵌） |
| spec 仕様の頻繁改訂対象、構造変化なし | C（footer-spec / marker-legend） |

---

## §3. 検証最終状態

| 検証項目 | 結果 |
|---|---|
| **CP gate** (`scripts/_cp_gate_check.py`) | PASS=14 / DIFF=1 (300) / EXTRA=0 / MISS=0 |
| **check_template_sync** | sync-required 7 領域すべて 8 templates byte-identical（head / css / body_pre_toc / marker_legend / part_c_d / footer_spec / js） |
| **validate-tx 全 15 件** | ERROR 0 / WARNING 0（Phase 4-4 で達成、Phase 4-5 で維持） |
| **baseline** | `_phase3_2_pre_patch_baseline.json` 据え置き（Phase 4-3〜4-5 はすべて byte-identical 維持型 patch のため、`docs/cp-gate.md` §4 規定により baseline 更新不要） |

300 のみ DIFF=1 は意図的（Phase 3-3 basis 構造化 + Phase 4-3 final_answer + Phase 4-4 anchor
注入 + 8th basis card 追加の累積結果、`docs/cp-gate.md` §1 「byte-identical 非保護」明示）。

---

## §4. 次セッション第 1 タスク候補

### 候補 A: remote 設定 + push（高優先）

`git remote -v` 空、累積 12〜13 commits 未 push。本セッション開始時点から継続している
issue。`gh repo create` or 既存 remote 設定後、`git push -u origin master` で一括反映可能。

```bash
# 既存 remote 設定がある場合
git remote add origin <url>
git push -u origin master

# 新規 GitHub repo を作成する場合 (要 gh auth)
gh repo create <name> --source=. --push
```

### 候補 B: Phase 4-6 着手（TOC slot 化）

BACKLOG §4 で Phase 4-6 最有力候補として明示済。

- **領域**: `toc` diff-allowed 6 variants（363-436 bytes / 10-12 lines × 6 種）
- **挑戦点**: Phase 4-2/4-5 の sync-required 領域 slot 化と異なり、`instruction_type`
  別ラベル差（ア〜オ / 1〜5 / A〜E 等）を render.py 側で生成する必要
- **設計予想**: `TOC_LABELS_BY_INSTRUCTION_TYPE: dict` + `render_toc(instruction_type)` 関数
- **commit 計画**: BACKLOG / render / templates の 3-commit パターン（Phase 4-3〜4-5 と同形）

### 候補 C: BACKLOG §6 整理

Phase 4-5 完了で確定した不要項目を削除:
- §6-4 (extra_legend_items hook) → universal 実証で不要確定、削除候補

維持項目:
- §6-1 (ref-law-X-Y-NNN qualifier) — 複数項参照問題が出現するまで保留
- §6-2 (段落クラス情報 id 注入) — chip mis-targeting 大量発生時の対応
- §6-3 (id→chip 逆方向検証) — 仕様 clean 性追求

### 推奨順序

1. **A (remote + push)** を先に消化（commit 累積を解消、外部 backup 確保）
2. **B (Phase 4-6 TOC)** 着手（次の slot 化技術応用）
3. **C (BACKLOG 整理)** は B の commit 1 (BACKLOG update) に統合可

---

## §5. 保留事項

### 5-1. per-problem `extra_legend_items` hook（Phase 4-5 §6-4）

- **状態**: Phase 4-5 で universality 実証され不要確定
- **アクション**: 次セッションで BACKLOG §6-4 を削除（Phase 4-6 commit 1 に統合）

### 5-2. `ref-law-X-Y-NNN` 規約（BACKLOG §6-1）

- **状態**: 同一条文の複数項を区別する将来課題
- **着手判断条件**: 246条1項 + 246条2項 を同時参照する問題が出現したとき
- **実装方針**: `inject_ref_ids()` 内で anchor 表示テキストから「N項」「N号」を正規表現抽出し
  id に追加

### 5-3. ref-case 段落クラス情報 id 注入（BACKLOG §6-2）

- **状態**: chip mis-targeting が大量発生した場合の対応案
- **着手判断条件**: 複数 chip 著者の手作業 NNN 割当ミスが累積してきたとき
- **note**: canonical 規約からの逸脱になるため規約改定の合意が必要

### 5-4. ref-id 双方向検証（BACKLOG §6-3）

- **状態**: 未使用 id 検出機能（仕様 clean 性追求）
- **アクション**: `validate-tx.py` の S8 を双方向化、または別 sanity check スクリプト追加

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

---

## §6. セッション統計

| 項目 | 数値 |
|---|---|
| 本セッション通算 commits（Phase 4-3〜4-5 + 本サマリ） | 11 |
| 本セッション通算 commits（CP infra + Phase 4-1+4-2 含む） | 13 |
| 14 protected ファイルの byte-identical 維持 | ✅ 全 commit |
| 300 (demo) の hash 変化 | Phase 4-3 / 4-4 / 4-5 で更新（DIFF=1 内維持） |
| 全 15 件 validate-tx ERROR 0 / WARNING 0 達成タイミング | Phase 4-4 完了時点 |
| templates 行数削減（marker-legend 集約のみ） | 8 templates × 10 lines = 80 行削減（5,536 bytes 削減） |
| BACKLOG.md 行数推移 | 168 行（新規）→ 245 行（P4-4 更新）→ 226 行（P4-5 更新） |

---

**本セッション、Phase 4-3 / 4-4 / 4-5 の 3 Phase 完走。**
