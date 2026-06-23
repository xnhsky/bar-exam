#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""フッターに「生成日時＋バージョン」を機械可読で刻むコアモジュール。

Lexia は問題HTML本文を raw.githubusercontent.com (GitHub API レート制限の対象外) で
取得し、フッターの「作成日：YYYY-MM-DD HH:MM ／ <version>」を読む。これにより Commits
API を1件も叩かずに各ファイルの生成日時・最新版を取得できる (レート制限の根本回避)。

刻印は冪等: 既存の <... class="lexia-genmeta">...</...> を必ず置換し、旧来の
<!-- 作成日：YYYY-MM-DD --> 固定コメントも除去する。再生成・再スタンプで二重化しない。

CLI:
    python scripts/stamp_footer.py <file> --datetime "2026-06-20 14:16" --version "JX v4.0.0 LOOP-FOLD"
    python scripts/stamp_footer.py <file> --now            # 現在時刻 (JST) で刻む・版は自動推定
"""
from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

JST = timezone(timedelta(hours=9))

# 刻印の lookup / 冪等アンカー。
GENMETA_CLASS = "lexia-genmeta"

# 既存の刻印 (どんなタグでも class に lexia-genmeta を含むもの) を丸ごと掴む。
_GENMETA_RE = re.compile(
    r'[ \t]*<([a-zA-Z][\w-]*)\b[^>]*\bclass="[^"]*\blexia-genmeta\b[^"]*"[^>]*>.*?</\1>[ \t]*\n?',
    re.DOTALL,
)
# 旧来の固定コメント <!-- 作成日：2026-06-20 --> (日付のみ・テンプレ複製) を除去。
_LEGACY_COMMENT_RE = re.compile(r'[ \t]*<!--\s*作成日：[0-9]{4}-[0-9]{1,2}-[0-9]{1,2}\s*-->[ \t]*\n?')
# TX 既存の日本語フッター行 <p class="footer-date">作成日：…</p> (genmeta 無し)。英語統一で置換する。
_NATIVE_FOOTERDATE_RE = re.compile(
    r'[ \t]*<p class="footer-date">作成日：.*?</p>[ \t]*\n?', re.DOTALL
)


_REF_LABEL = {"GDE": "Reference GDE", "MTD": "Reference MTD", "TAN": "Reference TAN", "RON": "Reference RON"}


def infer_version(path: str, html: str) -> str:
    """パスと本文からカテゴリ別の版文字列を推定する（Lexia が読む全カテゴリ対応）。"""
    p = path.replace("\\", "/")
    if "/ux/001_RX/" in p:
        m = re.search(r"AXIOM[^0-9]{0,14}v([0-9]+\.[0-9]+)", html)
        return f"RX AXIOM v{m.group(1)}" if m else "RX AXIOM v2.8"
    if "/ux/002_TREE/" in p:
        m = re.search(r"ARBOR v([0-9]+\.[0-9]+)", html)
        return f"TREE ARBOR v{m.group(1)}" if m else "TREE ARBOR v5.0"
    if "/ux/000_ARIADNE/" in p:
        m = re.search(r"ARIADNE[^0-9]{0,12}v([0-9]+\.[0-9]+)", html)
        return f"ARIADNE v{m.group(1)}" if m else "ARIADNE v0.3"
    # 参考資料（top-level references/ や outputs/ux/003_参考資料・ファイル名サフィックス _GDE 等）
    if "/references/" in p or "参考資料" in p or any(f"_{t}." in Path(p).name for t in _REF_LABEL):
        name = Path(p).name
        for tag, label in _REF_LABEL.items():
            if f"_{tag}." in name:
                vm = re.search(r"V(\d+)", name)  # 例 導き書V2_GDE → V2
                return f"{label}{' v' + vm.group(1) if vm else ''}"
        return "Reference"
    if "/000_TX/" in p:
        m = re.search(r"TX v([0-9]+\.[0-9]+\.[0-9]+)\s+([A-Z][A-Z-]+)", html)
        return f"TX v{m.group(1)} {m.group(2)}" if m else "TX v11.1.0 LOOP-CORE"
    if "/001_JX/" in p:
        m = re.search(r"JX v([0-9]+\.[0-9]+\.[0-9]+)\s+([A-Z][A-Z-]+)", html)
        return f"JX v{m.group(1)} {m.group(2)}" if m else "JX v4.0.0 LOOP-FOLD"
    return "v?"


def _build_line(dt: datetime, version: str) -> str:
    """英語表記の機械可読スタンプ行。Lexia は data-generated と本文 "Generated: …" を読む。"""
    disp = dt.astimezone(JST).strftime("%Y-%m-%d %H:%M")
    iso = dt.astimezone(JST).isoformat(timespec="minutes")
    return (
        f'<p class="footer-date {GENMETA_CLASS}" data-generated="{iso}">'
        f'Generated: {disp} / {version}</p>'
    )


def stamp_html(html: str, dt: datetime, version: str) -> str:
    """HTML 文字列に英語スタンプを施して返す (冪等)。

    配置はフッターのコンテナ内に収める:
      1) 既存の genmeta 行があればその場で置換（位置＝既存コンテナを維持）。
      2) TX 既存の日本語 footer-date 行 (footer-spec コンテナ内) をその場で英語置換。
      3) どちらも無ければ </footer> 直前（footer コンテナ内）に挿入。
      4) <footer> が無いカテゴリ(RX/ARIADNE 等)は <footer class="lexia-foot"> で包んで挿入。
    """
    line = _build_line(dt, version)
    html = _LEGACY_COMMENT_RE.sub("", html)
    # 1) 既存 genmeta をその場置換（先頭1件・重複があれば後段で1本化）。
    if _GENMETA_RE.search(html):
        return _GENMETA_RE.sub(lambda _m: line + "\n", html, count=1)
    # 2) TX 既存の日本語 footer-date をその場で英語置換（footer-spec コンテナ内を維持）。
    if _NATIVE_FOOTERDATE_RE.search(html):
        return _NATIVE_FOOTERDATE_RE.sub(line + "\n", html, count=1)
    # 3) </footer> 直前（footer コンテナ内）に挿入。
    idx = html.rfind("</footer>")
    if idx != -1:
        return html[:idx] + line + "\n" + html[idx:]
    # 4) footer 要素が無い → <footer> で包んでコンテナ化し </body> 直前へ。
    wrapped = f'<footer class="lexia-foot">{line}</footer>\n'
    idx = html.rfind("</body>")
    if idx != -1:
        return html[:idx] + wrapped + html[idx:]
    return html.rstrip("\n") + "\n" + wrapped


def stamp_file(path: str, dt: datetime, version: str | None = None, *, dry_run: bool = False) -> bool:
    """ファイルを刻印。変更があれば書き戻し True を返す。dry_run 時は書かない。"""
    raw = Path(path).read_text(encoding="utf-8")
    ver = version or infer_version(path, raw)
    out = stamp_html(raw, dt, ver)
    if out == raw:
        return False
    if not dry_run:
        Path(path).write_text(out, encoding="utf-8")
    return True


def _parse_dt(s: str) -> datetime:
    s = s.strip()
    if s.lower() == "now":
        return datetime.now(JST)
    for fmt in ("%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            d = datetime.strptime(s, fmt)
            return d.replace(tzinfo=JST)
        except ValueError:
            continue
    # ISO (タイムゾーン付き含む)
    return datetime.fromisoformat(s)


def main() -> int:
    ap = argparse.ArgumentParser(description="フッターに生成日時＋版を刻む")
    ap.add_argument("file")
    ap.add_argument("--datetime", "-d", help='例 "2026-06-20 14:16" / ISO / "now"')
    ap.add_argument("--now", action="store_true", help="現在時刻(JST)で刻む")
    ap.add_argument("--version", "-v", help="版文字列 (省略時はパス/本文から推定)")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    dt = datetime.now(JST) if a.now or not a.datetime else _parse_dt(a.datetime)
    changed = stamp_file(a.file, dt, a.version, dry_run=a.dry_run)
    print(("[would stamp] " if a.dry_run else "[stamped] " if changed else "[nochange] ") + a.file)
    return 0


if __name__ == "__main__":
    sys.exit(main())
