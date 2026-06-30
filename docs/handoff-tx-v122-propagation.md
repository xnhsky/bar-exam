# 引継ぎ：TX v12.2.0（重厚感・教科書化リデザイン）を全 v12 _lex へ伝播

宛先：Codex（このタスクで「アプデ＝伝播」を実行する人）
作成：2026-06-30 ／ 起点ブランチ：`design-restyle`（origin に push 済み）

---

## 0. これは何か（背景）

`design-restyle` ブランチで TX 正典 `canonical/GENESIS-CORE.html` を **v12.2.0** に確定済み（2 commit）：

- `909d3a41` 正典本体＋プレースホルダー契約＋ロック（G43）＋spec/CLAUDE.md
- `f5c72530` 伝播ツール（派生パレット復旧／凡例・is-case 本文修正）＋検査追従（G37 楕円ピル化）

**正典は確定済み。残りは「既存 _lex への伝播」だけ。** 設計内容は触らず、用意済みの決定論スクリプトを
順に流すだけでよい。**LLM 手編集は禁止**（接ぎ木の温床・§7／playbook）。新しい意匠が要るなら正典を先に直す。

### v12.2.0 でやったこと（伝播で再現される姿）
- インライン解説の物理順序：① 答案圧縮＝冒頭 ANSWER 箱（`✍ ANSWER` 食み出しタブ）→ ② 条文判例ボックス
  （条文=ブルー系 / 判例=`is-case` ピンク系）→ ③ 5点フロー（ラベル＝**楕円ピル＋立体**）→ ④ 記憶フック＝💡ワンポイント
  → ⑤ 詳説（必ず `data-partb-source="N"` panel）。旧 `.tx-cycle-aids` は廃止。
- 問題文原文 1字下げ／読み幅 container 1080px／凡例「論＝論文と重複」のみ（条/判マーカー廃止）。
- 多層シャドウ＋インセット光沢＋微パレットグラデで誌面を教科書化。実効スタイルは `<style>` 末尾
  「TX360 concrete template override」層（**ここが効く**。前方の同名ルールは上書きされる）。

### 2026-07-01 追補：TX355-359 実地修正で合意した恒久ルール

対象コミット：

- `22551584` `fix(tx-lex): promote 355-359 inline UI`
- `c515f8bb` `fix(tx-lex): hide final answer panel inline`
- `6cc7b1bc` `fix(tx-lex): restore basis boxes in details`

合意内容：

- 旧 `FINAL ANSWER` パネルは inline 型の画面には出さない。`.final-answer` は `data-answer-key` / G23 / Lexia 抽出のため DOM に残すが、`.answer-area.inline-prototype-mode .final-answer` で非表示固定にする。
- ANSWER 直後には必ず `tx-mini-law` を置く。条文本文・判例要旨を各肢の前面に出し、5点フローの「文言/趣旨/射程」だけで根拠を代用しない。
- `tx-mini-law` の本文冒頭に出る `本条` / `本文` / `①` / `②` / `109②` / `判旨核心` / `判例` は `tx-mini-law-para` の小ラベルで囲む。上段の `刑法` / 条文番号 / `判例` / 判例名チップも重厚な楕円ピルを維持する。
- 詳説の一番下にある条文・判例本文は、`sub-card basis-link` の `BASIS` ボックス内に収める。`.tx-detail-partb` のリセットで basis-link の枠・背景・`::before` タブを消さない。
- 詳説ボタンは空展開禁止。`tx-inline-detail` には必ず `tx-detail-panel tx-detail-partb` と `data-partb-source` を置く。
- 物語本文や強調語は太すぎるウェイトへ戻さない。特にモバイルで潰れる 700/800 系を本文強調に使わない。
- 条文本文横の項バッジは、2項以上ある条文だけ `本文` / `①` / `②` ... として表示する。単一項条文には付けない。
- 記憶フックはラベル列と本文列を分け、本文を字下げする。ラベルだけが左にぶら下がる表示へ戻さない。
- 5点フロー・条文項バッジ・機能ラベルは正典の楕円ピル。長方形バッジへ退行させない。
- 解法ナビは空枠禁止。検討順・判定コア・次操作を表示し、回答 UI の「解答を表示」導線を欠落させない。

---

## 1. セットアップ（衝突回避）

```bash
git fetch origin
git worktree add ../bar-exam-prop origin/design-restyle   # 専用 worktree 推奨（他作業と分離）
cd ../bar-exam-prop
git switch design-restyle
git pull --ff-only origin design-restyle
```

- 既存 worktree `.claude/worktrees/design`（私の作業ツリー）と `.claude/worktrees/txlex-spec-g42`（別作業）には触らない。
- Python 依存：標準＋`beautifulsoup4`（validate 用）。`git` は palette-restore が内部で `git show 76cecf5e:` を使う。
- 文字化け回避のため **必ず `python -X utf8`** で起動（cp932 パイプ事故対策）。

---

## 2. 伝播（順序厳守・全部 dry-run→確認→`--apply`）

対象ディレクトリ：`outputs/ux/000_TX/001_刑法`（刑法のみ。各スクリプトが非対象を自動 skip）。

```bash
D=outputs/ux/000_TX/001_刑法

# (1) 派生パレット復旧：必ず restyle の前。367-385 の block#3(violet 上書き)を破壊前 76cecf5e から復元。
python -X utf8 scripts/tx-lex-palette-restore.py $D            # dry-run
python -X utf8 scripts/tx-lex-palette-restore.py $D --apply

# (2) 意匠CSS伝播：正典<style>を全 v12 inline _lex へ。block#2+#3 パレット保全＋solve-nav CSS を正典注入。
python -X utf8 scripts/tx-lex-restyle.py $D                    # dry-run
python -X utf8 scripts/tx-lex-restyle.py $D --apply

# (3) DOM 移設＋詳説 panel 補完：答案圧縮→ANSWER箱／記憶フック→ワンポイント／空detailsに data-partb-source panel。冪等。
python -X utf8 scripts/tx-lex-answerbox.py $D                  # dry-run
python -X utf8 scripts/tx-lex-answerbox.py $D --apply

# (4) 本文小修正：凡例「論=論文と重複」＋「条/判」削除（※全 _lex 共通・362件）＋判例の is-case 化(368)。冪等。
python -X utf8 scripts/tx-lex-bodyfix.py $D                    # dry-run
python -X utf8 scripts/tx-lex-bodyfix.py $D --apply
```

**順序の理由**：restyle は file の block#3 をそのまま保存するので、先に (1) で正しい派生色へ戻す。
(2)→(3) は前後どちらでもよいが上記順で実証済み。(4) は本文の別箇所で独立。

### スコープ注意（重要）
- (1)(2)(3) は **v12 inline（`.tx-inline-card` を持つ＝刑TX360-385、386-389 も該当なら含む）だけ**に効く。
  v11 旧設計（001-359 等）は素通り（no-op）。
- (4) の **凡例修正は全 362 _lex 共通**（論マーカーの意味は普遍）。判例 is-case 化は 368 のみ（5件）。
  → v11「学習中」336問の凡例も変わる。これが望ましくないなら (4) を 26 問に絞る判断は可
  （ただし v11/v12 で凡例が割れる）。既定は全件（ユーザー指示「条/判 削除」は普遍）。

---

## 3. 検証（全部 PASS を確認）

```bash
# 各 v12 _lex は ALL PASS（G1〜G41＋G37 楕円ピル）になる。1件でも ERROR なら原因究明（手で直さない）。
for f in $D/刑TX3[6-8]*_lex.html; do python -X utf8 scripts/validate-tx-core.py "$f" | grep -E "ERROR|FAIL|PASS"; done

# push 前ゲート：G41(接ぎ木)+G42(組合せ当否)+G43(空詳説)。検出0で PASS。
python -X utf8 scripts/check-tx-lex-engine.py outputs/ux

# ファイル間：重複・ID不整合。検出時 exit 1。
python scripts/check-duplicates.py outputs
```

期待値：validate ALL PASS／gate PASS／duplicates 0。
**実証済み**：刑TX371（violet破綻＋空詳説）に (1)〜(4) を流すと validate ALL PASS・gate PASS・ヘッダーが
teal→teal で整合（従来 teal→violet）・凡例「論文と重複」・詳説がエンジンで hydrate。

---

## 4. レンダリング目視（数問）

`outputs/ux/000_TX/001_刑法/刑TX{361,368,371,375}_lex.html` をブラウザで開き、各記述の ○/× か「解説だけ閲覧」で
解説を展開して確認：

- 条文＝ブルー箱／判例＝ピンク箱、5点ラベルが**楕円ピル**（角丸長方形でない）、冒頭に `✍ ANSWER` 箱、末尾に 💡記憶フック。
- 「詳説を開く」で PART B が**中身入りで出る**（空でない）。ヘッダーのグラデが**同系色**（hue 割れなし）。
- 凡例が「凡例 | 論 論文と重複 | 高 … 中 … 低 …」（条/判が無い）。

---

## 5. 永続化（commit → master）

```bash
# pre-commit フック（lexia-genmeta スタンプ）を入れておく（冪等）
bash scripts/install-hooks.sh

git add outputs/ux/000_TX/001_刑法
# 巨大 diff になるので分けてもよい（任意）：設計26問 と 凡例全体 を別コミットにする等。
git commit -m "feat(tx-lex): v12.2.0 を全 v12 inline へ伝播＋凡例(論=論文と重複/条判削除)＋367-385 派生パレット復旧"

git fetch origin && git log --oneline origin/master -3     # master が動いていないか確認（動いていれば rebase）
git switch master && git pull --ff-only origin master
git merge --no-ff design-restyle -m "merge: TX v12.2.0 重厚感リデザイン＋伝播"
git push origin master
```

- push 前に必ず `git pull`（二台運用）。
- master へは ff か `--no-ff` マージで集約（ブランチ放置禁止・§8）。

---

## 6. 落とし穴・禁止（必読）

1. **手編集で意匠を直さない。** 全変換はスクリプト。ずれたら正典 `canonical/GENESIS-CORE.html` を直してから
   restyle を流し直す（接ぎ木＝§7 違反）。
2. **実効CSSは `<style>` 末尾「TX360 concrete template override」層**。前方に同名ルールが複数あるが上書きされる。
   検査 G37 は 4.9em/999px/6px 12px 7px を要求（楕円ピル）。
3. **palette-restore は restyle の前**。逆だと violet が残る。`--from` 既定 76cecf5e（d2fa8839 の直前）。
4. **空詳説は G43 で落ちる**。`data-partb-source` panel は answerbox が補完するので (3) を必ず実行。
5. **凡例は2系統**（標準＝判「裁判例」／変種5件＝論文関連・判「判例」）。bodyfix は両対応・冪等。
6. **冪等性**：全スクリプト再実行で no-op。中断しても安全に再開可。
7. **巨大単一出力禁止**は手編集の話。スクリプトのファイル書換は対象外（決定論）。
8. 私が確定した正典側 `<style>` には、上書きされて効かない**死んだ重複ルール**が一部残る（無害）。
   触らない（dedup は別タスク）。

---

## 7. ロールバック

```bash
git checkout -- outputs/ux/000_TX/001_刑法     # 未コミットの伝播を破棄
# コミット後に戻すなら該当コミットを revert（履歴に残す）。76cecf5e 等の履歴は保全。
```

---

## 付録：用意済みスクリプト一覧

| スクリプト | 役割 | 冪等 |
|---|---|---|
| `scripts/tx-lex-palette-restore.py` | block#3 派生パレットを 76cecf5e から復元（367-385） | ○ |
| `scripts/tx-lex-restyle.py` | 正典 `<style>`＋solve-nav CSS を全 v12 inline へ（block#2+#3 保全） | ○ |
| `scripts/tx-lex-answerbox.py` | 答案圧縮→ANSWER／記憶フック→ワンポイント／詳説 panel 補完 | ○ |
| `scripts/tx-lex-bodyfix.py` | 凡例(論/条判)＋判例 is-case 化 | ○ |
| `scripts/validate-tx-core.py` | 単一ファイル検証（G37 楕円ピル化済み） | — |
| `scripts/check-tx-lex-engine.py` | push 前ゲート（G41/G42/**G43 空詳説**） | — |
