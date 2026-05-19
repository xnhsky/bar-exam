tx-legacy/

既存 TX HTML ファイル（v8.10.2 以下、または v8.11.x の旧 minor）をアップグレード対象として
配置するディレクトリ。

使い方：
  Claude Code で `/upgrade-tx inputs/tx-legacy/{ファイル名}` を実行。
  v8.11.1 形式に変換され、`outputs/tx/{科目TX}/{日本語接頭辞}TX{番号}.html` として出力される。

アップグレード時の変更点：
  - レガシー接頭辞（K/KEN/MIN/SYO/MINS/KEIS/GSE）→ 日本語接頭辞 + TX 形式
  - §0-tri STEP 1（既存スタイル完全破棄）が最優先実行される
  - §24 readability layer の追加
  - A-3 共通根拠 section を PART A 内 → PART B 後ろに再配置
  - hanging-grid 段落構造化
  - font-weight 強化（.basis-card-body → 600）
  - footer-spec に v8.11.1 必須 feature-tag 追加

詳細は CLAUDE.md §3-4 を参照。
