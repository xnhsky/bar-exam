# -*- coding: utf-8 -*-
r"""
耳トレ TTS フィーダー（問題フォルダ単位・半自動／再帰版）

前提のフォルダ構造:
  (科目)\TTSファイル原本\(問題ID)\(問題ID)-1a.txt ...
  例) 1 刑法\TTSファイル原本\刑JX028\刑JX028-1a.txt

渡すフォルダ:
  「TTSファイル原本」フォルダ を渡す（または起動後に選択）。
  その直下の各サブフォルダ＝1問として扱い、フォルダ名から番号・声を判定。

ワークフロー:
  1問 = 中の全パート(.txt)。各タブにそのタブ用パートを1つずつ貼っていく。
  実行(Ctrl+Enter)・タブ移動・ダウンロードは xnh が手動。
  本ツールは「次パートの本文をアクティブなタブのText欄に貼り付ける」だけ。

操作:
  各タブで Text欄をクリック → ホットキー Ctrl+Alt+V で貼付＆次パートへ → 自分でCtrl+Enter
  1問の全パートを貼り終えたら「次の問題 ▶」で次の問題フォルダへ

声: 奇数=Aoede / 偶数=Laomedeia。「偶数Laomedeia」で起動すれば偶数問題だけ順に。
本文はそのまま貼る（話者ラベル不要・確認済み）。

必要ライブラリ: pip install pyperclip pyautogui keyboard --break-system-packages
使い方: python tts_feeder.py "(TTSファイル原本フォルダのパス)"
"""
import os, re, sys, time
import tkinter as tk
from tkinter import ttk, filedialog

try:
    import pyperclip; HAS_CLIP = True
except Exception:
    HAS_CLIP = False
try:
    import pyautogui; HAS_PAG = True
    pyautogui.FAILSAFE = False
except Exception:
    HAS_PAG = False
try:
    import keyboard; HAS_KB = True
except Exception:
    HAS_KB = False

VOICE_ODD  = "Aoede"
VOICE_EVEN = "Laomedeia"
LIMIT = 5000
HOTKEY = "ctrl+alt+v"

def problem_no(name):
    m = re.search(r"JX0*(\d+)", name)
    if not m:
        m = re.search(r"0*(\d+)", name)
    return int(m.group(1)) if m else None

def parity_voice(n):
    if n is None:
        return ("番号不明", "?")
    return ("奇数", VOICE_ODD) if n % 2 == 1 else ("偶数", VOICE_EVEN)

def part_key(fname):
    """刑JX028-2a → (2,'a') でソート。数字+英字を拾う。"""
    m = re.search(r"-(\d+)([a-zA-Z]*)", fname)
    if m:
        return (int(m.group(1)), m.group(2))
    return (9999, fname)

def load_problems(root_folder, parity="all"):
    """
    root_folder 直下の各サブフォルダ＝1問として読む。
    返り値: [(no, folder_name, folder_path, [part_filenames...]), ...] 番号順
    .txt が直下に直接ある場合も、その親を1問として拾う（保険）。
    """
    problems = []
    try:
        entries = sorted(os.listdir(root_folder))
    except Exception:
        return problems

    for name in entries:
        path = os.path.join(root_folder, name)
        if not os.path.isdir(path):
            continue
        parts = [f for f in os.listdir(path) if f.lower().endswith(".txt")]
        if not parts:
            continue
        n = problem_no(name)
        if n is None:
            # フォルダ名に番号が無ければ中のファイル名から拾う
            n = problem_no(parts[0])
        if parity == "odd" and (n is None or n % 2 == 0):
            continue
        if parity == "even" and (n is None or n % 2 == 1):
            continue
        parts.sort(key=part_key)
        problems.append((n, name, path, parts))

    problems.sort(key=lambda x: (x[0] is None, x[0] if x[0] is not None else 0))
    return problems


class Feeder:
    def __init__(self, root, folder):
        self.root = root
        self.folder = folder
        self.parity = tk.StringVar(value="all")
        self.autopaste = tk.BooleanVar(value=HAS_PAG)
        self.status = tk.StringVar(value="")
        self.problems = []
        self.pi = 0
        self.ti = 0

        root.title("耳トレ TTS フィーダー（問題フォルダ単位）")
        root.attributes("-topmost", True)
        root.geometry("470x580")

        top = ttk.Frame(root, padding=8); top.pack(fill="x")
        ttk.Button(top, text="フォルダ選択(原本)", command=self.choose).pack(side="left")
        self.folder_lbl = ttk.Label(top, text=folder or "(未選択)", foreground="#888")
        self.folder_lbl.pack(side="left", padx=6)

        pf = ttk.Frame(root, padding=(8, 0)); pf.pack(fill="x")
        ttk.Label(pf, text="対象:").pack(side="left")
        for txt, val in [("すべて", "all"), ("奇数Aoede", "odd"), ("偶数Laomedeia", "even")]:
            ttk.Radiobutton(pf, text=txt, value=val, variable=self.parity,
                            command=self.reload).pack(side="left")

        cur = ttk.Frame(root, padding=8); cur.pack(fill="x")
        self.prob = ttk.Label(cur, text="-", font=("", 11)); self.prob.pack(anchor="w")
        self.voice = ttk.Label(cur, text="-", font=("", 13, "bold")); self.voice.pack(anchor="w", pady=2)
        self.part = ttk.Label(cur, text="-", font=("", 15, "bold")); self.part.pack(anchor="w")
        self.chars = ttk.Label(cur, text="", foreground="#888"); self.chars.pack(anchor="w")

        bf = ttk.Frame(root, padding=8); bf.pack(fill="x")
        ttk.Button(bf, text="◀ 前の問題", command=self.prev_problem).pack(side="left")
        ttk.Button(bf, text="次の問題 ▶", command=self.next_problem).pack(side="right")

        bf2 = ttk.Frame(root, padding=(8, 0)); bf2.pack(fill="x")
        ttk.Button(bf2, text="◀ パート戻す", command=self.prev_part).pack(side="left")
        self.copy_btn = ttk.Button(bf2, text="📋 コピーのみ→次パート",
                                   command=lambda: self.do_paste(allow_autopaste=False))
        self.copy_btn.pack(side="left", expand=True, fill="x", padx=6)

        ttk.Checkbutton(root, text=f"ホットキー({HOTKEY})で自動Ctrl+V貼り付け",
                        variable=self.autopaste).pack()

        lf = ttk.Frame(root, padding=8); lf.pack(fill="both", expand=True)
        self.listbox = tk.Listbox(lf, activestyle="dotbox")
        self.listbox.pack(side="left", fill="both", expand=True)
        sb = ttk.Scrollbar(lf, command=self.listbox.yview); sb.pack(side="right", fill="y")
        self.listbox.config(yscrollcommand=sb.set)

        ttk.Label(root, textvariable=self.status, foreground="#0a7",
                  padding=6, wraplength=450).pack(fill="x")

        miss = [n for n, ok in [("pyperclip", HAS_CLIP), ("pyautogui", HAS_PAG), ("keyboard", HAS_KB)] if not ok]
        if miss:
            self.status.set("未導入: " + ", ".join(miss) + " → コピーのみ動作")

        if HAS_KB and HAS_CLIP:
            try:
                keyboard.add_hotkey(HOTKEY, self._hotkey)
            except Exception as e:
                self.status.set(f"ホットキー登録失敗: {e}（管理者で再起動 or コピーのみ）")

        root.bind("<Right>", lambda e: self.next_problem())
        root.bind("<Left>",  lambda e: self.prev_problem())

        if folder:
            self.reload()

    def choose(self):
        d = filedialog.askdirectory()
        if d:
            self.folder = d
            self.folder_lbl.config(text=d)
            self.reload()

    def reload(self):
        if not self.folder:
            return
        self.problems = load_problems(self.folder, self.parity.get())
        self.pi = 0; self.ti = 0
        self.refresh()

    def cur(self):
        if not self.problems:
            return None
        return self.problems[self.pi]

    def refresh(self):
        if not self.problems:
            self.prob.config(text="該当する問題なし（原本フォルダを渡したか確認）")
            self.voice.config(text="-"); self.part.config(text="-"); self.chars.config(text="")
            self.listbox.delete(0, "end")
            return
        self.pi = max(0, min(self.pi, len(self.problems) - 1))
        no, fname, fpath, parts = self.cur()
        par, v = parity_voice(no)
        self.prob.config(text=f"問題 {self.pi + 1}/{len(self.problems)}   {fname}")
        color = "#1565c0" if v == VOICE_EVEN else "#c62828"
        self.voice.config(text=f"{par} → {v} タブ群", foreground=color)

        self.listbox.delete(0, "end")
        for i, p in enumerate(parts):
            mark = "→ " if i == self.ti else "   "
            self.listbox.insert("end", f"{mark}{p}")
        if 0 <= self.ti < len(parts):
            self.listbox.selection_clear(0, "end")
            self.listbox.selection_set(self.ti); self.listbox.see(self.ti)

        if self.ti >= len(parts):
            self.part.config(text=f"✅ 全{len(parts)}パート貼付済み → 「次の問題 ▶」")
            self.chars.config(text="")
        else:
            p = parts[self.ti]
            self.part.config(text=f"パート {self.ti + 1}/{len(parts)} : {p}")
            try:
                with open(os.path.join(fpath, p), encoding="utf-8") as fh:
                    n = len(fh.read().strip())
                warn = "  ★5000字超：分割推奨" if n > LIMIT else ""
                self.chars.config(text=f"{n}字{warn}")
            except Exception as e:
                self.chars.config(text=f"読込エラー: {e}")

    def _hotkey(self):
        self.do_paste(allow_autopaste=True, from_hotkey=True)

    def do_paste(self, allow_autopaste=True, from_hotkey=False):
        if not self.problems:
            return
        no, fname, fpath, parts = self.cur()
        if self.ti >= len(parts):
            self.status.set("この問題は貼付完了。「次の問題 ▶」を押してください")
            return
        p = parts[self.ti]
        try:
            with open(os.path.join(fpath, p), encoding="utf-8") as fh:
                body = fh.read().strip()
        except Exception as e:
            self.status.set(f"読込失敗: {e}")
            return

        if HAS_CLIP:
            pyperclip.copy(body)
        else:
            self.root.clipboard_clear(); self.root.clipboard_append(body); self.root.update()

        if allow_autopaste and from_hotkey and self.autopaste.get() and HAS_PAG:
            time.sleep(0.08)
            pyautogui.hotkey("ctrl", "v")
            msg = f"貼付: {p} → 次パートへ（Ctrl+Enterで実行）"
        else:
            msg = f"コピー: {p} → タブにCtrl+Vで貼付、次パートへ"

        self.ti += 1
        self.root.after(0, self.refresh)
        self.root.after(0, lambda: self.status.set(msg))

    def next_problem(self):
        if self.pi < len(self.problems) - 1:
            self.pi += 1; self.ti = 0
            self.refresh()
            self.status.set("次の問題へ。タブ1から貼り直してください")
        else:
            self.status.set("最後の問題です")

    def prev_problem(self):
        if self.pi > 0:
            self.pi -= 1; self.ti = 0
            self.refresh()

    def prev_part(self):
        if self.ti > 0:
            self.ti -= 1
            self.refresh()


def main():
    folder = sys.argv[1] if len(sys.argv) > 1 else ""
    root = tk.Tk()
    Feeder(root, folder)
    root.mainloop()

if __name__ == "__main__":
    main()
