# 非特殊 v11 → v13.1.0 スロット・オーサリング手順（tx-lex-v11-to-v13.py）

> 純 v11 LOOP-CORE の `_lex`（inline カード無し・ox-grid）を、決定論ラッパー
> `scripts/tx-lex-v11-to-v13.py` で v13.1.0 LOOP-CARD へ再構成するための、**問題ごとに手執筆する
> `slots.json` ＋ `data.json`** の書き方。**PDF 不要**（既存 v11 本文が素材）。特殊型（≠5記述・組合せ・
> 穴埋め）は本ラッパー非対応（`SpecialTypeError`）＝PDF から R 再生成へ（`tx-v13-migration-targets.md`）。
> 実証：刑TX401-404（2026-07-07・リモート・全ゲート PASS）。

## 0. 全体の流れ

```
1. 抽出   : 記述原文5・ox論点コア・basis(条文/判例)・THE GIST を v11 から dump
2. 執筆   : slots.json（体系マップ＋横断＋マーキング＋v13m文）／data.json（規範核）
3. 変換   : python -X utf8 scripts/tx-lex-v11-to-v13.py <lex.html> slots.json data.json
4. 版付与 : python -X utf8 scripts/tx-lex-v13-stamp.py --apply <lex.html>   # 実体判定で v13.1.0
5. 検証   : validate-tx-core.py ／ check-tx-lex-engine.py ／ check-duplicates.py outputs
6. commit : _lex 1本ずつ（公式 000_TX は二系統設計どおり不変）
```

やり直すときは `git checkout -- <lex.html>` で v11 に戻す（ラッパーは v13.1.0 実体を
NOCHANGE ガードするため、変換済みには再実行できない）。

## 1. 抽出ヘルパー

`scripts/`（または scratchpad）に置いた dump で、記述原文・ox論点コア・basis-card
ヘッダー・`.syn-lead`（THE GIST）を一括表示し、それを素材に執筆する（例は
本セッションの `extract.py`：problem-text／`data-stmt`／`basis-card-header`／`syn-lead` を strip 表示）。

## 2. slots.json スキーマ

| キー | 内容 |
|---|---|
| `subject` | `gizou`/`houka` は自動ノード＆pbox が効く。**それ以外の任意文字列**（例 `tousou`/`kokka`）は `nodes` を明示指定し pbox は SKIP（＝正常。版判定は nb-badge＋brief-mark の実体で成立） |
| `top_title` / `head_subtitle` / `aria` / `panels_caption` | 体系マップ見出し |
| `nodes`[3] | 上段3ノード。`{x, code, label, lines[3], fill, stroke, headfill}`。x は `265 / 750 / 1235` 固定。色は赤系(`#fbeae8/#b0635c/#b0635c`)・琥珀系(`#f9f0dc/#c99a3a/#b58a2e`)・青系(`#e9f0f5/#5a86a8/#4d7391`) |
| `panels`[5] | 記述ごとの札。`{title(≲13字), sub(≲16字), color: red/amber/blue, stmt: 記述番号}` |
| `ox_line` | 帰結サマリ（○×の一言・答え自体は SVG 帰結箱が廃止のため表示されない） |
| `cross` | 3軸マトリクス。`{title, header[3], rows[[3]], kimete, throughline}`。`<b>` 可 |
| `mark` | `{"1":[verdict, phrase, fix], …}`。verdict=`o`/`x`（ox-key と一致）、phrase=**記述原文の完全一致部分文字列**（markup 除去後）、fix=正解方向の一言 |
| `gist` / `hook` / `trap` | `{"1": text, …}`。gist=💡THE GIST（やさしい版）／hook=🗝記憶のフック（締めの一行）／trap=⚠️横串・誤解の罠 |

## 3. data.json スキーマ

```json
{ "1": {"kihan": "…規範核 11〜14字…", "mark": ""}, "2": {…}, … "5": {…} }
```
- `kihan`：体系マップ記述札の ✍規範核バッジ（転用可能な規範の核・**11〜14字**）。
- `mark`：正誤表の印付き原文 HTML。空なら v131-author が `syn-orig` から自動生成（当面は空で可）。

## 4. 体系マップの型（重要）

- **単一テーマ型**（1問が1分野の5論点。例 逃走の罪＝刑TX402-404）：ノードは**条文の系統**
  （97単純／98加重／100援助 等）。
- **サーベイ型**（1問に別罪5つ。例 国家的法益＝刑TX401。400番台に多い）：ノードは
  **保護法益タクソノミー**（対公務／刑事司法／身柄・証人 等）。`subject` は任意文字列にして
  pbox SKIP でよい（客体三分に無理に押し込まない）。

## 5. 落とし穴チェックリスト（本セッションで実測）

- **G32/G34（ERROR）**：`gist`/`hook`/`trap` は syn-lead と **SM2 復習プール**へ入る＝
  **問題非依存の命題**で書く。`本問`／`本件`／`本肢`／`本記述`／`甲乙丙` を残さない
  （実体名・概念名で自己完結。「この記述は誤り」でなく「…する記述は誤り＝×」等）。
- **G50（WARNING）**：`cross.header` に **リテラル「本問の帰結」を使わない**（validator が
  廃止済みネタバレ箱と誤検出）。「本問の結論」等にする。
- **kihan は 11〜14字**（長いと札からはみ出す）。
- **mark.phrase は記述原文の完全一致**（`<strong>` 等で分断されると marking が silent fail）。
- **G11（WARNING・許容）**：`viewBox 下端余白 22px` は本ラッパーの SVG 生成に内在。配信可。
- 版が `11.x` のままなら **stamp `--apply` 未実行**（実体は v13.1.0 でもスタンプ文字列は別途付与）。

## 6. 対象と進捗（360-445 帯・非特殊v11）

台帳＝`tx-v13-migration-targets.md`「360-445 帯 v13.1.0 化 台帳」。
- 完了：刑TX401・402・403・404（2026-07-07）。
- 残り：405 407 409 410 413 414 417 419 421 422 423 425 432 434 435 436 437 438 440 441 442 443 444 445。
