# セッション用プロンプト集（Phase 1〜3）

> 確定日 2026-10-18。各 Phase を **別セッション（Opus 5.5・effort high）** で回すための起動文。
> そのままコピーして貼る。各ブリーフは「読むもの／やること／やらないこと／完了条件／報告」の 5 点で閉じる。
> Phase 3 だけは最上位モデルで回す（内容執筆と正典の本文鋳造）。

---

## Phase 1：Lexia に試験プロファイルとコア分離を入れる（lexia リポジトリ・Opus）

```
lexia リポジトリで Phase 1（試験プロファイル導入＋抽出器/トラッカーの src/lib 分離＋data-qid）を実装して。
計画書＝ docs/patches/LXA_FEAT_019_EXAM_PROFILE_CORE_SPLIT.md（必ず最初に読む）。背景と契約＝
bar-exam リポジトリの docs/shoshi/00-master-plan.md と 01-kijutsu-html-contract.md §0・§3。

やること（この順・極小コミット）：
1. src/lib/examProfile.js を新設。BAR_PROFILE（id・subjects・prefix 正規表現・RX 表・sync 取込元・categories・
   features・storage 名）と getActiveProfile()（VITE_EXAM_PROFILE 既定 'bar'）。
2. questionMeta.js / barExamSync.js のハードコード表（科目接頭辞・RX_PREFIX_*・BAREXAM_REPO・txCodeFromPath・
   isCanonicalJxFileName）をプロファイル参照に置換。bar の出力は 1 バイトも変えない。
3. App.jsx 1,204〜3,035 行の素の抽出関数（extractCaseContext / parseLabeledReviewSegments / extractStmtMeta /
   extractArenaPremise / buildArenaQuizContext / extractReferencesFromHtml / extractQuizzesFromHtml /
   extractQuizMiniHtml / buildFallbackMiniHtml / extractClozeData）を src/lib/htmlExtract.js へ移動（import で戻す）。
   QUIZ_TRACKER_SCRIPT 文字列を src/lib/quizTracker.js へ移動。
4. data-qid：extractQuizzesFromHtml の id と トラッカー ensureQuizId の両方で data-qid を最優先、無ければ従来の位置キー。
5. テスト：npm run test:all PASS。examProfile と data-qid の node テストを scripts/test-exam-profile.mjs /
   test-stmt-keys.mjs 拡張で追加し package.json の test:logic に組み込む。

やらないこと：UI 変更・kx 枝（Phase 2b）・shoshi プロファイルの値（Phase 2b）・main への直接 push。

完了条件：test:all PASS／npm run build 成功／bar の挙動不変（取込・復習プール・肢キーが従来どおり）／
ブランチを push して draft PR。PR 本文に「移動した関数一覧」と「bar で変わらないことの根拠（テスト名）」を書く。
```

## Phase 2a：コンテンツリポジトリ shoshi-exam を bootstrap する（新規リポジトリ・Opus）

```
司法書士試験のコンテンツリポジトリ shoshi-exam を bar-exam から bootstrap して。
設計＝ bar-exam の docs/shoshi/00-master-plan.md と 02-content-repo-canonical.md（必ず最初に読む）。
記述式の契約＝ docs/shoshi/01-kijutsu-html-contract.md。

やること：
1. GitHub に xnhsky/shoshi-exam（private）を作り、02 §1 の構造を作る。
2. 02 §5 の表どおり bar-exam から canonical/scripts/prompts/docs を複製（git subtree ではなくコピー＋出自コミットを
   docs/provenance.md に記録）。
3. scripts/subjects.json（02 §2）を単一情報源にし、validate-tx-core.py の G14・check-duplicates.py・
   tx-v13-runner.ps1・new-tx-headless-v13.md の科目ハードコードを JSON 読み出しに置換。
4. 02 §4 の S1〜S4 を validate-tx-core.py に追加（S1 は tx_basis_roles.py に is-precedent 種別を足し、
   GENESIS-CARD.html に TX-BASIS-PRECEDENT の CSS 区画を加える）。
5. CLAUDE.md を 02 §6 の骨子で書く（bar-exam の規律文をコピーせず、必要な規律だけ縮約。刑法 corpus の実績や
   TJR-S/G/D/I の残件は書かない）。docs/canonical-lineage.md を新設（active 行＝TX v13.1.0 継承・HX/KX は Phase 3 待ち）。
6. 受入試験：inputs/000_TX/010_不動産登記法/ にダミー番号の PDF を 1 本置き（本物は OWNER PC から Drive 経由）、
   new-tx の headless 経路で 不登TX が二系統 validate PASS することを確認（本文品質は問わない・構造の疎通だけ）。

やらないこと：HX/KX の canonical 本文鋳造（Phase 3）・択一の本文執筆・bar-exam 側のファイル変更。

完了条件：validate-tx-core / check-duplicates / check-lexia-preflight が shoshi-exam 上で exit 0／
疎通用 不登TX が outputs に出る／master へ push（新規リポなので直接 master で可・以後は PR）。
報告に「bar-exam から複製したファイル数」「置換した科目ハードコードの箇所数」を書く。
```

## Phase 2b：SCRIBA ビルド変種（lexia リポジトリ・Opus・Phase 1 マージ後）

```
lexia リポジトリで Phase 2b（司法書士版 SCRIBA ビルド変種）を実装して。Phase 1（LXA_FEAT_019）がマージ済みであること。
設計＝ bar-exam の docs/shoshi/00-master-plan.md §1-1 と 01-kijutsu-html-contract.md §2-5・§2-9・§3。

やること：
1. SHOSHI_PROFILE を examProfile.js に追加（科目 11・接頭辞 正規表現は長い方優先・sync 取込元 xnhsky/shoshi-exam・
   folders＝outputs/ux/000_TX, outputs/000_TX, outputs/001_HX, outputs/002_KX, references・categories に HX/KX・
   features.kx=true・storage: IndexedDB 名 'scriba-studyrec'・localStorage 接頭辞）。
2. ビルド変種：VITE_EXAM_PROFILE=shoshi で dist-shoshi/ を出す npm script、wrangler.shoshi.jsonc（name: scriba）、
   deploy.yml のマトリクス（bar=lexia Worker／shoshi=scriba Worker・VITE_SUPABASE_* は shoshi 用 Secrets 名を分ける）、
   manifest/アイコン/タイトルをプロファイルから生成。
3. トラッカー kx 枝（.kx-app graded → 各 .kx-field の is-correct/is-incorrect を kind 'kxfield' quizId=data-qid で送信・
   二重送信防止・__lexiaPeek/__lexiaRestoring ゲートは共通 send()）。recordQuizAttempt の対象 kind に kxfield。
4. プールの想起型カード面（.kx-field-prompt / .kx-field-answer / norm=self の .kx-rubric）。
5. src/lib/kxNormalize.js（exact / date-cause / set / number / lines の正規化＝01 §2-5 表）＋
   references/kx-aliases.json の読込＋scripts/test-kx-normalize.mjs（テストベクタは shoshi-exam 側 kx_norm.py と共有する
   JSON を fixtures に置く）。
6. ライブラリ・科目カードで HX/KX を表示（bar では非表示）。

やらないこと：bar ビルドの挙動変更・KX の回答履歴復元（後日）・LLM 採点。

完了条件：bar/shoshi 両ビルドが成功／test:all PASS／shoshi ビルドが別 URL で起動し shoshi-exam（空でも可）を取込める／
draft PR。
```

## Phase 3：gold 3 点と STYLUS/THOTH の本文鋳造（shoshi-exam・最上位モデル）

```
shoshi-exam で Phase 3（gold）を作って。設計＝ bar-exam の docs/shoshi/02-content-repo-canonical.md §8 と
01-kijutsu-html-contract.md 全文。内容レビューは「執筆者本人の自己照合 1 回＋的を絞った一次確認（条文・先例・
登録免許税法）」で、確信の持てない先例は裁判所・法務局資料で確認してから書く。

順序：
1. 不登TX×5（二系統・組合せ型→350 方式・S1 先例カード・S2 法令階層）→ validate PASS → 1 問ずつ commit。
2. STYLUS.html の本文鋳造＋不登HX001（所有権移転（売買））→ validate-hx を書いて PASS → placeholder 契約を固定。
3. THOTH.html の本文鋳造＋不登KX001（現行法で解ける直近年度）→ kx-build.py と validate-kx を書いて PASS →
   SCRIBA 実機で採点→SM-2 に乗ることを確認（スクショを docs/shoshi/gold-evidence/ に）。
4. ユーザー承認を得てから prompts/new-hx-headless.md / new-kx-headless.md を書く（Phase 4 の入口）。

やらないこと：量産・合格ゾーン等の解説文の転載・一次確認なしの先例引用。
完了条件：gold 3 点が全ゲート PASS かつ実機で復習プールに乗る／docs/canonical-lineage.md の active 行を更新。
```
