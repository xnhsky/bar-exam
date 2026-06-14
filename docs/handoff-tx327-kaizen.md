# 引き継ぎ書 ── 刑TX327 コア再設計（統合解説＋横断コラム）

> 最終更新：2026-06-14 / セッション：Claude Code on the web → VS Code へ引き継ぎ
> ブランチ：`claude/keisatsu-tx327-kaizen-xz6c15`（push 済み・作業ツリー clean）
> 直近コミット：`bdee1d5 feat(tx): 刑TX327 コア記述ブロックを再設計（統合解説＋横断コラム試作）`

---

## 0. まず VS Code 側でやること

```bash
git fetch origin
git switch claude/keisatsu-tx327-kaizen-xz6c15   # 既にあれば
git pull origin claude/keisatsu-tx327-kaizen-xz6c15
python scripts/validate-tx-core.py outputs/tx/刑TX/刑TX327.html   # G1〜G26 ERROR0 を確認
python scripts/check-duplicates.py outputs                         # 重複なしを確認
# ブラウザで outputs/tx/刑TX/刑TX327.html を開いて読み心地を確認
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

対象ファイル：`outputs/tx/刑TX/刑TX327.html` のみ（骨子・spec・validator は未変更）。

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
grep -oE 'id="ref-[a-z0-9-]+"' outputs/tx/刑TX/刑TX327.html | sort | uniq -d
# backlink ターゲット欠落（MISSING が出なければOK）
for t in $(grep -oE 'href="#ref-[a-z0-9-]+"' outputs/tx/刑TX/刑TX327.html | sed 's/href="#//;s/"//' | sort -u); do
  grep -q "id=\"$t\"" outputs/tx/刑TX/刑TX327.html || echo "MISSING: $t"; done
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
| 試作対象 | `outputs/tx/刑TX/刑TX327.html` |
| コア骨子 | `canonical/GENESIS-CORE.html` |
| ディープ骨子 | `canonical/GENESIS-DEEP.html` |
| 仕様 | `spec/tx-v11.0.0-core.md` |
| 検証（コア） | `scripts/validate-tx-core.py`（G1〜G26） |
| 検証（別冊） | `scripts/validate-tx-deep.py`（D1〜D13） |
| 重複ゲート | `scripts/check-duplicates.py` |
| 生成コマンド | `.claude/commands/new-tx.md`（v11）/ `/deepen-tx` |
