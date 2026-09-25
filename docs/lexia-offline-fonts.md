# Lexia オフラインフォント同梱（LEX-443・2026-08-26）

> iPad をオフラインで使うと誌面のフォントが全部おかしくなる問題の恒久対処。
> **結論：iOS 標準フォントへの置き換えはしない。Lexia アプリに woff2 を同梱する。**

---

## 1. 何が起きているか

TX/JX/RX/ARIADNE/TREE は **12 役割・11 書体**を `<link href="fonts.googleapis.com/css2?...">`
で読む。回線が無いと 1 書体も取れず、全役割が端末のフォールバックへ落ちる。
iPad にプリインストールされていて Safari の CSS から確実に引ける日本語書体は次の 3 つだけ：

| 書体 | CSS 名 |
|---|---|
| ヒラギノ角ゴシック | `Hiragino Sans` |
| ヒラギノ明朝 ProN | `Hiragino Mincho ProN` |
| ヒラギノ丸ゴ ProN | `Hiragino Maru Gothic ProN` |

凸版文久明朝・筑紫A丸ゴシック・クレー・游教科書体・游明朝などは iOS 13 以降
「**アプリからの要求で追加ダウンロードされる**」フォントで、Safari の CSS からは呼び出せない。

現行のフォールバックを iOS で解決すると **12 役割 → 4 書体**になる：

| 実際に当たる書体 | 潰れる役割 |
|---|---|
| ヒラギノ明朝 ProN | `display` `statute` `quote` `answer` `judgment` `keyword` ＝ **6 役割** |
| ヒラギノ角ゴ | `body` `note` `impact` |
| ヒラギノ丸ゴ | `soft` `professor` |
| Menlo | `mono` |

これが実機報告「フォントの割り当てがめちゃくちゃ」（LEX-442・CLAUDE.md §3）の正体で、
**CSS は健全なまま**起きる。切り分け手順は CLAUDE.md §3「実機で『フォントが違う』ときの一次切り分け」。

## 2. なぜ「iOS 標準フォントへの置き換え」を採らないか

2 つの実測でボツにした。

**(a) 役割が潰れるのは同じ。** iOS 標準は 3 書体しかないので、置き換えても 12 役割は
3 つに潰れる。オンラインでも潰れるぶん、現状より悪い。

**(b) ウェイト差での代替も無理。** 「ヒラギノ明朝 W3／W6 を役割ごとに固定して弁別を増やす」案は、
**フォント名でウェイトを固定すると `font-weight` への追随が死ぬ**ため採れない。canonical の CSS を
数えると 12 役割すべてが複数ウェイトで使われている（例：`--font-display` は 600/700/800/850/900、
`--font-soft` は 600/700/800/850/900）。`Hiragino Mincho ProN` は W3/W6 を 1 ファミリとして持ち、
`font-weight` に既に追随しているので、`HiraMinProN-W6` を差し込むと**むしろ階調を失う**。

→ フォールバックをいじって得られるものは実質ゼロ。**フォント実体を端末に置く**しかない。

## 3. 採る方法：サブセット woff2 を Lexia に同梱する

問題 HTML は `font-family:'Zen Old Mincho'` のように**書体名で参照している**だけなので、
表示する文書に `@font-face` が定義されていれば、どこからロードされたかを問わず当たる。
つまり **HTML 2,700 本は 1 バイトも触らずに**オフライン対応できる。

日本語フォントはフル版だと 1 face 2〜3MB あるが、**corpus が実際に使う文字だけ**へ
サブセット化すれば 1 face 200KB〜900KB に落ちる。

### 3-1. ビルド（2 コマンド）

```bash
python scripts/lexia-font-charset.py                    # 文字集合を書き出す
python scripts/build-offline-fonts.py --out dist/lexia-offline-fonts
python scripts/check-offline-fonts.py dist/lexia-offline-fonts   # 被覆検査
```

- 必要な依存：`pip install fonttools brotli`
- `lexia-font-charset.py` … corpus（`outputs/000_TX` `001_JX` `ux` `references`）の HTML を
  **タグを剥がさず**走査する（`<script>` 内の UI 文言・CSS `content:` の ✍📚 も誌面に出るため）。
  さらに安全網として **JIS X 0208 第1水準漢字＋全かな＋ASCII＋和文約物**を足す
  （今後の新問題が corpus に無い字を使っても収録済みにするため）。出力＝
  `docs/data/lexia-offline-charset.txt`（サブセットの単一情報源）。
  副産物に `docs/data/lexia-offline-charset.corpus.txt`（**安全網を除いた corpus 実使用ぶん**）も出す。
  被覆検査が「誌面に実害が出る欠落」と「安全網ぶんの欠落（将来リスクどまり）」を切り分けるのに使う。
- `build-offline-fonts.py` … corpus の Google Fonts リンクを全部読んで
  **必要な (書体, italic, ウェイト) を自動で集める**（＝リンクが正典。手で face 表を書かない）。
  各 face は**旧 UA を送って単一フル woff を取得**する。新しい UA だと Google は
  unicode-range で 120 分割した woff2 を返すが、法律日本語は ほぼ全分割に跨るため
  **合計 2.5MB/face と逆に太る**（Zen Old Mincho で実測：分割 122 個中 118 個が必要）。
  フル版を落として自前でサブセットする方が 3 倍小さい。

### 3-2. 実測（2026-08-26 ビルド）

| | |
|---|---|
| corpus 実使用文字 | **2,846 字**（漢字 2,315／かな 157／ASCII 94／約物・記号 312 ほか） |
| サブセット対象（＋安全網） | **3,767 字** |
| face 数 | **68**（和文 43／欧文 25） |
| バンドル合計 | **29 MB**（`dist/lexia-offline-fonts/`） |
| 参考：corpus の HTML | 2,708 ファイル・684 MB |

和文 1 face は 200KB〜960KB（明朝系が重い）。欧文（Source Code Pro・EB Garamond ほか）は 8〜40KB。
**corpus 全体 684MB に対して 29MB＝4%** なので、オフライン用の容量としては十分に軽い。

被覆検査の結果、Noto Sans/Serif JP と Klee One は corpus 実使用文字を**完全被覆**。
残りは 1〜5 字ずつ欠ける（`剝` `塡` `帮` `幫` `瘖` `贓` `懈` `逋` ほか）が、これは
**元フォントがその字を持っていない**ためで再ビルドしても増えない。該当字はその 1 文字だけ
端末フォントで描かれる（豆腐にはならない）。

> 副産物：この被覆検査が corpus の**文字化けを 2 件検出**した
> （`民JX017_ARIADNE`：`分水嶻`→`分水嶺`、`判敂2105号`→`判時2105号`）。同日修正済み。
> 「どの和文フォントも持っていない字」は、たいてい誤字か文字化けである。

### 3-3. Lexia 側の組み込み

生成物は `lexia-offline-fonts.css` ＋ 同階層の `*.woff2` だけ。アプリに同梱して、
**問題 HTML を表示している文書**へ読ませる。

- **iframe で表示している場合**：iframe の `document.head` に `<link>` を **append** する
  （HTML 自身の Google Fonts `<link>` より**後**に置く。同じ family/weight/style の
  `@font-face` は後勝ちなので、ローカルが勝ってネットワークを一切叩かなくなる＝オンラインでも速い）。
- **アプリの DOM に流し込んでいる場合**：アプリのグローバル CSS に import するだけでよい。

問題 HTML の Google Fonts `<link>` は**消さなくてよい**（オンライン時の保険として無害）。

### 3-4. ライセンス

同梱する書体はすべて再配布・サブセット化・アプリ同梱が許諾されている。

| 書体 | ライセンス |
|---|---|
| Shippori Mincho B1 / Shippori Antique / Zen Old Mincho / Zen Kaku Gothic Antique / Zen Kaku Gothic New / Zen Maru Gothic / Noto Serif JP / Noto Sans JP / Kaisei Decol / M PLUS 1p / M PLUS Rounded 1c / Klee One / Source Code Pro / EB Garamond / Cormorant Garamond / Crimson Pro / Quicksand | SIL Open Font License 1.1 |
| Kosugi Maru | Apache License 2.0 |

**配布時は各書体の `OFL.txt` / `LICENSE.txt` を添えること**（OFL 1.1 の条件）。

## 4. 再ビルドが要るタイミング

新しい問題が **corpus に無い漢字**を使ったとき。安全網（JIS 第1水準）に入っていれば収録済みなので、
実際に要るのは第2水準以上の珍しい字が出たときだけ。目安は年 1 回か、科目を 1 つ完走したとき。

収録から外れた字は**その 1 文字だけ端末フォントで描かれる**（豆腐にはならない）。
`check-offline-fonts.py` がどの書体が何字欠くかを出すので、出荷前に把握しておく。
元フォント自体が持っていない字（Zen Old Mincho の収録は 7,815 字）は再ビルドしても増えない。

## 5. 実機確認

1. iPad をオンラインにして Lexia で問題を開く（正しい誌面を目に焼き付ける）。
2. **機内モード**にして再読込。
> バンドルには確認ページ **`dist/lexia-offline-fonts/_font-test.html`** を同梱してある。
> フォルダごと iPad に置いて機内モードで開くと、12 役割の見本と
> `document.fonts.check()` による 12 書体の読み込み判定が出る。
> **まずこれが全部 [OK] になることを確認**してから Lexia 本体へ組み込むと切り分けが速い。

3. 見出し（明朝太）・本文解説（Shippori Antique）・判旨（Zen Old Mincho）・
   条文（Noto Serif JP）・🎓 講師枠（Kosugi Maru）・💡ワンポイント（丸ゴ）が
   **オンラインと同じに見えれば成功**。1 書体に潰れて見えたら CSS の読み込み順（3-2）を疑う。

> 生成環境（Claude Code on the web）は Google Fonts に到達できず `document.fonts.size = 0` に
> なるため、**スクショでの視覚検証はできない**。機械照合は computed style ＝宣言スタックの
> 先頭までが限界（CLAUDE.md §3）。最終確認は必ず実機で行う。
