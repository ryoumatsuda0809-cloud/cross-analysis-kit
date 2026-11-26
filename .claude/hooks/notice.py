#!/usr/bin/env python3
"""notice.py ｜ 検査結果を★本人の画面にだけ出すフック（移行 段6）

  python3 notice.py report   … PostToolUse（Write|Edit）。06 を書いたら check_report --draft の結果を出す
                               01・01i を書いたら①の検査（card_checks・01 は lint_01 も）の結果を出す（09-28）
  python3 notice.py anken    … SubagentStop。案件出力の形（B1〜B10）の違反を出す

  ★エージェントには返さない（systemMessage＝本人にだけ見える）。exit は常に 0 で、何も止めない。
    ④は今 check_report を自分で回していない。結果をエージェントに渡すと④の振る舞いが変わる＝設計の変更になる
    （tests/移行台帳.md §7）。見て、直すかを決めるのは本人。
  ★出すのは NG 行とルール名だけ（anken_checks は本文を返さない。check_report の NG 行は該当語だけ）。
"""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def say(msg):
    if msg:
        print(json.dumps({"systemMessage": msg}, ensure_ascii=False))


CARDS = ("01_外形カード_事実編.md", "01i_外形カード_内部用.md")


def card(path):
    """①の出力（01・01i）を保存したら、その案件の①の検査（tests/card_checks.py）と、01 なら lint_01 の結果を出す。
    ①はメイン会話で回るので SubagentStop が出ない。ここで流さないと pre-commit まで誰も見ない（台帳 §8・09-28）。"""
    sys.path.insert(0, os.path.join(ROOT, "tests"))
    import card_checks as C
    lines = [C.describe(v) for v in C.check_case(Path(path).parent)]
    if os.path.basename(path) == CARDS[0]:
        r = subprocess.run([sys.executable, os.path.join(ROOT, ".claude", "skills", "market-recon", "scripts", "lint_01.py"),
                            path], capture_output=True, text=True)
        lines += ["lint_01 " + l.strip() for l in r.stdout.splitlines() if l.strip().startswith(("NG", "WARN"))]
    name = os.path.basename(path).split("_")[0]
    say(f"[①の検査] {name} を保存。違反・注意 {len(lines)} 件\n" + "\n".join(lines[:15]) if lines
        else f"[①の検査] {name} を保存。違反 0 件")


def report(data):
    path = (data.get("tool_input") or {}).get("file_path", "")
    if not os.path.exists(path):
        return
    if os.path.basename(path) in CARDS:
        return card(path)
    if not path.endswith("06_課題仮説レポート.md"):
        return
    r = subprocess.run([sys.executable, os.path.join(ROOT, "対外資料", "_report_build", "check_report.py"),
                        "--draft", path], capture_output=True, text=True)
    ng = [l.strip() for l in r.stdout.splitlines() if l.strip().startswith("NG")]
    say(f"[check_report] 06 は NG {len(ng)} 件\n" + "\n".join(ng[:15]) if ng else "[check_report] 06 は NG 0 件")


def anken(_data):
    sys.path.insert(0, os.path.join(ROOT, "tests"))
    import anken_checks as A
    base = os.path.join(ROOT, "案件")
    if not os.path.isdir(base):
        return
    lines = []
    for d in sorted(os.listdir(base)):
        p = os.path.join(base, d)
        if os.path.isdir(p) and d != "_使わない" and not d.startswith("_TEST_"):
            lines += [f"{d}：{v}" for v in A.check_anken(p)]
    if lines:
        say("[案件出力の形] 違反 %d 件\n" % len(lines) + "\n".join(lines[:15]))


def main():
    try:
        data = json.loads(sys.stdin.buffer.read().decode("utf-8"))
    except Exception:
        data = {}
    try:
        {"report": report, "anken": anken}[sys.argv[1]](data)
    except Exception as e:          # 知らせるだけのフックが作業を止めない
        say(f"[notice.py] 実行できなかった：{type(e).__name__}")
    return 0


if __name__ == "__main__":
    for _s in (sys.stdout, sys.stderr):
        if hasattr(_s, "reconfigure"):
            _s.reconfigure(encoding="utf-8", errors="replace")   # Windows の端末でも日本語で落ちない
    sys.exit(main())
