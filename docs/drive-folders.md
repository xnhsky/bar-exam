# Google Drive 保存先フォルダ ID（HTML 成果物の自動保存・正典）

> リモート実行環境（Claude Code on the web）は ephemeral でコンテナが回収される。
> HTML 成果物は `.gitignore`（`outputs/**/*.html`）で git 管理外＝**Drive が唯一の永続先**。
> 生成・バッチ完了時に、本ファイルの ID へ HTML を **必ずアップロードする**（CLAUDE.md §9）。

## TX 短答（`マイドライブ / 1 TX_短答 /` 配下）

| 科目 | 接頭辞 | Drive フォルダ名 | Drive Folder ID |
|---|---|---|---|
| 刑法 | `刑TX` | `001_刑法` | `1Izo2LwFv72K6nOJBLRRuBn876D-lydn5` |
| 刑訴 | `刑訴TX` | `002_刑事訴訟法` | `1RMqEabOYCLq2LrpFHTmny8eMFh4ere0f` |
| 民法 | `民TX` | `003_民法` | `1dP0BcbySxIh033oOK2Q_bhEhz6fdqcYH` |
| 商法 | `商TX` | `004_商法` | `1PwYjfsSm-6NgBRq6x5TOEYPRPYTES4mi` |
| 民訴 | `民訴TX` | `005_民事訴訟法` | `1MdEnlzT6weW7b6pPAJVQHxb8fq4GU9EL` |
| 行政法 | `行政TX` | `006_行政法` | `1IihxYyE8czOIAAPAVHvZFmzbNe7VzbOJ` |
| 憲法 | `憲TX` | `007_憲法` | `1AZ_ZhFsOSdlqteeQYJzbGzcwxUpUJuri` |

> 親フォルダ `1 TX_短答` の ID：`1T8YW0_cOyQmtsbSMqqeqCd-HjREhMEMB`

## アップロード手順（Drive MCP `create_file`）

各 HTML を、ファイル名の接頭辞 → 上表の Folder ID へアップロードする：

```
mcp__<drive>__create_file(
  title            = "刑TX346.html",          # outputs のファイル名そのまま
  parentId         = "1Izo2LwFv72K6nOJBLRRuBn876D-lydn5",  # 科目フォルダ ID
  base64Content    = <HTML を base64 エンコードした文字列>,
  contentMimeType  = "text/html",
  disableConversionToGoogleType = true          # Google Docs へ変換させない
)
```

- **base64 で送る**（日本語本文・大容量でも安全、Google 形式変換を確実に回避）。
- 既存同名ファイルがある場合は、**重複アップロードを避ける**ため事前に
  `search_files`（`parentId = '<科目ID>' and title = '刑TX346.html'`）で存在確認し、
  既にあればスキップ or 上書き方針を user 確認（既定：重複させず skip 報告）。

## JX 論文（未確定・要拡張）

JX HTML（`刑JX001.html` 等）の Drive 保存先 ID は本ファイル未収録。
初回 JX バッチ時に `search_files` で `刑JX` 等のフォルダ ID を特定して本表に追記すること。
