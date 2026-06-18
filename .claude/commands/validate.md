---
description: TX または JX を自動判別して検証実行（修正なし・報告のみ）
---

HTML ファイルを TX または JX のどちらか判別し、対応する検証スクリプトを実行する。修正は行わず、結果を報告するのみ。

引数：対象 HTML ファイルのパス

## 手順

1. **ファイルパスから判別**：
   - パスに `outputs/000_TX/` または `刑TX`／`憲TX`／`民TX`／`商TX`／`民訴TX`／`刑訴TX`／`行政TX` を含む → **TX** と判定
   - パスに `outputs/001_JX/` または `刑JX`／`憲JX`／`民JX`／`商JX`／`民訴JX`／`刑訴JX`／`行政JX` を含む → **JX** と判定
   - 判別不能 → ファイル内 `<title>` や feature-tag を確認（"TX v8.11"→TX／"JX シリーズ" or "v3.2"→JX）

2. **検証実行**：
   - TX：
     ```bash
     python scripts/validate-tx.py <ファイル>
     ```
   - JX：
     ```bash
     python scripts/validate-jx.py <ファイル>
     ```

3. **結果報告**：
   - ERROR があれば違反項目（チェックID と内容）／該当箇所の簡単な説明／推奨修正案を列挙
   - WARNING があれば同様に列挙
   - ERROR 0 件なら「配信可能」と報告

## 出力フォーマット例

```
TX v8.11.7 検証結果: outputs/000_TX/001_刑法/刑TX302.html

❌ ERROR (2 件):
  [S11] PART A section 欠落: ['answer-area']
  [S68] canonical text leakage 検出: "畏怖の一材料"が本問（盗品等罪）に出現

⚠️  WARNING (1 件):
  [S46] section-title に sec-icon 欠落: 3 件

推奨修正案:
- S11: <section id="answer-area"> を A-1 と PART B の間に追加
- S68: 該当箇所の本文を §0-quad-3 IQ-2 から再執筆（本問は盗品等罪なので
       詐欺罪論点の文言は完全排除）
- S46: 該当する section-title に <span class="sec-icon">❀</span> を追加
```

```
JX v3.2 検証結果: outputs/001_JX/003_民法/民JX015.html

❌ ERROR (1 件):
  [J7] .key-box 防御セレクタ三者結合の不完全実装

⚠️  WARNING (0 件)

推奨修正案:
- J7: 仕様書第 13-1 項通り、.key-box / section .key-box / .container .key-box
       の三者結合セレクタで specificity を確保
```

## 鉄則

- **このコマンドは検証のみ**。ファイル修正は行わない
- 修正が必要な場合は `/upgrade-tx`（TX）または手動修正後に再度このコマンドを実行
- JX には現状アップグレード用 slash command がないため、修正は仕様書を参照しつつ手動で

$ARGUMENTS
