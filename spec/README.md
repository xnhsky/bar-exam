# spec/ について

> **「いま新規生成で使う canonical・spec・validator はどれか」の正典は
> [`docs/canonical-lineage.md`](../docs/canonical-lineage.md)（系譜・現行版マップ）。**
> 迷ったらそれを見る。このファイルは spec/ 直下の最小オリエンテーションのみ。

## spec/ 直下（active のみ）

| ファイル | 用途 |
|---|---|
| `tx-v12.1.0-inline-core.md` | TX 現行（v12.1.1 LOOP-CORE。ファイル名は互換維持）インライン肢カード正典 |
| `tx-v11.0.0-core.md` | TX 基盤（v12 が継承する肢単位管理・ox-grid 構造骨子） |
| `tx-v11.1.0-twotrack.md` | TX 二系統（公式5択 / Lexia `_lex`）規律 |
| `jx-v4.0.0-core.md` | JX 現行（v4.0.0 LOOP-FOLD）構造骨子 |
| `jx-v3.2-master.md` | JX 基盤規律（タイポ・配色等。v4 が継承） |
| `jx-ariadne-v1.1.0-core.md` | ARIADNE 現行（v1.1.0 MATRIX-THREAD）解法ナビ＋答案構成周回正典 |
| `jx-ariadne-v0.1-core.md` | ARIADNE 旧版（履歴用）。新規生成では使わない |
| `legacy/` | 旧 TX spec（v8.11.x・v9.x 計33点）。**read-only・新規生成では使わない**。`upgrade-tx`/`upgrade-ktx` 等が参照 |

現行版・旧版・validator・コードネーム（GENESIS / ATHENA）の対応はすべて
[`docs/canonical-lineage.md`](../docs/canonical-lineage.md) に集約。本ファイルはそこへの入口。
