# /new-ariadne — 検証済み JX から ARIADNE 解法ナビを生成

**用途**：既存の検証済み JX（ATHENA）から、初学者向けの「解法ナビ＋周回」教材 ARIADNE を1問生成する。
ATHENA（百科事典）はそのまま。ARIADNE は別系統の副産物（RX/ARB と同じく検証済み JX から蒸留）。

## 使い方
```
/new-ariadne 刑 001          # 科目＋番号
/new-ariadne outputs/001_JX/刑JX/刑JX001.html   # JX HTML パス直指定
```

## 正典・依存
- 骨子 spec：`spec/jx-ariadne-v0.1-core.md`
- 複製起点（スケルトン）：`canonical/ARIADNE.html`（v0.3 誌面風）
- 生成プロンプト：`prompts/new-ariadne-headless.md`
- 検証：`python scripts/validate-ariadne.py <出力>`（A1〜A21）

## 工程（要約）
1. `outputs/001_JX/{科目}JX/{科目}JX{NNN}.html`（ATHENA）を一次情報源に Read。事案と論点の自己照合（不一致は中断）。
2. `canonical/ARIADNE.html` を `outputs/004_JX_EX/ARIADNE/{00N_科目}/{科目}JX{NNN}_ARIADNE.html` へ複製→空化→鋳造。
3. 解法7手（SCAN→BUILD）＋骨子＋自己採点＋模範reveal＋深掘り＋**自己完結○× 10〜15枚**（`data-arena="1"`＋`data-correct-value`）。
4. `validate-ariadne.py` で A1〜A21 ERROR 0 を確認。
5. **master に commit/push**（Lexia は `barExamSync.js` で outputs/ を自動スキャン＝push で自動同期）。

## 規律
- 法的正確性は検証済み JX に厳密準拠（規範すり替え・条文誤り・判例射程の誤用禁止）。
- ○× は**本問前提なしで解ける一般原則／例題**（復習プール孤立表示でも解ける）。メタ除去regex・`</body>`リテラルを避ける。
- 配色＝フレーム(ATHENAプラム)／シート(マイルドクールグレー)／カード(薄クリーム)／内側(マイルドライナー)。役割別フォント・字下げ・バッジ＋色分けボックス。
