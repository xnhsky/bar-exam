# Codex 貼り付け用プロンプト（TX / JX）

> 下の ``` ブロックを Codex にそのまま貼る。`{科目}` `{NNN}` `{PDFパス}` だけ置換。
> 詳細・例外は `docs/codex-tx-jx-handoff.md`・`CLAUDE.md`・`spec/` が正典。

---

## A. TX を作らせる（公式5択＋Lexia用 _lex の二系統）

```
bar-exam リポジトリで TX 短答 HTML を生成して。対象 PDF: {PDFパス}

【鉄則】
- 起点は canonical/ だけ。outputs/ の既存 HTML を template に cp/Read/Edit しない。
- clone 後すぐ本文を空文字列で初期化してから PDF を見て新規執筆（canonical の本文を残さない/流用しない）。
- <script>…</script> 内に "</body>" リテラルを書かない（代替：「body 閉じタグ」「'</'+'body>'」）。
- 1 つの Write/Edit は 50KB 以下。render.py 実行禁止。応答は日本語・簡潔に。
- TX 1 問 = 2 ファイルを必ず出す（片方だけ禁止）。
- ファイル名は {接頭辞}TX{3桁0埋め}.html（番号は PDF 名の最初の連続数字。取れなければ中断して確認）。

【出力先】
- 公式: outputs/000_TX/{00N_科目}/{接頭辞}TX{NNN}.html（本物の5択）
- Lexia用: outputs/ux/000_TX/{00N_科目}/{接頭辞}TX{NNN}_lex.html（ox-grid＋解法ナビ＋物語解説）
  科目→フォルダ: 刑法=001_刑法/刑訴=002_刑事訴訟法/民法=003_民法/商法=004_商法/民訴=005_民事訴訟法/行政法=006_行政法/憲法=007_憲法
  接頭辞: 刑TX 刑訴TX 民TX 商TX 民訴TX 行政TX 憲TX

【手順】
1. PDF 解析: 問題番号・正答率・全記述ア〜オ原文・各記述の○×・本物の正解・出題形式を抽出。
   冒頭に「正答率 __% → P_『___』 → パレット『___』」を出力（≥60%=P1ピンク/40-60%=P2緑青/<40%=P3紫）。
2. cp canonical/GENESIS-CORE.html <公式パス> → 本文を空文字列で初期化。
3. section-by-section で執筆（各30〜50KB）:
   - HEAD :root{} は --accent/--mid/--soft/--light/--bg-dark＋派生だけ更新。--base は #F7F1E9 固定。
     <style>末尾 §18〜§22（配色オーバーレイ）は触らない。配色情報をヘッダー/フッター本文に書かない。
   - HEADER（exam-meta は正答率と難度のみ）。
   - PART A = ox-grid: data-answer-type="ox-grid" / data-correct-value="××○×○"（ア〜オの○×連結）。
     5 .ox-row 各行 = <p class="ox-gist">要点一行（記号フリー30〜50字・○×をにじませない・<b>）</p>
       ＋ <details class="ox-detail"><summary>全文</summary><span class="ox-stmt">自己完結命題（記号フリー）</span></details>。
     reveal-answer-btn 必須。final-answer 表 statement-verdict-table（data-answer-key="ア:x,…"）は hidden。
     answer-key・data-correct-value・○×表の三者一致。
     ※単純5択型では canonical 由来の末尾「（参照条文）blockquote.statute」「【組合せ】…番号リスト」を削除。
   - PART B（記述単位・choice-1=記述ア…）: .verdict（✓/✗＋法理のズレ・組合せ判定書かない）→
     .sub-card.synthesis（📜記述原文→💡THE GIST→①②③→💭INTUITION）→ .choice-points（📌POINT 2〜4・
     「正解は肢N/組合せ判定/他記述参照」禁止）→ .sub-card.basis-link（📚BASIS）。学説問題のみ .choice-premise（🔎前提見解を原文再掲）。
   - PART B+ .cross-column（🔗CROSS / 📊比較 / ⚠️罠）本文のみ。
   - 参考条文判例 #basis: 条文（文言＋保護法益/制度趣旨/要件）/判例（判旨=.judgment-text、判旨以外=.note）。
   - SVG 2枚（体系ツリー mindmap-tree＋放射 mindmap-radial）テキストのみ差替・座標/class据置。
   - footer-spec feature-tag 先頭 = TX v11.1.0 LOOP-CORE。
4. 二系統分離（順序厳守）:
   a. cp <公式パス> <_lexパス>（自己複製＝許可）。
   b. _lex に canonical/SOLVE-NAV.html の [STYLE]→head末/[SHELL]→answer-area直前/型別SCRIPT→</body>直前 を移植。
      エンジン JS は逐語コピー（編集禁止）、問題固有データのデリミタ内だけ本問値。
      独立5択=[SCRIPT-OX]（MODE='correct'/'incorrect'＋STMT各記述 q/tip/note）。
      組合せ・穴埋め・議論=[SCRIPT-COMBO]（COMBOS/OFFICIAL/ORDER/STEP）。tip は決め手1点・1文40〜70字。
      footer に lexia-oxgrid-solvenav 追記。
   c. 公式を de-grid: answer-area を data-answer-type="single"（多答 "multi"）/data-correct-value="本物の正解番号"、
      .answer-ox-grid を .answer-row（番号ボタン1〜5）に置換、instruction を「記述1〜5のうち…1つ選び」へ。
      解法ナビは公式に入れない。footer に official-5choice 追記。
   d. 整合: _lex の○の位置＝公式の正解番号。両ファイルの title/doc-header/footer の問題コードは同一。
5. 物語解説（_lex のみ）: .final-answer 冒頭に初学者向け読み物。記号フリー（①〜/(a)〜/A説/甲乙説/ア〜オ言及禁止）・
   6〜9段落・重要語<b>。JSON {"title":"この問題を物語で読む ── …","paras":[…]} を一時ファイルに python で出力し
   `python scripts/tx-inject-narrative.py {接頭辞}TX{NNN} <json>`。手本=outputs/ux/000_TX/001_刑法/刑TX311_lex.html。
   ※Type A（議論形式・空欄補充）なら `python scripts/tx-build-typeA.py <CODE> <DATA.json>`（物語内蔵＝5は不要）。判別は tx-classify-format.py。
6. SVG 重なり検査（rect/ellipse 全ペア AABB・マージン16px・衝突時 viewBox 拡張）。
7. 検証（両ファイル ERROR 0 まで修正→再検証）:
   python scripts/validate-tx-core.py <_lexパス>
   python scripts/validate-tx-core.py <公式パス>
   python scripts/check-duplicates.py outputs
   grep -c 'fa-narrative-title' <_lexパス>  # 1 以上
8. 永続化:
   python scripts/stamp-created-date.py
   git add <公式パス> <_lexパス>
   git commit -m "feat({接頭辞}TX): {接頭辞}TX{NNN} を二系統生成（公式5択／Lexia用 ox-grid＋解法ナビ）"
   git push -u origin <作業ブランチ>
```

---

## B. JX を作らせる（本体＋副産物 RX/TREE/ARIADNE）

```
bar-exam リポジトリで JX 論文/事例 HTML を生成して。対象 PDF: {PDFパス}

【鉄則】
- 起点は canonical/ だけ。outputs/ の既存 HTML を流用しない。clone 後すぐ本文を空化してから執筆。
- <script>…</script> 内に "</body>" リテラルを書かない。1 Write/Edit は 50KB 以下。render.py 禁止。応答は日本語。
- JX 1 問 = 本体 HTML ＋ 副産物3種（RX/TREE/ARIADNE）で 1 セット。HTML だけで完結扱いにしない。
  （Codex はサブエージェントが無いので副産物も自分で順に作る：RX→TREE→ARIADNE）
- ファイル名 {接頭辞}JX{3桁0埋め}.html。出力先・接頭辞は TX と同じ科目対応（JX フォルダは outputs/001_JX/{00N_科目}/）。

【手順】
0. 入力アラインメント: python scripts/check-jx-alignment.py {科目} {NNN}
   [OK] 以外は中断。内容照合で正しい逐語を特定し inputs/001_JX/transcript-map.json の overrides に追記して再実行。
   （重問PDFと講義逐語は番号がズレる系列がある＝同番号を無断前提にしない）
1. PDF＋逐語を併読（逐語が論点・規範・あてはめの一次情報源）。冒頭で逐語と PDF の事案一致を自己照合。
   不一致なら逐語を使わず中断・報告。spec/jx-v4.0.0-core.md＋spec/jx-v3.2-master.md を参照。
2. cp canonical/ATHENA.html outputs/001_JX/{00N_科目}/{接頭辞}JX{NNN}.html → 本文を空化。
3. 配色は全パレットから雰囲気で AI 自由選定→5役割（--base70/--accent25/--mid5/--soft/--light）。
   pale bg + dark text・WCAG AA 4.5:1・semantic 緑#438B48/#7BA980・金#ffd54f/#ffaa00 のみ越境可。刑は ATHENA 配色流用可。
4. 構造（v4 LOOP-FOLD・ATHENA 複製で骨格継承）:
   - 11役割タイポ＋Google Fonts 維持。exec-summary は作らない。
   - 事案足場（事案概要・登場人物図・時系列・ファクト仕分け・#issue-extraction）は前半コアに（結論先出し禁止）。
   - 後半 deep（第4部体系化＋第5部）は <details id="deep-dive"> で折りたたみ（DOM 温存）。
   - 模範答案＋採点講評は <details class="reveal-answer"> で封じる。用語集5-5/略語5-6 は deep の外（section#part5-ref）。
   - 第3部 reveal 直前に .collation-nav、各 H 末尾に .oral-skeleton。
   - 必須: .key-box（🔑KEY 防御セレクタ三者結合）/ラベルカード4種（💡NOTE/⚠WARN/✓TIP/✗NG）/
     blockquote.statute（薄グレー）・blockquote.case（薄ピンク）色差別化/.judgment-text/.para-num/.model-answer/.grading。
   - 逐語があれば .lecturer-advice（🎓）を該当論点・部の冒頭に（要点整理・逐語のまま貼らない）。
   - container max-width:1320px / doc-header position:absolute 右上 / 末尾スムーズスクロール JS / フッター励まし文言。
5. 検証: python scripts/validate-jx.py <本体パス> → J1〜J20（＋JC/JD）ERROR 0 まで修正。
6. 副産物3種を順に生成（いま PASS した JX HTML を一次情報源に再構成。各 headless プロンプト全文に従う・clone→空化→鋳造）:
   - RX: prompts/new-rx-headless.md / 起点 canonical/AXIOM.html /
     出力 outputs/ux/002_RX/{00N_科目}/{接頭辞}JX{NNN}/{接頭辞}RX{NNN}_*.html（1論点1枚）/
     検証 python scripts/validate-rx.py <DIR> {接頭辞}RX{NNN}
   - TREE: prompts/new-arb-headless.md（vendored＝canonical/ARBOR.html の構造シェルのみ参照・約13分枝/葉57/問題15/68KB）/
     出力 outputs/ux/003_TREE/{00N_科目}/{接頭辞}JX{NNN}_TREE.html / 検証 python scripts/validate-tree.py <file>
   - ARIADNE: prompts/new-ariadne-headless.md / 起点 canonical/ARIADNE.html /
     出力 outputs/ux/001_ARIADNE/{00N_科目}/{接頭辞}JX{NNN}_ARIADNE.html / 検証 python scripts/validate-ariadne.py <file>
   各副産物も </body> リテラル禁止・検証 ERROR 0 まで。3種そろえてから push。
7. 永続化: scripts/jx-push.sh "feat(jx): {接頭辞}JX{NNN} を生成保存（J1〜J20 PASS＋RX/TREE/ARIADNE）"
   （outputs/001_JX＋outputs/ux を stage・日時スタンプ・再試行付き。PDF 削除はローカル任せで実行しない。TTS は担当外）。
```
