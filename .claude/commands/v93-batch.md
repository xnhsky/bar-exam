# v93-batch コマンド

引数: 問題番号（複数可・スペース区切り）。例: `/v93-batch 308 309 310 311 312`

v9.2.0 PALETTE-MULTI-VARIANT 拡張版・27 サブパレット自動選択 + HSL 派生対応。

## 実行手順

各問題番号 $ID について順次以下を実行する。1 問でも FAIL したら以降を中断（既存 night-batch-runner と同規律）。

### Step 1: 事前確認
- inputs/tx-pdfs/$ID.pdf が存在することを確認（存在しなければ STOP）
- problems/$ID.json が既存ならスキップ提案（user 確認待ち）

### Step 2: spec・既存 JSON 読込
事前に以下を必ず読む（記憶に依存しない）:
- `spec/tx-v9.3.0-palette-multi-variant.md`（v9.3.0 配色 delta spec・最優先）
- `spec/tx-v9.2.0-deepdive-core.md`（base spec・構造規律全般）
- `problems/306.json` と `problems/307.json`（v9.2.0 骨格テンプレート参考）
- `scripts/render.py`（特に SUBPALETTES_V93 / derive_palette_v93 / select_subpalette_v93 / FOOTER_FEATURE_TAGS_V93 周辺）
- `scripts/validate-tx.py`（S88/S90/S91/S92 検出ロジック）

### Step 3: PDF 解析・設計判断

inputs/tx-pdfs/$ID.pdf を読み、以下を確定:
- subject (KEI 等の短縮形)
- crime / source / correct_rate / points / chapter / section / page
- instruction_type（spec の TEMPLATE_PATHS にある値のみ）
- answer
- **override_pattern 自動判定（v9.3.0 経路）**: 
  - 正答率 ≥70% → P1（桜彩 Sakura Spectrum）
  - 40-70% → P2（翠彩 Verdant Spectrum）
  - <40% → P3（玄彩 Mystica Spectrum）
- **sub_palette_id**: 通常は **unset**（auto 選択推奨）
  - 明示指定が必要な場合のみ JSON に記載
- **palette_strategy 自動判定**:
  - 学説問題（is_theory_selection=true）→ 同系統調和
  - P3 帯 → 同系統調和
  - 罪名識別型・判例対比型 → 寒色×暖色対比
  - その他 → 同系統調和
- theory_deep_dive 要否: 学説対立・判例対立が論点核心なら必須

設計判断を `docs/v93-batch-design-$ID.md` に記録。

### Step 4: JSON 起草

**spec_version は必ず `"v9.3.0"` で起草する**。

その他の規律は v9.2.0 通り（v9.3.0 は配色 delta であり構造体は据置）:

**density-v2 規律**（spec §0-quad-3 STEP IQ-5 強化版）:
- 各 choice の professor の純 char 数集計で:
  - point (locus + list 合計): 150+
  - process.steps 合計: 400+
  - image (scene+bridge+contrast): 300+
  - application (major+minor+conclusion): 300+
  - **合計: 1,500+ chars 目標**

**S78 ブラックリスト適合**（spec §0-quad-2 / validate-tx.py:63-90）:
- KTX301 由来 20 語句が出現しないことを起草中に常時確認

**S90 メタ説明禁止**（spec §0-quad-2-bis / validate-tx.py:203-219）:
- 14 patterns（「肢Nを選ぶ」「正解の肢は」「解答の手順」等）を professor/theory/part_c/key-phrase で使わない

**top-level 25-26 keys 構造**:
spec_version / subject / id / crime / source / correct_rate / points / chapter / section / page / instruction_type / answer / override_pattern / palette_strategy / instruction / answer_explanation / case / basis / choices / theory_deep_dive / mindmap_tree / mindmap_radial / flowchart_v2 / drill_blocks / part_c
（optional: sub_palette_id / palette_override_reason）

### Step 5: 起草後自己検証

起草直後、Python で以下を確認:

```python
import json, re
with open(f'problems/{id}.json', encoding='utf-8') as f:
    p = json.load(f)

# spec_version
assert p.get("spec_version") == "v9.3.0", f"spec_version must be v9.3.0"

# top-level keys (25 必須 + optional 2 件可)
assert 25 <= len(p) <= 27, f"top-level keys must be 25-27, got {len(p)}"

# density-v2 (v9.2.0 と同じ規律)
for c in p["choices"]:
    pr = c["professor"]
    pt_len = len(pr["point"]["locus"]) + sum(len(x) for x in pr["point"]["list"])
    pc_len = sum(len(x) for x in pr["process"]["steps"])
    im_len = sum(len(pr["image"][k]) for k in ("scene","bridge","contrast"))
    ap_len = sum(len(pr["application"][k]) for k in ("major","minor","conclusion"))
    assert pt_len >= 150, f"choice {c['label']} point {pt_len} < 150"
    assert pc_len >= 400, f"choice {c['label']} process {pc_len} < 400"
    assert im_len >= 300, f"choice {c['label']} image {im_len} < 300"
    assert ap_len >= 300, f"choice {c['label']} app {ap_len} < 300"
    total = pt_len + pc_len + im_len + ap_len
    assert total >= 1150, f"choice {c['label']} total {total} < 1150"

# S78 blacklist
blacklist = [...]  # validate-tx.py:63-90 から取得
text = json.dumps(p, ensure_ascii=False)
hits = [b for b in blacklist if b in text]
assert not hits, f"S78 violation: {hits}"

# S90 meta-explanation
meta_patterns = [...]  # validate-tx.py:203-219 から取得

# drill_blocks 12
assert len(p["drill_blocks"]) == 12

# theory_deep_dive 文字数
t = p["theory_deep_dive"]
assert len(t["major"]["why_adopted"]) >= 200
assert len(t["minor"]["why_not_adopted"]) >= 200

# v9.3.0 specific: override_pattern (自動的に category と一致するはず)
correct_rate = int(re.search(r"(\d+)", p["correct_rate"]).group(1))
if correct_rate >= 70: expected_cat = "P1"
elif correct_rate >= 40: expected_cat = "P2"
else: expected_cat = "P3"
assert p["override_pattern"] == expected_cat, f"override_pattern mismatch"

print(f"[SELF-VERIFY PASS] {id}.json (v9.3.0)")
```

**全 assert PASS でなければ Step 6 に進まない**。FAIL したら起草修正に戻る（最大 3 回試行・3 回失敗で STOP）。

### Step 6: render.py 経由生成 + 検証 + commit

```powershell
python scripts\render.py $ID
$html = "outputs\tx\刑TX\刑TX$ID.html"
$size = (Get-Item $html).Length
$ft = (Select-String -Path $html -Pattern 'class="feature-tag"' -AllMatches).Matches.Count
$tdg = (Select-String -Path $html -Pattern 'theory-detail-grid' -AllMatches).Matches.Count
$ps = (Select-String -Path $html -Pattern 'palette-strategy:' -AllMatches).Matches.Count
$sp = (Select-String -Path $html -Pattern 'sub-palette:' -AllMatches).Matches.Count  # v9.3.0 新規
$db = (Select-String -Path $html -Pattern 'drill-block' -AllMatches).Matches.Count
$validate = python scripts\validate-tx.py $html 2>&1 | Out-String

# v9.3.0 では feature-tag が 35 件（v9.2.0 33 件 + 2）
$pass = ($ft -eq 35) -and ($tdg -ge 1) -and ($ps -ge 1) -and ($sp -ge 1) `
        -and ($db -ge 12) `
        -and ($validate -notmatch "ERROR\s*[1-9]") `
        -and ($size -gt 160000) -and ($size -lt 250000)

if (-not $pass) { Write-Host "FAIL: STOP" -ForegroundColor Red; break }
```

全 PASS なら:

```powershell
Copy-Item $html _experimental\刑TX$ID.html -Force
git add problems\$ID.json _experimental\刑TX$ID.html docs\v93-batch-design-$ID.md
# commit message は設計判断ファイルから自動生成
git commit -m "feat(content): 刑TX$ID v9.3.0 (Phase 15 CC-batch)

- 設計判断は docs/v93-batch-design-$ID.md 参照
- spec_version: v9.3.0 PALETTE-MULTI-VARIANT
- sub-palette: [選択結果]"
```

### Step 7: 次の問題へ

5 問完了後 push。途中失敗時は失敗箇所までで push せず STOP（user に報告）。

### 失敗時の報告フォーマット

```
=== Phase 15 v93-batch FAILURE ===
失敗問題: $ID
失敗 step: $STEP (1-6)
失敗詳細: [self-verify error / validate-tx error / size out-of-range 等]
推奨対応: [起草修正 / Claude.ai レビュー / STOP]
```

## v9.3.0 vs v9.2.0 主な差分

| 観点 | v9.2.0 | v9.3.0 |
|---|---|---|
| 配色パターン | 3 種固定（P1/P2/P3）| 3 カテゴリ × 9 サブパレット = 27 種 |
| サブパレット選択 | なし | seed=problem.id でランダム選択 |
| 派生色生成 | 固定 hex 値 | HSL アルゴリズム計算導出 |
| feature-tag | 33 件 | 35 件（palette-multi-variant / hsl-derivation / sub-palette: ... 追加） |
| 構造体 | （v9.2.0 通り） | 据置（差分なし） |
| density 規律 | （v9.2.0 通り） | 据置（差分なし） |
| 検査項目 | S85-S91 | S85-S91 + S92（サブパレット ID 整合性） |

## サブパレット一覧（27 件）

### 🌸 P1 桜彩 (Sakura Spectrum) - ピンク・易問
sakura-haze (桜霞) / spring-twilight (春薄明) / peony-glow (牡丹陽) / hydrangea-dusk (紫陽花宵) / wisteria-moon (藤霞月) / kerria-bloom (山吹陽) / crimson-camellia (鮮椿青) / hydrangea-morn (紫陽朝) / spring-aureate (春金苑)

### 🌿 P2 翠彩 (Verdant Spectrum) - グリーン・中問
verdant-rose (翠紅園) / golden-verdant (山吹翠苑) / young-sprout (若苗野) / moss-blossom (苔月華) / azure-orchid (群青蘭) / early-jade (早春翠) / vermilion-garden (朱檀苑) / crimson-jade (朱赭翠) / golden-harvest (黄金穂)

### 🌙 P3 玄彩 (Mystica Spectrum) - パープル・難問
moonfrost-violet (月霜紫) / starlit-amethyst (星辰深紫) / wine-galaxy (葡萄銀河) / dusk-violet (黄昏菫) / hydrangea-afterglow (紫陽花残光) / sapphire-moon (紺碧月華) / dawn-nebula (暁星雲) / violet-firework (紫煙花火) / emerald-violet (青翠菫光)
