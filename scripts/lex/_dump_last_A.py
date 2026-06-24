# -*- coding: utf-8 -*-
"""命題化の一次情報源を抽出：各問の cv/keys・記述本文（problem-text）・
   verdict-table コア・data-explanation を読みやすく dump する（編集補助・非配信）。"""
import re, sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SUBJ = os.path.join(ROOT, "outputs/000_TX/001_刑法")

def dump(num):
    h = open(os.path.join(SUBJ, f"刑TX{num}.html"), encoding="utf-8").read()
    m = re.search(r'<div class="answer-area" id="answer-area" data-correct-value="([^"]*)"[^>]*data-answer-type="([^"]*)"[^>]*data-explanation="(.*?)">', h, re.S)
    cv, at, expl = m.group(1), m.group(2), m.group(3)
    keys = re.findall(r'<div class="ox-row" data-stmt="([^"]*)"', h)
    # instruction
    pm = re.search(r'<p style="font-weight:600;">(.*?)</p>', h, re.S)
    instr = re.sub(r'<[^>]+>', '', pm.group(1)) if pm else '??'
    instr = re.sub(r'\s+', '', instr)
    # statement texts (problem-text with choice-num-inline)
    stmts = re.findall(r'<div class="problem-text"><span class="choice-num-inline">([^<]*)</span>(.*?)</div>', h, re.S)
    # verdict core
    cores = re.findall(r'<tr data-stmt="([^"]*)" data-verdict="([^"]*)">.*?<td>(.*?)</td></tr>', h, re.S)
    out = [f"################ {num}  type={at}  cv={cv}  keys={''.join(keys)}",
           f"INSTR: {instr[:160]}", ""]
    out.append("--- 記述本文 ---")
    for k, t in stmts:
        t = re.sub(r'<[^>]+>', '', t).strip()
        out.append(f"[{k}] {t}")
    out.append("")
    out.append("--- verdict コア ---")
    for k, v, c in cores:
        c = re.sub(r'<[^>]+>', '', c).strip()
        vv = '○' if v == 'o' else '×'
        out.append(f"[{k}={vv}] {c}")
    out.append("")
    out.append("--- explanation ---")
    out.append(re.sub(r'<[^>]+>', '', expl).strip())
    out.append("")
    return "\n".join(out)

if __name__ == '__main__':
    nums = sys.argv[1:]
    res = "\n\n".join(dump(n) for n in nums)
    open("/tmp/dump_last_A.txt", "w", encoding="utf-8").write(res)
    print(f"dumped {len(nums)} → /tmp/dump_last_A.txt ({len(res)} chars)")
