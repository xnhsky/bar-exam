# Phase 2: PART C schema 設計

> 参照: `docs/phase2-part-c-structure-analysis.md` (刑TX300 逆解析)
> 適用: `schema/problem.schema.json` の `properties` に `part_c` (optional) 追加
> 原則: 全 PART C フィールドは optional。既存 JSON への影響ゼロ。

---

## 1. part_c top-level

```json
"part_c": {
  "type": ["object", "null"],
  "additionalProperties": false,
  "description": "PART C 体系・記憶（Phase 2）。null/未定義の場合は既存スタブ HTML が出力される。",
  "properties": {
    "systematic":          { "$ref": "#/$defs/PartC_Systematic" },
    "comparison":          { "$ref": "#/$defs/PartC_Comparison" },
    "connections":         { "$ref": "#/$defs/PartC_Connections" },
    "doctrines":           { "$ref": "#/$defs/PartC_Doctrines" },
    "flowchart":           { "$ref": "#/$defs/PartC_Flowchart" },
    "related_problems":    { "$ref": "#/$defs/PartC_RelatedProblems" },
    "three_layer_memory":  { "$ref": "#/$defs/PartC_ThreeLayerMemory" }
  }
}
```

各サブセクションも個別に optional。`systematic` だけ提供して他は stub のまま、という運用も可能。

---

## 2. C-1 systematic

```json
"PartC_Systematic": {
  "type": "object",
  "additionalProperties": false,
  "required": ["intro_key_phrase_html"],
  "properties": {
    "title_suffix":         { "type": "string", "description": "H2 末尾、例 '──詐欺罪の成立要件と他罪の限界'" },
    "subheading":           { "type": "string", "description": "H3 趣旨見出し" },
    "intro_key_phrase_html":{ "type": "string", "description": "key-phrase-box 内 raw HTML" },
    "summary_html":         { "type": "string", "description": "要約段落 (<p>) 内 raw HTML" },
    "table": {
      "type": "object",
      "additionalProperties": false,
      "required": ["title", "headers", "rows"],
      "properties": {
        "title":   { "type": "string" },
        "headers": { "type": "array", "items": {"type":"string"}, "minItems": 1 },
        "rows": {
          "type": "array", "minItems": 1,
          "items": {
            "type": "object", "additionalProperties": false,
            "required": ["cells"],
            "properties": {
              "cells":   { "type": "array", "items": {"type":"string"}, "minItems": 1 },
              "row_key": { "type": "boolean", "default": false }
            }
          }
        }
      }
    },
    "footer_note_html": { "type": "string", "description": "末尾 <p> 注釈 raw HTML（小フォント）" }
  }
}
```

---

## 3. C-2 comparison

```json
"PartC_Comparison": {
  "type": "object",
  "additionalProperties": false,
  "required": ["tables"],
  "properties": {
    "tables": {
      "type": "array", "minItems": 1,
      "items": {
        "type": "object", "additionalProperties": false,
        "required": ["title", "headers", "rows"],
        "properties": {
          "title":   { "type": "string" },
          "headers": { "type": "array", "items": {"type":"string"} },
          "rows": {
            "type": "array",
            "items": {
              "type": "object", "additionalProperties": false,
              "required": ["cells"],
              "properties": {
                "cells":   { "type": "array", "items": {"type":"string"} },
                "row_key": { "type": "boolean", "default": false }
              }
            }
          }
        }
      }
    }
  }
}
```

---

## 4. C-3 connections

```json
"PartC_Connections": {
  "type": "object",
  "additionalProperties": false,
  "required": ["cards"],
  "properties": {
    "cards": {
      "type": "array", "minItems": 1,
      "items": {
        "type": "object", "additionalProperties": false,
        "required": ["label", "title", "rows"],
        "properties": {
          "label": { "type": "string", "description": "<span class='cc-label'>分野名、例 '刑法各論'" },
          "title": { "type": "string", "description": "h4 本文" },
          "rows": {
            "type": "array", "minItems": 1,
            "items": {
              "type": "object", "additionalProperties": false,
              "required": ["key", "body_html"],
              "properties": {
                "key":       { "type": "string", "description": "cc-key、例 '共通点'" },
                "body_html": { "type": "string", "description": "本文 raw HTML（リンク・strong 等含む）" }
              }
            }
          }
        }
      }
    }
  }
}
```

---

## 5. C-4 doctrines (optional)

```json
"PartC_Doctrines": {
  "type": "object",
  "additionalProperties": false,
  "required": ["topics"],
  "properties": {
    "topics": {
      "type": "array", "minItems": 1,
      "items": {
        "type": "object", "additionalProperties": false,
        "required": ["title", "rows"],
        "properties": {
          "title":   { "type": "string", "description": "h3 例 '① 欺罔行為の「重要事項」性'" },
          "headers": {
            "type": "array",
            "items": {"type":"string"},
            "default": ["学説", "結論", "論拠"],
            "description": "省略時は既定 ['学説','結論','論拠']"
          },
          "rows": {
            "type": "array",
            "items": {
              "type": "object", "additionalProperties": false,
              "required": ["cells"],
              "properties": {
                "cells":   { "type": "array", "items": {"type":"string"} },
                "row_key": { "type": "boolean", "default": false }
              }
            }
          }
        }
      }
    }
  }
}
```

---

## 6. C-5 flowchart

```json
"PartC_Flowchart": {
  "type": "object",
  "additionalProperties": false,
  "properties": {
    "intro_key_phrase_html": { "type": "string" },
    "figure": {
      "type": "object",
      "additionalProperties": false,
      "required": ["svg_html"],
      "properties": {
        "svg_html": { "type": "string", "description": "<svg>...</svg> 全体 raw HTML（任意ジオメトリ）" },
        "caption":  { "type": "string", "description": "<p class='figure-caption'>" }
      }
    },
    "rules": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "title": { "type": "string", "description": "h3 例 '運用上の鉄則'" },
        "items": {
          "type": "array",
          "items": { "type": "string", "description": "<li> 内 raw HTML" }
        }
      }
    }
  }
}
```

---

## 7. C-6 related_problems (optional)

```json
"PartC_RelatedProblems": {
  "type": "object",
  "additionalProperties": false,
  "properties": {
    "trends": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "title": { "type": "string", "description": "h3 例 '出題傾向の分析'" },
        "items": { "type": "array", "items": { "type": "string" } }
      }
    },
    "related": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "title": { "type": "string", "description": "h3 例 '関連問題・参考'" },
        "items": { "type": "array", "items": { "type": "string" } }
      }
    }
  }
}
```

---

## 8. C-7 three_layer_memory

```json
"PartC_ThreeLayerMemory": {
  "type": "object",
  "additionalProperties": false,
  "required": ["layers"],
  "properties": {
    "intro_key_phrase_html": { "type": "string" },
    "layers": {
      "type": "array", "minItems": 1, "maxItems": 3,
      "items": {
        "type": "object", "additionalProperties": false,
        "required": ["priority", "title", "items"],
        "properties": {
          "priority": {
            "type": "string",
            "enum": ["a", "b", "c"],
            "description": "memory-item class priority-{a|b|c}。S 層は priority-c"
          },
          "title": { "type": "string", "description": "h3 例 'Priority A — 各記述の核心命題（試験直前必須・5項目）'" },
          "items": {
            "type": "array", "minItems": 1,
            "items": {
              "type": "object", "additionalProperties": false,
              "required": ["badge", "title", "body_html"],
              "properties": {
                "badge":     { "type": "string", "description": "例 'A1' 'B3' 'S2'" },
                "title":     { "type": "string", "description": "mem-title 本文" },
                "body_html": { "type": "string", "description": "本文 raw HTML（strong・リンク含む）" },
                "hint_html": { "type": "string", "description": "mem-hint raw HTML（▶ で始まる場合は呼出側で付与）" }
              }
            }
          }
        }
      }
    }
  }
}
```

---

## 9. 既存スタブとの互換戦略

- 7 セクション全 slot のデフォルト値 = 既存テンプレ PART C スタブの inner HTML（byte-identical）
- `part_c.{section}` が `null` / 未定義 → render はスタブ inner を返却
- `part_c.{section}` が object → render は構造化 HTML を生成

これにより:
- 既存 14 件（part_c なし）= byte-identical 維持（CP2-CP4 通過）
- 新規問題 = `part_c` を提供して構造化 PART C を出力

---

## 10. 不採用案（記録）

| 案 | 理由 |
|---|---|
| 全 PART C を `part_c_html: string` 1 フィールドに raw HTML 集約 | データ構造化のメリット消失。再利用・横断検索不可。 |
| inline HTML を全 escape | 既存 KTX_template の sub-card で raw HTML 流通済。escape 化は API 破壊変更。 |
| `final-answer` を C-7 末尾に schema 化 | 既存 14 件は basis セクション末尾配置で byte-identical 必須。C-7 末尾配置は 刑TX300 固有 = 将来課題。 |
