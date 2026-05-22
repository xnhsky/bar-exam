# scripts/

## .ps1 ファイル保存規律

- すべての .ps1 ファイルは **BOM 付き UTF-8 (utf-8-sig)** で保存する
- 理由：Windows PowerShell 5.1 系は BOM 無し UTF-8 を cp932 として誤読する
- PowerShell 7+ は BOM 無し UTF-8 も正常に扱うが、互換性のため統一する
- 検証方法：`head -c 3 <file> | xxd` で `efbbbf` を確認
- night-batch-runner.ps1 など本番ファイル新規作成時も必ず BOM 付きで保存すること
