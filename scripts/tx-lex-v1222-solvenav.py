#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""TXLEX v12.2.2 solve-nav upgrader (deterministic, idempotent).

Old v12.2.1 _lex files carry the "軽量版・057系" solve-nav that only points the
learner to the ox-grid below ("下の一問一答") — this fails G44 (needs in-nav ○×
via .sn-answer-choices / .sn-nav-ox and "このナビ内" wording).

This tool ports the upgraded engine + solve-nav CSS block verbatim from the gold
sample 刑TX367_lex.html, preserving each target file's OWN problem-specific STEP /
ORDER data (same {label,q,tip,hint} contract). Newlines preserved (newline='').

Only touches files whose 2nd solve-nav <script> is the "軽量版" variant; files that
already use the newer engine (var STMT / SCRIPT-OX) are skipped.

Usage: python -X utf8 scripts/tx-lex-v1222-solvenav.py <target_lex.html> [...]
"""
import io, re, sys, os

ENGINE_SRC = os.path.join(os.path.dirname(__file__), "..",
                          "outputs", "ux", "000_TX", "001_刑法", "刑TX367_lex.html")

CSS_START = "/* === 解法ナビ CSS（canonical/SOLVE-NAV.html 正典より注入） === */"
CSS_END = "/* === 選択肢の高速化：要点一行"
ENGINE_NEEDLE = "解法ナビ（軽量版"


def read(p):
    return io.open(p, encoding="utf-8", newline="").read()


def write(p, t):
    with io.open(p, "w", encoding="utf-8", newline="") as f:
        f.write(t)


def find_script(html, needle):
    for m in re.finditer(r"<script>.*?</script>", html, re.S):
        if needle in m.group(0):
            return m.start(), m.end(), m.group(0)
    return None


def var_line(script, varname):
    m = re.search(r"(?m)^[ \t]*var[ \t]+" + varname + r"\b.*$", script)
    return m


def main():
    src = read(ENGINE_SRC)
    cs = src.index(CSS_START)
    ce = src.index(CSS_END, cs)
    src_css = src[cs:ce]
    s = find_script(src, ENGINE_NEEDLE)
    if not s:
        print("[FATAL] engine template not found in", ENGINE_SRC); sys.exit(2)
    src_script = s[2]

    for target in sys.argv[1:]:
        h = read(target)
        tscript = find_script(h, ENGINE_NEEDLE)
        if not tscript:
            print("[SKIP] %s (already newer engine / no 軽量版 script)" % target)
            continue
        # 1. swap solve-nav CSS block
        tcs = h.index(CSS_START)
        tce = h.index(CSS_END, tcs)
        h = h[:tcs] + src_css + h[tce:]
        # 2. re-locate target script after CSS swap, preserve its STEP/ORDER
        t0, t1, t_body = find_script(h, ENGINE_NEEDLE)
        t_order = var_line(t_body, "ORDER")
        t_step = var_line(t_body, "STEP")
        if not (t_order and t_step):
            print("[SKIP] %s (no STEP/ORDER found)" % target); continue
        new_script = src_script
        new_script = re.sub(r"(?m)^[ \t]*var[ \t]+ORDER\b.*$",
                            lambda _m: t_order.group(0), new_script, count=1)
        new_script = re.sub(r"(?m)^[ \t]*var[ \t]+STEP\b.*$",
                            lambda _m: t_step.group(0), new_script, count=1)
        h = h[:t0] + new_script + h[t1:]
        write(target, h)
        print("[OK] %s solve-nav upgraded (engine+CSS from 367, own STEP/ORDER kept)" % target)


if __name__ == "__main__":
    main()
