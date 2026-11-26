"""build.sh の配線を固定する（B 群の延長その2。tougou-report #445・#538）。

★合成データだけを使う。実在の 06 は読まない。PDF も作らない：
  偽の pandoc（終了コード 42）を PATH の先頭に置き、「検査を通って PDF 化の手前まで来たか」だけを見る。
★見るのは配線だけ：内部メモを除去してから check_report に掛けるか（#445）、NG なら PDF を作らずに止まるか（#538）。
  check_report そのものの判定は test_check_report.py が見る。
"""
import os
import shutil
import subprocess
import sys

import pytest

from conftest import REPO
from test_check_report import report

BUILD = REPO / "対外資料" / "_report_build" / "build.sh"
REACHED_PANDOC = 42

def _bash():
    """Windows では Git Bash を使う（PATH の bash が WSL のことがある）。"""
    if sys.platform.startswith("win"):
        for p in (r"C:\Program Files\Git\bin\bash.exe", r"C:\Program Files (x86)\Git\bin\bash.exe"):
            if os.path.exists(p):
                return p
        return None
    return shutil.which("bash")


BASH = _bash()
pytestmark = pytest.mark.skipif(BASH is None, reason="bash（Windows は Git Bash）が無い")


@pytest.fixture
def build(tmp_path):
    fake = tmp_path / "bin"
    fake.mkdir()
    (fake / "pandoc").write_text(f"#!/bin/sh\nexit {REACHED_PANDOC}\n", encoding="utf-8")
    (fake / "pandoc").chmod(0o755)
    out = tmp_path / "out"   # リポジトリの外（build.sh の許可リストの「関与しない」側）
    out.mkdir()
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env["PATH"] = f"{fake}{os.pathsep}{env.get('PATH', '')}"

    def _run(text):
        src = out / "06.md"
        src.write_text(text, encoding="utf-8")
        pdf = out / "x.pdf"
        r = subprocess.run([BASH, str(BUILD), str(src), str(pdf)], env=env,
                           capture_output=True, text=True, timeout=60)
        return r.returncode, r.stdout + r.stderr, src, pdf
    return _run


def test_internal_memo_is_stripped_before_check(build):
    """#445：内部メモ（封・定規・実走ログの語を含む）は除去してから検査する。除去しなければ check_report が落とす。"""
    text = report(comment=True)
    code, out, src, pdf = build(text)
    assert code == REACHED_PANDOC, out
    assert "内部メモ 1 件を除去した" in out
    assert src.read_text(encoding="utf-8") == text, "元の 06 を書き換えた"


def test_ng_stops_before_pdf(build):
    """#538：check_report が NG なら PDF を作らずに止まる（pandoc まで行かない）。"""
    code, out, _, pdf = build(report(comment=False, drop="次の一歩"))
    assert code == 1, out
    assert "検査に通らなかったので PDF は作っていません" in out
    assert not pdf.exists()


def test_internal_word_outside_memo_stops(build):
    """#538：本文（内部メモの外）に内部語が残っていれば止まる。除去が本文まで消していないことの裏返し。"""
    code, out, _, pdf = build(report(comment=False) + "\n棄却した説明は載せていません。\n")
    assert code == 1, out
    assert not pdf.exists()
