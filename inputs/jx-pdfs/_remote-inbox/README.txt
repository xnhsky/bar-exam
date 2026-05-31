_remote-inbox/  — 外出先専用 PDF ドロップゾーン（JX）

目的：
  スマホ / GitHub Web UI から外出先でアップロードする JX 問題 PDF を置く専用フォルダ。

仕組み・運用は TX 版に準ずる（inputs/tx-pdfs/_remote-inbox/README.txt 参照）。
JX の取り込みは：

  bash scripts/remote-intake.sh --jx
    → _remote-inbox/*.pdf を inputs/jx-pdfs/{NNN}.pdf へ正規化

その後は /new-jx inputs/jx-pdfs/{NNN}.pdf で個別生成。
（JX は 1 問 1〜2 時間のためバッチではなく単発運用が安定・CLAUDE.md §8）

命名は CLAUDE.md §2-3 準拠（最初の連続数字・3 桁ゼロ埋め・数字なしはスキップ）。
