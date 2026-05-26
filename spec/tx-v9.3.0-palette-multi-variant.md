# TX v9.3.0 PALETTE-MULTI-VARIANT 仕様書

**v9.2.0 DEEP-DIVE からの差分仕様書（delta spec）**

> v9.3.0 は v9.2.0 DEEP-DIVE の**構造体・density 規律・theory_deep_dive・mindmap 三種・flowchart_v2 等は全て据置**とし、**配色 spec のみを多変量化**した進化仕様。v9.2.0 spec 本体（`spec/tx-v9.2.0-deepdive-core.md`）を base としつつ、本仕様書の §32 / §32-5 / §32-bis / §32-ter / §31 S88・S92 / AP-47 で **override** する。

---

## v9.3.0-palette-multi-variant (2026-05-26)

### 改訂サマリ（1 系統 5 項目）

1. **27 サブパレット導入**: 単一配色（P1/P2/P3 各 1 種）から **3 カテゴリ × 9 サブパレット = 27 種類**に拡張
2. **カラーパレット命名**: ピンク系 = **桜彩 / Sakura Spectrum** / グリーン系 = **翠彩 / Verdant Spectrum** / パープル系 = **玄彩 / Mystica Spectrum**
3. **HSL アルゴリズム派生**: アンカー 3 色（accent / mid / base）から派生色 24 個を HSL 計算で自動導出
4. **seed-based ランダム選択**: `random.seed(int(problem.id))` で同問題は常に同サブパレット（再現性確保）
5. **JSON override 機構**: `sub_palette_id` フィールドで明示指定可能（auto / explicit のハイブリッド運用）

### 構造変更

- §32 改訂: 27 色変数 → 27 サブパレット × 各 27 色 = 729 hex 値（うち機能色 14 個は全サブパレット共通固定）
- §32-5 強化: HSL アルゴリズム明文化（具体的パラメータ表 8 件）
- §32-bis 据置: 4 戦略は維持（サブパレット選択とは独立軸）
- §32-ter 新規: サブパレット選択ロジック仕様
- §31 検査: S88 改訂（HSL 導出値妥当性）+ S92 新規（サブパレット ID 整合性）
- AP-47 新規: サブパレット ID 不整合

### 内容追加

- カラーパレット原典: ingectar-e COLOR PICKUP #16 / #22 / PURPLE
- footer-spec feature-tag: 31 件 + 4 件追加 = **35 件**（v9.2.0 の 33 件 + `palette-multi-variant` / `hsl-derivation` / `sub-palette: [名前]` × 2 軸）

### 設計原則

- v9.2.0 既存 5 ファイル（303/304/305/306/307）は**完全据置**（v9.2.0 baseline 維持）
- v9.3.0 は新規生成 308 以降に適用
- HSL 計算は Python colorsys モジュールで標準実装
- 絶対派生 3 個（neutral-cream / contrast-warm / contrast-cool）は全サブパレット共通固定（既存 v9.2.0 値継承）
- 機能色 14 個（recall / rank / freq / hl / tan 系）は §32-bis-5 通り全サブパレット共通固定

### 遡及範囲

- 308 以降の新規生成: spec_version="v9.3.0" 適用
- 既存 v9.2.0 ファイル: 据置（再生成しない）
- v9.1.0 / v8.11.7 以下: 据置（version-aware）

---

## §32. 3 パターン × 9 サブパレット色変換ルール（v9.3.0 改訂）

### §32-1. パターン判定（正答率紐付け・v9.2.0 継承）

| パターン | 名称 | 紐付け | 印象 |
|---|---|---|---|
| **P1** | 桜彩 / Sakura Spectrum | 正答率 ≥70%（易問） | ピンク系・親しみ・春のエネルギー |
| **P2** | 翠彩 / Verdant Spectrum | 正答率 40-70%（中問） | グリーン系・自然・落ち着き |
| **P3** | 玄彩 / Mystica Spectrum | 正答率 <40%（難問） | パープル系・神秘・集中 |

### §32-2. P1 absolute canon 鉄則（v9.2.0 継承・改訂なし）

P1 absolute canon は v9.2.0 spec §32-2 通り。`#7a1f37` / `#d4533c` 等の旧 P1 値は **v9.2.0 専用**として保持され、v9.3.0 では P1 が「桜彩カテゴリ・9 サブパレット」として再構成される。両 spec の混在は禁止（per-file spec_version で識別）。

### §32-3. 27 色変数 → 27 × 27 色変数

v9.2.0 では `:root{}` ブロックに 27 色変数を定義。v9.3.0 では **27 サブパレット × 27 色変数 = 729 値**を `_PALETTES_V93` 定数で render.py 側に保持し、サブパレット選択結果に応じて `:root{}` ブロックを動的生成する。

#### 27 色変数の役割分類（不変）

| カテゴリ | 個数 | 派生種別 | サブパレット連動 |
|---|---|---|---|
| アンカー 3 色（accent / mid / base） | 3 | 直接定義 | ○ |
| 相対派生 8 個（accent-light / accent-darker / accent-soft / accent-soft-2 / mid-warm / mid-cool / mid-soft / surface-tint） | 8 | HSL 計算導出 | ○ |
| 絶対派生 3 個（neutral-cream / contrast-warm / contrast-cool） | 3 | 固定値 | × |
| 機能色 14 個（recall / rank / freq / hl / tan 系） | 14 | 固定値 | × |
| **合計** | **28** | | |

注: v9.2.0 spec §32-5 では「派生色 10 個」と表記されていたが、これは相対派生 7 個 + 絶対派生 3 個の合計を指す。v9.3.0 では `--accent-soft` も HSL 計算派生に統合し、相対派生を 8 個に拡張する（v9.2.0 では `--accent-soft` が 27 色 base 表に含まれていた）。全体としては 27 色変数 + accent-soft 1 個 = 28 色変数になるが、機能等価で v9.2.0 既存仕様と互換性を保つ。

### §32-4. override の厳密形式

v9.3.0 では `:root{}` ブロック内に**サブパレット ID コメント**を必須記載：

```css
:root {
  /* sub-palette: 桜霞 (sakura-haze) / category: P1 / spec: v9.3.0 */
  --accent: #E3969F;
  --mid: #A0C3D9;
  --base: #699091;
  --accent-light: #ECB5BC;     /* HSL 導出: accent L+15% */
  --accent-darker: #B36B73;    /* HSL 導出: accent L-20% */
  --mid-warm: #C8B2C8;          /* HSL 導出: mid H+15° */
  /* ... 残り 21 色 */
}
```

S92 検査が `sub-palette:` コメントと feature-tag の `sub-palette: [名前]` の整合性を検証する。

### §32-5. HSL 派生アルゴリズム（v9.3.0 強化版）

#### §32-5-1. 派生色の分類（v9.2.0 §32-5-1 改訂）

| 分類 | 個数 | 値の挙動 | サブパレット連動 |
|---|---|---|---|
| **アンカー 3 色** | 3 | 各サブパレット表で直接定義 | ○ |
| **相対派生（HSL 計算）** | 7 | アンカー色から計算導出・サブパレットごとに値が変わる | ○ |
| **絶対派生** | 3 | 全サブパレット共通固定 | × |

#### §32-5-2. HSL 派生パラメータ表（v9.3.0 新規・確定）

```python
HSL_DERIVATIONS = {
    # 派生色名               派生元   H 増減   S 増減   L 増減
    "accent-light":         ("accent",  0,   -8,    +13),
    "accent-darker":        ("accent",  0,   +5,     -4),
    "accent-soft":          ("accent",  0,  -25,    +18),
    "accent-soft-2":        ("accent",  0,  -15,    +25),
    "mid-warm":             ("mid",    +8,   +5,    +6),
    "mid-cool":             ("mid",    -8,   -5,    +0),
    "mid-soft":             ("mid",     0,  -10,    +20),
    "surface-tint":         ("accent",  0,  -20,    +30),
}
```

これらのパラメータは v9.2.0 既存配色（P1 朱赤系）の派生色から逆算した実用値であり、機能的妥当性（背景・ボーダー・テキストの可読性確保）を担保する。v9.3.0 では 27 サブパレット全てで同一パラメータを適用することで、サブパレット間で一貫した派生関係を確保する。

**設計判断**: 27 サブパレットの中にはアンカー色 L 値が 70-90% の淡い色が多く存在するため、dL は最大 +30% に抑制した。これにより白飛び（#FFFFFF）を回避し、全サブパレットで派生色の識別性を確保する。一方、これにより v9.2.0 P1（accent L=30%）における surface-tint #fef9fb のような「ほぼ白」の派生色は再現できないが、v9.3.0 の主目的は「複数サブパレット対応の機能的妥当性確保」であり、v9.2.0 完全互換ではない（v9.2.0 既存 5 ファイルは spec_version 据置で保護される）。

- H（色相）の単位は度（0-360）
- S（彩度）/ L（明度）の単位は %（パーセントポイント加減算）
- 結果が範囲外（H<0 / H≥360）の場合は modulo 演算で循環

#### §32-5-3. Python 実装（参考）

```python
import colorsys

def hex_to_hsl(hex_str: str) -> tuple[float, float, float]:
    """#RRGGBB → (h[0-360], s[0-100], l[0-100])"""
    hex_clean = hex_str.lstrip("#")
    r, g, b = (int(hex_clean[i:i+2], 16) / 255.0 for i in (0, 2, 4))
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return (h * 360, s * 100, l * 100)

def hsl_to_hex(h: float, s: float, l: float) -> str:
    """(h, s, l) → #RRGGBB"""
    h_norm = (h % 360) / 360.0
    s_norm = max(0, min(100, s)) / 100.0
    l_norm = max(0, min(100, l)) / 100.0
    r, g, b = colorsys.hls_to_rgb(h_norm, l_norm, s_norm)
    return "#" + "".join(f"{int(c * 255):02X}" for c in (r, g, b))

def derive_relative(anchor_hex: str, dh: int, ds: int, dl: int) -> str:
    """アンカー色から HSL 差分で派生色を導出"""
    h, s, l = hex_to_hsl(anchor_hex)
    return hsl_to_hex(h + dh, s + ds, l + dl)
```

#### §32-5-4. 絶対派生 3 個（全サブパレット共通固定・v9.2.0 継承）

| # | 変数名 | hex | 主用途 |
|---|---|---|---|
| 1 | `--neutral-cream` | `#f4ede0` | KEY box 背景（紙質風） |
| 2 | `--contrast-warm` | `#d97a4f` | フローチャート不成立（テラコッタ） |
| 3 | `--contrast-cool` | `#6a8aa8` | 学説対立 cool 行帯（ダスティブルー） |

#### §32-5-5. 検証（S88 改訂）

- S88（派生色変数導出値検査）が 7 相対派生 + 3 絶対派生 + 14 機能色 = 24 個の `:root` 内 hex 形式定義を検査
- 相対派生はアンカー色からの HSL 差分が §32-5-2 パラメータと一致することを検証（許容誤差 ±1 hex 値）
- 違反時 AP-45「派生色変数欠落」または AP-47「サブパレット ID 不整合」

---

## §32-bis. AI 自由設計運用条項（v9.2.0 据置）

v9.2.0 §32-bis-1〜§32-bis-6 はそのまま継承。4 戦略（同系統調和 / 寒色×暖色対比 / 紙質風 / 黒板風）は据置で、サブパレット選択とは独立した軸として共存する。

戦略選択は feature-tag に `palette-strategy: [戦略名]` で記載（v9.2.0 通り・必須）。

### §32-bis-1. 戦略選択禁止条件の追加（v9.3.0）

v9.2.0 §32-bis-4 既存規律に加え、以下を追加：

| 条件 | 強制戦略 |
|---|---|
| カテゴリ P3 玄彩 + ロマンティック系サブパレット（P3-1/P3-2/P3-7/P3-9） | 同系統調和を強制 |

---

## §32-ter. サブパレット選択ロジック（v9.3.0 新規）

### §32-ter-1. 選択フロー

```
1. JSON に sub_palette_id があれば → explicit 経路（auto をスキップ）
2. なければ correct_rate からカテゴリ判定:
   - correct_rate ≥ 70 → P1 桜彩
   - 40 ≤ correct_rate < 70 → P2 翠彩
   - correct_rate < 40 → P3 玄彩
3. random.seed(int(problem.id)) を設定
4. SUBPALETTES_V93[category] から random.choice() で 1 件選択
5. 選択された subpalette_id に基づき derive_palette_v93() で 27 色変数を生成
6. :root{} ブロックを HTML に注入
7. feature-tag に sub-palette: [名前 (英語コード)] を追加
```

### §32-ter-2. JSON フィールド仕様

```json
{
  "spec_version": "v9.3.0",
  "id": "308",
  "correct_rate": "75%",
  "sub_palette_id": "sakura-haze",  // optional: 明示指定（unset で自動選択）
  ...
}
```

- `sub_palette_id` が unset → seed=problem.id で自動選択
- `sub_palette_id` が文字列 → そのサブパレットを使用
- `sub_palette_id` が **異なるカテゴリのもの**（例: P1 問題で P3-1 を指定）→ AP-47 違反として S92 で検出

### §32-ter-3. 27 サブパレット定義表

#### 🌸 P1 桜彩 / Sakura Spectrum（ピンク系・易問・正答率 ≥70%）

| ID | 日本語名 | 英語コード | accent | mid | base |
|---|---|---|---|---|---|
| P1-1 | 桜霞 | `sakura-haze` | #E3969F | #A0C3D9 | #699091 |
| P1-2 | 春薄明 | `spring-twilight` | #EDBFBF | #F2E8CB | #B4D9E2 |
| P1-3 | 牡丹陽 | `peony-glow` | #C05191 | #AE78AB | #E3E6DF |
| P1-4 | 紫陽花宵 | `hydrangea-dusk` | #A0B1D8 | #E6E6DB | #DC7783 |
| P1-5 | 藤霞月 | `wisteria-moon` | #BD9DC4 | #DFA4B4 | #E2C3B1 |
| P1-6 | 山吹陽 | `kerria-bloom` | #E8E9C7 | #B2C0C9 | #E08B92 |
| P1-7 | 鮮椿青 | `crimson-camellia` | #005FAA | #D54B8D | #EDB886 |
| P1-8 | 紫陽朝 | `hydrangea-morn` | #DFE6E9 | #CF82AD | #7B7FB8 |
| P1-9 | 春金苑 | `spring-aureate` | #E4E594 | #C3B4D1 | #E190A2 |

#### 🌿 P2 翠彩 / Verdant Spectrum（グリーン系・中問・正答率 40-70%）

| ID | 日本語名 | 英語コード | accent | mid | base |
|---|---|---|---|---|---|
| P2-1 | 翠紅園 | `verdant-rose` | #3F9C54 | #DE6079 | #E7E7E3 |
| P2-2 | 山吹翠苑 | `golden-verdant` | #5E7960 | #FFDF76 | #78A95B |
| P2-3 | 若苗野 | `young-sprout` | #648B45 | #9ABE74 | #C3CE6A |
| P2-4 | 苔月華 | `moss-blossom` | #84C46E | #C0EBE6 | #78A991 |
| P2-5 | 群青蘭 | `azure-orchid` | #3C828F | #A989B8 | #F7F0B5 |
| P2-6 | 早春翠 | `early-jade` | #A6CEC1 | #68BC83 | #EEEFAF |
| P2-7 | 朱檀苑 | `vermilion-garden` | #438B48 | #DD792E | #DDDEE0 |
| P2-8 | 朱赭翠 | `crimson-jade` | #50804C | #ECE0A7 | #BD513A |
| P2-9 | 黄金穂 | `golden-harvest` | #7BA980 | #E7A93B | #E2D050 |

#### 🌙 P3 玄彩 / Mystica Spectrum（パープル系・難問・正答率 <40%）

| ID | 日本語名 | 英語コード | accent | mid | base |
|---|---|---|---|---|---|
| P3-1 | 月霜紫 | `moonfrost-violet` | #CFB4C5 | #998BBE | #857A8C |
| P3-2 | 星辰深紫 | `starlit-amethyst` | #DDC3DC | #4B2680 | #7E5B9F |
| P3-3 | 葡萄銀河 | `wine-galaxy` | #8D3B51 | #BC9FD7 | #B2618E |
| P3-4 | 黄昏菫 | `dusk-violet` | #AD76C7 | #F4AF62 | #F1A4D8 |
| P3-5 | 紫陽花残光 | `hydrangea-afterglow` | #B86E8C | #DCB0CB | #F2DDDA |
| P3-6 | 紺碧月華 | `sapphire-moon` | #F39DF4 | #2E2979 | #9B95EB |
| P3-7 | 暁星雲 | `dawn-nebula` | #E6A1AB | #C1A8D0 | #99D7FF |
| P3-8 | 紫煙花火 | `violet-firework` | #E9DFDA | #905999 | #99846B |
| P3-9 | 青翠菫光 | `emerald-violet` | #8CAFA9 | #CBAEDE | #4A4AB3 |

### §32-ter-4. 命名規律

- **日本語名**: 漢字 2-4 文字を基本とし、和の情緒を喚起する語彙を選定
- **英語コード**: kebab-case 形式（`sakura-haze` 等）。render.py の dict key として使用
- **絵文字接頭辞**: 🌸 P1 / 🌿 P2 / 🌙 P3
- **footer-spec 表記**: `sub-palette: 桜霞 (sakura-haze)`（日本語名 + 英語コード括弧書き）

---

## §31. SEVERE 自己検証 S1〜S92（v9.3.0 改訂）

### 既存 S1〜S91 据置

v9.2.0 §31 の S1-S91 はそのまま継承。S85-S91 が「TX v9.2.0 DEEP-DIVE」含む場合のみ起動するのと同様、S92 は「TX v9.3.0 PALETTE-MULTI-VARIANT」含む場合のみ起動する。

### S88 改訂（派生色変数導出値検査・v9.3.0 強化）

#### v9.2.0 規律（継承）

- :root 内に 10 派生色変数の hex 形式定義が存在
- 違反時 AP-45「派生色変数欠落」

#### v9.3.0 追加規律

- spec_version="v9.3.0" 時、相対派生 7 個の値がアンカー色からの HSL 差分（§32-5-2 パラメータ）と一致することを検証
- 許容誤差: ±1 hex 値（HSL → RGB 変換の丸め誤差を考慮）
- 違反時 AP-47「サブパレット ID 不整合」

### S92 新規（サブパレット ID 整合性検査・v9.3.0 専用）

#### 検査項目

1. `:root{}` 内の `sub-palette:` コメント存在検査
2. footer-spec feature-tag に `sub-palette: [日本語名] ([英語コード])` 形式の tag 存在検査
3. `:root{}` コメントと feature-tag の英語コード一致検査
4. JSON `correct_rate` から導出されるカテゴリ（P1/P2/P3）と subpalette_id の **prefix 一致検査**
   - 例: P1 問題（correct_rate≥70%）で sub_palette_id="moonfrost-violet"（P3）→ 違反
   - 例外: JSON で `sub_palette_id` を明示指定し、その理由を `palette_override_reason` で記載した場合

#### 違反時の対応

- AP-47「サブパレット ID 不整合」として ERROR 出力
- ERROR 1 件で validate-tx 全体 FAIL

### S91 据置（教授解説密度検査・v9.2.0 通り）

教授解説密度 150/400/300/300 字規律は v9.3.0 でも完全継承。

---

## §31-6. アンチパターンカタログ AP-1〜AP-47（v9.3.0：AP-47 追加）

### AP-1〜AP-46 据置

v9.2.0 §31-6 通り。

### AP-47（v9.3.0 PALETTE-MULTI-VARIANT 新規）：サブパレット ID 不整合

#### 検出パターン

1. `:root{}` 内に `sub-palette:` コメントが存在しない
2. footer-spec feature-tag に `sub-palette: ...` 形式の tag が存在しない
3. `:root{}` コメントの英語コードと feature-tag の英語コードが不一致
4. correct_rate と subpalette_id のカテゴリ不一致（override_reason 未記載時）
5. 相対派生 7 個の値がアンカー色からの HSL 差分パラメータと不一致（許容誤差 ±1 hex 値超過）

#### 修正アクション

- subpalette_id を JSON で明示指定するか、削除して auto 選択に戻す
- `derive_palette_v93()` の HSL 計算結果を `:root{}` に正しく注入する
- カテゴリ override が意図的であれば `palette_override_reason` フィールドに理由を記載

---

## §33. footer-spec feature-tag（v9.3.0 改訂）

### v9.2.0 footer feature-tag 31 件（据置）

v9.2.0 spec §33 通り。

### v9.3.0 追加 feature-tag

| # | tag | 役割 |
|---|---|---|
| 32 | `palette-multi-variant` | spec 全体特性（27 サブパレット運用） |
| 33 | `hsl-derivation` | HSL アルゴリズム派生方式 |
| 34 | `OVERRIDE_PATTERN`（P1/P2/P3） | カテゴリ表示 |
| 35 | `palette-strategy: [戦略名]` | §32-bis 戦略選択（v9.2.0 据置） |
| 36 | `sub-palette: [日本語名] ([英語コード])` | サブパレット個別表示 |

v9.3.0 footer feature-tag **合計 35 件**（v9.2.0 31 固定 + 4 動的）

---

## §A. v9.3.0 移行・運用ガイド

### A-1. spec_version の判定

- problem JSON の `spec_version` フィールド値が `"v9.3.0"` の場合に本仕様が適用される
- v9.2.0 / v9.1.0 / v8.11.7 以下は据置（version-aware）

### A-2. 既存 v9.2.0 ファイルとの並存

- 303/304/305/306/307 は v9.2.0 据置（再生成しない）
- CP gate は v9.2.0 / v9.3.0 両方を自動 SKIP（spec_version aware・既存仕様）

### A-3. 新規生成時のフロー

```
1. problem JSON に spec_version="v9.3.0" を設定
2. correct_rate を設定（必須・サブパレット選択の入力）
3. sub_palette_id は optional（unset で自動選択推奨）
4. render.py が SUBPALETTES_V93 + derive_palette_v93 で 27 色変数を計算
5. :root{} に sub-palette: コメント + 27 色変数を注入
6. footer-spec に palette-multi-variant + hsl-derivation + sub-palette: タグを追加
7. validate-tx の S88/S92 で整合性検証
```

### A-4. 再現性保証

- `random.seed(int(problem.id))` により同問題は何度 render しても同サブパレット
- 学習者の視覚記憶（「306 は桜霞色」等）が安定する
- ただし spec 改訂で SUBPALETTES_V93 を再配列すると seed 結果が変動するので、定数 dict の順序は仕様確定後変更しない

---

## §B. v9.3.0 完了基準

- [ ] spec/tx-v9.3.0-palette-multi-variant.md 完成 + commit
- [ ] scripts/render.py に SUBPALETTES_V93 / derive_palette_v93 / select_subpalette_v93 実装
- [ ] scripts/render.py の build_slot_dict で spec_version="v9.3.0" 分岐実装
- [ ] scripts/validate-tx.py の S88 改訂 + S92 新規実装
- [ ] .claude/commands/v93-batch.md 作成
- [ ] 308 で試験生成・サブパレット選択ロジック動作確認
- [ ] CP gate 不変確認（PASS=11 / DIFF=1 / SKIP_v92=N / SKIP_v93=M）

---

## §C. v9.2.0 spec 本体への参照

本仕様書は **delta 仕様書**であり、以下の v9.2.0 規律は全て継承する：

- §0-tri〜§0-quad（ゼロベース再構築・コンテンツ独立性プロトコル）
- §1-bis（PDF 入力 → 出力ファイル命名規則）
- §2（PART 構成・navigation）
- §3-quater（12-role font system）
- §4-ter / §4-quater（DOM 骨格 / section-title sec-icon）
- §6-§29（PART A〜D / canonical 構造一式）
- §17-ter（C-4 学説対立 deep-dive）
- §22-tree / §22-radial / §22-flowchart-v2
- §24-§29（Readability / hanging-indent-grid 等）
- §31 S1-S91 検査（S88/S92 を除く部分）
- §31-6 AP-1-AP-46 アンチパターン
- §32-bis AI 自由設計運用条項

v9.3.0 は配色 spec を多変量化することのみを目的とし、構造体・density 規律・theory_deep_dive・mindmap 三種・flowchart_v2 等は v9.2.0 通り。

---

**END OF v9.3.0 PALETTE-MULTI-VARIANT SPEC**
