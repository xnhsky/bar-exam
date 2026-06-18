# Phase 14 - 311 gold skeleton WIP 引継ぎ

**作成日**: 2026-05-27
**状態**: 30% 完了・WIP（work-in-progress）保存済
**経緯**: ユーザー指示「303-gold をスケルトン構造にして AI 判断で実行」に基づく 311.html フルリライト中

---

## 1. 背景・経緯

### 元の課題
JSON-render 経路（render.py 経由）で 311.html を生成しても 303-gold quality に到達せず。ユーザーから繰り返し品質指摘あり：
- basis のジャンプリンクが乏しい
- 体系ツリー / マインドマップ が見切れ・重なり
- C-3 で生 HTML テキストが表示される（escape バグ）
- 学説対立のレイアウトが違う
- 総合フローチャートが見切れ

JSON 経路の改善（render.py 修正・basis_link_card 追加・手書き SVG 等）でも視覚的に gold 同等に届かないため、ユーザー指示で方針転換：

> **303-gold をスケルトン構造にして AI 判断で 311 内容を埋め込む**

### 採用アプローチ
1. `_experimental/刑TX303-gold.html` (258KB / 4243行) をコピーして 311.html の基底に
2. 全 4243 行を section-by-section に 311 内容で置換
3. HTML/CSS/SVG 座標構造は 303-gold のものを継承
4. 出題形式：**single-choice-5 を保持**（303 は ox-grid-5 だが 311 PDF 原型に従う）→ PART A/B は再構築

---

## 2. 完了した作業（このセッション・約30%）

### 2-1. HEAD 部分
- `<title>`：刑TX303 → 刑TX311（不法原因給付と横領・共通H29-16）
- 配色パレット：弐 群青蘭 → **壱 紅蓮 (P1 #8A1F3A)** に全変数差替済
  - --accent / --mid / --light / --base / --soft / --bg-dark / --accent-3 / --accent-soft / --border-mid / --kp-text-color
  - --hl-* / --tan-* / --rank-* / --freq-* （全派生色）
  - --recall-incorrect / -light も紅蓮系へ

### 2-2. HEADER 部分
- doc-header: 刑TX303 → 刑TX311
- exam-badge 4 枚: 刑法 / 司法試験 / H29 / 共通H29-16
- h1: `No.311 ── 不法原因給付と横領（共通H29-16）`
- theme-tag 8 個: 横領罪 / 委託物横領罪 / 不法原因給付 / 民法708条 / 刑法252条1項 / 他人の物 / 反射的効果論 / 最大判昭45.10.21
- exam-meta: 正答率 85 / 難度 ★☆☆ / 配色 壱 紅蓮 (Crimson Lotus)
- toc-row: 肢1〜肢5 リンク

### 2-3. PART A (A-1 問題文 + A-2 解答エリア)
**完全再構築（ox-grid-5 構造 → single-choice-5 構造）**

A-1 問題文：
- instruction: 「次の【見解】に関する後記アからオまでの各【記述】のうち、正しいものの組合せは、後記1から5までのうちどれか。」
- case-description: 1 case-scene (【見解】= 横領罪肯定の民刑独立論文)
- 【記述】5 項目（ア〜オ）
- 参照条文：民法708条（blockquote.statute スタイル）
- 【組合せ】5 項目（1: アエ / 2: アオ / 3: イウ / 4: イエ / 5: ウオ）

A-2 解答エリア：
- `<div class="answer-area" data-correct-value="5" data-answer-type="single" data-explanation="...">`
- 5 ボタン（answer-slot 形式・1〜5）
- reveal-answer-btn + answer-feedback

### 2-4. PART B - 肢1（アエ・誤・両方虚像射撃）
完全 311 化・約 115 行：
- header-block: badge "1" / verdict-incorrect / choice-summary
- sub-card original: 「ア　エ」
- sub-card explanation: ア・エ両方が虚像射撃である分析
- sub-card basis-link: gold-style chip 3 個（刑252 / 民708 / 最判昭23.6.5）
- sub-card professor: 4 prof-heading
  - ポイント
  - 考え方の道筋（3段落）
  - イメージで掴む（弓道の標的・3段落・prof-analogy + scene-title）
  - あてはめ + warning + cross-link
- choice-points (ol with 3 li)
- 中間 inline ref-* id 付与: ref-law-708-101, ref-case-saihan-s23-6-5-101 等

### 2-5. PART B - 肢2（アオ・誤・虚像+実像混在）
完全 311 化・約 115 行：
- header-block: badge "2" / verdict-incorrect / choice-summary（混在構成の罠）
- 全 sub-card 構造同様
- explanation: オは有効批判だがアは虚像射撃で組合せ全体は誤り
- basis-link: chip 3 個（最大判昭45.10.21 / 最判昭23.6.5 / 民708）
- professor 4 prof-heading 完備
- 部分正解の罠 warning + 肢1との接続 cross-link
- 中間 inline ref-* id: ref-case-saidai-s45-10-21-201/202/203, ref-law-708-201/202, ref-law-252-201 等

---

## 3. 残作業（次セッション・約70%）

### 3-1. PART B - 肢3〜肢5（3 sections・各 ~75-115 行）
| 肢 | 組合せ | 判定 | キー論点 |
|---|---|---|---|
| 肢3 | イ　ウ | 誤 | イ=方向逆転 + ウ=実像狙撃の混在 |
| 肢4 | イ　エ | 誤 | イ=方向逆転 + エ=虚像射撃 = 誤批判 × 2 |
| 肢5 | ウ　オ | **正解** | ウ=民法708条衝突 + オ=反射的効果論 = 実像狙撃 × 2 完全組合せ |

### 3-2. A-3 basis セクション（~100 行）
現状：303-gold の 9 cards（詐欺・横領・盗品関与等の混合体系）
要変更：311 の 5 cards へ差替
- statute: 刑法252条1項 横領罪
- statute: 民法708条 不法原因給付
- case: 最判昭23.6.5（百選Ⅱ63・本問主題判例）
- case: 最大判昭45.10.21（百選Ⅱ73・記述オ前提）
- statute: 刑法235条 窃盗罪（盗品窃取均衡論参照条文）

各 card には back-link で choice 側 ref-* id への navigation chip を付与。

### 3-3. SVG 3 種（座標枠は 303 のまま、テキストのみ差替）

#### mindmap-tree SVG (~70 行)
viewBox `0 0 1500 820` 維持。テキスト差替：
- L0: 「刑法252条1項 横領罪」
- L1: 「①委託に基づく自己の占有」「②他人の物（本問核心）」「③不法領得意思の発現」
- L2: 6 個別論点（占有概念 / 委託信任関係 / 民事所有権論 / 構成要件論 / 領得意思 / 領得行為）
- L3 (active=橙): 民刑独立論【見解】/ 民法708条本文 / 反射的効果論 / 民事返還権要件不要
- issue-box: 「【見解】への5批判の方向性評価」+「実像狙撃 vs 虚像射撃 vs 方向逆転」

#### mindmap-radial SVG (~120 行)
viewBox `0 0 1500 1180` 維持。テキスト差替：
- center: 「【見解】への5批判の方向性評価」（ellipse 180×75）
- 7 主要枝 (radial 8 等分配置の 7 + issue branch):
  - 記述ア（誤・虚像射撃）・記述イ（誤・方向逆転）・記述ウ（正・実像狙撃）
  - 記述エ（誤・虚像射撃）・記述オ（正・実像狙撃）
  - 【見解】の核心命題・判例実務（重畳的論理）
- issue branch（橙）: 本問の論点（批判方向性 3 類型）
- 正解表示（最下部）: 「正解：5（記述ウ・オが正しい批判＝実像狙撃 × 2）」

#### flowchart_v2 SVG (~80 行・C-5 内)
viewBox `0 0 1200 1280` 維持。テキスト差替：
- START: 「START：批判の方向性評価」
- decision 4 個（菱形）:
  - ① 前提とする【見解】像は正確か？
  - ② 矛盾指摘の方向は論理的に正しいか？
  - ③ 波及帰結を正面から指摘しているか？
  - ④ 反射的効果論前提で『他人の物』性を否定？
- chip 4 個: 記述ア・エ（虚像射撃）/ 記述イ（方向逆転）/ 記述ウ（実像狙撃）/ 記述オ（実像狙撃）
- end-fail: 不適切批判（批判不成立）
- end-success: 正しい批判（ウ・オ）＝『実像狙撃 × 2』完全組合せ（正解：肢5）

### 3-4. C-1 〜 C-7 (5+ sections・合計 ~340 行)

#### C-1 体系的解説
303現状: 詐欺・横領・盗品の罪間関係の体系
要変更: 横領罪『他人の物』性の体系的整理 + 判例実務の重畳的論理

#### C-2 概念比較・全肢俯瞰
303現状: 3 罪の概念比較表
要変更: 肯定説 vs 否定説の対比 + 5肢の質的分類表

#### C-3 関連の深い科目との接続 (cross-card 形式)
303現状: 民法 / 不法原因給付 / 刑法総論
要変更: 民法708条 / 刑法252条 / 盗品窃取均衡論（3 cross-card）

#### C-4 学説対立 (theory-detail-grid)
303現状: 刑法独自占有説 vs 民法統一説
要変更: 民刑独立論（【見解】）vs 反射的効果論（記述オ前提）

#### C-5 総合フローチャート
SVG は §3-3 で差替済前提

#### C-6 関連問題・出題傾向
303現状: 詐欺・横領・盗品関連
要変更: 学生発言型（310） / 委託物横領 / 業務性ある横領 / 横領後の横領 / 盗品関与罪

#### C-7 三層構造記憶
303現状: 3 priority層
要変更: 311の Priority A/B/C （核心命題・正解組合せ・誤批判3類型・判例射程）

### 3-5. PART D - 12 drill blocks (~80 行)
303現状: 12 ○× drill（詐欺・横領・盗品テーマ）
要変更: 311の 12 ○× drill（不法原因給付・民刑独立論・反射的効果論テーマ）
- ○:× = 6:6 balanced を保持
- 各 drill の question/answer/explanation を 311 内容に差替

### 3-6. footer-spec (~30 行)
303現状: 33 feature-tag + override_pattern: P2 + palette-strategy
要変更: 311 メタ（パターン P1 / 紅蓮）

---

## 4. 引継ぎファイル一覧

### 4-1. WIP HTML（次セッション開始時の起点）
- **`_experimental/刑TX311-wip-gold-skeleton.html`**：現在の WIP（30%完了・260KB・4210行）
- これを `outputs/000_TX/刑TX/刑TX311.html` にコピーして作業継続

### 4-2. 参考ファイル
- `_experimental/刑TX303-gold.html` (258KB / 4243行)：構造リファレンス
- `inputs/tx-pdfs/311.pdf` (385KB)：問題原文
- `problems/311.json` (90KB)：JSON 経路の構造化データ（参照用）
- `docs/GOLD-QUALITY-RECIPE.md`：gold pattern 仕様
- `docs/PHASE-13C-COMPLETION-HANDOFF.md`：Phase 13C 引継ぎ

### 4-3. 関連 commit / git 状態
**未 commit（明示指示なきため保留）:**
- `scripts/render.py` (gold-style basis-link + theory-detail-grid CSS 注入)
- `problems/310.json` (gold-quality lift)
- `problems/311.json` (新規・gold fixes 全反映)
- `docs/GOLD-QUALITY-RECIPE.md` (新規)

---

## 5. 次セッションの開始手順

```powershell
# 1. WIP を outputs に復元
cp _experimental/刑TX311-wip-gold-skeleton.html outputs/000_TX/刑TX/刑TX311.html

# 2. 現状確認
wc -l outputs/000_TX/刑TX/刑TX311.html  # 4210行のはず
grep -n 'id="choice-' outputs/000_TX/刑TX/刑TX311.html  # choice-1, 2 が 311 / choice-3,4,5 が 303

# 3. 残作業を順次実行（推奨順序）
# step 1: 肢3 (イウ・誤) リライト
# step 2: 肢4 (イエ・誤) リライト  
# step 3: 肢5 (ウオ・正解) リライト（最重要・最詳細）
# step 4: A-3 basis 5 cards リライト
# step 5: mindmap-tree SVG テキスト差替
# step 6: mindmap-radial SVG テキスト差替
# step 7: C-1〜C-7 リライト（5+ sections）
# step 8: C-5 flowchart SVG テキスト差替
# step 9: PART D 12 drill blocks リライト
# step 10: footer-spec リライト
# step 11: ブラウザで視覚確認

# 4. validate-tx は skip（render.py 経由でないため）
# 視覚確認のみで品質判定
```

---

## 6. 重要な注意事項

### 6-1. render.py 経由禁止
- 本作業中は `python scripts/render.py 311` を**絶対に実行しない**
- 実行すると JSON-render 結果が 311.html を上書きし、WIP 作業が全消失

### 6-2. 構造要件
- HTML/CSS は 303-gold のものを継承（変更しない）
- inline ref-* id は連番管理（重複避ける・例: ref-law-708-101 から 201, 301, 401, 501）
- 各 choice の sub-card 構造（original / explanation / basis-link / professor / points / back-to-top）は維持
- gold-style basis-link `<div class="back-link-row"><a class="back-link">→ label</a>` を継続

### 6-3. S78 content independence
- KTX301 由来禁止語句に注意（「業務上横領罪」→「業務性ある横領罪」など）
- 303-gold の問題固有テキスト（甲・乙・丙・本件不動産・大連判大11.12.15）は**全て 311 内容に差替**必須
- 残存すると content leakage 違反

### 6-4. 視覚確認重視
- validate-tx.py は 303-gold ベース HTML を直接検査するため、構造規約は緩い
- ブラウザで開いて「303-gold 同等のレイアウト・色合い・密度」を最終判定
- ユーザーは 303-gold との視覚比較で gold quality を判定する

---

## 7. 推定残工数

| 残セクション | 推定 Edit 数 | 推定時間 |
|---|---|---|
| 肢3・4・5 | 3 大 Edit | 30-45 分 |
| A-3 basis | 1 大 Edit | 10-15 分 |
| mindmap-tree SVG | 1 中 Edit | 10 分 |
| mindmap-radial SVG | 1 中 Edit | 15 分 |
| C-1〜C-7 | 5 中 Edit | 25-35 分 |
| C-5 flowchart SVG | 1 中 Edit | 10 分 |
| PART D drill | 1 中 Edit | 15 分 |
| footer-spec | 1 小 Edit | 5 分 |
| **合計** | **14 Edit** | **2-2.5 時間** |

次セッションで集中投入すれば完遂可能。
