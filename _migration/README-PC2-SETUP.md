# PC2 セットアップ手順（2026-05-27）

OWNER PC から PC2 への移行用ドキュメント。v10.0.0 GOLD-SKELETON 経路で
312 以降のバッチ運用を継続するために必要な手順。

---

## 1. リポジトリのクローン

PC2 で任意のディレクトリを選び、リポジトリを clone：

```powershell
git clone https://github.com/xnhsky/bar-exam.git
cd bar-exam
```

ブランチを移行コミットに合わせる：

```powershell
git fetch origin
git checkout claude/practical-archimedes-WfOOi
git pull
```

> **注**：master に merge 済みであれば `git checkout master` で OK。

---

## 2. inputs/tx-pdfs/ の取得

問題 PDF は git 管理外。Google Drive 等から PC2 にコピー：

```
inputs/tx-pdfs/312.pdf
inputs/tx-pdfs/313.pdf
...
```

---

## 3. outputs/000_TX/刑TX/刑TX311.html の取得（参考視覚確認用）

HTML 成果物は git 管理外（.gitignore で除外）。
311 をブラウザで参照したい場合は Google Drive 等から：

```
outputs/000_TX/刑TX/刑TX311.html
```

> **重要**：v10.0.0 経路では `canonical/GENESIS.html`（git 管理対象）が
> 新規生成の唯一の起点。outputs/ の 311 は視覚参考のみ。

---

## 4. memory の復元

`_migration/memory-2026-05-27.zip` を PC2 の Claude memory 配下に展開：

### 4-1. PC2 上のプロジェクトディレクトリ Hash を確認

PC2 で Claude Code を一度起動し、プロジェクトを開くと：

```
C:\Users\{PC2_USERNAME}\.claude\projects\c--Users-{PC2_USERNAME}-bar-exam\
```

が自動生成される。`memory\` サブディレクトリも空で作られているはず。

### 4-2. ZIP 展開

PowerShell：

```powershell
$dest = "$env:USERPROFILE\.claude\projects\c--Users-$env:USERNAME-bar-exam\memory"
New-Item -ItemType Directory -Force -Path $dest | Out-Null
Expand-Archive -Path "_migration\memory-2026-05-27.zip" -DestinationPath $dest -Force
Get-ChildItem $dest
```

> **注**：プロジェクトパスのハッシュ表記（`c--Users-OWNER-bar-exam`）は
> 元 PC のユーザー名を含むため、PC2 では別の表記
> （例：`c--Users-xnh-bar-exam`）になる。`$env:USERNAME` で自動置換される。

### 4-3. 内容物確認

展開後、以下 7 ファイルが配置されていることを確認：

- `MEMORY.md`（インデックス）
- `project_311_finalized.md`
- `project_palette_v2.md`
- `project_skeleton_ai_workflow.md`
- `reference_ingectar_palette.md`
- `feedback_semantic_exceptions.md`
- `feedback_svg_box_overlap.md`

---

## 5. Python 環境

`validate-tx-gold.py` / `validate-tx.py` / `validate-jx.py` は
`beautifulsoup4` を要求：

```powershell
pip install beautifulsoup4
```

---

## 6. 動作確認

PC2 で 311 baseline を検証：

```powershell
python scripts/validate-tx-gold.py canonical/GENESIS.html
```

→ **G1〜G16 ALL PASS** が出れば移行成功。

---

## 7. 312 以降のバッチ生成

Claude Code を PC2 で起動し、プロジェクトを開いて：

```
/batch-tx 312
```

Phase 0 で 5×1 / 5×2 / キャンセルを選択。
v10.0.0 GOLD-SKELETON 経路で `canonical/GENESIS.html` から
新規鋳造される。

---

## 8. 移行後のクリーンアップ（任意）

PC2 セットアップが完了したら、リポジトリから `_migration/` を削除して
履歴を綺麗に保てる：

```powershell
git rm -r _migration
git commit -m "chore: PC2 migration completed, remove transient memory backup"
git push
```

> **保管推奨**：将来再びマシン移行する可能性を考えると、ZIP は
> Google Drive 等にバックアップしてから削除すると安全。

---

## トラブルシュート

### Q. memory を展開したが Claude が認識しない

→ プロジェクトパスのハッシュが一致していない可能性。PC2 上の Claude を
一度起動して `~/.claude/projects/` 配下に自動生成されたディレクトリ名を
確認し、その配下の `memory\` に展開する。

### Q. validate-tx-gold.py が ImportError

→ `pip install beautifulsoup4` 未実行。

### Q. /batch-tx が見つからない

→ `.claude/commands/batch-tx.md` がリポから pull できていない可能性。
`git pull` で最新化。
