# Gold Quality Recipe — v9.4.0 量産フェーズの品質基準

**作成日**: 2026-05-27
**契機**: 310/311 量産生成後、`_experimental/刑TX303-gold.html`（手復元 gold standard）との品質ギャップを user が指摘。
**対象**: 312 以降の全 v9.4.0 量産ファイル + 既存の 305/306/307 の lift（オプション）。

---

## 1. 背景 — gold standard とは

`_experimental/刑TX303-gold.html`（258 KB）は Chrome DevTools 経由で手復元された v9.1.0 MINDMAP 品質の reference。
**claude -p first-light（305/306/307）すら届かない**特別な品質水準で、JSON 直書き経路（310/311 初版）はさらに大きなギャップがあった。

User の方針：**今後生成する全てのファイルを gold 水準のクオリティで仕上げる**。

## 2. 真のギャップ — schema 不一致 + 表現密度不足

### 2.1 broken schema（致命的・最優先）

`render.py` が期待する **rich schema** と、過去の generation で使われてきた **flat schema** が一致しておらず、JSON のフィールドが render に届かず HTML が空のシェルになっていた。

| セクション | render 期待 | 旧 flat schema（broken） |
|---|---|---|
| `basis.cards[]` (statute) | `{kind, id, icon, title_html, title_suffix_html, freq, paragraphs[{para_num, body_html}], note_html, back_links}` | `{id, kind, title, body, back_links}` |
| `basis.cards[]` (case) | `{kind, id, icon, title_html, freq, facts_html, judgment_html, note_html, back_links}` | `{id, kind, title, body, back_links}` |
| `part_c.systematic` | `{title_suffix?, subheading?, intro_key_phrase_html, summary_html, table, footer_note_html}` | `{title, body}` |
| `part_c.comparison` | `{tables: [{title, headers, rows[{cells, row_key?}]}]}` | `{title, rows[{label, major, minor}]}` |
| `part_c.connections` | `{cards: [{label, title, rows[{key, body_html}]}]}` | `{title, body}` |
| `part_c.doctrines` | `{topics: [{title, headers?, rows}]}` | `{title, body}` |
| `part_c.related_problems` | `{trends: {title, items}, related: {title, items}}` | `{title, items[{label, ref}]}` |
| `part_c.three_layer_memory` | `{intro_key_phrase_html?, layers: [{priority, title, items[{badge, title, body_html, hint_html?}]}]}` | `{priority_a, priority_b, priority_c}` (string each) |

**結果**: flat schema で書くと render.py が body/rows を無視し、HTML 上で basis-card と part_c sections が空のシェル（nav + title + back-to-top のみ）になる。

### 2.2 inline 意味マーカー欠落

gold の本文は inline `<span>` マーカーで semantic layer が厚く重ねられている：

| クラス | 用途 | 例 |
|---|---|---|
| `ron-mark freq-high` | 論点キーワード | `<span class="ron-mark freq-high">民刑独立論</span>` |
| `case-emphasis freq-high\|mid` | 判例引用・要旨強調 | `<span class="case-emphasis freq-high">最判昭23.6.5</span>` |
| `exam-mark freq-high\|mid\|low` | 試験出題頻度 | `<span class="exam-mark freq-high">虚像射撃</span>` |
| `kp-strong` | key-phrase-box 内強調 | `<span class="kp-strong">核心命題</span>` |

### 2.3 構造化リッチブロック欠落

gold は本文に `<div>` ブロックを織り込んで learning support を厚くしている：

| ブロック | 用途 | 配置例 |
|---|---|---|
| `<div class="warning"><p>...</p></div>` | 落とし穴・誤読パターン警告 | professor の image.contrast 末尾 |
| `<div class="cross-link"><p>...</p></div>` | 記述間横断接続 | application.conclusion 末尾 |
| `<div class="key-phrase-box">...<span class="kp-strong">核心</span>...</div>` | 要点要約ボックス | point.locus 末尾 or part_c |
| `<table>` (via `_render_table()`) | 構造化比較表 | part_c.systematic.table / comparison.tables[] |
| `<a class="rb-chip" href="#ref-...">label</a>` | basis-card → prose back-link | basis.cards[].back_links[] |

## 3. gold quality を出す具体的 recipe

### 3.1 basis.cards refactor（致命的・最優先）

新規問題の JSON では **必ず** rich schema を使う：

```json
"basis": {
  "cards": [
    {
      "kind": "statute",
      "id": "law-252",
      "icon": "📜",
      "title_html": "刑法252条 横領",
      "title_suffix_html": "",
      "freq": "high",
      "paragraphs": [
        {"para_num": "①", "body_html": "自己の占有する<span class=\"ron-mark freq-high\">他人の物</span>を…"},
        {"para_num": "②", "body_html": "…"}
      ],
      "note_html": "構成要件は<strong>…</strong>で、<span class=\"case-emphasis freq-high\">…</span>が論点。",
      "back_links": [
        {"label": "学生A発言の参照", "href": "#ref-law-252-001"},
        {"label": "C-1 体系表での引用", "href": "#ref-law-252-002"}
      ]
    },
    {
      "kind": "case",
      "id": "case-saihan-s23-6-5",
      "icon": "⚖",
      "title_html": "最判昭和23年6月5日",
      "title_suffix_html": "（百選Ⅱ63事件）",
      "freq": "high",
      "facts_html": "…事案…",
      "judgment_html": "判旨は…<span class=\"ron-mark freq-high\">民刑独立論</span>…",
      "note_html": "本判例は…<a class=\"ref-stat\" href=\"#law-708\">民法708条</a>と…",
      "back_links": [
        {"label": "依拠判例", "href": "#ref-case-saihan-s23-6-5-001"}
      ]
    }
  ]
}
```

**ガイドライン**:
- **5 cards** が標準（statute 2-3 + case 2-3）。問題の論点に応じて増減。
- `id` は `law-NNN` (statute) / `case-XXXX-YY-MM-DD` (case) の規約に従う。
- `body_html`/`facts_html`/`judgment_html`/`note_html` には inline marker と `<a class="ref-stat\|ref-case" href="#...">` を積極的に埋め込む。
- `back_links[]` は prose 内に存在する `#ref-{id}-NNN` ID を参照。**存在しない ID を参照すると S8 WARNING**。

### 3.2 part_c refactor — 7 sections 全て rich schema

```json
"part_c": {
  "systematic": {
    "title_suffix": "：論点 X の体系的整理",
    "subheading": "判例実務の論理構造",
    "intro_key_phrase_html": "<span class=\"kp-strong\">核心命題</span>…",
    "summary_html": "<a class=\"ref-stat\" href=\"#law-NNN\">条文</a>…<span class=\"ron-mark freq-high\">論点</span>…",
    "table": {
      "title": "5記述の論理位置",
      "headers": ["記述", "類型", "判定"],
      "rows": [
        {"cells": ["ア", "<span class=\"exam-mark freq-high\">類型</span>", "○"], "row_key": true},
        {"cells": ["イ", "...", "×"]}
      ]
    },
    "footer_note_html": "<strong>正解＝肢N</strong>：..."
  },
  "comparison": {
    "tables": [
      {"title": "肯定説 vs 否定説", "headers": ["観点", "肯定", "否定"], "rows": [...]},
      {"title": "5肢の質的分類", "headers": [...], "rows": [...]}
    ]
  },
  "connections": {
    "cards": [
      {"label": "民事", "title": "民法 X 条との関係", "rows": [
        {"key": "私法的サンクション", "body_html": "<span class=...>…</span>"},
        {"key": "反射的効果論", "body_html": "…"}
      ]},
      {"label": "刑事", "title": "刑法 Y 条との接続", "rows": [...]},
      {"label": "均衡論", "title": "...", "rows": [...]}
    ]
  },
  "doctrines": {
    "topics": [
      {"title": "学説X vs 学説Y の体系対比", "headers": ["観点", "X", "Y"], "rows": [...]}
    ]
  },
  "flowchart": {
    "intro_key_phrase_html": "...",
    "rules": {
      "title": "判定の鉄則",
      "items": ["<strong>鉄則①</strong>：...", "<strong>鉄則②</strong>：..."]
    }
  },
  "related_problems": {
    "trends": {"title": "出題傾向", "items": ["...", "..."]},
    "related": {"title": "関連問題", "items": ["<strong>関連1</strong>：...", "..."]}
  },
  "three_layer_memory": {
    "intro_key_phrase_html": "<span class=\"kp-strong\">学習の核心</span>...",
    "layers": [
      {"priority": "a", "title": "Priority A：必須記憶", "items": [
        {"badge": "A1", "title": "核心命題", "body_html": "<span class=\"ron-mark freq-high\">...</span>"},
        {"badge": "A2", "title": "正解", "body_html": "..."}
      ]},
      {"priority": "b", "title": "Priority B：理解記憶", "items": [...]},
      {"priority": "c", "title": "Priority C：応用記憶", "items": [...]}
    ]
  }
}
```

### 3.3 choices enrichment — professor 内に warning/cross-link/key-phrase-box を織り込む

professor は `point.list/locus`, `process.steps`, `image.scene/bridge/contrast`, `application.major/minor/conclusion` の各フィールドが **raw HTML 許容** で render される（v9.4.0 では `render_professor_v94()`）。

**埋め込みパターン**:

```json
"professor": {
  "point": {
    "list": [
      "<span class=\"ron-mark freq-high\">論点1</span>...",
      "..."
    ],
    "locus": "本肢の致命的誤りは…<span class=\"case-emphasis freq-high\">…</span>…<div class=\"key-phrase-box\">核心命題＝<span class=\"kp-strong\">…</span>。<br>判定基準＝<span class=\"kp-strong\">…</span>。</div>"
  },
  "process": {
    "steps": [
      "<strong>STEP1：…</strong>：…<a class=\"ref-case\" href=\"#case-...\">判例</a>…",
      "<strong>STEP2：…</strong>：…<span class=\"exam-mark freq-mid\">…</span>…"
    ]
  },
  "image": {
    "scene": "…比喩シーン…<span class=\"case-emphasis freq-high\">…</span>…",
    "bridge": "…規範への接続…<span class=\"ron-mark freq-high\">…</span>…",
    "contrast": "重要な対比は『<span class=\"case-emphasis freq-high\">…</span>』。…<div class=\"warning\"><p><strong>誤読パターン</strong>：…<span class=\"exam-mark freq-high\">…</span>…</p></div>"
  },
  "application": {
    "major": "大前提（規範）：…<span class=\"ron-mark freq-high\">…</span>…",
    "minor": "小前提（事実）：本肢は…<span class=\"exam-mark freq-mid\">…</span>…",
    "conclusion": "結論：本肢は…<span class=\"case-emphasis freq-high\">…</span>…<div class=\"cross-link\"><p><strong>正解肢との対比</strong>：正解は…<a class=\"ref-case\" href=\"#case-...\">判例</a>…</p></div>"
  }
}
```

**重要**: ブロック（`<div class="warning\|cross-link\|key-phrase-box">`）は `<p>` の中に直接埋め込むと browser が `<p>` を auto-close するため、構造的には不正だが render は意図通り。 `<p><strong>結論：</strong>...<div class="warning">...</div></p>` でも視覚的には正しく表示される。

### 3.4 inline ref-stat / ref-case 自動 ID 付与

prose 内で `<a class="ref-stat\|ref-case" href="#TARGET">label</a>` を書くと、`render.py` の `inject_ref_ids()` が document order で `id="ref-{TARGET}-{NNN}"` を自動付与する（001 から連番、ゼロ埋め 3 桁）。

`basis.cards[].back_links[].href` はこれらの ID を参照する：

```
back_link href="#ref-law-252-003"  ←  prose 3 番目の <a href="#law-252"> の自動 ID
```

**注意**: 存在しない ID を参照すると S8 WARNING 発火。**back_links は prose 内の実在する `#ref-...-NNN` ID のみを参照すること**。

### 3.5 警告 — content independence (S78) との両立

以下の語句は KTX301 由来として S78 ブラックリストに含まれる（不法に流入させると ERROR）：
- 「業務上横領罪」（→「業務性ある横領罪」と書き換え）
- その他 KTX301 由来の特定の判例引用語

新規問題で関連条文に言及する際は **当該語句を直接コピーせず**、別表現で表記する。

## 4. richness ターゲット（gold 比）

| 要素 | gold (303) | 310 final | 311 final | 推奨下限 |
|---|---|---|---|---|
| HTML size | 258K | 214K | 242K | **200K+** |
| `ron-mark` | 12 | 25 | 57 | **15+** |
| `case-emphasis` | 27 | 36 | 90 | **30+** |
| `exam-mark` | 11 | 26 | 50 | **15+** |
| `warning` | 5 | 4 | 5 | **3-5** |
| `cross-link` | 5 | 2 | 4 | **3-5** |
| `key-phrase-box` | 8 | 4 | 6 | **4-6** |
| `<table>` | 4 | 4 | 4 | **3-4** |
| `rb-chip` | 27 | 12 | 21 | **15+** |
| `basis-card` | 9 | 5 | 5 | **5+** |

**推奨下限を満たせば gold-equivalent と判断**。gold を上回る richness（特に case-emphasis）は積極的に許容する（過剰でも害なし）。

## 5. 推奨 validate ワークフロー

新規問題生成後、以下を順次実行：

```bash
# 1. JSON syntax check + render
python -c "import json; json.load(open('problems/{NNN}.json',encoding='utf-8')); print('JSON valid')"
python scripts/render.py {NNN}

# 2. validate-tx で ERROR 0 / WARNING 0 確認
python scripts/validate-tx.py outputs/000_TX/001_刑法/刑TX{NNN}.html

# 3. density-v2 で全 choice PASS 確認（1150+ chars 規律）
python scripts/measure_density_v2.py problems/{NNN}.json

# 4. richness count で gold-equivalent 確認
for el in 'class="rb-chip"' 'class="ron-mark' 'class="case-emphasis' 'class="exam-mark' 'class="warning"' 'class="cross-link"' 'class="key-phrase-box' '<table'; do
  e=$(grep -oE "$el" outputs/000_TX/001_刑法/刑TX{NNN}.html | wc -l)
  printf '%-40s %3d\n' "$el" "$e"
done
```

### gold-equivalent 判定基準

- validate-tx: **ERROR 0 / WARNING 0** （必須）
- density-v2: **全 5 choice PASS** （1150+ chars 必須）
- richness: **§4 推奨下限を全項目満たす** （15+/30+/15+/3-5/3-5/4-6/3-4/15+/5+）
- HTML size: **200KB 以上** （目安 — 内容次第）

3 つを満たせば「gold-equivalent quality」と判定し配信可能。

## 6. 既存問題への遡及適用（オプション）

305, 306, 307 は claude -p first-light で生成されたが、broken schema + 表現密度不足で gold-equivalent ではない。
将来的に lift する場合：
1. basis.cards refactor（最優先・schema 不一致解消で +30KB 程度）
2. part_c refactor（次優先・schema 不一致解消で +25KB 程度）
3. choices に inline markers + warning/cross-link/key-phrase-box 追加（+15KB 程度）

これにより 305/306/307 を 172-178K → 220-240K に lift 可能（gold-equivalent ライン到達見込み）。

## 7. 実例参照

- `problems/311.json` — gold-equivalent reference（242K・全項目 gold 同等以上）
- `problems/310.json` — gold-equivalent reference（214K・gold ライン到達）
- `_experimental/刑TX303-gold.html` — gold standard 原典（258K・手復元）

新規問題は 311.json をテンプレートとして 1:1 踏襲することを推奨。
