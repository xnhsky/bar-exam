# Phase Y-4-bis-impl (戦略 η) HANDOFF ── 新セッション継続用

> **作成日**: 2026-05-26 (旧セッション終了時)
> **目的**: 旧セッションで開始した戦略 η（AI 直接生成方式で 303.html 再構築）を新セッションで継続するための完全ハンドオフ
> **HEAD**: `8408439` (Phase Y-4-bis-impl Commit 2-sexies 完了状態)

---

## 0. 新セッション初動

新セッションで以下を user が入力：

```
docs/PHASE-Y-4-bis-eta-HANDOFF.md を読んで戦略 η の続きを進めて
```

CC は本ドキュメント全文を読み、context を再構築してから残作業に着手する。

### 0.1 状態整理（旧セッション終了時の退避処理済）

- `outputs/tx/刑TX/刑TX303.html` = **HEAD = 8408439 時点の v9.4.0 HTML に復元済**
  - `python scripts/render.py 303` で再生成した状態
  - validate-tx: ✅ ERROR 0 / WARNING 0
  - title: `刑TX303 - 詐欺、横領及び盗品等（共通H26-20）`
  - feature-tag: TX v9.4.0 COMPLETE-BASELINE
  - これは「次善の baseline」（戦略 ε / Commit 2-sexies 由来の v9.4.0 で、戦略 η の理想形ではない）

- `outputs/tx/刑TX/刑TX303-eta-wip.html` = **戦略 η の WIP 退避ファイル**（210,868 bytes・git untracked）
  - 309 baseline base + 記述ア書き換え済（Step 1-3 + Step 4(1/5)）
  - **新セッションではこのファイルを参照し、Step 4(2-5/5) 以降の作業を再開する**
  - 推奨: WIP ファイルを再び `outputs/tx/刑TX/刑TX303.html` に上書きコピーして作業継続
    ```bash
    cp "outputs/tx/刑TX/刑TX303-eta-wip.html" "outputs/tx/刑TX/刑TX303.html"
    ```

---

## 1. 戦略 η の本質（必読）

- **render.py を経由しない**「AI 直接 HTML 執筆方式」
- 309.html（恐喝罪・司法予備R7-10・ox-grid-5・v9.1.0 MINDMAP）を **baseline template** として採用
- 309 → 303 (詐欺・横領・盗品等罪・H26-20) への**コンテンツ全面書き換え**作業
- 配色は v9.3.0 PALETTE-MULTI-VARIANT の **群青蘭 (azure-orchid)**（P2・seed=303 で自動選択済）

### v9.4.0 = 313 baseline + v9.2.0 加算 + v9.3.0 加算

| 加算 | 内容 |
|---|---|
| v9.1.0 baseline (309) | 構造美・CSS・key-phrase-box / warning / cross-link / choice-points 等 |
| v9.2.0 加算 6 件 | density-v2 (1,150+ chars) / theory-deep-dive / palette-derivatives / tree-mindmap / radial-mindmap / flowchart-v2 |
| v9.3.0 加算 1 件 | PALETTE-MULTI-VARIANT (27 サブパレ・seed 選択) |

---

## 2. 「過ちを繰り返さない」5 原則（契約事項）

| # | 原則 |
|---|---|
| 1 | `:root{}` cascade 後勝ち方式（merge 禁止・2-3 個構造維持） |
| 2 | 既存関数・既存ファイルは保護・新規追加で対応 |
| 3 | JSON schema は v9.1.0 流儀（structured） |
| 4 | 段階導入（v9.2.0 完了 → v9.3.0） |
| 5 | 検査先行（TDD-like） |

---

## 3. 旧セッションの進捗（完了部分）

### 3.1 git 履歴（HEAD = 8408439）

```
8408439 fix(v94): 313 baseline 構造化 - professor 領域を v9.1.0 シンプル形式に統一 (Commit 2-sexies)
89b197b fix(v94): professor 見出しを pill バッジ化 (Commit 2-quinquies)
f70bc38 fix(v94): professor 領域 デザイン readability 改善 (Commit 2-quater)
b5f9376 fix(v94): PART B 上左 artifact 修正 (Commit 2-ter)
785e780 fix(v94): SVG class CSS rules post-process injection (Commit 2-bis)
0174b69 feat(content): 刑TX303 v9.4.0 first-light (Phase Y-4-bis-impl Commit 2)
2c963a7 feat(v94): Phase Y-4-bis-impl-A 検査先行 + 基盤拡張
```

戦略 η の作業は**git untracked**（commit していない・working tree のみ）。

### 3.2 working tree の現状

`outputs/tx/刑TX/刑TX303.html` (約 207 KB) の状態：

- ✓ **Step 1**: ヒーロー部書き換え完了
  - title: `刑TX303 ｜ 共通H26-20 詐欺・横領及び盗品等の罪間関係`
  - doc-header: `刑TX303`
  - exam-badge × 4: 📚刑法 / 📝司法試験 / 📅H26 / 🔢共通H26-20
  - h1: `No.303 ── 詐欺・横領及び盗品等の罪間関係（共通H26-20）`
  - theme-tags × 8: 詐欺罪（246条）/ 不動産詐欺の既遂時期 / 横領罪（252条1項）/ 不可罰的事後行為 / 幇助の時的限界 / 盗品等有償譲受け罪（256条2項）/ 不法原因給付（民708条）/ 刑法独自占有説
  - exam-meta: 正答率 50% / 難度 ★★☆ / パターン P2 群青蘭（azure-orchid）

- ✓ **Step 2**: PART A 問題文書き換え完了
  - 指示文: `次の【事例】に関する後記アからオまでの各【記述】を判例の立場に従って検討し、正しい場合には1を、誤っている場合には2を選びなさい。`
  - 事案 4 段落（甲がAから不動産取得 → 乙へ転売 → 丙が代金管理 → 丙が馬券で費消）
  - 5 記述（ア〜オ）原文

- ✓ **Step 3**: PART A-2 解答エリア書き換え完了
  - data-correct-value="12212"
  - data-answer-type="ox-grid"
  - data-explanation: 正解解説（記述ア〜オ各々の判例規範あてはめ）

- ✓ **Step 4 (1/5)**: PART B **記述ア** (詐欺既遂時期・大連判大11.12.15) 完了
  - choice-summary / sub-card.original / sub-card.explanation / sub-card.basis-link / sub-card.professor (ポイント・考え方の道筋・key-phrase-box・prof-analogy・あてはめ・warning・cross-link) / choice-points 全て 303 用に書き換え済

- ✓ **配色**: :root{} を群青蘭テーマに完全変更済
  - --accent: #3C828F (青緑) / --mid: #A989B8 (紫) / --base: #F4F1E8 (温暖クリーム微紫)
  - 派生色・rgb triple も連動済

### 3.3 残作業（必須）

#### Step 4 (2-5/5): 記述イ〜オ書き換え

各記述ごとに以下を書き換える（記述ア の構造を踏襲）：

**記述イ** (× 誤・横領罪不成立 = 不可罰的事後行為)
- 判定: × 誤
- 中心論点: 詐欺既遂後の処分は不可罰的事後行為 → 横領罪は別罪として成立しない
- 中心判例: なし（学説 + 一般理論）・刑法 246条 / 252条
- 中心条文: law-246 / law-252
- 記述原文: `甲が本件不動産の乙への所有権移転登記を行った行為について、別途、横領罪が成立する。`

**記述ウ** (× 誤・幇助犯不成立)
- 判定: × 誤
- 中心論点: 幇助の時的限界 = 正犯の実行行為以前 or 同時に限る
- 中心条文: law-62 (刑法62条1項)
- 記述原文: `乙には、本件不動産の自己への所有権移転登記が完了した時点で、詐欺既遂罪の幇助犯が成立する。`

**記述エ** (○ 正・盗品等有償譲受け罪成立)
- 判定: ○ 正
- 中心論点: 盗品等有償譲受け罪（256条2項）の要件 = ①盗品性 ②認識 ③有償取得
- 中心条文: law-256 (刑法256条2項)
- 記述原文: `乙には、本件不動産を取得したことについて、盗品等有償譲受け罪（刑法256条2項）が成立する。`

**記述オ** (× 誤・委託物横領罪成立)
- 判定: × 誤（記述自体は「成立しない」とするため誤り）
- 中心論点: 刑法独自占有説 = 民法上の所有権帰属と独立に「他人の物」性を判断
- 中心判例: case-saiko-s23-6-5 (最判昭23.6.5・百選Ⅱ63事件)
- 関連判例: case-saiko-s39-1-24 / case-saiko-s45-10-21
- 中心条文: law-252 / law-mn-708 (民708条 不法原因給付)
- 記述原文: `丙が現金1000万円を自己の借金返済に充てて費消した行為について、丙には、委託物横領罪は成立しない。`

#### Step 5: basis section 書き換え

309 の basis-card 7 件（条文 + 判例）を 303 用 9 件に置換：

**条文 5 件**:
- law-246: 刑法246条 詐欺
- law-252: 刑法252条1項 横領
- law-256: 刑法256条 盗品等
- law-62: 刑法62条1項 幇助
- law-mn-708: 民法708条 不法原因給付

**判例 4 件**:
- case-dairen-t11-12-15: 大連判大11.12.15（不動産詐欺既遂時期）
- case-saiko-s23-6-5: 最判昭23.6.5（百選Ⅱ63事件・刑法独自占有説）
- case-saiko-s39-1-24: 最判昭39.1.24（共有関係補強判例）
- case-saiko-s45-10-21: 最大判昭45.10.21（民法708条反射効）

各 basis-card には back_links (記述本文への戻りリンク) を含める。

#### Step 6: mindmap-tree SVG 再設計（体系ツリー）

横領罪体系（252-254条）+ 詐欺罪（246）+ 盗品等（256）の罪間関係を表現する 4 階層ツリー：

- L0: 詐欺・横領・盗品等の罪間関係
- L1: 詐欺罪 / 横領罪 / 盗品等罪 / 幇助・事後関与
- L2: 各罪の要件
- L3: 本問 5 記述のマッピング

309 の tree-svg を参考に group/text/rect で構築。色は群青蘭 (accent #3C828F / mid #A989B8) を使用。

#### Step 7: mindmap-radial SVG 再設計（論点放射状）

中心: 本問の罪間関係
放射枝: 詐欺既遂時期 / 不可罰的事後行為 / 幇助時的限界 / 盗品等罪要件 / 刑法独自占有説

#### Step 8: flowchart-v2 SVG 再設計（判定フロー）

5 段階判定フロー：
1. 取得段階（甲のA欺罔）→ 詐欺罪成否
2. 第一処分段階（甲→乙売却）→ 横領罪 vs 不可罰的事後行為
3. 関与段階（乙の認識下売買）→ 幇助 vs 盗品等罪
4. 代金管理段階（丙の受託）→ 占有関係
5. 代金処分段階（丙の馬券費消）→ 横領罪成否（刑法独自占有説）

#### Step 9: PART C 1-7 書き換え

309 の PART C を 303 用に：
- C-1 体系・記憶
- C-2 概念比較
- C-3 関連科目接続（民法 177条 / 民法 708条 / 共犯論）
- C-4 学説対立（刑法独自占有説 vs 民法統一説・theory-deep-dive）
- C-5 総合フローチャート（Step 8 と連動）
- C-6 関連問題・出題傾向（H21-19 / H24-21 / H30-22 等）
- C-7 三層構造記憶（必修3 + 推奨2 + 体系3 の 3 層）

#### Step 10: PART D drill 12 問書き換え

309 の drill 12 を 303 用 12 問に：

1. 不動産詐欺既遂時期（○・大連判大11.12.15）
2. 動産詐欺との既遂時期の差異（×）
3. 不可罰的事後行為論（○）
4. 詐欺既遂後の横領罪不成立（○）
5. 幇助の時的限界（○・刑法62条1項）
6. 実行行為終了後の関与（×）
7. 盗品等有償譲受け罪の要件（○・256条2項）
8. 盗品性の認識（○）
9. 刑法独自占有説（○・最判昭23.6.5）
10. 民法708条と刑法評価（○）
11. 罪間関係の整理（○）
12. 5罪体系俯瞰（○）

#### Step 11: footer-spec を v9.4.0 用に拡張

309 の v9.1.0 MINDMAP 17 tag を v9.4.0 COMPLETE-BASELINE の **38 tag** に拡張：

```html
<span class="feature-tag">TX v9.4.0 COMPLETE-BASELINE</span>
<!-- v9.2.0 加算 (31 件) -->
<span class="feature-tag">genkei-skeleton</span>
... (v9.2.0 DEEP-DIVE の 31 tag 全て)
<span class="feature-tag">P2</span>
<span class="feature-tag">palette-strategy: 同系統調和</span>
<!-- v9.4.0 識別 (4 件) -->
<span class="feature-tag">v94-hero-extra</span>
<span class="feature-tag">v94-choice-summary</span>
<span class="feature-tag">v94-sub-card-basis-link</span>
<span class="feature-tag">v94-mindmap-section</span>
<!-- v9.3.0 加算 (3 件) -->
<span class="feature-tag">palette-multi-variant</span>
<span class="feature-tag">hsl-derivation</span>
<span class="feature-tag">sub-palette: 群青蘭 (azure-orchid)</span>
```

---

## 4. 必読リソース

| ファイル | 用途 |
|---|---|
| `/tmp/313-baseline/刑TX313.html` | v9.1.0 baseline の構造美参考（multi-select-2 形式・参考のみ） |
| `outputs/tx/刑TX/刑TX303.html` | **現在の作業中ファイル**（309 base + 記述アまで 303 化済） |
| `problems/303.json` | 303 のコンテンツデータ（chapter/section/case/basis/part_c/choices/mindmap_*/theory_deep_dive/drill_blocks 全 27-29 keys） |
| `scripts/validate-tx.py` | 検証スクリプト（spec_version 自動判定・S95-S97 v9.4.0 検査含む） |
| `git show f633cd5:outputs/tx/刑TX/刑TX309.html` | 309 baseline 原本（参考） |

---

## 5. 群青蘭 (azure-orchid) サブパレ定義

```
spec: v9.3.0 PALETTE-MULTI-VARIANT
category: P2 翠彩 (Verdant Spectrum)
sub-palette: 群青蘭 (azure-orchid)
seed: 303 (problem.id)

アンカー 3 色:
  --accent: #3C828F  (青緑)
  --mid:    #A989B8  (紫)
  --base:   #F4F1E8  (温暖クリーム微紫・v9.1.0 baseline #fbf3ed を群青蘭風に微調整)

HSL 派生 (v9.3.0 spec §32-5-2 適用):
  --accent-light:   #5FA2AE  (accent から H+0 / S-8 / L+13)
  --accent-darker:  #317885  (accent から H+0 / S+5 / L-4)
  --accent-soft:    #829FA4  (accent から H+0 / S-25 / L+18)
  --accent-soft-2:  #8EB5BC  (accent から H+0 / S-15 / L+25)
  --mid-warm:       #BF98C7  (mid から H+8 / S+5 / L+6)
  --mid-cool:       #A28EB3  (mid から H-8 / S-5 / L+0)
  --mid-soft:       #D6CDDA  (mid から H+0 / S-10 / L+20)
  --surface-tint:   #A2BDC2  (accent から H+0 / S-20 / L+30)

RGB triples (rgba() 用):
  --accent-rgb: 60,130,143
  --mid-rgb:    169,137,184

absolute 派生 (全 sub-palette 共通):
  --neutral-cream: #F4EDE0
  --contrast-warm: #D97A4F
  --contrast-cool: #6A8AA8
```

---

## 6. 完了基準

全 Step 完了後、以下を満たすことを確認：

1. **validate-tx**: ✅ ERROR 0 / WARNING 0
2. **HTML size**: 200-280 KB 範囲
3. **:root{} count**: 2-3 個（v9.1.0 baseline + 群青蘭）
4. **feature-tag**: 38 件（v9.4.0 spec）
5. **choice-section**: 5 個（記述ア〜オ）
6. **basis-card**: 9 個（条文 5 + 判例 4）
7. **ref-case + ref-stat**: 80+ 件（相互リンク密度・313 並み）
8. **TODO stub 残数**: 0
9. **SVG**: tree / radial / flow 3 個（群青蘭着色）

---

## 7. 完了後の commit + push

```bash
git add outputs/tx/刑TX/刑TX303.html docs/PHASE-Y-4-bis-eta-HANDOFF.md
git commit -m "feat(v94): 刑TX303 v9.4.0 完全再構築 (戦略 η・309 baseline + 群青蘭)"
git push origin master
```

---

## 8. user 要望事項チェックリスト（screenshot 11 項目への対応）

完了確認時に以下が改善されていることを目視確認：

| # | 要望 | 対応 Step |
|---|---|---|
| 1 | 問題文を読みやすく・薄く・背景色 | Step 2（PART A）+ 309 baseline CSS |
| 2 | 論文マーク・重要ラインマーカー | 全 Step で ron-mark / exam-mark / case-emphasis を多用 |
| 3 | basis ジャンプリンク機能 | Step 5（basis） + 各 sub-card.basis-link |
| 4 | 教授解説 readability | Step 4・309 baseline CSS（prof-num + prof-heading + prof-analogy 等） |
| 5 | warn / cross-link | Step 4 各 choice で warning + cross-link box を含める |
| 6 | KEY フレーズ | Step 4 各 choice で key-phrase-box を含める |
| 7 | 肢ポイントまとめ統合 | Step 4 各 choice 末尾の choice-points |
| 8 | 条文・判例相互リンク密度 | 全 Step で ref-case / ref-stat 多用（80+ 件目標） |
| 9 | tree / mindmap 構造 | Step 6, 7（手書き SVG 再設計） |
| 10 | flowchart 可読性 | Step 8（手書き SVG 再設計） |
| 11 | 運用鉄則・出題傾向 readability | Step 9 (PART C-5 / C-6) で構造改善 |

---

## END OF HANDOFF
