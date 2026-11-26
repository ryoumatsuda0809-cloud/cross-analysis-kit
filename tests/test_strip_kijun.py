"""strip_kijun.py（③に埋め込む前に事前の基準を外す）の挙動を固定する。

★架空の 03 と、本物のテンプレ（名前に _封 が無い assets）だけを使う。実在の 03・02b は読まない。
★本物のテンプレで確かめる理由：外部の試作は架空の 03 では通ったが、本物のテンプレの説明
  （「当たり／外れ：…」「手段：…」「社内だけ」）を外し残した（10-03）。形が変わったらここで落とす。
"""
import random
import subprocess
import sys

import pytest

from conftest import REPO, SCRIPTS, load_script

sk = load_script("strip_kijun")
ASSETS = REPO / ".claude" / "skills" / "market-recon" / "assets"

FAKE_03 = """# 【封】仮説｜架空のX社
## 現実とのギャップ仮説
> 各仮説に 根拠・出典・担当タグ・事前の基準 を付ける。
> - p：当たる見込み。0.8／0.5／0.2 のどれか
> タグは固定リスト：`#市場` `#現場オペ`
1. 【仮説】段取り替えが特定の1人に寄っている可能性 〔根拠／出典〕架空の求人票 〔タグ：#現場オペ〕
   〔当たり〕作業日報で… 〔外れ〕… 〔いつ〕現場の直後 〔手段〕書類 〔p〕0.8
2. 【仮説】受注の波が月末に寄る可能性 〔根拠／出典〕架空の決算公告 〔タグ：#財務〕 〔p〕0.5
"""


def run(stdin, *args):
    return subprocess.run([sys.executable, str(SCRIPTS["strip_kijun"]), *args],
                          input=stdin, capture_output=True, text=True)


def test_removes_criteria_and_keeps_hypotheses():
    body, dropped, cut, left = sk.strip(FAKE_03)
    assert left == []
    for w in ("〔p〕", "〔当たり〕", "当たる見込み", "事前の基準"):
        assert w not in body
    assert "段取り替えが特定の1人に寄っている可能性" in body
    assert "〔タグ：#財務〕" in body                 # 印より前は残す
    assert "`#市場`" in body                         # 基準と関係ない説明は残す
    assert (dropped, cut) == (3, 1)


@pytest.mark.parametrize("name", ["03-hypotheses-sealed-template.md", "02b-mitate-sealed-template.md"])
def test_engine_templates_leave_no_trace_of_criteria(name):
    src = (ASSETS / name).read_text(encoding="utf-8")
    assert sk.MARK.search(src), "テンプレから基準の行が消えた。strip_kijun とこのテストを見直す"
    body, _, _, left = sk.strip(src)
    assert left == []
    assert not sk.MARK.search(body)
    quoted = [l for l in body.splitlines() if l.lstrip().startswith(">")]
    assert not [l for l in quoted if sk.NOTE.search(l.lstrip())], "説明の行に基準の話が残っている"
    kept = [l for l in src.splitlines() if l.startswith("#")]
    assert all(h in body.splitlines() for h in kept)  # 見出しは全部残す（案件名の照合に使う）


def test_property_random_lines():
    rnd = random.Random(20261003)
    marks = ["〔当たり〕a", "〔外れ〕b", "〔いつ〕3か月後", "〔手段〕数字", "〔p〕0.2", "〔ｐ〕0.8"]
    plain = ["普通の行", "1人当たりの受注", "〔タグ：#DX〕", "## 見出し", ""]
    for _ in range(300):
        lines = [rnd.choice(plain) + (" " + " ".join(rnd.sample(marks, rnd.randint(1, 3))) if rnd.random() < 0.5 else "")
                 for _ in range(rnd.randint(1, 8))]
        body, _, _, left = sk.strip("\n".join(lines))
        assert left == [] and not sk.MARK.search(body)
        kept = [l for l in lines if l and not sk.MARK.search(l)]
        assert all(k in body.splitlines() for k in kept)          # 印の無い行は消さない・順も保つ


def test_cli_refuses_file_args(tmp_path):
    r = run("", str(tmp_path / "03_仮説_x.md"))
    assert r.returncode == 2 and r.stdout == ""


def test_cli_fail_closed_on_leftover():
    r = run("この見立ては p＝0.8 程度\n")      # 印でない形の p は外さず、外し残しとして止める
    assert r.returncode == 1 and r.stdout == ""


def test_cli_prints_counts_only():
    r = run(FAKE_03)
    assert r.returncode == 0
    assert "段取り替え" in r.stdout and "段取り替え" not in r.stderr
    assert "行ごと 3・一部 1" in r.stderr


def test_cli_empty_input():
    r = run("")
    assert r.returncode == 0 and r.stdout == ""
