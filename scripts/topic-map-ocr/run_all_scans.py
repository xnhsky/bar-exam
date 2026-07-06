# -*- coding: utf-8 -*-
"""全6冊の柱スキャンを順に実行(再開可能)。実行中はスリープ阻止、終了時に解除。
DATA_DIR に PDF(keiso.pdf 等)と出力先 toc_ocr/ がある前提。
既に <name>_headers.jsonl が存在(>100B)する冊はスキップ(=再開)。
実行: python run_all_scans.py            (全冊、済みはスキップ)
      python run_all_scans.py --force    (全冊やり直し)
"""
import ctypes, importlib.util, sys, time, os

# ★ PDF と出力(toc_ocr/)がある作業ディレクトリ。temp が消えたら PDF を再配置してこのパスを更新。
DATA_DIR = r"C:\Users\xnrg2.DESKTOP-5664QR6\AppData\Local\Temp\claude\C--Users-xnrg2-DESKTOP-5664QR6\7d7b8729-a15f-47d6-ae1e-017a26b3e582\scratchpad"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BOOKS = ["keiso", "kenpo", "minpo1", "minpo2", "minso", "shoho"]

ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001

def keep_awake(on):
    try:
        ctypes.windll.kernel32.SetThreadExecutionState(
            (ES_CONTINUOUS | ES_SYSTEM_REQUIRED) if on else ES_CONTINUOUS)
    except Exception as e:
        print("keep_awake err", e)

def load_scan():
    spec = importlib.util.spec_from_file_location(
        "scan_headers", os.path.join(SCRIPT_DIR, "scan_headers.py"))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m

def done(name):
    """完了判定: jsonl の最終ページが PDF 総ページ数の -3 以内なら完了。
    (open(w) はバッファ flush で途中書きされるため getsize では部分書きと区別不可)"""
    import json as _json, fitz as _fitz
    f = os.path.join(DATA_DIR, "toc_ocr", f"{name}_headers.jsonl")
    if not os.path.exists(f) or os.path.getsize(f) < 100:
        return False
    try:
        last = None
        for line in open(f, encoding="utf-8"):
            line = line.strip()
            if line: last = line
        lastp = _json.loads(last)["p"]
        total = _fitz.open(os.path.join(DATA_DIR, name + ".pdf")).page_count
        return lastp >= total - 3
    except Exception:
        return False

def main():
    force = "--force" in sys.argv
    os.chdir(DATA_DIR)
    os.makedirs("toc_ocr", exist_ok=True)
    sh = load_scan()
    import fitz
    keep_awake(True)
    try:
        with open("toc_ocr/_scan_progress.log", "a", encoding="utf-8") as lg:
            lg.write(f"[{int(time.time())}] === run_all_scans start (force={force}) ===\n")
        for b in BOOKS:
            if not force and done(b):
                print(f"skip {b} (done)"); continue
            n = fitz.open(os.path.join(DATA_DIR, b + ".pdf")).page_count
            sh.run(b, 15, n)
            print(f"done {b}")
        open("toc_ocr/_SCAN_DONE", "w").write("done")
        print("ALL DONE")
    finally:
        keep_awake(False)

if __name__ == "__main__":
    main()
