# Phase 13C — SVG 3 種 redesign + 残課題 HANDOFF

> **作成日**: 2026-05-26（Phase 13B 完了直後）
> **目的**: Phase 13B handoff §3-8 で明示的に分離された SVG 3 種（tree / radial / flowchart）の overlap・接続線欠落・不格好 を auto_layout 関数の algorithm 改善で解消する。あわせて Bug-2（場面タイトル α 化）と Bug-8（306.json v9.4.0 昇格）を整理する。
> **HEAD**: `761c44c` (Phase 13B Bug-1 fix 完了状態)

---

## 0. 新セッション初動

新セッションで user が以下を入力：

```
docs/PHASE-13C-SVG-REDESIGN-HANDOFF.md を読んで Phase 13C を進めて
```

CC は本ドキュメント全文を読み、**まず現状の auto_layout 関数 3 件と現在の SVG 出力例（303.html）を観察してから** algorithm 改修に着手する。**いきなり関数を書き換えない**。

---

## 1. 背景：Phase 13B で残った視覚問題

Phase 13B (`b9ac4f3` + `761c44c`) では fb-1〜fb-5 CSS + 群青蘭 palette + footer hidden 化を成功させたが、user の視覚 sanity（2026-05-26 23:30 頃の 28 枚スクショ）で以下 4 点が「不完全・不格好」と指摘された：

1. **体系ツリー（mindmap_tree）**: L3 ノード（10+ 個）が画面下部で重なり合い、接続線が見えない／消えている。viewBox 1100×600 に対し L3 ノード数が多すぎる。
2. **論点マインドマップ（mindmap_radial）**: 中央楕円から放射する主要枝・sub-nodes が散らばっており、放射構造（spoke + ring）が成立していない。接続線（branch lines）が見えない／斜めに通っているだけ。
3. **総合フローチャート（flowchart_v2）**: 4 decision diamond の YES/NO 分岐 chip が diamond と重なっている。末端 5 つ（success 1 + fails 4）が下部で密集してラベル相互に被っている。
4. **Bug-2 場面タイトル**: Phase 13B では γ 方式（「場面 1」「場面 2」… の機械タイトル）で実装。user は α 方式（意味のあるタイトル：例「不動産の詐取」「乙への転売」「丙の代金受領」「丙の馬券費消」）を期待していた。

これらは Phase 13B handoff §3-8 末尾で「Phase 13C に分離するのが現実的」と明記されていた。

---

## 2. ゴール (Definition of Done)

| 項目 | 基準 |
|---|---|
| 体系ツリー視覚 | L3 ノード重なりゼロ・接続線が全て描画される・viewBox 自動拡大が機能 |
| マインドマップ視覚 | 中央 → 主要枝 → sub-nodes の 3 層放射構造が視認できる・接続線描画 |
| フローチャート視覚 | decision diamond と YES/NO chip が重ならない・末端 5 個が水平配置で重ならない |
| Bug-2 α 化 | 303.json に `case.scenes: [{title, body}]` を追加・render.py が α 優先で render |
| Bug-8 検討 | 306.json を v9.4.0 へ昇格させる方針判断（実装は 13C スコープ外でも OK） |
| 検証 | 303 / 306 ともに validate-tx.py ERROR 0 / WARNING 0 維持 |
| 視覚確認 | 新スクショで上記 3 SVG の崩れが解消していること（user 確認必須） |
| commit | Phase 13C 各 fix を独立 commit（Bug-3 / Bug-4 / Bug-5 / Bug-2 / Bug-8 別） |

---

## 3. 修正対象詳細

### 3-1. Bug-3: 体系ツリー SVG（auto_layout_tree）

**関数位置**: `scripts/render.py:598-695` (`auto_layout_tree`)

**現状の問題**:
- viewBox は max_per_layer / depth で 4 段階に自動拡大するが、L3 ノード 10+ 個では `1100×600` か `1100×700` 程度で gap が約 100px しか取れない。各 L3 ノードのテキストは 4-8 文字あるため box width 100px 前後で必要、文字サイズ次第で隣接 box と重なる。
- 接続線（lines）は parent_idx ベースで生成するが、ノード box の bounding rect ではなく中心点 (x,y) ベースで line 端点を計算しているため、box 内側を line が貫通して見えなくなる場合がある。
- L2 (7-box の例：303.html では「詐欺罪」「横領罪」など罪種別) も同様に幅不足で密集する。

**改修案**:
1. viewBox 幅を node 数に応じて動的拡大：`w = max(1100, max_per_layer * 130)` のような線形スケール
2. L3 nodes 数が 9 以上の場合は 2 段組み（odd-index は上段、even-index は下段）に折り返す
3. ノード box 寸法（width × height）を node の text 文字数から推定し、その bounding rect の上下辺で接続線端点を補正
4. 接続線が複数同じ親から出る場合、親 y+box_h/2 の同一 y から fanout（複数子に向かう均等放射）

**現状の出力例**: outputs/000_TX/001_刑法/刑TX303.html 内 `<section id="mindmap-tree">` 周辺 viewBox `0 0 1100 600` か 700

**参考スクショ**: 303/スクリーンショット 2026-05-26 223222.png（L3 が下部で完全に重なっている）

---

### 3-2. Bug-4: 論点マインドマップ radial（auto_layout_radial）

**関数位置**: `scripts/render.py:698-755` (`auto_layout_radial`)

**現状の問題**:
- `V92_RADIAL_BRANCH_POSITIONS` の 7 つの既定座標を順に使うが、303.html の branches 数が 7+ ある場合に座標不足で 中心に重なる。
- sub_nodes は branch から放射方向に `90 + (j-mid)*40` でオフセットするが、複数 branch が近接していると sub_nodes 同士が衝突する。
- 接続線（branch line・sub_node line）が描画されていない（出力 HTML の `<line>` タグが少ない）。auto_layout_radial は座標は決めるが line を**生成していない**ことが原因。`render_mindmap_radial_v92` 側で line 描画は行うが、auto_layout で算出した座標を `branch.line_*` 等に注入していない。

**改修案**:
1. 中心楕円 (cx_center=550, cy_center=450) から各 branch までの line を `lines` 配列として auto_layout 内で生成
2. 各 branch から sub_nodes へも放射状に line 生成
3. branch 座標は `V92_RADIAL_BRANCH_POSITIONS` を使わず、branches 数から角度を等分配（`angle_i = 2π * i / N`）で再計算
4. sub_nodes は branch を中心とした扇形（branch から外側に向かう方向）で配置

**参考スクショ**: 303/スクリーンショット 2026-05-26 223224.png（box が散らばっていて中央楕円との接続が見えない）

---

### 3-3. Bug-5: 総合フローチャート（auto_layout_flowchart）

**関数位置**: `scripts/render.py:757-844` (`auto_layout_flowchart`)

**現状の問題**:
- decisions[] の YES/NO chip の `yn_pos` は `yes_x=540, no_x=360` 固定。diamond の cx は 450（中央）なので、yes chip と no chip が diamond と被る。
- end_fails の cx 計算は `200 + i*250` で 4 ヶ所均等だが、viewBox=900 では 200/450/700/950 となり最後 (950) が画面外に出る。
- end_success の cx=450 と end_fails の最初 (cx=200) が斜めに重なる可能性。

**改修案**:
1. YES/NO chip の x 座標を diamond cx ± 100 (diamond の右下・左下) に固定し、chip y を diamond cy + box_h/2 + 20 にして diamond の外に出す
2. viewBox 幅を `max(900, 250 * (n_fails+1) + 200)` 程度に拡大して end_fails の最右端が画面内に収まる
3. end_success は中央上に、end_fails は別行（end_success より 80px 下）に水平配置で 4 ヶ所均等
4. decision → chip → end_box の接続線を auto_layout 内で生成

**参考スクショ**: 303/スクリーンショット 2026-05-26 223245.png（4 diamond は OK だが下部 brown 末端 box が密集）

---

### 3-4. Bug-2: 場面タイトル α 化

**関連箇所**: `scripts/render.py:2710-2754` （CASE_BODY slot 構築）

**現状の実装**: γ 方式 = paragraphs index から「場面 N」の機械タイトル生成。
**目標**: α 方式 = JSON 側に `case.scenes: [{title, body}]` を持ち、render.py がそれを優先する（既に実装済・分岐は完了）。残作業は **JSON 側に scenes を追加**。

**作業**:
1. problems/303.json の `case.paragraphs` (4 個) を `case.scenes` (4 個 + title) に変換
   - 場面 1 → タイトル「不動産の詐取（甲 vs A）」、body は既存 paragraph[0]
   - 場面 2 → 「乙への転売（甲→乙の詐欺取得物処分）」
   - 場面 3 → 「丙の代金受領（甲の指示による）」
   - 場面 4 → 「丙の馬券費消（横領）」
2. 既存 `case.paragraphs` は temporarily 残しても OK（render.py は scenes 優先）。完了後に削除。
3. 再生成 → 303 hero 直下の case-scene カード上段にタイトル表示確認

---

### 3-5. Bug-8: 306.json v9.4.0 schema 昇格

**動機**: 306 は v9.2.0 で生成されており、user のスクショ確認で「303 の初期作成段階レベル」と指摘された。具体的に欠落しているのは：
- 4 個の exam-badge（📚刑法 / 📝司法試験 / 📅R7 / 🔢共通R7-4）→ v9.4.0 hero-extra のみ
- theme-tags（8 個程度のチップ群）→ v9.4.0 hero-extra のみ
- case-scene カード化（v9.4.0 でしか動かない my Phase 13B 実装）
- footer-spec hidden 化（v9.4.0 only）

**作業候補**:
1. **A 案 minimum**: 306.json の `"spec_version": "v9.2.0"` → `"v9.4.0"` に変更し、必要な v9.4.0 fields (theme_tags, exam_year, etc.) を追加
2. **B 案 full content rewrite**: 306 を v9.4.0 density-v2 + mindmap-tree 等 完全実装に書き直し
3. **C 案 skip**: Phase 13C は SVG fix に集中、306 昇格は Phase 13D に分離

推奨は **C 案 skip** （13C scope は SVG fix だけにする）。306 は別 phase で個別対応。

---

## 4. 実装ワークフロー（推奨手順）

```
Step 0. (新セッション初動) このファイル + render.py auto_layout_* 関数 + 303.html 該当 SVG を確認
Step 1. python scripts/render.py 303 で現状 SVG を保存 → /tmp/303-svg-before.html
Step 2. Bug-3 (体系ツリー) auto_layout_tree を改修
  2-A. viewBox 動的拡大ロジック
  2-B. ノード box bounding rect 推定
  2-C. 接続線端点補正
  2-D. python scripts/render.py 303 → 視覚確認（user スクショ依頼 or 自分で grep）
Step 3. Bug-4 (radial) auto_layout_radial を改修
  3-A. 等角度分配
  3-B. branch line / sub_node line を auto_layout 内で生成
  3-C. render_mindmap_radial_v92 と整合確認
Step 4. Bug-5 (flowchart) auto_layout_flowchart を改修
  4-A. yn_pos を diamond cx±100 へ
  4-B. viewBox 幅拡大
  4-C. end_fails 水平配置
Step 5. Bug-2 (303.json case.scenes 追加)
Step 6. validate-tx.py で 303 / 306 ERROR 0 / WARNING 0 維持確認
Step 7. user に再スクショ依頼 → 3 SVG の崩れ解消を視覚確認
Step 8. 各 Bug 独立 commit
Step 9. Phase 13C 完了 commit
```

---

## 5. 必読ファイル（新セッション開始時）

1. **本ドキュメント全文**
2. `docs/PHASE-13B-RENDER-PY-HANDOFF.md`（Phase 13B 文脈・特に §3-8 SVG 分離の判断）
3. `scripts/render.py`:
   - 行 598-844: auto_layout_tree / auto_layout_radial / auto_layout_flowchart
   - 行 846-: render_mindmap_tree / render_mindmap_radial_v92 / render_flowchart_v2
4. `outputs/000_TX/001_刑法/刑TX303.html`（現状 SVG 出力・改修前 baseline）
5. `problems/303.json`（mindmap_tree / mindmap_radial / flowchart_v2 の JSON 構造例）

参考スクショ（user 提供・git untracked）:
- `303/スクリーンショット 2026-05-26 223222.png` - 体系ツリー overlap
- `303/スクリーンショット 2026-05-26 223224.png` - radial 散乱
- `303/スクリーンショット 2026-05-26 223245.png` - flowchart end-box clustering

---

## 6. 絶対禁止事項（CLAUDE.md §7 由来 + 本 Phase 固有）

- ❌ `outputs/000_TX/001_刑法/刑TX303.html` の本文・解説文字列を template / render.py にコピーすること（AP-42 / S78 違反）
- ❌ `auto_layout_*` 関数の既存呼び出し位置（`render_mindmap_tree` 冒頭等）を変更すること（後方互換性破壊）
- ❌ SVG fix のために validate-tx.py の検査をゆるめること（S80-S91 はそのまま）
- ❌ render.py を 1 メッセージで 50KB 超出力（API socket error 予防）
- ❌ Phase 13C で 306.json v9.4.0 化（B 案 / 13D へ分離推奨）

---

## 7. Phase 13B からの引継ぎ事項

### 7-1. gold standard 不在問題（継続）

Phase 13B 開始時、handoff §1 が前提とした 252,977 bytes の gold standard 303.html が消失していた。Phase 13B は handoff §3 spec 記述を権威として absorb 作業を完遂したが、視覚同等性の判定は user スクショ依頼でのみ可能。

→ Phase 13C も同様に **gold なし** で進める。user に再スクショ依頼するサイクルで判定。

### 7-2. eta-wip ファイル（参考）

`outputs/000_TX/001_刑法/刑TX303-eta-wip.html` (210,868 bytes) は戦略 η（AI 直接生成）の WIP。Phase 13C では参照しなくて OK（render.py 経路に集中）。

### 7-3. 8 templates 共通 CSS

Phase 13B で `scripts/_phase13b_propagate_templates.py` を作成し、8 templates すべてに fb-* CSS が伝播済。Phase 13C で template CSS を更に変更する場合、同様の伝播スクリプトを書くこと。

---

## 8. 完了 commit テンプレート

```
fix(render): Phase 13C - SVG 3 種 (tree/radial/flowchart) overlap 解消

303.html の視覚 sanity で指摘された SVG 3 種の崩れを解消：
- auto_layout_tree: viewBox 動的拡大 + 接続線端点補正
- auto_layout_radial: 等角度分配 + branch/sub_node line 自動生成
- auto_layout_flowchart: yn_pos diamond 外配置 + end_fails 水平配置
- 303.json: case.scenes 追加で α 方式タイトル化

検証: 303 / 306 ともに validate-tx.py ERROR 0 / WARNING 0 維持。
306 の v9.4.0 schema 昇格は Phase 13D へ分離。

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```

---

**末筆**: Phase 13B → 13C の引継ぎは「SVG 3 種は handoff §3-8 で分離済」が明示的なので scope 拡大しない。ただし auto_layout 関数の algorithm 改修は地味に重く、user の視覚チェックサイクルが必要。新セッションは Step 0 を確実に通してから着手すること。
