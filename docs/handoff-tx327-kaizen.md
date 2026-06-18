# 引き継ぎ書 ── 刑TX327 コア再設計（統合解説＋横断コラム）

> 最終更新：2026-06-15 / セッション：VS Code（Claude Code）で UI/ビジュアル調整中
> ブランチ：`claude/keisatsu-tx327-kaizen-xz6c15`
> 直近コミット：`773313e docs: 刑TX327 再設計の引き継ぎ書を追加（VS Code 続行用）`
> **⚠️ 作業ツリーに未コミットの UI 変更あり**（下記「6. 2026-06-15 セッション」）。
> プレビュー駆動の微調整は **VS Code のまま継続が最適**（ローカル HTML を Chrome で開き、
> 編集→`Ctrl+R` リロードで即確認。web チャットは 177KB の貼り直しになり非推奨）。

---

## 0. まず VS Code 側でやること

```bash
git fetch origin
git switch claude/keisatsu-tx327-kaizen-xz6c15   # 既にあれば
git pull origin claude/keisatsu-tx327-kaizen-xz6c15
python scripts/validate-tx-core.py outputs/000_TX/001_刑法/刑TX327.html   # G1〜G26 ERROR0 を確認
python scripts/check-duplicates.py outputs                         # 重複なしを確認
# ブラウザで outputs/000_TX/001_刑法/刑TX327.html を開いて読み心地を確認
```

依存：`pip install beautifulsoup4`（validator が使用）。

---

## 1. 背景（受験生フィードバック）

刑TX327（v11 LOOP-CORE・コア）の解説が「まとまりがなく、全部読もうとするとどこを
読めばいいか分からない」。真因は **PART B 各記述ブロックで同じ内容を散文で3回**
言い直していたこと（`.choice-summary` ＋ `📖解説原文` ＋ `👨‍🏫教授①②`）。
高速周回教材として致命的だった。

ユーザー合意（AskUserQuestion 回答済み）：
1. 解説原文と教授カードは **完全1本化**
2. 新設コラムは **問題末に横断コラム1つ**
3. 適用範囲は **まず327で試作 → 確認後に骨子展開**（← いまここ。骨子展開は未着手）

---

## 2. 327 に加えた変更（実装済み・検証通過）

対象ファイル：`outputs/000_TX/001_刑法/刑TX327.html` のみ（骨子・spec・validator は未変更）。

### 2-1. PART B 各記述ブロックの新構成
維持：`.verdict`（答え1文）／`.choice-points`（足ポイント）／`.sub-card original`（記述原文＋点線）。
**置換**：`📖解説原文` ＋ `👨‍🏫教授①②` の2カード → **🎯統合解説 `.sub-card.synthesis` 1枚**。
- `.syn-lead`【一言で】→ `.syn-path` の【筋道】①条文・文言 ②保護法益 ③あてはめ ④結論
  （`.syn-concl`）→ `.syn-image`【イメージ】（直感の喩え1行）。
- 教授③イメージ深掘り・④あてはめ誤読は **ディープ別冊に温存**（コア/ディープ分担厳守）。
- 記述ア〜エの4枚すべて実装済み。

### 2-2. 横断・比較・罠コラム（新設）
PART B 末尾（`#cross-column-sec`・`#basis` の直前）に `.cross-column` を1つ追加：
1. 🔗 刑×民横断（256条客体性 × 民193条 2年回復請求）対照表＋決め手＋横断の型
2. 📊 本問4記述を貫く「客体性の4つの軸」比較表（ア=由来/ウ=直接領得/エ=本犯の犯罪性/イ=存続期間）
3. ⚠️ 間違いやすいポイント（罠①〜③）＋追求権で束ねる覚え方

### 2-3. CSS（`<style>` 内・§13-bis / §13-ter として追加）
`.sub-card.synthesis` `.syn-lead` `.syn-tag` `.syn-path` `.syn-step` `.syn-concl`
`.syn-image` ／ `.cross-column` `.col-block` `.col-lead` `.col-key` `.col-type` `.col-warn`。
既存パレット変数（`--accent`/`--accent-soft`/`--accent-darker`/`--mid`/`--light`/
`--border-mid`/`--bg-dark`/`--paper` 等）のみ使用（palette 外 hex は緑系 #1b5e20/#2e7d32 と
金系 #b8860b/#d9a300 の semantic のみ）。

### 2-4. リンク健全性（重要・展開時も死守）
basis セクションの逆参照チップ（`.ref-backlinks .rb-chip`）が PART B 内の
`id="ref-..."` 15件を指す。explanation/professor を消す際、**全15 ID を統合解説へ移設**して
リンク切れゼロを確保済み。検証コマンド：

```bash
# 重複 ID（出力が空ならOK）
grep -oE 'id="ref-[a-z0-9-]+"' outputs/000_TX/001_刑法/刑TX327.html | sort | uniq -d
# backlink ターゲット欠落（MISSING が出なければOK）
for t in $(grep -oE 'href="#ref-[a-z0-9-]+"' outputs/000_TX/001_刑法/刑TX327.html | sed 's/href="#//;s/"//' | sort -u); do
  grep -q "id=\"$t\"" outputs/000_TX/001_刑法/刑TX327.html || echo "MISSING: $t"; done
```

---

## 3. 検証ゲートの注意点（展開時）

`scripts/validate-tx-core.py`（G1〜G26）で 327 は ERROR/WARNING 0。関連ゲート：
- **G21** 禁止句（組合せ導出・選択戦略語彙）：統合解説・コラム本文に持ち込まない。
- **G22** choice-points 規律：「本記述は誤り/正しい」「記述[ア-オ]は」「正解は肢」を入れない。
- **G24** 参考条文判例の深度：basis の完全プロファイルは従来どおり（コラムとは別物）。
- 現状 validator は explanation/professor の存在を必須にしていない（だから synthesis 置換でも PASS）。

---

## 4. 次のステップ（未着手・要ユーザー確認後に実施）

ユーザー判断「327で良ければ骨子展開」。OK が出たら：

1. **骨子反映**：`canonical/GENESIS-CORE.html` の PART B シェルを
   synthesis 構成へ差し替え＋`.cross-column` の空シェルを追加（本文は空文字列の雛形）。
2. **spec 改訂**：`spec/tx-v11.0.0-core.md` 第2項の PART B 順序記述
   （現「解説原文 → 根拠リンク → 教授①②」）を「🎯統合解説（一言で→筋道①〜④→イメージ）
   → 根拠リンク → 🔗横断コラム」へ更新。第3項 choice-points 規律は維持。
3. **validator 追加**：synthesis 必須（`.sub-card.synthesis` が記述数ぶん存在）、
   旧 explanation/professor の混在禁止、横断コラム存在（任意 or WARNING）を G27 等で追加。
4. **コマンド/プロンプト**：`.claude/commands/new-tx.md`・`prompts` の工程記述を同期。
5. **既存197問（v10）には触れない**。v11 既存生成物への遡及は別途方針決め。

### 設計上の保留・調整候補（327で詰める対象）
- 【イメージ】の濃さ（コアは1行に抑制／深掘りはディープ）。
- 横断コラムの分量（3ブロックは多いか。最小は刑×民横断1本＋罠）。
- 足ポイント（choice-points）の型化：今回は「位置維持・内容温存」。①規範コア
  ②決め手・限定句 ③ひっかけの3行に定型化する案は未適用（ユーザー再確認待ち）。

---

## 5. 関連ファイル早見

| 種類 | パス |
|---|---|
| 試作対象 | `outputs/000_TX/001_刑法/刑TX327.html` |
| コア骨子 | `canonical/GENESIS-CORE.html` |
| ディープ骨子 | `canonical/GENESIS-DEEP.html` |
| 仕様 | `spec/tx-v11.0.0-core.md` |
| 検証（コア） | `scripts/validate-tx-core.py`（G1〜G26） |
| 検証（別冊） | `scripts/validate-tx-deep.py`（D1〜D13） |
| 重複ゲート | `scripts/check-duplicates.py` |
| 生成コマンド | `.claude/commands/new-tx.md`（v11）/ `/deepen-tx` |

---

## 6. 2026-06-15 セッション：UI/ビジュアル調整（未コミット・受験生フィードバック反映）

iPad プレビューのスクショ指示に沿って 327 の**見た目だけ**を調整（本文ロジック・論点は不変）。
対象は `outputs/000_TX/001_刑法/刑TX327.html` のみ。`validate-tx-core.py` G1〜G26＝ERROR/WARNING 0、
`check-duplicates.py`＝重複なしを維持。**validator はこれらの class 文言/存在を要求しないので
自由に微調整して良い**（ただし G8 配色文言・G13 本文 5-gram・G19/G21/G22 は従来どおり死守）。

### 6-1. バッジの英語化（THE GIST 系）
- `.syn-tag`：`一言で`→**THE GIST**（4）／`イメージ`→**INTUITION**（4）
- `.col-warn`：`罠①②③`→**TRAP 1/2/3（エ/イ/ウ）**／`.col-type`：`横断の覚え方`・`横断の型`→**THROUGH-LINE**（2）
- 地の文・節タイトルの「横断/罠」は**保持**（バッジのみ英語化）。

### 6-2. 記述カード冒頭の要約文 `.choice-summary` を削除（全4カード）
verdict＋肢ポイント＋統合解説と重複していたため撤去（CSS 規則は未使用のまま残置・無害）。

### 6-3. ORIGINAL を最上部へ移動＋一文解説を箱内に（全4カード）
- `.sub-card.original` を **verdict 直下（`.choice-points` より前）** へ移動。
- 箱内＝**原文 →(点線 `.orig-gist` の border-top)→ `<p class="orig-gist">` 一文解説**。
- verdict 見出しは説明節を削り `✗ ×（誤り）`/`✓ ○（正しい）` に簡潔化（説明は一文解説へ集約）。
- 新 CSS：`.sub-card.original .orig-gist` ／ `.orig-gist-tag`（`一文解説` バッジ）。

### 6-4. SYNTHESIS の筋道 ①〜④ を美装（核心の調整ポイント）
- 番号：丸囲み文字 `①②③④` → **プレーン数字 `1〜4`**（`.syn-step` 円内で明瞭。視認性の主因）。
- 見出し：`.syn-step + strong`（隣接セレクタで**見出し strong だけ**を特定）を
  **小型・淡色バッジ**化（`--accent-soft` 地＋`--accent-darker` 字＋`--accent` 細枠・`font-size:.8em`）。
  見出し直後の全角コロン「：」は16か所とも除去（バッジ直後に本文が続く形）。
- 整列（ずれ対策）：**絶対配置をやめ `padding-left + text-indent` のぶら下げ**に変更。
  番号は行頭、本文は段下げ。番号円と見出しバッジは `vertical-align:middle` で芯合わせ。
- ④結論 `.syn-concl`：**緑の淡色帯**（番号円・バッジも緑）で締めのメリハリ。
- 色の流れ：THE GIST(淡violet帯) → 1〜3(violet数字＋淡バッジ・点線区切り) → 4結論(緑帯) → INTUITION(金帯)。

### 6-5. 該当 CSS の場所（`<style>` 内）
`.sub-card.original` 群（`.orig-gist`/`.orig-gist-tag` を直後に追加）／
`.syn-path` `.syn-step` `.syn-step + strong` `.syn-concl`（synthesis 美装ブロック）。

### 6-6. 次にやること（プレビュー駆動の微調整・候補）
- 数字円/バッジのサイズ・色・余白の最終詰め（メリハリの好みに合わせて）。
- 同じ仕上げを **PART A の ox-grid 表・「間違いやすいポイント(TRAP)」コラム**へ広げるか判断。
- OK 確定後に **1問1コミットで commit/push**（CLAUDE.md §9）。**確定するまで未コミットのまま微調整**。
- 骨子（GENESIS-CORE）への横展開は「4. 次のステップ」の通り（UI も含めるか別途決定）。

### 6-7. 環境メモ
- ブランチ切替時、未追跡の 刑JX044 TTS（1〜16・本ブランチ未管理）が衝突 →
  `C:\Users\xnrg2.DESKTOP-5664QR6\bar-exam-tts-backup\刑JX044\` へ退避済み。
  `jx-v4-loopfold` に戻る際は `outputs/002_TTS/001_刑法/刑JX044/` へ戻す。
- 依存：`pip install beautifulsoup4`。プレビューは `file:///C:/Users/xnrg2.DESKTOP-5664QR6/bar-exam/outputs/000_TX/001_刑法/刑TX327.html` を Chrome で。
