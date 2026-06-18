#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""density-v2 char 数計測ツール（罠 10 解消・参考実装）

Phase 13C-4: claude.ai 起草段階と HTML 生成後の両経路で同一の density-v2 char 数
判定を実現。Phase 14 量産時の規律準拠検証ツールとして機能。

使い方:
    python scripts/measure_density_v2.py problems/305.json     # JSON モード
    python scripts/measure_density_v2.py outputs/000_TX/001_刑法/刑TX305.html  # HTML モード
"""
import sys
import json
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")  # Windows cp932 回避

THRESHOLD_PASS = 1150
THRESHOLD_WARN = 800


def verdict(total: int) -> str:
    if total >= THRESHOLD_PASS:
        return "PASS"
    elif total >= THRESHOLD_WARN:
        return "WARN"
    else:
        return "FAIL"


def measure_json(json_path: Path) -> list[dict]:
    """JSON フィールド値の純 char 数を集計（罠 10 直接対応）"""
    data = json.loads(json_path.read_text(encoding="utf-8"))
    results = []
    for i, choice in enumerate(data.get("choices", []), 1):
        prof = choice.get("professor") or {}
        if not prof:
            continue
        p = prof.get("point", {})
        pr = prof.get("process", {})
        im = prof.get("image", {})
        ap = prof.get("application", {})

        point_chars = len(p.get("locus", "")) + sum(len(x) for x in p.get("list", []))
        process_chars = sum(len(x) for x in pr.get("steps", []))
        image_chars = sum(len(im.get(k, "")) for k in ("scene", "bridge", "contrast"))
        app_chars = sum(len(ap.get(k, "")) for k in ("major", "minor", "conclusion"))
        total = point_chars + process_chars + image_chars + app_chars

        results.append({
            "choice": i,
            "point": point_chars,
            "process": process_chars,
            "image": image_chars,
            "application": app_chars,
            "total": total,
            "verdict": verdict(total),
        })
    return results


def measure_html(html_path: Path) -> list[dict]:
    """HTML 内 prof-heading の text 純 char 数を集計（事後検証用）"""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")

    all_headings = soup.find_all("div", class_="prof-heading")
    if len(all_headings) % 4 != 0:
        raise RuntimeError(f"prof-heading 数 {len(all_headings)} が 4 の倍数でない")

    n_choices = len(all_headings) // 4
    results = []
    for i in range(n_choices):
        chunk = all_headings[i * 4:(i + 1) * 4]
        counts = {"point": 0, "process": 0, "image": 0, "application": 0}
        for h in chunk:
            # 見出し h4/h5 を除去（JSON 計測と整合させるため）
            h_copy = BeautifulSoup(str(h), "html.parser")
            for tag in h_copy.find_all(["h4", "h5"]):
                tag.decompose()
            text = h_copy.get_text(strip=False)
            # whitespace 圧縮（HTML 整形改行を JSON 計測に揃える）
            text = "".join(text.split())

            classes = h.get("class", [])
            if "prof-point" in classes:
                counts["point"] = len(text)
            elif "prof-process" in classes:
                counts["process"] = len(text)
            elif "prof-image" in classes:
                counts["image"] = len(text)
            elif "prof-application" in classes:
                counts["application"] = len(text)

        total = sum(counts.values())
        results.append({
            "choice": i + 1,
            **counts,
            "total": total,
            "verdict": verdict(total),
        })
    return results


def print_table(results: list[dict], src: str, mode: str):
    print(f"== density-v2 計測: {src} ({mode} mode) ==")
    print(f"{'choice':<7}|{'point':>7}|{'process':>9}|{'image':>7}|{'application':>13}|{'total':>7}| verdict")
    print("-" * 70)
    for r in results:
        print(f"{r['choice']:<7}|{r['point']:>7}|{r['process']:>9}|{r['image']:>7}|{r['application']:>13}|{r['total']:>7}| {r['verdict']}")
    print(f"\n規律: {THRESHOLD_PASS}+ (PASS) / {THRESHOLD_WARN}-{THRESHOLD_PASS - 1} (WARN) / <{THRESHOLD_WARN} (FAIL)")

    n_pass = sum(1 for r in results if r["verdict"] == "PASS")
    n_warn = sum(1 for r in results if r["verdict"] == "WARN")
    n_fail = sum(1 for r in results if r["verdict"] == "FAIL")
    print(f"集計: PASS={n_pass} / WARN={n_warn} / FAIL={n_fail} / 全件={len(results)}")


def main():
    if len(sys.argv) != 2:
        print("使い方: python scripts/measure_density_v2.py <JSON または HTML パス>", file=sys.stderr)
        sys.exit(1)

    target = Path(sys.argv[1])
    if not target.exists():
        print(f"ERROR: ファイルが存在しない: {target}", file=sys.stderr)
        sys.exit(1)

    suffix = target.suffix.lower()
    if suffix == ".json":
        results = measure_json(target)
        mode = "JSON"
    elif suffix == ".html":
        results = measure_html(target)
        mode = "HTML"
    else:
        print(f"ERROR: 未対応の拡張子: {suffix}", file=sys.stderr)
        sys.exit(1)

    if not results:
        print("WARNING: density-v2 (professor) フィールド未検出", file=sys.stderr)
        sys.exit(0)

    print_table(results, str(target), mode)

    n_fail = sum(1 for r in results if r["verdict"] == "FAIL")
    sys.exit(1 if n_fail > 0 else 0)


if __name__ == "__main__":
    main()
