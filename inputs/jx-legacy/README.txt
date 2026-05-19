jx-legacy/

既存 JX HTML ファイル（v3.1 以下）をアップグレード対象として配置するディレクトリ。

注意：
  本プロジェクトには現状 /upgrade-jx slash command は存在しない。
  既存 JX ファイルの v3.2 アップグレードは手動で実施する：

  1. spec/jx-v3.2-master.md の付録 C「v3.1 → v3.2 移行クイックリファレンス」を参照
  2. 主要な変更点：
     - タイポグラフィ 6 役割 → 11 役割（5 役割追加：--font-keyword, --font-judgment,
       --font-note, --font-professor, --font-mono）
     - .key-box の豪華装飾化（'🔑 KEY' ラベル + specificity 防御セレクタ三者結合）
     - blockquote.statute（薄グレー）/ blockquote.case（薄ピンク）の視覚差別化
     - <strong>第N項</strong> → <span class="para-num">第N項</span>
     - .note-box / .warn-box / .success-box / .danger-box にラベル付きカード型刷新
     - 本文インデント設計（padding-left:1.4em / 第 23 項）
     - body: line-height:2.0 / letter-spacing:.04em / font-weight:500
     - container max-width:1080px
     - .statute-emphasis / .case-emphasis の border-bottom 廃止
  3. python scripts/validate-jx.py で J1〜J20 全件通過を確認

詳細は spec/jx-v3.2-master.md および CLAUDE.md §4 を参照。
