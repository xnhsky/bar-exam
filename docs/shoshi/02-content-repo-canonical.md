# コンテンツリポジトリ `shoshi-exam` の正典設計 v0.1

> 確定日 2026-10-18。`00-master-plan.md` §3 の正典順位 3 位。Phase 2a（bootstrap）と Phase 3（gold）の仕様。
> bar-exam と同じ思想＝**canonical 物理複製→スロット鋳造／決定論ツールで伝播／機械ゲート三層**。

---

## 1. リポジトリ構造（bar-exam と対称・番号は司法書士用に振り直す）

```
shoshi-exam/
  CLAUDE.md                      司法書士版の指示書（§6）
  canonical/
    GENESIS-CARD.html            択一 _lex の起点（bar-exam から複製・§4 追補）
    GENESIS-CARD.placeholder.html
    GENESIS-CORE.html            択一 公式5択の起点
    GENESIS-CORE.placeholder.html
    SOLVE-NAV.html               解法ナビ エンジン
    STYLUS.html                  HX ひな形の起点（Phase 3 で本文を鋳造）
    STYLUS.placeholder.html
    THOTH.html                   KX 記述式の起点（Phase 3 で本文を鋳造）
    THOTH.placeholder.html
  spec/   docs/   prompts/   scripts/   references/   locks/
  inputs/000_TX/{00N_科目}/{N}.pdf          1問1PDF（git 非管理・Drive 共有）
  inputs/002_KX/{010|011}/{年度}.pdf        記述式（問題＋答案用紙）
  outputs/000_TX/{00N_科目}/{接頭辞}TX{NNN}.html          公式5択（Lexia 非取込）
  outputs/ux/000_TX/{00N_科目}/{接頭辞}TX{NNN}_lex.html   Lexia 用
  outputs/001_HX/{010|011}/{接頭辞}HX{NNN}.html
  outputs/002_KX/{010|011}/{接頭辞}KX{NNN}.html
  references/statutes/*.md       条文索引（build-statute-index 流用）
  references/precedents/*.md     先例索引（新設）
  references/kx-aliases.json     記述式の別名表（01 §2-5-bis・Lexia も読む）
```

Lexia（SCRIBA）の同期フォルダ＝`outputs/ux/000_TX`・`outputs/000_TX`（`_lex` 不在の移行期のみ）・`outputs/001_HX`・`outputs/002_KX`・`references`。

## 2. 科目表（11 科目・単一情報源は `scripts/subjects.json`）

| # | フォルダ | 接頭辞 | 科目 | 部 | 択一問数 | 記述 |
|---|---|---|---|---|---|---|
| 001 | `001_憲法` | `憲` | 憲法 | 午前 | 3 | — |
| 002 | `002_民法` | `民` | 民法 | 午前 | 20 | — |
| 003 | `003_刑法` | `刑` | 刑法 | 午前 | 3 | — |
| 004 | `004_商法会社法` | `商` | 商法・会社法 | 午前 | 9 | — |
| 005 | `005_民事訴訟法` | `民訴` | 民事訴訟法 | 午後 | 5 | — |
| 006 | `006_民事執行法` | `民執` | 民事執行法 | 午後 | 1 | — |
| 007 | `007_民事保全法` | `民保` | 民事保全法 | 午後 | 1 | — |
| 008 | `008_司法書士法` | `書士` | 司法書士法 | 午後 | 1 | — |
| 009 | `009_供託法` | `供託` | 供託法 | 午後 | 3 | — |
| 010 | `010_不動産登記法` | `不登` | 不動産登記法 | 午後 | 16 | ◯ |
| 011 | `011_商業登記法` | `商登` | 商業登記法 | 午後 | 8 | ◯ |

- 接頭辞の正規表現は **長い方を先に**：`民訴|民執|民保|不登|商登|供託|書士|憲|民|刑|商`。
- `subjects.json` の形：`[{ "dir":"010_不動産登記法", "prefix":"不登", "name":"不動産登記法", "session":"pm", "mcq":16, "kijutsu":true }, …]`。
  validator（G14 の命名整合）・TJR の科目検知順・Lexia の試験プロファイルは **この JSON から生成**する（手書きの重複表を持たない）。
- 科目検知順（TJR）＝比重順：不登法 → 民法 → 商登法 → 会社法 → 民訴 → 供託 → 憲法 → 刑法 → 民執 → 民保 → 司法書士法。

## 3. 番号抽出と入力

- 択一：bar-exam §2-3 と同じ（PDF 名の最初の連続数字→3 桁ゼロ埋め・抽出不能は中断して確認）。番号は科目内通し番号（年度順に振る。年度↔番号は `docs/tx-index.md` に記録）。
- 記述式：`inputs/002_KX/{010|011}/{年度}.pdf`（例 `R06.pdf`）。番号は `docs/kx-index.md` の対応表で確定（`不登KX001`＝最古年度から昇順）。
- 入力 PDF は法務省公表の試験問題を 1 問 1 PDF に分割したもの（bar-exam の「抽出PDF」運用と同じ）。git 非管理・Drive 往復 2 本（`tx-push-inputs-to-drive.ps1`／`tx-pull-inputs-from-drive.ps1` を流用）。
- **市販問題集の解説文は取り込まない**（解説は自前執筆。正答率の数値だけ「出所」として参照してよい＝G72 の帯判定に使う）。
- 記述式の正解は非公表。模範は **自作して一次確認**（条文・先例・登録免許税法）。`verified` を JSON に必ず書く（01 §2-10）。

## 4. 択一 TX の司法書士追補（canonical 複製後に加える・S ゲート）

| ID | 追補 | 内容 |
|---|---|---|
| S1 | 先例カード | `.tx-basis-item.is-precedent`（新種別）。見出しラベル「先例」、本文の役割フォントは **条文系**（`judgment-text` を付けない＝G77 の単一情報源 `tx_basis_roles.py` に種別を追加）。引用形式「昭和/平成/令和 n.n.n 民三/民商 第n号」 |
| S2 | 法令階層の明記 | BASIS の条文 head に法令名を必ず書く（不動産登記法／不動産登記令／不動産登記規則／商業登記法／商業登記規則／登録免許税法／供託法／供託規則）。ERROR |
| S3 | 法令基準日ノート | `tx-current-law-note` を流用し「確認日・当該年 4/1 施行」を明記。直近改正（相続登記義務化・住所等変更登記義務化・会社法改正）前の年度は必須 |
| S4 | 正答率の出所 | §5 宣言に出所（過去問集名・年版）を 1 行添える（G71/G72 はそのまま） |

その他の TX 規律（二系統・○×反転防止 G60・自己完結 G65/G70/G79/G80・原文不可侵 G19/G74/G75・パレット G71/G72・図解 G67/G78・答案圧縮 G73・ものがたり帯・GIST ストーリー G81・DEDUP G82・🔰導入 G84）は **bar-exam の現行 v13.1.0 をそのまま継承**。司法書士の択一は組合せ型が主なので、`_lex` は 350 方式（記号→実体置換）が既定になる。

## 5. bar-exam から複製するもの（Phase 2a・初回だけ。以後は shoshi-exam が独立に保守）

| 区分 | 複製対象 |
|---|---|
| canonical | `GENESIS-CARD.html`／`.placeholder.html`／`GENESIS-CORE.html`／`.placeholder.html`／`SOLVE-NAV.html`。STYLUS/THOTH の素材として `ARIADNE.html`（想起カード・骨子パズル・下書き・周回モードの CSS/JS 区画を抽出するため。複製後に不要部を落とす） |
| scripts（検証） | `validate-tx-core.py`＋`tx_*.py`（basis_roles／gist_story／intro_rules／palette_rules／person_symbols／source_text／sysmap_geom／v15_rules）／`check-tx-lex-engine.py`／`check-duplicates.py`／`check-font-vars.py`／`check-lexia-preflight.py`／`check-stale-law-refs.py`／`check-cross-file-claims.py` |
| scripts（伝播・修復） | `tx-sysmap-fit.py`／`tx-lex-repaint-palette.py`＋`tx-palette-templates.json`／`tx-restore-original.py`／`tx-gist-story.py`／`tx-v15-dedup.py`／`tx-intro.py`／`tx-lex-verdict-redesign.py`／`tx-basis-role-fix.py`／`fix-solvenav-step-mismatch.py` |
| scripts（運用） | `stamp-created-date.py`／`stamp-staged.py`／`git-hooks/pre-commit`／`install-hooks.sh`／`TJR.ps1`／`tx-v13-runner.ps1`／`tjr-claim.ps1`／`tjr-audit.py`／`tx-push-inputs-to-drive.ps1`／`tx-pull-inputs-from-drive.ps1` |
| prompts | `new-tx-headless-v13.md`（科目表・接頭辞・出力先を shoshi 用に差替） |
| docs | `tx-v12.2.1-inline-lock.md`（参照コピー・改定しない）／`canonical-revision-migration-playbook.md`／`content-audit.md`／`run-patterns.md`（司法書士向けに縮約） |
| memory/references | `reference_palette_v3.md`（復旧済み hex 正典）／`docs/palette-v3_2.pdf` |

複製直後にやること：①科目ハードコード（`刑訴|民訴|行政|刑|憲|民|商` の正規表現・`001_刑法` 等のフォルダ表）を **`subjects.json` 読み出しに置換**（validate の G14・check-duplicates・runner・prompt）②bar-exam 固有の規律文（刑法 corpus の実績・TJR-S/G/D/I の残件管理）を CLAUDE.md から落とす③`validate-tx-core.py` が bar-exam の gold（刑TX362 等）を参照している箇所を shoshi の gold に差し替える（Phase 3 後）。

## 6. shoshi-exam の CLAUDE.md 骨子（Phase 2a で作る）

1. 入口ルール（番号指定だけで active 正典へ流す・`docs/canonical-lineage.md` を最初に読む）
2. 命名規則（§2 の 11 科目・TX/HX/KX）
3. TX の運用（bar-exam v13.1.0 を継承・S1〜S4 追補・解説品質レビューと最新法令レビューは必須＝「最上位モデル・推論最大・執筆者本人の自己照合 1 回」）
4. HX/KX の運用（`docs/shoshi/01-kijutsu-html-contract.md` を正典として参照。`kx-build.py`／`hx-build.py` で組み、手書き禁止）
5. 検証（validate-tx-core／validate-hx／validate-kx／check-duplicates／check-lexia-preflight）と push 規律（PASS のみ・1 問 1 commit・pre-commit フック）
6. TJR（T=択一／H=ひな形／K=記述式／F=修復・claim・ESCALATE）
7. 絶対禁止（bar-exam §7 の共通項＋01 §4）
8. 二台運用と本線（master 一本・作業前 pull・入力は Drive 往復）

## 7. TJR 移植（Phase 4 の準備・Phase 2a で雛形だけ）

| 記号 | ストリーム | エンジン |
|---|---|---|
| F | 修復（毎バッチ先頭・`tjr-audit.py`） | 流用 |
| T | 新規 TX（11 科目を §2 の検知順で均等配分） | `tx-v13-runner.ps1`（科目表差替） |
| H | HX ひな形（登記類型リスト `docs/hx-index.md` を若番から） | `hx-runner.ps1`（新規・headless が JSON 仕様→`hx-build.py apply`） |
| K | KX 記述式（`docs/kx-index.md` を若番から） | `kx-runner.ps1`（新規・headless が JSON 仕様→`kx-build.py apply`） |

headless は Opus 5.5 固定・10 本/バッチ・PASS のみ commit・2 回失敗で ESCALATE（bar-exam と同じ）。

## 8. Phase 3 gold の範囲（最上位モデル）

1. **不登TX×5**（二系統）。司法書士の択一を TX 契約で通す実証（組合せ型→350 方式・先例カード S1・法令階層 S2）。
2. **不登HX×1 群**（所有権移転（売買）を推奨：添付情報・税・申請人の 3 型が全部出る）。STYLUS 正典の本文鋳造を兼ねる。
3. **不登KX×1**（直近の現行法で解ける年度）。THOTH 正典の本文鋳造を兼ねる。JSON 仕様→`kx-build.py`→validate-kx PASS→SCRIBA で実機採点→SM-2 に乗ることを確認。
4. gold 3 点の **内容レビュー**（執筆者本人の自己照合 1 回＋的を絞った一次確認＝条文・先例・登録免許税）。
5. ユーザー承認後に placeholder 契約（STYLUS/THOTH）を固定し、Phase 4 の prompts（`prompts/new-hx-headless.md`／`new-kx-headless.md`）を書く。
