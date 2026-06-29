# Claude Handoff: ARIADNE v1.2.0 PLACEHOLDER-LOCK

> Scope: **ARIADNE only**. TX v12 / GENESIS / TX360 changes are a separate handoff.
> This file summarizes the Codex-side ARIADNE canonicalization and the rules Claude should use for future ARIADNE generation or retrofit work.

## Current State

- Active ARIADNE canonical: `canonical/ARIADNE.html`
- Active ARIADNE slot contract: `canonical/ARIADNE.placeholder.html`
- Active ARIADNE spec: `spec/jx-ariadne-v1.2.0-core.md`
- Active version name: **ARIADNE v1.2.0 PLACEHOLDER-LOCK**
- Generator prompt: `prompts/new-ariadne-headless.md`
- Primary validator: `scripts/validate-ariadne.py` A1-A31
- Cross-file guard: `scripts/check-ariadne-canonical.py`
- Preflight route: `scripts/check-lexia-preflight.py`

Recent ARIADNE commits to know:

- `038c8cd0 docs(ariadne): canonize matrix thread v1.1`
- `42731ecf fix(jx): gate ariadne canonical before persisting outputs`
- `e5e3f15e fix(ariadne): dedupe RX links for JX020-022`
- Earlier visual rollout/fixes:
  - `f83be72a style(ariadne): apply matrix outline canonical to JX007-015`
  - `1ac1ca91 style(ariadne): indent problem statements`
  - `33a62667 style(ariadne): tighten fact cue columns`
  - `7327a534 test(ariadne): guard canonical layout regressions`

## Meaning Of The Canonicalization

ARIADNE is now the main JX learning loop for:

1. Reading the JX problem.
2. Building an answer outline.
3. Active recall.
4. Jumping to RX when a recall point fails.
5. Using TREE for issue-structure understanding.

Role split must stay clean:

- **ARIADNE**: repeated learning route and answer-construction training.
- **RX**: answer-ready論証 cards to output in exam writing.
- **TREE**: issue structure / doctrinal tree understanding.
- **ATHENA/JX**: encyclopedia-level source and full case material.

Do not collapse these roles into one UI.

## Version Meaning

- **v1.0.0 major**: JX019 matrix-style answer outline became the official ARIADNE canonical form.
- **v1.1.0 minor / historical baseline**: production refinements were locked in:
  - problem text one-character indent,
  - label/body two-column layout,
  - compact facts two-column layout,
  - dotted separators between outline/facts items,
  - Mildliner-style labels,
  - strict but educationally selective RX `data-rx` wiring,
  - validator/preflight guards.
- **v1.2.0 minor / active**: the design is locked as a placeholder-driven template:
  - `canonical/ARIADNE.html` is the fixed DOM/CSS/JS source,
  - `canonical/ARIADNE.placeholder.html` lists the only AI-editable `{{{...}}}` slots,
  - AI may choose only the existing EASY/STD/HARD ACTIVE base-color preset by difficulty,
  - AI must not redesign cards, columns, spacing, class names, functional colors, or JS.

## Placeholder-Lock Rule

Treat ARIADNE generation as **copy fixed canonical -> fill variable slots**.

Allowed AI judgment:

- problem-specific text,
- issue selection and ordering within the canonical matrix,
- facts/evaluation words,
- answer-construction coaching content,
- model-answer paragraphs in Claude canonical form,
- deep-dive legal content grounded in the source JX,
- selective `data-rx` wiring,
- ACTIVE base-color preset selection: EASY / STD / HARD only.

Forbidden AI judgment:

- changing section order,
- changing CSS/JS,
- inventing new cards or wrappers,
- changing label/body two-column structure,
- changing `.facts li` grid values,
- changing the draft-card layout: relation/timeline on the top two columns and facts as bottom full-width `span2`,
- changing Mildliner functional colors,
- changing puzzle engine structure,
- changing model-answer card structure.

## Non-Negotiable Content Rules

- **Model answer stays Claude canonical.**
  Keep the existing model-answer form: 問規当結 cards, Mincho text, indentation, fact/evaluation markers.
  Do not revive the abandoned A/B-answer split direction.

- **Answer outline becomes matrix/chip training.**
  Use `.bone.matrix-bone` with `.bsec`, `.mrow`, `.bn`, `.mcell`, `.mline`, `.mstage`, `.mtext`.
  The goal is to train arrangement, thickness, and conclusion flow.

- **Issue chips must not leak order.**
  Use `【論点】...`, not `【論点①】...` or `【論点1】...`.
  The order is represented by `.b1` / section headings, not by issue-chip numbering.

- **RX wiring must be exact, not maximal.**
  Add `data-rx` only when the recall card clearly corresponds to a specific RX論証.
  Do not link merely because an RX file exists.
  General method / generic recall cards may omit `data-rx`.
  Within the same JX, avoid duplicate `data-rx` unless the duplicate is pedagogically intentional and both cards genuinely test the same論証.

- **TTS consistency.**
  The `.bc-col` / 教授のひとこと / answer-construction coaching should correspond to the TTS side's answer-construction, case-analysis, and "difference-making point" content.
  Do not add generic coaching that contradicts or bypasses the JX/TTS theory.

## Layout Rules To Preserve

Bad pattern to avoid: a badge/label followed by a long sentence on the same line, causing the text to hang awkwardly.

Use a label column and body column for:

- CASE / problem statements,
- `.draft-problem`,
- `.draft-digest`,
- `.facts li`,
- `.bc-inst`,
- `.mline` in matrix outlines.

Text rules:

- Badges, labels, and headings are not indented.
- Body text in the body column is indented.
- `.problem .pq` must keep `text-indent:1em`.
- `.facts li` two-column canonical form is:
  `grid-template-columns:minmax(18em,32em) minmax(16em,28em); column-gap:18px; justify-content:start`
- Draft structure is fixed: relationship map and timeline are the top two columns; facts is the bottom full-width `draft-card span2`.
- `.cue` text must not start with `...` or `…`; those are visual separators leaking into body text.
- The old wide facts form is forbidden:
  `minmax(24em,1.35fr) minmax(18em,1fr); column-gap:24px`

## Validation Guards Now In Place

`scripts/validate-ariadne.py`:

- A29: recall-card `data-rx` format and RX existence.
- A30: `.problem .pq` indentation guard.
- A31: facts compact columns, draft-card full-width placement, and no leading ellipsis in facts cue text.

`scripts/check-ariadne-canonical.py`:

- validates `canonical/ARIADNE.html`,
- checks `canonical/ARIADNE.placeholder.html` exists and contains the v1.2.0 slot marker,
- validates all `outputs/ux/001_ARIADNE/**/*_ARIADNE.html`,
- checks `canonical/ARIADNE.html` contains `ARIADNE v1.2.0 PLACEHOLDER-LOCK`.

`scripts/check-lexia-preflight.py` now runs:

1. duplicate/id drift,
2. Lexia sync contract,
3. ARIADNE canonical guard,
4. ARIADNE -> RX coverage.

JX persistence routes:

- `scripts/jx-finalize.ps1` blocks commit/push if ARIADNE canonical guard fails.
- `scripts/jx-push.sh` runs preflight before committing/pushing remote JX outputs.
- `scripts/jx-batch-runner.ps1` already generates RX / TREE / ARIADNE after JX validation, then TTS.

## Commands Claude Should Run

For one ARIADNE file:

```bash
python scripts/validate-ariadne.py outputs/ux/001_ARIADNE/001_刑法/刑JXNNN_ARIADNE.html
```

For the full ARIADNE canonical guard:

```bash
python scripts/check-ariadne-canonical.py
```

For RX coverage:

```bash
python scripts/check-rx-coverage.py --summary --strict
```

For full Lexia preflight:

```bash
python scripts/check-lexia-preflight.py --skip-self-test
```

For target RX/TREE validation:

```bash
python scripts/validate-rx.py outputs/ux/002_RX/001_刑法/刑JXNNN 刑RXNNN
python scripts/validate-tree.py outputs/ux/003_TREE/001_刑法/刑JXNNN_TREE.html
```

## Generation Instructions For Future Claude Work

When generating or regenerating ARIADNE:

1. Treat `spec/jx-ariadne-v1.2.0-core.md` as the active spec.
2. Clone from `canonical/ARIADNE.html`.
3. Read `canonical/ARIADNE.placeholder.html` and edit only the corresponding variable content.
4. Preserve the Claude canonical model-answer style.
5. Use JX019-style matrix answer outlines.
6. Build active-recall cards around rules, elements, definitions, and discriminations.
7. Wire `data-rx` only to clearly matching RX論証 cards.
8. Keep facts and outline layouts readable with the v1.2.0 two-column/indent rules.
9. Choose ACTIVE base color by difficulty only from EASY / STD / HARD.
10. Run `validate-ariadne.py` and `check-ariadne-canonical.py`.
11. For JX generation, make sure RX / TREE / ARIADNE are all present before persistence.

## Known Acceptable Current State

As of the ARIADNE v1.2.0 work:

- `check-ariadne-canonical.py`: 66 targets, FAIL 0.
- `check-lexia-preflight.py --skip-self-test`: PASS.
- `check-rx-coverage.py --summary --strict`: dangling 0 / UNREACHABLE 0.
- SAFETY-NET RX items may remain; they are treated as delayed-injection safety-net, not immediate blockers.

## What Not To Touch In This Handoff

- TX v12 / GENESIS / TX360 inline-review-loop work.
- TX validators unless the separate TX handoff asks for it.
- Non-ARIADNE generated files except when validating RX/TREE connectivity for a specific JX.
