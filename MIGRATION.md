# 既存 bar-exam フォルダからの移行手順

このドキュメントは、TX v8.11.x の複数バージョン（v8.11.3〜v8.11.6）が混在し JSON パイプライン等で複雑化した
旧 `bar-exam/` フォルダから、本クリーン版（TX v8.11.7 + JX v3.2）への移行手順を示す。

---

## 移行の基本方針

旧プロジェクトには以下が混在していた：

- `spec/tx-v8.11.1〜v8.11.6` の **5 世代並列**
- `templates/KTX_template*.html` の **7 種類テンプレート**
- `problems/*.json` を経由する **JSON 中間パイプライン**
- `scripts/render.py` / `validate_structure.py` / `validate_content.py` 等の関連スクリプト
- `docs/` 配下の **10 個以上のセッションログ**
- `_quarantine/` / `_baseline*.json` / `_tmp_*.py` 等の累積ファイル
- `outputs/tx/` 配下の **過去生成済 HTML 群**

これらは「正典引用化対策の試行錯誤」で積み上がったものだが、本クリーン版では
**仕様書（spec/tx-v8.11.7-core.md）の §0-quad で問題自体を解決**したため不要となった。

ただし、**過去に生成済みの HTML（outputs/ 配下）と入力 PDF（inputs/ 配下）は保全する**ことが重要。

---

## 推奨手順（Windows PowerShell）

### 1. 旧フォルダを丸ごとバックアップ

```powershell
$old = "H:\マイドライブ\CATALINA＿G共有\■予備試験進行中\Claude Code\files\bar-exam"
$backup = "${old}_backup_$(Get-Date -Format yyyyMMdd_HHmmss)"
Copy-Item -Path $old -Destination $backup -Recurse
Write-Host "バックアップ完了: $backup"
```

### 2. 救出するファイルの一覧

旧フォルダから保全すべきもの：

| 保全対象 | 旧パス | 新パス | 備考 |
|---|---|---|---|
| 入力 PDF（TX） | `inputs/tx-pdfs/*.pdf` | `inputs/tx-pdfs/` | そのまま移動 |
| 入力 PDF（JX） | `inputs/jx-pdfs/*.pdf` | `inputs/jx-pdfs/` | そのまま移動 |
| 既存 TX HTML（生成済） | `outputs/tx/{科目TX}/*TX*.html` | `outputs/tx/{科目TX}/` | 検証通過済みのもののみ移動 |
| 既存 JX HTML（生成済） | `outputs/jx/{科目JX}/*JX*.html` | `outputs/jx/{科目JX}/` | 検証通過済みのもののみ移動 |
| アップグレード対象 | `outputs/tx/*/[v8.10.x ファイル]` | `inputs/tx-legacy/` | `/upgrade-tx` で v8.11.1 化 |

**捨ててよいもの：**

- `spec/tx-v8.11.3〜v8.11.6-*.{md,css,html,js}` 全 24 ファイル（自己完結化により不要）
- `templates/KTX_template*.html` 全 7 ファイル（仕様書埋込により不要）
- `problems/*.json` 全件（JSON 中間層を廃止）
- `scripts/render.py` / `scripts/build_*.py` / `scripts/check_template_sync.py` / `scripts/upgrade_v8111*.py` / `scripts/pdf_to_png.py` / `scripts/validate_all.py` / `scripts/validate_structure.py` / `scripts/validate_content.py`（新 `validate-tx.py` で代替）
- `schema/problem.schema.json`（JSON 経路廃止により不要）
- `docs/*.md` 全 10 ファイル（過去セッションログ・参考保存したい場合は別場所に退避）
- `_baseline*.json` / `_sha256_baseline.json` / `_template_baseline*.json` / `_tmp_*.py` / `_tmp_pdf_pages/`（一時ファイル群）
- `.claude/commands/new-ktx.md` / `upgrade-ktx.md` / `validate.md` / `new-jx.md`（旧版・新版で置換）
- `outputs/tx/*/_quarantine/` / `outputs/tx/*/_quarantine_pre_pipeline/`（隔離済み失敗 HTML）

### 3. クイック移行スクリプト（PowerShell）

```powershell
# 旧フォルダのパス
$old = "H:\マイドライブ\CATALINA＿G共有\■予備試験進行中\Claude Code\files\bar-exam"
# 新フォルダのパス（zip 展開先）
$new = "H:\マイドライブ\CATALINA＿G共有\■予備試験進行中\Claude Code\files\bar-exam-new"

# (a) 入力 PDF を新フォルダにコピー
Copy-Item -Path "$old\inputs\tx-pdfs\*.pdf" -Destination "$new\inputs\tx-pdfs\" -ErrorAction SilentlyContinue
Copy-Item -Path "$old\inputs\jx-pdfs\*.pdf" -Destination "$new\inputs\jx-pdfs\" -ErrorAction SilentlyContinue

# (b) 既存生成済 HTML を新フォルダにコピー（旧形式 K302.html 等を含む）
$txSubjects = @("刑TX","憲TX","民TX","商TX","民訴TX","刑訴TX","行政TX","行TX")
foreach ($s in $txSubjects) {
    $src = "$old\outputs\tx\$s"
    $dst = "$new\outputs\tx\$s"
    if (Test-Path $src) {
        Get-ChildItem -Path $src -Filter "*.html" | Where-Object {
            $_.FullName -notmatch "_quarantine"
        } | Copy-Item -Destination $dst -ErrorAction SilentlyContinue
    }
}

# 行TX があれば 行政TX にリネーム
if (Test-Path "$new\outputs\tx\行TX") {
    Get-ChildItem "$new\outputs\tx\行TX\*.html" | Move-Item -Destination "$new\outputs\tx\行政TX\"
    Remove-Item "$new\outputs\tx\行TX" -Recurse -Force -ErrorAction SilentlyContinue
}

# (c) 旧フォルダを backup にリネーム
$backupName = "bar-exam_legacy_$(Get-Date -Format yyyyMMdd)"
Rename-Item -Path $old -NewName $backupName

# (d) 新フォルダを bar-exam に昇格
Rename-Item -Path $new -NewName "bar-exam"

Write-Host "移行完了。旧フォルダは ${backupName} に保全されています。"
```

### 4. 既存 HTML を v8.11.1 形式に揃える

旧プロジェクトで生成済みの HTML は、レガシー接頭辞（K302、KEN087 等）の場合があるため、
**段階的に `/upgrade-tx` でアップグレード**する：

```powershell
# 例：刑TX 配下の全 HTML を一括アップグレード（Claude Code で 1 問ずつ実行）
Get-ChildItem "outputs/tx/刑TX/*.html" | ForEach-Object {
    Write-Host "アップグレード対象: $($_.Name)"
    # Claude Code で /upgrade-tx <パス> を実行
}
```

ただし、Claude Code のスラッシュコマンドは 1 件ずつ手動実行することを推奨（バッチ実行は文脈混乱の原因）。

---

## 移行後の検証

### TX 側

```powershell
python scripts\validate-tx.py outputs\tx\刑TX\刑TX299.html
```

期待値：ERROR 0 件。WARNING は実情に応じて。

### JX 側

```powershell
python scripts\validate-jx.py outputs\jx\民JX\民JX015.html
```

期待値：ERROR 0 件。

### よくある検証エラーと対処

| エラー | 原因 | 対処 |
|---|---|---|
| `[S70] ファイル名が v8.11.1 形式に非該当` | レガシー命名（K302.html 等） | リネーム + `/upgrade-tx` |
| `[S70] レガシー接頭辞 'K' がメタ情報に残存` | `<title>`/`doc-header`/footer に旧 ID | 3 箇所を新形式に統一 |
| `[S71] 出力先サブフォルダ不整合` | 接頭辞とフォルダの不整合 | 適切なフォルダに移動 |
| `[S68/AP-30] canonical text leakage 検出` | KTX301 由来文言が混入 | `/upgrade-tx` で §0-quad 適用 |
| `[S51] feature-tag 'jp-prefix-naming' 欠落` | v8.11.0 footer-spec | `/upgrade-tx` で feature-tag 更新 |

---

## 注意事項

- **canonical/KTX301.html は本クリーン版に含まれている**（旧プロジェクトと同じバイナリ）。コピー不要。
- **`spec/tx-v8.11.7-core.md` は自己完結**（§Annex A/B/C 全文埋込）。旧 `spec/tx-v8.11.6-annex-{A,B,C}.*` 等の分離ファイルは不要。
- **旧 CLAUDE.md の PATCH §0〜§4 の方針**（canonical = 構造参考のみ・本文流用禁止・二段検証）は本クリーン版に**仕様書レベルで取り込み済み**（§0-quad）。新 CLAUDE.md と旧 CLAUDE.md PATCH の差分はほぼゼロ。
- **問題 PDF はそのまま保全**：仕様変更で再生成が必要になっても、PDF さえあれば `/new-tx` または `/upgrade-tx` で対応可能。

---

## 質問が出やすい点

### Q. 「JSON 中間層を廃止して大丈夫？」

A. 大丈夫。旧 PATCH §3 で導入した「JSON 経由の content 制御」は **canonical text leakage 対策**だった。
本クリーン版では仕様書本体（§0-quad）で同等の対策を AI に強制するため、JSON 中間層なしで同じ品質が保てる。
むしろ JSON ↔ HTML の二重管理コストが消える分、運用がシンプルになる。

### Q. 「複数バージョン仕様（v8.11.3〜v8.11.6）を統合した v8.11.7 とかは作らないの？」

A. 作らない。v8.11.0 → v8.11.1 で本質的な課題（canonical text leakage と命名規則）が解決済み。
v8.11.3〜v8.11.6 で追加された S73〜S77 等の微調整チェックが必要であれば、
個別に `validate-tx.py` に追記する形が筋。一連のバージョンを統合したマイナーアップは、また
仕様書の肥大化と多バージョン混在の原因になる。

### Q. 「行政TX なのか 行TX なのか？」

A. 本クリーン版では **行政TX**（TX）と **行政JX**（JX）を採用（ユーザー指示「TX を JX に置き換えるだけ」に従って対称化）。
旧プロジェクトの `outputs/tx/行TX/` フォルダは `outputs/tx/行政TX/` にリネームして使用する。
JX v3.2 仕様書内部のパレットアンカー名「行JX」は仕様書側の表記であり、ファイル名・フォルダ名とは独立。

### Q. 「templates/ フォルダは何だった？」

A. 旧プロジェクトで「slot 差替方式」の HTML 生成を試みたときの作業残骸。
本クリーン版では仕様書（`spec/tx-v8.11.7-core.md`）の §Annex B body skeleton を AI が直接適用するため不要。
