---
description: 深掘り別冊 -deep.html を core HTML から後追い生成（v11.0.0 LOOP-CORE DEEP：GENESIS-DEEP baseline・教授③④＋判例完全プロファイル＋フローチャート＋PART C）
---

既存の v11 コア（`{接頭辞}{NNN}.html`）に対し、深掘り別冊 `{接頭辞}{NNN}-deep.html` を後追い生成する。

> **v11.0.0 LOOP-CORE DEEP 経路（2026-06-13 確定）**：正典 `spec/tx-v11.0.0-core.md`（v0.4・第5項）。
> 深掘り別冊は**全問では作らない**。Lexia の誤答データが解禁条件を満たした問題にだけ作る（導き書 鉄則②）。
> - 唯一の起点：`canonical/GENESIS-DEEP.html`。検証：`scripts/validate-tx-deep.py`（D1〜D13）。
> - 一次情報源は**対応する core HTML**（問題文・記述・正解・解説・参考条文判例の要約を内蔵）。PDF 不要。
>   判例の事案・判旨原文が要るときのみ Drive「抽出PDF」原本を参照。
> - 別冊の構成：D-1 記述別補講（教授③④）／D-2 判例完全プロファイル／D-3 総合フローチャート／D-4 PART C。
>   **PART D（12問ドリル）は存在しない**。体系ツリー・放射マップは core にあるので別冊に重複させない。

引数：問題番号（例：`341`）または core HTML のパス（例：`outputs/000_TX/刑TX/刑TX341.html`）

---

## 解禁条件（これを満たした問題だけ生成・導き書 §3-5/§3-6）

(a) 2周目以降に同じ記述を繰り返し誤答した／(b) 弱点克服帳に同一論点が反復登場する／(c) 直前期の弱点総ざらい。
解禁の根拠（どの記述・論点が弱いか）は Lexia の肢キー記録（`{問題ID}#stmt-{記述}`）・弱点克服帳から得る。

## 必須手順

### Phase 0：前提確認

0a. **対応する core HTML の存在を確認**（`outputs/000_TX/{科目TX}/{接頭辞}{NNN}.html`）。
    無ければ**中断**（別冊の単独生成は禁止＝`/new-tx` で先にコアを作る・validate-tx-deep D12）。
0b. **既存の `-deep.html` があるか確認**。あれば上書き可否を確認。
0c. template 流用禁止：`outputs/*/` の既存 HTML を起点に `cp`/`Read`/`Edit` しない。起点は GENESIS-DEEP のみ。

### Phase 1：core HTML 読解（一次情報源）

1. **core HTML を Read** し次を把握：問題文・【見解】・記述ア〜オ・正解（記述○×）・各記述の解説原文・
   choice-points（論点コア）・参考条文判例（条文文言＋保護法益＋制度趣旨／判例の一行ルール＋射程要点）・
   配色（`:root{}` の CSS 変数）。**別冊は core と同じ配色を使う**（同一問題の続き）。
2. **判例の事案・判旨原文が core に無い**ため必要なら Drive「抽出PDF」原本を参照（任意・無ければ core 要約から執筆）。

### Phase 2：ファイル名・出力先

3. core と同フォルダ・同接頭辞で `{接頭辞}{NNN}-deep.html`（例：`outputs/000_TX/刑TX/刑TX341-deep.html`）。

### Phase 3：GENESIS-DEEP の clone と本文初期化

4. **`canonical/GENESIS-DEEP.html` を Read**（別冊生成の唯一の起点）。
5. **対象ファイル名でコピー作成**（Write 経由 or bash `cp`。前面 PowerShell の Copy-Item はブロック）：
   `cp canonical/GENESIS-DEEP.html outputs/000_TX/{科目TX}/{接頭辞}{NNN}-deep.html`
6. **コピー直後に本文を空文字列で初期化**（content-independence）。空化対象：
   - deep header の h1／exam-meta／back-link 先（core ファイル名へ）
   - D-1（#d-1）記述別補講の `.sub-card.professor` 本文（③④）
   - D-2（#basis）各 `.basis-card-body` の判例完全プロファイル本文（【事案】【判旨】【補足】）
   - D-3 フローチャート（flow-svg）内 `<text>`（座標・class 据置）
   - D-4 PART C（#c-1〜#c-7）各 section 本文（table 含む）
   - footer-spec

### Phase 4：section-by-section 鋳造（各 Edit 30〜50KB・1メッセージ50KB超禁止）

#### 4a. HEAD `:root{}`：core と同一配色を反映（同一問題の別冊）。
#### 4b. deep header：h1「{接頭辞}{NNN} 深掘り別冊 ── {テーマ}」／back-link を `{接頭辞}{NNN}.html` へ。
#### 4c. D-1 記述別補講（教授③④）
各記述（ア〜オ）について、core の教授①②の続きとして **③イメージで掴む（例え話）・④あてはめ＋誤読パターン・
他肢対比** を執筆（`prof-num` 3,4＋`prof-analogy`＋`warning`＋`cross-link`）。core にある①②は繰り返さない。
**禁止句（組合せ導出・選択戦略）は別冊でも書かない（D9）。**
#### 4d. D-2 判例完全プロファイル（#basis）
core の判例「一行ルール＋射程要点」を、**【事案】【審級経過】【判旨原文引用】【補足・反対意見】**の
ラベル付き完全プロファイルへ展開（`<strong>【事案】</strong>` 等・`.judgment-text`）。条文は要件効果の網羅一覧・
体系的位置・立法経緯まで。**ここが完全プロファイルの唯一の置き場（D7 必須）。**
#### 4e. D-3 総合フローチャート（flow-svg）
本問の判断フロー（decision diamond／chip／end）を flow-svg の text に。座標・class は GENESIS-DEEP 据置。
class は定義済みのみ（独自命名は黒塗り・D6）。
#### 4f. D-4 PART C（C-1〜C-7）
C-1 体系図解説／C-2 概念比較・全肢俯瞰／C-3 cross-grid（関連科目接続）／C-4 学説対立（主要2説・
why-adopted/why-not-adopted）／C-5 総合フロー解説（4e と接続）／C-6 重要判例詳細／C-7 memory-item（3層 priority）。
#### 4g. footer-spec
feature-tag 先頭＝**`TX v11.0.0 LOOP-CORE DEEP`**。続けて genesis-deep-baseline／
prof-34-full-profile-flow-partc／no-part-d／content-independence／jp-prefix-naming。

### Phase 5：SVG 重なり機械検査（flow-svg）

7. flow-svg の `<rect>`/`<ellipse>` の bounding box 全ペア AABB 衝突判定（衝突 0・マージン16px以上）。
   衝突時は viewBox 拡張を最優先（[[feedback-svg-box-overlap]]）。

### Phase 6：検証と配信

8. **`python scripts/validate-tx-deep.py <出力ファイル>`** を実行。
9. **D1〜D13 ERROR 0 件確認**（特に D2 構造・D3 flow-svg/tree・radial 不在・D7 完全プロファイル・D8 PART D不在・
   D10 feature-tag・D12 コアファイル存在）。WARNING は配信可。
10. ERROR 修正 → 視覚確認 → `present_files`。

### Phase 7：git コミットで永続化（§9）

11. `git add outputs/000_TX/{科目TX}/{ファイル名}-deep.html` → 本問単位 commit（例：`feat(刑TX): 刑TX341 深掘り別冊を生成`）→ push。
12. `present_files` に commit hash 併記。

---

## 鉄則

- **起点は `canonical/GENESIS-DEEP.html` のみ**。core や他 outputs/*.html を template 参照しない。clone 直後に本文空化。
- **core が無ければ生成しない**（別冊の単独生成禁止・D12）。一次情報源は core HTML（PDF 不要）。
- **完全プロファイル【事案】【判旨】【補足】は別冊 D-2 にのみ置く**（core には置かない＝役割分担）。
- **体系ツリー・放射マップは別冊に作らない**（core 専用・D3）。flow-svg は別冊専用。
- **PART D（12問ドリル）を作らない**（廃止・D8）。第一原理（記述であって肢ではない）・禁止句は別冊でも遵守（D9）。
- 1メッセージ 50KB 超の Write/Edit 禁止。中断時も GENESIS-DEEP ＋ core から続行。

$ARGUMENTS
