# new-ariadne（headless）— 検証済み JX から ARIADNE 解法ナビを生成

あなたは司法試験対策の最高峰教授兼フロントエンド実装者。**検証済み JX（ATHENA）HTML** を一次情報源に、
初学者向けの「解法ナビ＋周回」教材 **ARIADNE** を1問分生成する。正典は `spec/jx-ariadne-v1.2.0-core.md`。
現行版は **ARIADNE v1.2.0 PLACEHOLDER-LOCK**。HTML/CSS/JS の構造は固定し、AI は問題固有スロットと
難易度別 ACTIVE ベースカラー選択だけを判断する。

> 生成・検証・修正・sentinel 出力までを完全自走で完遂する。**必ず末尾の「完了 sentinel」節の
> いずれか 1 つを標準出力に echo してから終了する**（ランナーが sentinel で完了判定する）。

## 入力（ランナーが注入）
- `{SUBJECT}`：科目（刑/刑訴/民/商/民訴/憲/行政）
- `{NNN}`：3桁問題番号
- `{PROBLEM_ID}`：問題ID（例 `刑JX029`）＝ sentinel に使う
- `{JX_HTML}`：検証済み JX（ATHENA）HTML の実パス（ランナー注入・一次情報源）
- `{SKELETON}`：`canonical/ARIADNE.html`（固定HTML/CSS/JS複製起点・v1.2.0 PLACEHOLDER-LOCK active）
- `{SLOT_CONTRACT}`：`canonical/ARIADNE.placeholder.html`（AIが置換してよい `{{{...}}}` スロット契約）
- `{OUT}`：`outputs/ux/001_ARIADNE/{00N_科目}/{PROBLEM_ID}_ARIADNE.html`
  （科目→フォルダは 001_刑法/002_刑事訴訟法/003_民法/004_商法/005_民事訴訟法/006_行政法/007_憲法）

## 手順
1. **{JX_HTML} を Read**し、次を抽出：問題文／登場人物／論点（過不足・配点順）／模範答案／採点講評の減点ポイント／
   規範コア／判例（射程）／参照条文。**自己照合**：問題文の事案と論点が整合するか確認（不一致なら中断・報告）。
2. **{SKELETON} を {OUT} へ複製**（Copy）し、**{SLOT_CONTRACT} を Read**して、三重波括弧 `{{{...}}}` で示された
   編集可能スロット相当箇所だけを問題固有内容へ置換する。ATHENA/skeleton の本文は逐語転載しない。
   **スロット外のHTML/CSS/JS・class名・section順・余白・字下げ・Mildliner機能色・パズルエンジンを変更しない。**
   新しいカード構造や見出し構造を思いついても、個別生成物へ入れず、正典更新が必要な変更として中断・報告する。
3. **各部を鋳造**（spec §2〜5）：
   - マストヘッド（科目・問題ID・「回す型：罪責検討の7ステップ SCAN→BUILD」）／問題文＋登場人物＋講師プルクオート。
   - **解法ナビ7ステップ**（SCAN/AIM/ORDER/MARCH/BREAK(＋5′)/BRIDGE/BUILD）を、抽出した論点構造から起こす。
     各ステップ＝`.do`（次にやること）＋`details.peek`（▶自分で1つ→確認）＋周回ドリル○×。**ORDER・BRIDGE を含め各ステップに `💡 box-tip` のコツ箱を1つ**（凸凹なく）。
     チェックポイント＝論点には `.tag-issue`＋1行の超短定義を併記（初学者が deep を開かず1周できるよう）。
   - **骨子**（`.bone.matrix-bone`）＝第1/第2/…の番号＋見出しを、JX019正典の**マトリクス型**で作る。各行は `.mrow`、本文は `.mcell`、中身は `.mline` に分け、ラベルは `.mstage q/r/a/c/cut`（問・論・規・当・結・削）、本文は `.mtext`。違法性・責任は必要な場合だけ一言で通過し、無理に独立行を作らない。**構造は {SLOT_CONTRACT} の許容断片から外れないこと。**
   - **照合・自己採点**（`.rubric`）＝採点講評の減点ポイントを☐リスト化（**AI採点に依存しない**）。`.collate`、`details.reveal-answer`、`details#deep-dive` は骨子コンテナ `.skeleton` の内側に置く。背景上へ外置きしない。
   - **模範答案**（`details.reveal-answer`）＝JX 模範を簡潔化して収録（字下げ・明朝）。**各段落 `<p>` に問規当結の役割クラスを付与**（spec §10）：問題提起=`class="role r-issue"`／規範=`class="role r-norm"`（説名は `<b class="rule">`）／あてはめ=`class="role r-apply"`／結論=`class="role r-concl"`（`.ma-h` 見出しには付けない）。あてはめ段落では **事実=`<span class="fact">`（生の事実）／評価語=`<span class="eval">`（「現実的危険を有する」等の橋渡し評価）** を括る。CSS は canonical 継承。
   - **深掘り層**（`details#deep-dive`）＝**アテナ級**に鋳造（spec §11）。判例・学説・条文は **TX 参考条文判例書式**で：
     ①規範（`.box-norm`）②学説対立（`.gakusetsu > .gk`・本問採用説に `.gk.adopt`）③**判例 完全プロファイル**
     （`.basis-card.case-card`：ヘッダ `⚖ 判例名`＋`.freq-badge` ★、本文は **【事案】【判旨】【補足】** を
     `<p class="hanging"><strong>…</strong><span class="hang-body">…`、【判旨】は `.judgment-text`）④**条文 完全プロファイル**
     （`.basis-card.statute-card`：`.para-num` 項番号＋条文文言、`.note>.note-body` に制度趣旨/保護法益/要件/射程を
     `.kd-label.r-shushi/r-hogo/r-youken/r-shatei` で整理。周辺条文は `.kd-item` 一覧）。相互参照は `a.ref-stat`/`a.ref-case`。
     CSS は {SKELETON} 継承。**法的正確性は {JX_HTML} に厳密準拠**（無い判例・規範を創作しない）。
     **末尾に「アテナで詳しく」ボタン**：`<a class="go-athena" role="button" tabindex="0" data-athena-code="{元問題ID}" data-athena-href="../../../001_JX/{00N_科目}/{元問題ID}.html">…</a>`
     （`data-athena-code` は `_ARIADNE` を付けない元 ID＝例 `刑JX001`。文言にメタ除去 regex 語＝`本問`/`正解は肢` 等を含めない）。
3-bis. **答案構成パズル（spec §9・周回の主役）** ─ エンジン（CSS/JS/ヒント・フォールバック）は {SKELETON} 継承で自動。生成時に**問題固有の下記**を付与する：
   - **骨子タグ**：`.bone.matrix-bone` 内で 論点=`<span class="iss">`／結論=`<u>`／見出し=`<span class="b1">` に加え、**規範=`<span class="krule">`／あてはめキー事実=`<span class="kfact">`** を付ける（Lv2 用）。**論点チップは `【論点】…` と書き冠番号を付けない（`【論点①】`/`【論点1】` 禁止＝無番号おとりと番号の有無で識別できネタバレになる・配置順は `.b1` 第1/第2 見出しで担保・spec §9-2・validate-ariadne A28 が ERROR）**。
   - **骨子の見た目規律（JX019を正典化）**：`.bsec` ごとに罪責・小問を区切る。各 `.mrow` は番号 `.bn`＋本文の2カラム。問規当結の複数行は `.mline` で縦に積み、`.mline + .mline` の点線区切りを活かす。ラベル色は `--ml-red/teal/green/gold/violet` のマイルドライナー系。文章本体は `.mtext` 側だけ字下げし、ラベルやバッジは字下げしない。
   - **おとり**：`.bone` に `data-kp-decoys="iss:…|u:…|rule:…|fact:…"`（近い誤りを 4〜6 個）。おとり論点も `iss:【論点】…`（冠番号なし）で本物と識別不能にする。
   - **試験下書き `.drafting`**（骨子の直前）：先頭に **`.draft-problem`＝問題文原文の再掲（上部 `.problem .pq` を逐語コピー＝答案構成で上へ遡らず済む）**、その直下に **`.draft-digest`＝骨子用に一行へ圧縮したメモ**（`<span class="ddl">骨子用に一行圧縮</span><span class="ddbody">…</span>` の2カラム）を置く。続けて `.draft-grid` 上段に①人物関係図 `.rel-map` と②時系列 `.timeline` を2カラム、下段に③拾う文言 `.facts` を `.draft-card span2` で全幅に置く。人物関係図を `span2` にしない。`.facts li` は引用 `.ph`＋理由 `.cue` の2カラムで、右余白が空きすぎないよう引用側を広めに取る。`.cue` の先頭に `...` / `…` を置かない。**いずれも生の事実抽出まで**（論点名・規範は書かない＝パズルの想起対象）。
   - **想起カード**：○×のうち**規範名・要件・定義を問える3枚前後**を `class="self-check-quiz recall" data-recall="1" data-rx="{SUBJECT}RX{NNN}_{論点序号}" data-correct-value="○"`＋`.recall-reveal`（onclick で `.quiz-answer` 開示）＋`.recall-grade` に「書けた○/書けなかった×」へ格上げ。**`data-rx`＝その想起が問う論点に対応する RX 論証カードのコード**（同JX配下 `outputs/ux/002_RX/{00N_科目}/{SUBJECT}JX{NNN}/` の `_1/_2/_3`＝論点①②③順。手順1で抽出した論点と RX タイトルを突合し1枚ずつ確定。1カード=1RX・多対一可・対応RX無しは省略）。Lexia は誤答時その RX を復習プールへ注入（LXA_FEAT_008）。**同じJX内の重複 data-rx は、教育上同じ論証を2枚で問う意図が明確な場合だけ許す。迷う場合は1枚だけに配線する。**
3-ter. **答案構成の作法（spec §12・教授のひとこと＋ステップ別周回ドリル）** ─ 構造（`.bc-wrap`／5ステップ＝予測・軸・骨・重心・締め／`.bc-col` CSS）は {SKELETON} 継承。**手順タイトル・5枚の周回ドリル○×は汎用＝原則そのまま流用可**（ドリルは復習プール単独表示の制約で必ず汎用）。**🎓教授のひとことコラム（`.bc-col`・5枚）は問題固有＝各問 TTS（耳トレ台本の答案構成/差がつく点/事案分析）から本問コーチングを抽出して鋳造**（端的な `.bc-inst` と register を分け重複回避・型タイトル維持）。`.bc-inst` は必ず `<span class="ji">本問</span><div class="bi">本文</div>` の2カラムにし、本文だけ字下げする。生成時に**問題固有**を鋳造する：各ステップ `.bc-inst`（本問の登場人物・罪名・順序）／④重心の `.bc-weight` 配点バー＋`.bc-cap` 字数目安／⑤締めの `.box-trap` 書かないことリスト／末尾 `.bc-rhythm` リズム超簡略版。**ドリルは答案構成の転用可能な手順原理**（設計優先・重い罪先行・規範先出し・重心集中・実益薄論点の切捨て）を○×で、**正解は偏らせない（○×混在）**。位置は解法ナビ（BRIDGE）と骨子（手7 BUILD）の間。
4. **周回○×（10枚前後・最重要・spec §4／§9-5）**：
   - 各 `.self-check-quiz` に **`data-arena="1"`** と **`data-correct-value="○/×"`**、`.quiz-question`、`.quiz-btn[data-value]`×2、`.quiz-answer`。
   - **本問の前提なしで解ける自己完結の一般原則／【例題】**にする（復習プールで孤立表示されても解ける）。状況依存設問は禁止。
   - **【最重要】教示↔ドリル 非重複（spec §4-bis）**：各手のドリルは、直上の **教示（`.do`/`.peek`）を読めば答えが割れる言い換え**にしない。教示＝「本問でどう動くか」の手続ナビ、ドリル＝「どこでも効く規範・定義・区別・要件」の能動想起、と**認知の的を分ける**。教示が戦術的選択（例「教唆で足りる」「正犯から書く」「規範は再掲せず接続」）を述べているなら、ドリルは**その選択を支える一段深い転用知識**（共謀共同正犯の要件／共犯従属性／法定的符合説の定義 等）を問う。**各手で「教示を隠さず読んでもドリルが解けてしまわないか」を必ず自己点検**。法的根拠は {JX_HTML} 内に必ずあるものに限る（創作禁止）。
   - 設問文を Lexia メタ除去 regex（`(本問|本設問)[0-20字]正解｜正解は肢｜正解はどれ｜正解の組`）に当てない。
   - `<script>` 内に `</body>` リテラルを書かない（「`</`+`body>`」等で回避）。
5. **体裁強化を冪等付与（必須）**：`python scripts/ariadne-enhance.py {OUT}`（①深層部 条文の「N項」バッジ化＋項を点線区切り／③マストヘッド目次ジャンプTOC／④各セクション区切り＋深掘り前に「▲先頭へ戻る」）→ `python scripts/ariadne-autolink.py {OUT}`（②本文インライン相互リンク＝条文・判例・学説・用語を語そのままリンク・解法ナビ⇄深層部・カード間相互）。両者**冪等**。
6. **検証**：`python scripts/validate-ariadne.py {OUT}` を実行し **A1〜A32 ERROR 0**。ERROR は該当部を修正して再検証。
7. **完了 sentinel を echo**（下記節のいずれか1つ）してから終了。本文は返さない。

## 注意
- 法的正確性は {JX_HTML}（検証済み正典）に厳密準拠。規範のすり替え・条文番号誤り・判例射程の誤用は禁止。
- 巨大 Edit を避け、部ごとに鋳造（1メッセージ 50KB 超の出力禁止）。
- 配色・フォント・誌面骨格は {SKELETON} を継承（TX v11 V3 Twilight Violet 見本＝spec §5。フォント＝Shippori Mincho B1／Zen Kaku Gothic Antique／Zen Maru Gothic／Source Code Pro、機能色＝規範ティール/事実グリーン/罠コーラル/ヒント金）。
- 体裁は **Claude正典＋JX019マトリクス正典**を継承する。バッジ・ラベル・見出し以外の本文は本文カラム側で字下げし、ラベル横に長文を直置きしてぶら下げない。ラベル＋本文は原則2カラム（`.pq-grid`/`.dp-row`/`.draft-digest`/`.bc-inst`/`.mline`）。
- **★ ベースカラーは難易度別にAI判断可**：{SKELETON} 継承の `:root` 「▼ ACTIVE」プリセットを、問題の難易度で **EASY=ローズ(P1)／STD=クリスタルブルー(P2)／HARD=バイオレット(P3)** から1つ選び、ラベル＋値2行だけを差し替える（3案 hex は `:root` コメントにカタログ常時記載）。基礎・典型→EASY／中堅・頻出（正当防衛・過失共犯等）→STD／重論点・罠多・錯誤や不作為や原自行為等の難所→HARD。**AIがデザイン判断してよいのはこのACTIVEプリセット選択だけ。新色創作、機能色変更、余白・構造変更は禁止。** ○×ボタンはコンパクト固定（`flex:1` にしない）。

## 完了 sentinel（必ず 1 つだけ echo して終了）

**完全成功時（validate A1〜A32 ERROR 0）：**
```
echo "BATCH_ITEM_COMPLETED:{PROBLEM_ID}-ARIADNE"
```

**生成成功・検証未達時（HTML はあるが ERROR/WARN 残）：**
```
echo "BATCH_ITEM_COMPLETED_WITH_ISSUES:{PROBLEM_ID}-ARIADNE:errors=<N>:warnings=<M>"
```

**生成不能時（中断・照合不一致・致命エラー）：**
```
echo "BATCH_ITEM_FAILED:{PROBLEM_ID}-ARIADNE:reason=<具体的理由>"
```
