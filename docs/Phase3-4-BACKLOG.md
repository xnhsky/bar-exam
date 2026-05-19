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

CP gate 正準 baseline: `_phase3_2_pre_patch_baseline.json` (`docs/cp-gate.md` §1)

---

## §1. Phase 4-4: rb-chip back-link 解決（S8 WARNING 撤去）

### 1-1. 問題の所在

Phase 3-3 で basis cards を構造化レンダリング化した際、各 card に `back_links[{href, label}]`
配列を持たせる schema を導入した。300.json 基盤の rb-chip back-link チップは PART B 各記述解説
への戻り導線として機能するが、現状 **chip の `href="#ref-X-NNN"` に対応する `id="ref-X-NNN"`
target が PART B 内のどこにも存在しない**ため、`validate-tx.py` の S8（未解決アンカー）警告が
300.html に対して発生する。

```
[S8] 未解決アンカー: ['ref-case-saiko-h15-3-12-001', 'ref-case-saiko-h18-8-21-002',
                      'ref-case-saiko-h15-3-12-002', 'ref-case-saiko-h22-7-29-001',
                      'ref-law-246-1-001', ...]
```

300.html の 7 つの basis cards から計 **18 個の rb-chip** が出力されるが、全 chip が
unresolved。14 protected ファイルは basis 構造化未着手のため chip 不在で影響なし。

### 1-2. canonical KTX301 の参考実装

```html
<a class="ref-case" id="ref-case-saiko-s28-5-8-001" href="#case-saiko-s28-5-8">最判昭28.5.8</a>
<a class="ref-stat" id="ref-law-247-001" href="#law-247">247条</a>
```

inline 引用毎に `id="ref-{href から '#' 除去}-{NNN}"` を付与（NNN = 当該 target の出現順 1-indexed）。
canonical KTX301 では `id` は 18 個全て付与済だが、その target を狙う rb-chip 自体が canonical
には未実装（Phase 3-3 で初めて chip 側を導入）。

### 1-3. 現状の counts（300.html 解析）

| target href | inline 出現数 | basis chip 期待 NNN |
|---|---|---|
| `#law-246` | 22 | 001, 005, 008, 011, 013 (5 chips) |
| `#case-saiko-h18-8-21` | 10 | 001, 002 |
| `#case-saiko-h22-7-29` | 9 | 001, 002 |
| `#case-saiko-h15-3-12` | 9 | 001, 002 |
| `#case-saiko-s45-6-30` | 7 | 001, 002 |
| `#case-saiko-s42-12-21` | 7 | 001, 002 |
| `#case-dairen-t11-12-15` | 6 | 001, 002 |
| `#case-saiko-h8-4-26` | **0** | 001 (1 orphan) |

合計 70 個の inline anchor / 7 target / 18 chip。orphan 1 件あり（後述 1-5）。

### 1-4. canonical 命名規約との不整合

300.json basis back_links は法条文 chip に `ref-law-246-1-NNN`（**項番号 `-1-` qualifier 付き**）
を採用しているが、canonical KTX301 の inline id は `ref-law-247-NNN`（**qualifier なし**）。
規約が異なると auto-injection で一致させられないため、Phase 4-4 では **canonical 規約に揃える**
（`ref-law-XXX-NNN`、項 qualifier 削除）。

300 では 246条1項以外の参照がないため、規約変換は単純な「`-1-` 削除」で済む。NNN の数字
（001, 005, 008, 011, 013）は出現順インデックスとして温存可能。

### 1-5. orphan chip の扱い（inject 採用）

case-saiko-h15-3-12 card の "関連" chip `#ref-case-saiko-h8-4-26-001` は、target case
（最判平8.4.26）が 300.html 内で **plain text として 3 箇所言及**されている（記述4 prof-note /
PART C §④学説対立表 / C-7 memory item）が、いずれも `<a class="ref-case">` 化されていないため
auto-injection で id 生成されず orphan 化。

**対処方針**: Commit 3 にて記述4 prof-note の "（最判平8.4.26）" 部分を
`<a class="ref-case" href="#case-saiko-h8-4-26">最判平8.4.26</a>` に変換し anchor 化。
これにより inject_ref_ids() が `id="ref-case-saiko-h8-4-26-001"` を自動付与 → chip resolve。

**判例関連性**（commit 2 着手前に文書化必須）: 最判平8.4.26 は記述4（誤振込払戻詐欺・最決平15.3.12）
の民事的背景を確定する先行判例であり、両判例の対比により民事と刑事の独立判断が際立つ重要対。
本 BACKLOG では Phase 4-4 commit 2 着手直前に独立した 1 文サマリで明示確定する。

---

## §2. 設計（schema 変更なし・render.py post-processing）

### 2-1. 採択方針

| 項目 | 設計 |
|---|---|
| schema 変更 | **なし**。既存 `basis.cards[].back_links[]` schema を据え置き |
| render.py 改修 | `inject_ref_ids(html)` 関数を追加、`main()` で render 後 → 出力前に post-processing |
| 14 protected への影響 | **0 個の inline ref-X anchor** → 注入対象なし → byte-identical 自動維持 |
| 300.html への影響 | 70 個の inline anchor に `id="ref-X-NNN"` 注入で hash 変化（既存 DIFF=1 内維持） |
| 300.json データ更新 | (a) basis.cards.back_links の `ref-law-246-1-NNN` → `ref-law-246-NNN` 規約整理、(b) 記述4 prof-note の "（最判平8.4.26）" を `<a class="ref-case" href="#case-saiko-h8-4-26">最判平8.4.26</a>` に anchor 化（orphan chip 解消） |
| **呼出経路前提** | `render.py` の `render()` 関数は本 repo 内では `main()` から **のみ** 呼ばれる（テスト経路・他スクリプトからの直接 import なし）。inject_ref_ids() の配置は `main()` 内で完結し、`render()` 関数本体は post-processing を持たない（unit test 経路を将来追加する際は明示的に呼出側で `inject_ref_ids()` を chain する設計を採る）。 |

### 2-2. inject_ref_ids 関数仕様

```python
def inject_ref_ids(html: str) -> str:
    """全 <a class="ref-case|ref-stat" href="#X"> に id="ref-X-NNN" を注入。

    NNN は当該 target に対する 1-indexed 出現順（document order）、ゼロ埋め 3 桁。
    既に id 属性を持つ <a> はスキップ（idempotent）。
    """
    pattern = re.compile(r'<a class="(ref-case|ref-stat)" href="#([^"]+)">')
    counters: dict[str, int] = {}

    def repl(m: re.Match) -> str:
        cls, target = m.group(1), m.group(2)
        counters[target] = counters.get(target, 0) + 1
        n = counters[target]
        return f'<a class="{cls}" id="ref-{target}-{n:03d}" href="#{target}">'

    return pattern.sub(repl, html)
```

- 入力: render() 出力済 HTML
- 出力: `id` 属性注入済 HTML
- 既存 `id` 属性付き `<a>` は regex がマッチしないためスキップ（idempotent）
- 配置: `scripts/render.py` の `main()` 内、`rendered = render(template, slots)` 直後に `rendered = inject_ref_ids(rendered)` を挟む

### 2-3. 300.json 更新内容

(a) law-246 card の chip naming を `-1-` qualifier 削除版に整理:

```jsonc
"back_links": [
  { "href": "#ref-law-246-001", "label": "記述1" },
  { "href": "#ref-law-246-005", "label": "記述2" },
  { "href": "#ref-law-246-008", "label": "記述3" },
  { "href": "#ref-law-246-011", "label": "記述4" },
  { "href": "#ref-law-246-013", "label": "記述5" }
]
```

(b) case-saiko-h15-3-12 card の "関連" chip (`#ref-case-saiko-h8-4-26-001`) は **温存**。
記述4 prof-note 内の plain text "（最判平8.4.26）" を anchor 化することで自動的に target
を生成する:

```html
<!-- Before -->
（最判平8.4.26）

<!-- After -->
（<a class="ref-case" href="#case-saiko-h8-4-26">最判平8.4.26</a>）
```

PART C 表セルおよび C-7 memory item の同 plain text は anchor 化しない（chip "関連" は 1st
occurrence を狙うため 1 箇所の anchor 化で十分。複数化すると -002, -003 が生成されるが
chip は -001 のみ参照のため不要な id が増えるだけ）。

### 2-4. NNN インデックス確認

300.html 上で law-246 が 22 回出現するが、basis chip 著者が指定した順序（記述1=001 / 記述2=005 /
記述3=008 / 記述4=011 / 記述5=013）が実際の document order と一致するか、commit 2 適用後の
auto-injected id と照合し確認する。**ズレが見つかれば 300.json 側の NNN を実際の順番に合わせ
更新**（chip 著者は手数で書いた値なので、最終的に inject 出力の正典に合わせる）。

各 case の 001/002 もそれぞれ「記述N解説」「あてはめ」（or 「考え方」）の 2 つを当該記述の
解説段落と prof-note 段落に対応させる前提。1st mention が「記述N解説」段落、2nd mention が
prof-note 段落の想定。

---

## §3. 3 commit 実装計画

各 commit 後 STOP for review。各 commit で CP gate + check_template_sync + validate-tx (代表 4 件 + 300) を実行。

| # | commit subject | 影響範囲 | CP gate | sync | validate-tx |
|---|---|---|---|---|---|
| 1 | `docs: BACKLOG.md §0 Phase 4-3 完了追記 + §1 Phase 4-4 スコープ` | docs only | PASS=14 / DIFF=1 | ✅ | 14 protected ERROR 0/WARNING 0、300 ERROR 0/WARNING 1 維持 |
| 2 | `feat(phase4-3 render): inject_ref_ids() 後処理 + main 配線` | scripts/render.py + outputs/tx/刑TX/刑TX300.html | PASS=14 / DIFF=1 (300 hash 更新) | ✅ | 14 protected 不変、**300 でも S8 一部 resolve**（チップ NNN と実際 NNN の整合次第） |
| 3 | `feat(phase4-4 data): 300.json basis back_links 規約整理 + 最判平8.4.26 anchor 化` | problems/300.json + outputs/tx/刑TX/刑TX300.html | PASS=14 / DIFF=1 | ✅ | **300 S8 WARNING 解消 → ERROR 0 / WARNING 0** |

### 各 commit 後の検証コマンド

```bash
python scripts/_cp_gate_check.py
python scripts/check_template_sync.py
for f in 刑TX/刑TX326 憲TX/憲TX001 行政TX/行政TX001 刑訴TX/刑訴TX001 刑TX/刑TX300; do
  python scripts/validate-tx.py "outputs/tx/$f.html"
done
```

### Phase 4-4 完了条件

- 全 15 件 `validate-tx.py` で ERROR 0 / WARNING 0
- CP gate PASS=14 / DIFF=1 (300 のみ、Phase 4-4 で hash 更新)
- check_template_sync sync-required 7 領域 PASS
- 300.html 内 rb-chip 18 個（orphan inject 解消含む）全て resolve

---

## §4. Phase 4-5 以降の候補（参考、未着手）

| 候補 | 領域 | 主要懸念 | 優先度 |
|---|---|---|---|
| PART D drill-block 12 件 (`drill-block` literal) | part_c_d sync 領域内 | drill_blocks JSON は既存、template の `<div class="drill-block">` 構造を slot 化 | 中 |
| TOC 行（`<div class="toc-row">`）| toc diff-allowed 領域 (6 variants) | instruction_type 別の TOC ラベル差を render.py 側で生成 | 低 |
| marker-legend ブロック | marker_legend sync 領域 | リテラル固定だが、spec bump 時に同期手修正が必要 | 低 |
| body_pre_toc（`<div class="doc-header">` 等）| body_pre_toc sync 領域 | 静的、変更頻度低 | 低 |
| PART A 見出しコメント（pre_part_a diff-allowed 8 variants）| pre_part_a | コメント文言の集約 | 低 |

Phase 4-4 完了後、優先度順にスコープ化する。

---

## §5. 検証スクリプトと baseline

| スクリプト | 目的 | Phase 4-N 期待値 |
|---|---|---|
| `scripts/_cp_gate_check.py` | 全 15 件再 render → baseline と sha256 比較 | PASS=14 / DIFF=1 (300) |
| `scripts/check_template_sync.py` | 8 templates の sync-required 7 領域一致確認 | 全 commit で PASS |
| `scripts/validate-tx.py` | S1〜S82 構造/feature-tag/content independence 検証 | ERROR 0 / WARNING 0（Phase 4-4 完了後は 300 も含む） |

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
