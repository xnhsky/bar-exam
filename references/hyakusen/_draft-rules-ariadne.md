# 判例百選仕様 case-card 起草ルール（サブエージェント共通）

刑法判例百選の見開き画像（2頁）を Read し、ARIADNE 判例カード本文を下記マークアップで起草する。
画像 DIR＝`C:\Users\XNRG2~1.DES\AppData\Local\Temp\claude\C--Users-xnrg2-DESKTOP-5664QR6-bar-exam--claude-worktrees-elated-nobel-00af23\dc00a3ac-1c8e-41b3-8216-620f9947fc9e\scratchpad\hycase`。

## ⚠著作権（厳守）
- 【判旨】＝画像の「決定要旨／判決要旨」ボックスの**原文をそのまま『』で引用**（判決文＝著作権フリー）。
- 【事案】【解説】【射程】＝画像の「事実の概要」「解説」を読み、**自分の言葉で要旨化**（執筆者の文を逐語で写さない）。

## 出力（各判例。前後に説明文を書かない・HTMLエスケープしない）
```
=== 刑法百選{巻}-{番号} ===
<p class="hanging"><strong>【事件情報】</strong><span class="hang-body">{裁判所・元号年月日・小法廷／掲載(刑集○巻○号○頁・判時・判タ)／事件番号}</span></p>
<p class="hanging"><strong>【事案】</strong><span class="hang-body">{事実の概要を自分の言葉で3〜5文}</span></p>
<p class="hanging"><strong>【判旨】</strong><span class="hang-body"><span class="judgment-text">『{要旨ボックスの原文引用}』</span></span></p>
<p class="hanging"><strong>【解説】</strong><span class="hang-body">{問題の所在・学説対立・本判決の位置づけを自分の言葉で3〜6文}</span></p>
<p class="hanging"><strong>【射程】</strong><span class="hang-body">{射程・含まれる/含まれない事案・後続判例を自分の言葉で}</span></p>
<p class="hanging"><strong>【百選】</strong><span class="hang-body">刑法百選{巻}-{番号}（第8版）</span></p>
```

## 規約
- 元号・年月日・巻号頁・事件番号は画像から正確に転記（判例照合の結合キー）。「元」年はそのまま。数字半角。
- 【百選】欄の巻番号は各判例のもの（指定どおり）に必ず合わせる。
- 判旨原文は核心を落とさず引用。原文に無い語を足さない。読めない字は前後から補わず `？` を残す。
- `</`+`body>` 等の危険リテラルを書かない。1判例ごとに `=== 刑法百選X-N ===` 見出しで区切る。
- 正確さ最優先。著作権（判旨=引用・他=要旨）を必ず守る。
