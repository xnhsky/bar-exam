# CP gate — baseline 正準化（Phase 4 以降）

> Phase 4-2 footer-spec 着手にあたり、CP（Checkpoint）gate の正準 baseline を確定する。
> 旧 baseline はすべて historical artifact として扱い、Phase 4 以降は参照しない。

---

## 1. 正準 baseline

**`_phase3_2_pre_patch_baseline.json`** が Phase 4 以降の唯一の CP gate baseline である。

- 件数: 15 entries（全 outputs/tx/*.html）
- 形式: `{ "tx/<科目>TX/<科目>TX<id>.html": "<sha256 hex>" }`
- 補捉時点: 2026-05-19 16:31:54（Phase 3-2 basis_slot template patch 直前）
- ハッシュ対象: 出力ファイルの **CRLF（Windows 改行）** バイト列（`pathlib.Path.write_text` 既定動作と一致）

### byte-identical 保護対象（14 件）

下記 14 件は Phase 4 以降のすべての template / render.py 変更で **byte-identical 維持必須**：

| 出力 | template | 備考 |
|---|---|---|
| `tx/刑TX/刑TX303.html` 〜 `刑TX305.html` | sc5 / 各種 | 法学旧問 |
| `tx/刑TX/刑TX326.html` 〜 `刑TX330.html` | ox4 / msel5 / 他 | 直近検証セット |
| `tx/憲TX/憲TX001.html` | fillin | K1 案 β 検証 |
| `tx/民TX/民TX001.html` | sc5 | — |
| `tx/商TX/商TX001.html` | sc5 | — |
| `tx/民訴TX/民訴TX001.html` | sc5 | — |
| `tx/刑訴TX/刑訴TX001.html` | fillin8 | — |
| `tx/行政TX/行政TX001.html` | ox3comb8 | — |

### byte-identical 非保護（1 件、意図的）

- `tx/刑TX/刑TX300.html` — Phase 3-3 で `problems/300.json` に `basis` フィールドを追加（structured basis 描画の demo case）。baseline の hash `d41bdbf5...` は backup `problems/_300_v6_backup.json` 由来。新規 hash は Phase 3-3 適用後の正常な変化なので CP gate 評価では「DIFF 1 / 14 PASS」を成功状態とみなす。

## 2. CP gate 健全性チェック

```bash
python scripts/_cp_gate_check.py
```

期待出力（Phase 4-2 着手前の正常状態）:

```
PASS=14  DIFF=1  EXTRA=0  MISS=0  / baseline=15
```

DIFF が 300 以外に発生したら **即座に該当変更を巻き戻す**。Phase 4-2 適用後も同様：300 は DIFF 許容、他 14 は PASS 必須。

## 3. Historical artifact（Phase 4 以降は参照しない）

下記 5 baseline は v8.11.7 以前の段階的検証で使われたが、Phase 4 では参照しない：

| File | mtime | 内容 | 役割 |
|---|---|---|---|
| `_sha256_baseline.json` | 05-19 08:42 | 5 件（刑TX326-330）| 単科目 baseline |
| `_html_baseline.json` | 05-19 09:35 | 8 件（5 + 民/商/民訴）| 4 科目拡張 |
| `_html_baseline_10.json` | 05-19 10:16 | 10 件（+憲/行政）| 6 科目完備 |
| `_template_baseline.json` | 05-19 09:35 | 5 templates | template sync 旧 |
| `_template_baseline_7.json` | 05-19 10:16 | 7 templates | fillin8 追加前 |

**削除方針:** これらは git 未追跡だが、移行記録として残置する。Phase 4 完了後の整理 commit でまとめて削除候補とする（緊急性なし）。

## 4. baseline 更新ルール

Phase 4-N 適用ごとに新 baseline を切る場合は以下に従う：

1. patch 適用前に **既存 `_phase3_2_pre_patch_baseline.json` で CP gate を走らせ PASS=14** を確認
2. patch 適用後、`python scripts/render.py` で全 15 件を再 render
3. 新 baseline を `_phase4_<N>_pre_patch_baseline.json` 等の命名で出力
4. **本ファイル（`cp-gate.md`）の §1 を新 baseline に更新**し、旧 baseline を §3 historical artifact に降格
5. commit メッセージに baseline 切替の事実を明記

逆に **byte-identical を維持する patch**（Phase 3-2 / 3-3 / 4-1 と同様の slot 化型）は baseline 切替不要。`_phase3_2_pre_patch_baseline.json` を据え置く。

## 5. 関連スクリプト

- `scripts/_cp_gate_check.py` — 全 15 件再 render → CRLF 形式で baseline と sha256 比較
- `scripts/check_template_sync.py` — 8 templates の sync-required 7 領域（HEAD / CSS / body_pre_toc / marker_legend / part_c_d / footer_spec / JS）の hash 一致確認
- `scripts/validate-tx.py` — S1〜S82（feature-tag 整合・content independence 等を含む）
