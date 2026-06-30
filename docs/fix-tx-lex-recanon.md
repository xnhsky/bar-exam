# 既存 TX `_lex` の接ぎ木修復手順（codex / 任意エージェント向け）

> codex に「既存 _lex を v12 インラインへ手で直させる」と、毎回 §7 禁止の
> **保守的書き換え＝接ぎ木**（旧 Annex C JS 流用＋後付けパッチ `tx-inline-v1211-upgrade-js`＋
> 不足 CSS）になって収束しない。**HTML を手で編集してはならない。** 修復は決定論的
> スクリプトに任せ、エージェントは「実行→検証→push」だけを担う。

## 背景（なぜ手編集が失敗するか）

- canonical `canonical/GENESIS-CORE.html` の**単一 `<script>` エンジン**が inline カードを
  完全自前で配線する（reveal / browse / トースト / PART B 自動注入）。
- 接ぎ木版は旧エンジンを流用し、足りない動きを band-aid script で後付けするため、
  デザイン崩れ・機能不全・本文肥大（+30〜70K）を起こす。
- `tx-lex-recanon.py` が**本文（問題固有内容）を温存したまま土台（CSS＋エンジン）だけ
  canonical へ載せ替える**ので、内容を書き換えずに正典化できる。

## 手順（この3コマンドだけ。HTML は開いて編集しない）

```bash
# 1) 対象確認（read-only / dry-run）— 接ぎ木の問だけが「対象」に出る
python scripts/tx-lex-recanon.py outputs/ux/000_TX

# 2) 修復を適用（本文不変・土台のみ正典化・冪等）
python scripts/tx-lex-recanon.py outputs/ux/000_TX --apply

# 3) 検証ゲート（両方 PASS が必須）
python scripts/check-tx-lex-engine.py outputs/ux          # G41 接ぎ木ゼロ
for f in outputs/ux/000_TX/001_刑法/*_lex.html; do
  python scripts/validate-tx-core.py "$f" | grep -q 'ALL.*PASS' || echo "FAIL: $f"
done
```

3 が全て PASS なら push（§9 の動線・`scripts/jx-push.sh` でも可。push 前 preflight が
G41 を再チェックする）。

## スクリプトが行う3つの決定論的変換（手で再現しない）

1. `<style>` を canonical のものへ差し替え。ただし**AI 選定パレット（2つ目の `:root{}`）は元のまま**
   → 不足していた toast / result / inline CSS が canonical 品質で揃う・配色は不変。
2. `<script>` を「**canonical 単一エンジン ＋ 元の解法ナビ(solve-nav)**」の最大 2 本へ再構成
   → 旧 Annex C JS と `tx-inline-v1211-upgrade-js` を物理削除。
3. 本文の `.tx-inline-explain` に初期 `hidden` を付与（canonical 契約・G40）。

本文（HEADER / PART A / ox-grid / inline カード本文 / PART B / 参考条文判例 / SVG /
物語解説 / 解法ナビの問題固有データ）は**一切触らない**。

## やってはいけないこと

- HTML を開いて手で書き換える（接ぎ木の再発・収束しない）。
- `tx-inline-v1211-upgrade-js` 等の band-aid script を足す（G41 で弾かれる）。
- canonical 以外の既存 _lex を template にコピーする（§7）。
- 検証 PASS を待たずに push する。

## 想定どおりに直らない場合

スクリプトが「対象」に出さない／変換でエラーになる問は、本文構造が想定外なので
**その問だけ PDF から `/new-tx` 経由で再生成**する（手編集で繕わない）。
正実装の参照は `刑TX360〜365_lex.html`。
