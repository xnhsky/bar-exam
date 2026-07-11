# TX `_lex` 既存ファイル改修 実行計画（handoff・2026-07-11 確定）

> **これは何**：2026-07-11 のテンプレート監査3ラウンド（正典 gold 化・G61〜G64・oxgrid 配線）の後に残った
> **問題ファイル単位の改修**の実行計画。ユーザー確定方針＝**「刑法 360-445 を優先で改修、それ未満の旧版は TJR で消化」**
> ＋監査で判明した补正（v13.0.0 は TJR-R の対象外なので別パスが要る）を反映。
> **実行モデルは Opus 4.8 で可**（量産パイプラインは既に `--model claude-opus-4-8[1m]` ピン留め・ゲートが strict で守る）。
> 執筆規律＝author-once（[[feedback_lean_verification_author_once]]・執筆者本人が丁寧に1回＋機械ゲート＋的絞りWeb一次確認）。

## 前提（読むべき正典）

- 生成・改修規約：`.claude/commands/new-tx.md`（特殊型ガイド・写経元表・Phase 6 ゲート）／`spec/tx-v13.1.0-loopcard-core.md`
- 解説の書き方：`docs/tx-v12.2.1-inline-lock.md` §v13m（やさしい版 GIST・cross-cut 罠・🗝フック）・§v13n（不可侵ブロック）
- 特殊型 ○×健全性：`docs/lex-oxgrid-integrity-audit.md`（L1-L4・strict 化トリガー）
- **§7 遵守**：既存 `_lex` への band-aid・接ぎ木禁止。○×は常に「命題の真偽」（G60）。canonical/GENESIS-CARD が唯一の複製起点。

## 実行順序（A → B →〔C は常時並行〕→ D）

### パスA【最初に・4本】全○キーの distractor 化（学習実害の除去）

- **対象**：刑TX**089**(N=4)・**174**(N=6)・**218**(N=4)・**256**(N=6)＝v13.0.0・answer-key 全○
  （L4 退化＝「全部○と確認するだけ」で判別性ゼロ・SM2 弱点記録が機能しない。**現在配信中の実害**）。
- **やること（1本1パス）**：
  1. **distractor 差し替え**：一部の記述を典型的誤り（対立説・別条文・逆結論）の命題に書き換えて×にし、
     **○×混在キー**にする。写経元＝刑TX406(×○××○)/408/416/433（new-tx.md 実例表の「混在キー gold」行）。
     書き換えは **ox-stmt・.tx-inline-stmt-text・.syn-orig（正誤マーキング）・.tx-v13-verdict バッジ・
     data-correct-value・data-answer-key・data-brief-mark を全部同期**（ズレは G60/G63/G64 が ERROR で止める）。
     公式（`outputs/000_TX/...`）は本物の組合せ5択なので**触らない**。
  2. **v13.1.0 版アップ**：`python scripts/tx-lex-verdict-redesign.py`（土台注入）→ 規範核バッジ
     `.nb-badge-text`（転用可能な規範核1文・11〜14字）と `data-brief-mark`（印付き原文の要約版）を各記述で執筆 →
     `python scripts/tx-lex-sysmap-pbox.py`（親箱）→ `python scripts/tx-lex-v13-stamp.py`（版スタンプ整合）。
  3. **厚み直し**：§v13m A/C（やさしい版 GIST・cross-cut 罠）。gold＝刑TX362/436。256 は薄GIST5＋薄罠3で最多。
  4. **CSS 統一**：`python scripts/tx-lex-css-canonize.py --apply <file>`（正典 <style> へ載せ替え・palette 保持）。
- **検証（1本ごと・全部 strict）**：
  `validate-tx-core.py`（G1〜G64）／`check-tx-lex-engine.py <file>`／
  `check-lex-oxgrid-integrity.py <file>`（**L4 が消えること**）／`check-duplicates.py outputs`／
  `check-tx-v13m-depth.py <file> --detail`（薄さ自己照合）／静的サーバーで実機表示確認。

### パスB【優先帯・ユーザー指定】刑法 360-445 のアプデ

この帯は**既に全部 v13.1.0**（版移行は不要）。アプデの中身は2つだけ：

1. **薄GIST/罠の厚み直し（11ファイル・2026-07-11 時点）**：
   390(罠4)・392(GIST5)・396(GIST2,3,4,5)・398(罠3)・411(GIST2,3,5)・413(GIST3)・414(GIST4)・
   420(GIST1,2,4,5)・421(GIST1,3)・423(GIST3,5)・427(GIST2,3,4)。
   **リストは着手時に `python -X utf8 scripts/check-tx-v13m-depth.py outputs/ux/000_TX --detail` で再取得**
   （数値は腐る・実測が正）。§v13m の失敗シグネチャ表（薄い GIST＝verdict直開始の羅列／薄い罠＝結論言い換え）
   に沿って書き直し、作業後に depth を再実行して候補が消えたことを確認。誤爆（良質な簡潔版）は著者判断で除外可。
2. **CSS canonize の帯内展開**：`tx-lex-css-canonize.py --apply` を 360-445 へ。**適用後に型サンプルで実機確認**
   （標準5記述＋会話8穴埋め=381＋blank-mode=428 の3型は必ず開いて、正誤表・体系マップ・トグル・チップの
   表示崩れ 0・pageerror 0 を見る）。問題なければ `--check` の不一致が帯内 0 になる。

### パスC【常時並行】TJR（360 未満の旧版）

- 号令「**TJR処理 刑**」（または R だけなら `-Only R`）。純v11 帯（266本・全部ローカルPDFあり）を
  PDF から v13.1.0 で再生成。**旧v11帯の残欠陥（L2/L3/L4 の16件・ボタン潰れ・旧UI・古CSS）はここで全部消える**
  ＝個別パッチは二度手間なのでしない。
- runner は validate＋engine＋**oxgrid strict** を各問で通し、NG は commit しない（判別性は機械が強制）。

### パスD【B の後・19本】v13.0.0 残りの版アップ

- **対象**：125・290〜302（13本）・355〜359＝**TJR-R の対象外**（-Regen は v13 世代を SKIP・
  migration-targets §手順5）なので、**このパスを飛ばすと誰にも拾われず残る**。
- **やること**：パスA の手順2〜4 と同じ（distractor は不要・キーは既に混在）。290-302 帯は薄罠が集中して
  いるので厚み直しを同梱。**359 は canonical/GENESIS-CARD がほぼ完全実体なので、複製ベースで最安**
  （title/doc-header/footer の問題コードと genmeta を維持）。

## 完了条件と strict 化（機械判定可能）

1. `python -X utf8 scripts/tx-classify-type.py` で **v13.0.0＝0**・純v11＝0（刑法）。
2. `python -X utf8 scripts/check-lex-oxgrid-integrity.py outputs/ux` で **検出0**。
3. `python -X utf8 scripts/tx-lex-css-canonize.py --check` で **不一致0**。
4. → 2 が 0 になったら `check-lexia-preflight.py` の oxgrid 呼び出しから `--warn-only` を外して
   **strict 既定化**（`docs/lex-oxgrid-integrity-audit.md` §2 のトリガー・2026-07-11 明文化済み）。
5. → 3 が 0 になったら `check-tx-lex-engine.py` の CSS ドリフト可視化を**ブロッキング昇格**
   （`_run_css_canonize_advisory` のコメント参照）。

## ゲート早見（何が止めて・何が助言か）

| 層 | strict（ERROR で止まる） | advisory（表示のみ） |
|---|---|---|
| 単発 validate／pre-commit | G1〜G64（G60 極性・G61/G62 v13n・G63 三点整合・G64 バッジ⇄key矛盾 含む） | G56/G57 深さ・G59 XNAV |
| push 前 engine | G41〜G45・G50-G55・G58・G60〜G64・SNTIP・元号割れ・CORE/CARD 契約 | CSS ドリフト・oxgrid L2-L4 |
| 生成（runner／new-tx Phase 6／headless §5） | 上記＋ **check-lex-oxgrid-integrity（L1-L4）strict** | — |

## 禁止・注意（再掲）

- 旧 `_lex` を Read/Edit の起点にした接ぎ木・band-aid 禁止（§7）。厚み直し・distractor 化は**該当スロットの
  中身だけ**を書き換える（CSS/JS/class/DOM/節順は不変）。
- ○×は「提示文（命題）の真偽」固定。事例の帰結記号を answer-key に流用しない（§3・G60）。
- 判例は年月日を一次確認（非著名・下級審だけ的を絞って裁判所検索・百選等）。PDF 官製解説が一次資料
  （[[feedback_pdf_is_primary_cite_source]]）。
- 写経元の組合せ4本（089/174/218/256）は**パスA完了までは answer-key を写さない**（実例表の⚠参照）。
- 大量ファイルの一括 python 適用は CRLF 保持・atomic write・終了後 `find -size 0` 検査（過去事故：タイムアウト
  強制終了で 0 バイト空化）。
