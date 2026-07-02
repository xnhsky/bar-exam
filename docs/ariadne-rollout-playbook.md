# ARIADNE 展開（ロールアウト）手順書 — v1.2.0 PLACEHOLDER-LOCK ／ v1.2.1 SIMPLE-BONE

> 既存 ARIADNE を現行正典へ移行し、新規 ARIADNE を安全・反復可能に量産するための「土台」と反復手順。
> 正典＝`spec/jx-ariadne-v1.2.0-core.md`（§17 SIMPLE-BONE 含む）／複製起点＝`canonical/ARIADNE.html`。
> 最終更新：2026-07-02。

---

## 0. 土台（展開前にこれが揃っていること）

- **複製起点 gold**：`canonical/ARIADNE.html` ＝ simple `.bone`・`.warn-box` 無・版 v1.2.0・`.bc-inst` の `.bi` 2カラム・`.draft-problem` 逐語（**A35〜A39 全 PASS を実測確認済み**）。ここから複製すれば新規・移行とも自動的にゲート適合する。
- **ゲート A1〜A39**（`scripts/validate-ariadne.py`）：構造 A1-A11／Lexia 周回契約 A12-A21／パズル A22／教示↔ドリル A23／模範答案 A24／深掘りアテナ級 A25／アテナジャンプ A26／作法 A27／論点冠番号 A28／RX A29／レイアウト A30-A31／入れ子 A32／品質 A33／**骨子 SIMPLE-BONE A34（matrix は WARN）**／**A35 深掘りテンプレ流用（ERROR）**／A36 版 drift・A37 未定義 box・A38 draft 逐語・A39 bc-inst（WARN）。
- **横断ゲート**：`scripts/check-ariadne-canonical.py`（canonical ＋ `outputs/ux/001_ARIADNE/**` を全走査・A35 が ERROR で落とす）。`scripts/check-lexia-preflight.py` に内蔵＝Lexia 同期前に必ず通る。
- **生成プロンプト**：`prompts/new-ariadne-headless.md`（simple bone 指示・検証 A1〜A39）。

---

## 1. 欠陥クラス → 直し方（監査で判明した型と担当ツール）

| 欠陥 | 検出 | 直し方 | 担当 |
|---|---|---|---|
| 骨子が matrix-bone（旧型） | A34 WARN | simple `.bone` へ蒸留（`.mline` フル文→1行に圧縮） | **LLM WF** |
| 深掘りが別問題流用（018型） | **A35 ERROR** | 元JX から本問論点で深掘り全面再鋳造 | **LLM WF** |
| 版スタンプ v0.3/v1.1.0 残置 | A36 WARN | v1.2.0 へ統一 | `ariadne-conform-fix.py` |
| `.warn-box` 未定義（素描画） | A37 WARN | `.key-box` へ | `ariadne-conform-fix.py` |
| `.draft-problem` 圧縮 | A38 WARN | `.problem .pq` 逐語へ | `ariadne-draftproblem-backfill.py` |
| `.bc-inst`/`.draft-digest` 2カラム欠 | A39/監査 | `.bi`/`.ddbody` 2カラム化 | `ariadne-restyle-backfill.py` 系 / fix WF |
| current-law-note 他問流用・汎用 | 監査(LLM) | 本問罪名・論点へ差替（拘禁刑の骨格は保持） | **LLM** |
| A32 入れ子外れ | A32 ERROR | 照合/模範/深掘りを `.skeleton` 内へ | fix WF / 手 |
| RX 配線まばら | A29 WARN | 想起カードに `data-rx` | `ariadne-backfill-rx-link.py` / LLM |
| 論点チップ冠番号 | A28 ERROR | 冠番号除去 | `ariadne-iss-denumber-backfill.py` |

---

## 2. 反復ループ（1バッチ＝数問ずつ・**直列**）

1. **骨子 simple 化（LLM WF）**：matrix-bone の問だけ対象。gold 見本＝`刑JX009_ARIADNE.html`（before/after）。
2. **機械修正**：`python -X utf8 scripts/ariadne-conform-fix.py "outputs/ux/001_ARIADNE/00N_科目/対象*.html"`（版＋warn-box・冪等）→ `python -X utf8 scripts/ariadne-draftproblem-backfill.py <file>`（draft 逐語）→ 必要なら `ariadne-restyle-backfill.py`／`ariadne-enhance.py`→`ariadne-autolink.py`。
3. **適合監査（LLM WF・read-only）**：A1〜A39 の全次元。**A35（深掘りテンプレ流用）を最優先で拾う**。
4. **内容修正（LLM WF）**：深掘り再鋳造（元JX を一次情報・gold 見本＝`刑JX018_ARIADNE.html`）／current-law-note の本問適合／A32 入れ子／RX 配線。
5. **検証**：`python -X utf8 scripts/check-ariadne-canonical.py`（ERROR 0）＋各問 `python -X utf8 scripts/validate-ariadne.py <file>`。
6. **commit**（pre-commit フック `scripts/git-hooks/pre-commit` が `lexia-genmeta` の生成日時を刻む）。

---

## 3. LLM が必須（機械置換で壊さない・CLAUDE.md §7）

- 骨子の一行蒸留（法的中身を保ったまま短フレーズ化）。
- 深掘りテンプレ流用の再鋳造（本問論点の条文/判例/学説/用語を**元JX の検証済み本文から**・創作禁止）。
- current-law-note の本問適合と最新法令・判例・学説レビュー（§11-1-bis）。

---

## 4. 運用上の注意（実地の教訓・2026-07-02）

- **ワークフローは直列で回す**。変換 WF と監査 WF を同時起動すると API レート制限で一部エージェントが落ちる（実害：監査 11 問中 6 問が rate-limited → `resumeFromRunId` で回収）。1 本ずつ。
- **A35 は ERROR**。展開前に `check-ariadne-canonical.py` を全コーパスで回すと、018 以外の潜在流用も炙り出して preflight を落とす（＝網が効いている）。移行途中で落ちすぎて困る場合のみ、`validate-ariadne.py` の `E('A35', …)` を `W(` に一時降格して段階移行する。
- **box-tip は要所主義**（最低 ORDER・BRIDGE、他は任意＝canonical も 4/7 手）。全手に強制せず filler を作らない（spec §12-3）。
- **PLACEHOLDER-LOCK**：骨子（simple 化後）・パズルエンジン・配色・フォント・CSS・DOM 構造は触らない。編集は問題固有スロットのみ。
- **conform-fix は冪等・本文不変**。再実行しても旧版トークンが無ければ no-op。`--dry-run` で事前確認可。

---

## 5. 展開対象の棚卸し

- **完了（2026-07-02）**：刑JX009-020（骨子 simple 化＋適合監査＋修正・018 は深掘り全面再鋳造）。
- **刑法・残 matrix-bone 10問**：刑JX007・008・021・022・023・024・071・072・073・074（§2 ループで順次）。
- **他科目**（002_刑事訴訟法〜007_憲法）の ARIADNE：まず `check-ariadne-canonical.py` の A34/A35/A36 出力で現状を棚卸し→ §2 ループ。

---

## 6. gold 参照

- 誌面・構造・骨子の gold＝`outputs/ux/001_ARIADNE/001_刑法/刑JX001_ARIADNE.html`（元設計）。
- 骨子 matrix→simple 変換の before/after 見本＝`刑JX009_ARIADNE.html`。
- 深掘り再鋳造（別問題流用→本問論点）の見本＝`刑JX018_ARIADNE.html`。
