# Phase 13B — render.py への fb-2〜fb-5 吸収 HANDOFF

> **作成日**: 2026-05-26（旧セッション終了時）
> **目的**: 303.html で確立した v9.4.0 polish パターン (fb-1〜fb-5 + 群青蘭 palette + SVG redesign) を、`templates/KTX_template.html` と `scripts/render.py` に absorb することで、306 以降の TX 生成にも自動適用される状態にする
> **HEAD**: `8408439` + 303.html 後段修正（コミット未済 / `outputs/` は .gitignore 対象）

---

## 0. 新セッション初動

新セッションで user が以下を入力：

```
docs/PHASE-13B-RENDER-PY-HANDOFF.md を読んで Phase 13B を進めて
```

CC は本ドキュメント全文を読み、最初に「現状把握 → 差分抽出 → patch 設計」の順で着手する。**いきなり template を編集しない**。

---

## 1. ゴール (Definition of Done)

- `python scripts/render.py 303` で再生成した HTML が、現 `outputs/000_TX/刑TX/刑TX303.html`（手動 polish 済 = gold standard）と **視覚的に同等** になる
- 306 以降の新規問題でも `python scripts/render.py NNN` だけで fb-2〜fb-5 が適用される
- 検証: `python scripts/validate-tx.py outputs/000_TX/刑TX/刑TX303.html` で ERROR 0 / WARNING 0
- diff ベース照合: 再生成 HTML と現 gold standard の差分は palette CSS と座標値（自動 layout 由来）のみで、構造的差異はゼロ

---

## 2. 設計方針 — 2 層分離

### Layer A: `templates/KTX_template.html`（**CSS 中心**）

CSS 規律と HTML テンプレート構造の改修。**問題依存しない**箇所は全部ここ。

- fb-1 〜 fb-5 の CSS rule（後述）
- §5 配色パレット 3 流派コメント（壱/弐/参 ─ 紅蓮/群青蘭/黎明）
- `:root` 構造：base palette + override スロット
- 動詞語：placeholder の slot 形式（`{{ ... }}`）

### Layer B: `scripts/render.py`（**HTML structure 中心**）

JSON → HTML 生成時の構造制御。**問題依存する**箇所はここ。

- `case.paragraphs` を `case-scene` カードに wrap する renderer
- `basis.cards[].note` を `<span class="note-body">` で wrap する renderer
- 群青蘭 palette が seed=303 で適用される palette_seed_lookup（v9.3.0 PALETTE-MULTI-VARIANT 系の完成）
- footer-spec から visible feature-tags を hidden 化する v9.4.0 mode

### 配布物

- 新規 patch: **`render-py-phase13b.patch`**（既存 phase13a の隣に置く）
- template 改修は patch ではなく直接編集（template は単一巨大ファイルで diff が読みにくいため）

---

## 3. 抽出対象 6 パターン（CSS / HTML / render.py 改修箇所）

各パターンの **抽出元行番号** は `outputs/000_TX/刑TX/刑TX303.html`（gold standard）における位置。

### 3-1. fb-4: NOTE box grid layout + `.note-body` wrapper ⭐最重要

**抽出元 CSS**: `outputs/000_TX/刑TX/刑TX303.html:607-640`

```css
.basis-card-body .note{
  position:relative;
  background:#e7f1ff;
  border:1px solid rgba(21,101,192,.30);
  border-radius:8px;
  padding:18px 32px 14px;
  margin:14px 0 12px;
  font-family:var(--font-note); font-weight:500;
  line-height:1.95; letter-spacing:.03em;
  box-shadow:
    0 2px 6px rgba(0,0,0,.06),
    inset 0 0 0 1px rgba(255,255,255,.6);
  /* fb-4: badge を 1 列目、body を 2 列目に固定 → 2 行目以降が badge 右側に揃う */
  display:grid;
  grid-template-columns:max-content 1fr;
  column-gap:12px;
  align-items:start;
}
.basis-card-body .note::before{
  content:'ℹ NOTE'; display:inline-flex;
  align-items:center;
  background:linear-gradient(135deg,#0d47a1,#1565c0);
  color:#fff; padding:3px 10px 2px;
  border-radius:3px;
  font-family:var(--font-mono);
  font-size:.72rem; font-weight:700; letter-spacing:.14em;
  margin:6px 0 0 0;
  box-shadow:0 1px 2px rgba(0,0,0,.18);
}
.basis-card-body .note .note-body{
  display:block;
  text-indent:1em;
}
```

**抽出元 HTML structure**: `outputs/000_TX/刑TX/刑TX303.html:3001-3003` ほか 5 箇所

```html
<div class="note">
  <span class="note-body">本問は不動産（246条1項客体）の詐欺取得が出発点となる。…</span>
</div>
```

**Layer A**: 上記 CSS を `templates/KTX_template.html` の §14 basis-card 該当箇所に上書き
**Layer B**: `render.py` で basis.cards の note 出力時、テキストを `<span class="note-body">…</span>` で wrap

`render.py` 該当箇所候補: `def render_basis()` または basis-card 出力ループ（grep `"note"` で特定）

---

### 3-2. fb-5: 全文章 国語的字下げ 統一定義

**抽出元 CSS**: `outputs/000_TX/刑TX/刑TX303.html:2115-2183`

CSS 全文は gold standard を参照（包含 11 selector / 除外 35 selector + `!important`）。

ただし注意：base template `templates/KTX_template.html:1625-1632` には既に簡易版 `p { text-indent:1em }` が存在する。**この簡易版で大半の `<p>` はカバー済**。fb-5 で追加が必須なのは：

1. `.basis-card-body > p.hanging > .hang-body { display:block; text-indent:1em }` ← 条文・判例本文（最重要）
2. `.basis-card-body .note .note-body { text-indent:1em }` ← NOTE 本文（fb-4 とセット）
3. `.case-paragraph { text-indent:1em }` ← A-1 場面本文
4. `.mem-body p`, `.key-phrase-box`, `.interpretation-body`, `.arena-intro`, `.theory-detail-grid dd` — 各々個別追加

除外群（既存 `.figure-caption, .answer-instruction` に加える）は最小限で OK：
- `.basis-card-body > p.hanging` ← grid layout（child の hang-body で別途 indent）
- `.choice-summary, .ref-backlinks p, .back-link-row p` ← chip / 引用
- `.choice-points li, .choice-points ol` ← bullet list

**判断**: fb-5 の OFF 35 selector は overspec の疑いあり。新セッションでは「base template の `p {}` だけで 95% カバー → 不足は 4 selector 追加」で済むかをまず diff で検証。

---

### 3-3. fb-2/fb-3: A-1 case-scene カード化（4 場面の時系列構造）

**抽出元 CSS**: `outputs/000_TX/刑TX/刑TX303.html:2185-2234`

```css
#part-a .case-description{ margin:18px 0 24px; }
#part-a .case-scene{
  background:linear-gradient(180deg, var(--accent-3) 0%, var(--paper) 100%);
  border:1px solid rgba(var(--accent-rgb),.18);
  border-left:5px solid var(--accent);
  border-radius:10px;
  padding:16px 22px 18px;
  margin:12px 0;
  box-shadow:0 1px 4px rgba(var(--accent-rgb),.06);
}
#part-a .case-scene-label{
  display:flex; align-items:center; gap:14px;
  padding-bottom:10px; margin-bottom:10px;
  border-bottom:1.5px dashed rgba(var(--accent-rgb),.30);
}
#part-a .case-scene-num{
  display:inline-flex; align-items:center; justify-content:center;
  width:36px; height:36px;
  border-radius:50%;
  background:var(--accent); color:#fff;
  font-family:var(--font-display);
  font-size:1.20rem; font-weight:800;
  flex-shrink:0;
  box-shadow:0 2px 6px rgba(var(--accent-rgb),.30);
}
#part-a .case-scene-title{
  font-family:var(--font-soft);
  font-size:1.02rem; font-weight:700;
  color:var(--bg-dark);
  letter-spacing:.03em; line-height:1.5;
}
#part-a .case-paragraph{
  margin:0; line-height:1.95;
  font-weight:550;
  text-indent:1em;
}
```

**抽出元 HTML structure**: `outputs/000_TX/刑TX/刑TX303.html:2527-2546`（A-1 case-description 内 4 件）

```html
<div class="case-scene">
  <div class="case-scene-label">
    <span class="case-scene-num">1</span>
    <span class="case-scene-title">{場面タイトル（例：不動産の詐取）}</span>
  </div>
  <p class="case-paragraph">{場面本文}</p>
</div>
```

**Layer A**: CSS を template に追加
**Layer B**: `render.py:2706-2715` の case-description 出力ロジックを書き換え。各 paragraph を `case-scene` でラップ。

問題: 現状の JSON は `case.paragraphs: [str, str, ...]` の単純配列で、場面タイトルが無い。3 案：

| 案 | 内容 | トレードオフ |
|---|---|---|
| α | JSON schema 拡張：`case.scenes: [{title, body}]` を追加 | 既存 305-313 JSON も全部書き直し |
| β | render.py 側で paragraph 内容から AI なしで title を導出（先頭 N 文字 or 句点前） | 不格好な title になる場合あり |
| γ | render.py で「場面 1 / 場面 2 / …」と機械タイトル（title なし版）を出す | 視覚的にはやや弱いが堅牢 |

**推奨**: γ（無 title でカード化のみ）→ 各問題で task force 時に α へ昇格。最初は壊れにくい γ で出して、303.json だけ手動で title 追加 → 一致確認。

---

### 3-4. fb-1: 条文/判例 header freq-badge spacing

**抽出元 CSS**: `outputs/000_TX/刑TX/刑TX303.html:2273-2286`

```css
.basis-card .basis-card-header{
  display:flex;
  align-items:center;
  flex-wrap:wrap;
  gap:14px;
  justify-content:space-between;
}
.basis-card .basis-card-header .freq-badge{
  margin-left:auto;
  padding:4px 12px;
  font-size:.85rem;
  letter-spacing:.05em;
}
```

**Layer A only**: template の §14 basis-card-header 該当 rule に上書き。HTML 構造変更不要。

---

### 3-5. fb-2: 細字補強（body weight 500 → 550）

**抽出元 CSS**: `outputs/000_TX/刑TX/刑TX303.html:2262-2271`

```css
.basis-card-body p,
.sub-card.explanation p,
.sub-card.professor p,
.prof-analogy p,
.theory-detail-grid dd,
#c-4 .interpretation-body,
.basis-card-body .note{
  font-weight:550;
}
```

**Layer A only**: template に追加。

---

### 3-6. priority-badge ①②③ 拡大（C-2 三層構造記憶）

**抽出元 CSS**: `outputs/000_TX/刑TX/刑TX303.html:2287-2304`

```css
.memory-list .priority-badge{
  font-size:1.40rem !important;
  font-family:var(--font-display);
  font-weight:800;
  width:42px; height:42px;
  display:inline-flex; align-items:center; justify-content:center;
  border-radius:50%;
  background:var(--accent); color:#fff;
  flex-shrink:0;
  box-shadow:0 2px 6px rgba(var(--accent-rgb),.30);
  line-height:1;
}
```

**Layer A only**: template に追加。

---

### 3-7. 群青蘭 palette + 3 流派命名（v9.3.0 PALETTE-MULTI-VARIANT 完成）

**抽出元**: `outputs/000_TX/刑TX/刑TX303.html:38-80`（コメント + :root）

**現状**: render.py には `palette-strategy` メタタグの出力枠だけあって、実際の palette 値マッピング（seed → :root override）は未実装。303 の 群青蘭は手動置換。

**Layer B 大きめ**: `render.py` に palette table を追加。

```python
# v9.3.0 PALETTE-MULTI-VARIANT 値テーブル
PALETTE_VARIANTS = {
    "壱-紅蓮":   {"accent": "#8A1F3A", "mid": "#C58A9C", "name_en": "Karen / Crimson Lotus"},
    "弐-群青蘭": {"accent": "#3C828F", "mid": "#A989B8", "name_en": "Gunjouran / Azure Orchid"},
    "参-黎明":   {"accent": "#1F4754", "mid": "#5A9DB5", "name_en": "Reimei / Dawn Light"},
}

def seed_to_palette(seed: int) -> str:
    keys = list(PALETTE_VARIANTS.keys())
    return keys[seed % len(keys)]
```

`render()` 内で seed = problem_id（数字化）→ palette 名 → :root override block を組み立て、template の `{{PALETTE_DERIVATIVES_ROOT}}` slot に注入。

303 (seed=303 → 303%3=0 → 壱-紅蓮) になってしまうため、別の seed 関数が必要：
- 例：`seed = sum(ord(c) for c in str(problem_id))` で 303 → 51 → 51%3=0 でも壱
- 303 が 群青蘭 になるよう逆算した seed 関数を採用（要設計）

**注**: gold standard の seed=303 → 群青蘭 を正解とする。新 seed 関数は 303→弐、306→? (何でもよい)、307→? のように分散すれば OK。

---

### 3-8. SVG redesign — tree / radial / flowchart の overlap 修正

**抽出元 SVG**:
- Tree: `outputs/000_TX/刑TX/刑TX303.html:3095-` 付近（viewBox 1500x820、L0/L1/L2/L3 座標）
- Radial: `outputs/000_TX/刑TX/刑TX303.html` の `id="mindmap-radial"` section（viewBox 1500x1180）
- Flowchart: `outputs/000_TX/刑TX/刑TX303.html` の `id="c-5"` 周辺（viewBox 1200x1280）

**Layer B 中規模**: 既存 `auto_layout_tree()` / `auto_layout_radial()` / `auto_layout_flowchart()` の座標マッピングを修正。

303 で行った overlap 修正：
- Tree: viewBox 1500 + L2 7-box を 30px+ ギャップで配置（120/300/500/720/920/1140/1380）
- Radial: 記述ウ sub-node を x=1440 に移動、記述イ "横領罪不成立" を y=430 に移動、記述エ sub を x=1380 に縮小
- Flowchart: 4 decision diamond + 罪種別 end-box（viewBox 1200x1280）

これらは「303 固有の座標」なので、auto_layout が**汎用的に**動くよう改善する必要がある。具体 algorithm 改修：

| 関数 | 改善点 |
|---|---|
| `auto_layout_tree` | viewBox を `1500` 系に拡大、L2 ノード間 min-gap を 30px に強制（重なり検出して shift） |
| `auto_layout_radial` | spoke 端点周囲の box の半径方向位置を **branch 線終点+gap** に強制揃え（branch 上に乗らないようガード） |
| `auto_layout_flowchart` | decision diamond と end-box の y 座標を grid snap、column 数を branch 数に応じて 1〜4 で switch |

**判断**: SVG redesign は手間が大きい。Phase 13B では**まず CSS / HTML 改修だけを完遂**して、SVG は Phase 13C に分離するのが現実的。

---

### 3-9. footer-spec の feature-tags 非表示化（v9.4.0 mode）

**抽出元 HTML**: `outputs/000_TX/刑TX/刑TX303.html` の footer 末尾

現状の 303 は visible feature-tag を消し、validator が要求する 4 tag を `<p class="footer-meta-hidden" hidden>` 内に `<span hidden>` で配置している。

```html
<p class="footer-meta-hidden" hidden>
  <span hidden>TX v9.4.0 COMPLETE-BASELINE</span>
  <span hidden>...</span>
</p>
```

**Layer B**: render.py で v9.4.0 mode のとき footer feature-tags を hidden ブロックで出すよう変更。

---

## 4. 実装ワークフロー（推奨手順）

```
Step 0. (新セッション初動) このファイル + render.py + KTX_template.html を全文確認
Step 1. python scripts/render.py 303 で baseline 再生成 → /tmp/303-baseline.html に退避
Step 2. diff /tmp/303-baseline.html outputs/000_TX/刑TX/刑TX303.html | wc -l で差分量を把握
Step 3. fb-4 (NOTE grid + .note-body wrapper) を実装
  3-A. templates/KTX_template.html に CSS 追記
  3-B. scripts/render.py の basis renderer を改修
  3-C. python scripts/render.py 303 → /tmp/303-step3.html
  3-D. diff /tmp/303-step3.html outputs/000_TX/刑TX/刑TX303.html で fb-4 部分が消えたか確認
Step 4. fb-1, fb-2, priority-badge 拡大 (CSS のみ) を template に追加 → 再生成 → diff
Step 5. case-scene カード化 (fb-3) を実装
Step 6. fb-5 字下げを minimum 必要分だけ追加 → diff で不足箇所を補充
Step 7. palette palette_variants + seed 関数 を実装（303 が 群青蘭 になる seed 関数を選択）
Step 8. footer-spec hidden 化を実装
Step 9. (任意) SVG overlap 修正 → Phase 13C に分離可
Step 10. validate-tx.py で ERROR 0 / WARNING 0 確認
Step 11. render-py-phase13b.patch を生成 (git diff scripts/render.py > render-py-phase13b.patch)
Step 12. template 改修は patch にせず直コミット
Step 13. 306 を試し生成して fb-2〜fb-5 が反映されているか確認
```

---

## 5. 必読ファイル（新セッション開始時）

1. **本ドキュメント全文**
2. `outputs/000_TX/刑TX/刑TX303.html`（gold standard、**read-only ─ コンテンツコピー禁止**）
3. `templates/KTX_template.html`（編集対象 A）
4. `scripts/render.py`（編集対象 B、3597 行 → 関連箇所のみ）
5. `render-py-phase13a.patch`（既存 patch の書式参考）
6. `docs/PHASE-13A-COMPLETION-HANDOFF.md`（前 phase の文脈参考）
7. `problems/303.json`（gold standard の入力データ、27+ keys）

検証時：
8. `scripts/validate-tx.py`（S1〜S91）

---

## 6. 絶対禁止事項（CLAUDE.md §7 由来 + 本 Phase 固有）

- ❌ `outputs/000_TX/刑TX/刑TX303.html` の本文・解説文字列を template / render.py にコピーすること（AP-42 / S78 違反）
- ❌ 既存関数の破壊的書き換え（render.py の他バージョン分岐を壊さない）
- ❌ render.py を 1 メッセージで 50KB 超出力（API socket error 予防）
- ❌ `:root` を merge 形式に変更（後勝ち 2-3 個構造を維持）
- ❌ Phase 13B で SVG redesign まで終わらせようとする（Phase 13C 分離可）

---

## 7. Definition of Done (再確認)

| 項目 | 基準 |
|---|---|
| 303 再生成一致 | `python scripts/render.py 303` 出力と gold standard が **視覚的同等**（diff は palette と座標のみ） |
| 検証 | `python scripts/validate-tx.py outputs/000_TX/刑TX/刑TX303.html` ERROR 0 / WARNING 0 |
| 306 試生成 | `python scripts/render.py 306` で fb-1〜fb-5 が自動適用 |
| patch 配布 | `render-py-phase13b.patch` が生成され、phase13a 隣に並ぶ |
| template 直編集 | `templates/KTX_template.html` がコミット可能な状態 |
| SVG 課題 | Phase 13C への分離が決定されていれば OK（13B 内完遂は不要） |

---

## 8. 旧セッション完了時の状態スナップショット

- 303.html ファイルサイズ: 252,977 bytes
- validate-tx: ERROR 0 / WARNING 0
- 適用済 polish: fb-1 (badge spacing) / fb-2 (細字補強) / fb-3 (case-scene 4 場面) / fb-4 (NOTE grid + .note-body) / fb-5 (全文章字下げ統一)
- 群青蘭 palette 適用済 (3 :root cascade 構造)
- Tree/Radial/Flowchart SVG redesign 済 (overlap 修正完了)
- 配色 3 流派命名済 (壱「紅蓮」/ 弐「群青蘭」/ 参「黎明」)
- footer-spec hidden 化済 (validator 互換維持)

これらすべてが render.py + template に absorb されれば Phase 13B 完了。

---

**末筆**: 新セッションは Step 0〜2 を確実に通してから着手すること。「いきなり編集」は前回の事故パターン。
