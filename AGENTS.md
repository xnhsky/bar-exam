# AGENTS.md — bar-exam（Codex 用エントリポイント）

> このファイルは OpenAI Codex（codex CLI 等のコーディングエージェント）向けの入口です。
> **実体の指示は同梱の [`CLAUDE.md`](./CLAUDE.md) が正典**です。重複管理を避けるため、
> ここには内容を複製せず、`CLAUDE.md` を参照する方式を採ります。

## 最初に必ずすること

1. **`./CLAUDE.md` を読み、その指示にそのまま従う**（命名規則・TX/JX 運用・配色・
   検証スクリプト・副産物生成・絶対禁止事項はすべて `CLAUDE.md` が正典）。
2. 生成系・系譜の早見は `docs/canonical-lineage.md`、各コマンドは `.claude/commands/` を参照。

## このリポの最重要ポイント（詳細は CLAUDE.md）

- **本線ブランチ：`master`**。HTML 成果物も git 管理し、生成＝コミットで永続化する（CLAUDE.md §9）。
- 2 シリーズ運用：**TX**（短答式・正典 `canonical/GENESIS-CORE.html` / `spec/tx-v11.0.0-core.md`）と
  **JX**（事例式・正典 `canonical/ATHENA.html` / `spec/jx-v4.0.0-core.md`）。
- **唯一の起点は canonical**：新規生成は `canonical/` を複製→本文を空文字列化→鋳造する。
  `outputs/*/` の既存 HTML を template 流用するのは**禁止**（content leakage の温床・§7）。
- **JX は副産物 3 種（RX/TREE/ARIADNE）まで含めて 1 セット**（§4-6・省略禁止）。
- 配布前ゲート：`python scripts/check-duplicates.py outputs` と各 `validate-*.py` を通す。

## 作業のルール

- §2 命名規則・出力先サブフォルダを厳守。1 問ずつ commit（巨大 diff を避ける）。
- 完了後は必ず commit & push（リモート環境は ephemeral）。
- 絶対禁止事項（§7）を必ず確認してから生成・編集する。
