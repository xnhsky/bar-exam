# 配色 V3 リファレンス（11 名前付きパレット × 5 色 hex）

> **正典**。出典：`docs/palette-v3_2.pdf`（画像内 chip ラベルを一次値とする）。
> CLAUDE.md §3-4・`.claude/commands/new-tx.md` Phase 1-3〜1-5 が参照する
> 「正答率帯 → P1/P2/P3 → 帯内パレット選定 → 5 役割割当て」の hex 一覧。
>
> **来歴**：本ファイルは 2026-07-21 に復旧した（LEX-403）。それ以前はリポジトリに存在せず
> （参照だけが残った宙吊り状態）、生成セッションがパレット hex を引けないことが
> 「パレット工程スキップ→正典既定色のまま出荷」（_lex 483 本中 216 本）の一因だった。
> 機械ゲート＝`validate-tx-core.py` G71/G72・単一情報源＝`scripts/tx_palette_rules.py`。

---

## 帯 → パレット対応（正答率で自動判定）

| パターン | 正答率帯 | パレット候補 |
|:-:|:-:|:--|
| **P1** | ≥ 60% | Sweet Berry / Fresh Citrus / Rose Mist / Antique Pearl / Maison Blanche |
| **P2** | 40〜60% | Crystal Blue / Dusty Sage / Mint Tea / Fresh Mint |
| **P3** | < 40% | Twilight Violet / Sunset Harmony |

## 5 役割割当て（§3-4 と同一）

| 役割 | 比率 | CSS 変数 | 備考 |
|:--|:-:|:--|:--|
| ベース | 約70% | `--base` | **全問固定クリーム `#F7F1E9`**（2026-06-16 確定・パレット非依存） |
| メイン | 約25% | `--accent` | pastel chip をそのまま使わず **HSL darken（L≒46）した派生**。palette identity は `--accent-light` に chip 1 を保存 |
| アクセント | 約5% | `--mid` | 11 パレット内 chip から反対色を借用（palette 外 hex 禁止・L=55-65） |
| サブ1 | 残 | `--soft` | card 枠・border |
| サブ2 | 残 | `--light` | 補助 surface |
| 文字 | - | `--bg-dark` | L<40 可・雰囲気で AI 判断 |

---

## パレット一覧（PDF chip 5 色＋実運用の派生 accent）

> 「派生 accent」= corpus 実証済みテンプレ（`scripts/tx-palette-templates.json`・
> 逐語ブロック）の `--accent`。新規生成はこの値をそのまま使ってよい（chip1 darken 済み）。

### P1（≥60%・易しめ＝暖色系）

| ID | パレット | KEYWORDS | chip 1〜5 | 派生 accent |
|:-:|:--|:--|:--|:--|
| 05 | **Sweet Berry** | 甘美、可憐、みずみずしさ、優しさ | `#F2D4D7` `#E8B4BC` `#D4E2E9` `#E8E4E4` `#F9E7E7` | `#B86878` |
| 13 | **Fresh Citrus** | フレッシュ、元気、明るい、若々しい | `#F4E8B8` `#E8F4D9` `#F2D6C9` `#D9EBE8` `#F2EEE2` | `#B05F3C` |
| 03 | **Rose Mist** | 優しさ、女性らしさ、上品な可愛らしさ | `#FFE8E8` `#F5D4D4` `#F4ACB7` `#E8D6D7` `#FFE5E5` | `#AE5266` |
| 09 | **Antique Pearl** | 気品、優美、輝き、しっとり、エレガント | `#D4B5C4` `#E8E2EC` `#D9E5E5` `#E8E4DC` `#F2E6E6` | `#A07895` |
| 12 | **Maison Blanche** | 洗練、エレガント、都会的、優美さ | `#E8D4DC` `#D4E2E2` `#E2E2E2` `#F2E6E6` `#F5F2F2` | `#9A6B7E` |

### P2（40〜60%・中難度＝グリーン・ブルー系）

| ID | パレット | KEYWORDS | chip 1〜5 | 派生 accent |
|:-:|:--|:--|:--|:--|
| 06 | **Crystal Blue** | 透明感、清らか、みずみずしい、繊細な輝き | `#D4E6EB` `#F0E8ED` `#FFFCD6` `#DCE8E8` `#F5F0F2` | `#4A7C8C` |
| 14 | **Dusty Sage** | 落ち着き、上質、ナチュラル、シンプル、洗練 | `#BCCFC5` `#E2D5D5` `#D5E2E2` `#E8E0D4` `#F2F2EC` | `#50715E` |
| 02 | **Mint Tea** | 爽やか、癒し、みずみずしさ、清涼感 | `#AAD1B0` `#F0F4D8` `#F2F2EC` `#C3DBC5` `#E2EFE4` | （corpus 未使用・chip1 darken で派生） |
| 04 | **Fresh Mint** | 爽やか、癒し、ナチュラル、優しい清涼感 | `#D4E9E2` `#F9E4E4` `#B8DCD4` `#F2D6D6` `#E8F4F1` | （corpus 未使用・chip3 darken で派生） |

### P3（<40%・難問＝バイオレット系）

| ID | パレット | KEYWORDS | chip 1〜5 | 派生 accent |
|:-:|:--|:--|:--|:--|
| 10 | **Twilight Violet** | 優美、エレガント、しっとり、落ち着き | `#E2D4E2` `#F7EBD6` `#E8D4D4` `#D4E2E2` `#F8F2F2` | `#8E6E9A` |
| 11 | **Sunset Harmony** | ロマンティック、優美、柔らか | `#F2D6C9` `#E8B5B5` `#D4C6E2` `#F7E8D6` `#F2E6E6` | `#9A5C76` |

---

## 注記（出典 PDF との差分・既知の混乱源）

1. **Rose Mist の palette ID**：PDF のスター番号は `01`、corpus の §5 コメントは `03` で定着。
   判定（G72）は名前で行うため実害なし。本表は corpus 継続性を優先して `03` を記載。
2. **PDF 下段 COLOR 行の誤植**：Fresh Citrus（p.1 下段）の COLOR 行は Sunset Harmony の値が
   誤って印字されている。Antique Pearl / Crystal Blue / Mint Tea も chip ラベルと COLOR 行が
   一部食い違う。**画像内 chip ラベルが正**（corpus の `--accent-light` 実測と一致）。
3. **既定色との衝突（最重要）**：`#A07895`（Antique Pearl accent）は旧正典 GENESIS.html の
   既定 hex、`#8E6E9A`（Twilight Violet accent)は GENESIS-CORE の既定 hex と同一。
   「既定のまま」か「選定の結果」かは hex では区別できず、**§5 宣言コメント
   （`§5 V3 P{N} {Name} (palette ID: NN) ─ … AI 選定配色/帯別再選定`）の有無で判定**する
   （`validate-tx-core.py` G71/G72）。GENESIS-CARD の既定 `#A8666E` はどのパレットの
   正規 accent でもない（Sunset Harmony chip2 `#E8B5B5` の darken 派生）。
4. **Semantic exception**（§3-4）：✓緑 `#438B48`/`#7BA980`・🏆金 `#ffd54f`/`#ffaa00` は
   全パレットで palette 越境可。
