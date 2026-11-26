"""runner/run_stage.py の封（渡さない）を確かめる。AI は呼ばない（10-18・STATUS §2 1b）
★封のファイルは作らない・開かない（conftest の seal_guard）。名前の表と、読む前に止めることだけを見る"""
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "runner"))
import run_stage as r  # noqa: E402


def make_case(tmp_path, with_01i=True):
    case = tmp_path / "案件X"
    (case / "_材料/B_現場").mkdir(parents=True)
    (case / r.MEMO).write_text("【工場長】現場の話\n", encoding="utf-8")
    if with_01i:
        (case / "01i_外形カード_内部用.md").write_text("従業員数 32名／35名\n", encoding="utf-8")
    (case / "01_外形カード_事実編.md").write_text("提出用の体裁\n", encoding="utf-8")
    (case / "04_現場分析.md").write_text("04 の本文\n", encoding="utf-8")
    (case / "05_反証レポート.md").write_text("05 は封の中身を含む\n", encoding="utf-8")
    return case


@pytest.mark.parametrize("stage", ["2", "B1"])
def test_表に封も05以降も無い(stage):
    st = r.STAGES[stage]
    for n in st["repo_files"] + st["case_files"] + list(st["fallback"].values()):
        assert "封" not in n
        assert not Path(n).name.startswith(("03", "02b", "05", "06", "07", "08"))


def test_2は01iがあれば提出用の01を渡さない(tmp_path):
    case = make_case(tmp_path)
    prompt, items = r.build("2", case, case, str(r.PROMPTS))
    got = {Path(n).name for n, _ in items}
    assert "01i_外形カード_内部用.md" in got and "01_外形カード_事実編.md" not in got
    assert "05 は封の中身を含む" not in prompt


def test_2は01iが無ければ01で代用する(tmp_path):
    case = make_case(tmp_path, with_01i=False)
    _, items = r.build("2", case, case, str(r.PROMPTS))
    assert "01_外形カード_事実編.md" in {Path(n).name for n, _ in items}


def test_B1はメモと04だけ(tmp_path):
    case = make_case(tmp_path)
    _, items = r.build("B1", case, case, str(r.PROMPTS))
    assert {Path(n).name for n, _ in items} == {"現場メモ.md", "04_現場分析.md"}


def test_seal_の名前の添付は読む前に止める(tmp_path, monkeypatch):
    case = make_case(tmp_path)          # 03 は作らない。読もうとすれば conftest が止める
    monkeypatch.setitem(r.STAGES["B1"], "case_files", [r.MEMO, "03_仮説_封.md"])
    with pytest.raises(SystemExit, match="封のファイルを渡そうとした"):
        r.gather("B1", case, case)


def test_ぶれの集計はB1の判定を数え本文を書かない(tmp_path):
    import k_runs as k
    d = tmp_path / "r1"
    d.mkdir()
    (d / "B-1.md").write_text(
        "| 04 の節 | 行の # | 判定 | メモの行番号 | 理由 |\n|---|---|---|---|---|\n"
        "| §1 | 1 | あり | L3 | |\n| §1 | 2 | 一部 | L4 | メモに無い数字 |\n| §2 | 1 | なし | | メモに無い人物 |\n",
        encoding="utf-8")
    s = k.summarize(tmp_path, 2, {2: "② 失敗"})
    assert "| r1 | 2 | 1 | 1 | 1 | 1 |" in s
    assert "§1#2（一部：メモに無い数字）" in s
    assert "回せた回数：1/2" in s


FAKE_03 = "# 【封】仮説｜株式会社テスト\n\nH1 在庫が多い可能性\n〔当たり〕棚卸で確認〔外れ〕在庫が少ない〔p〕0.8\n"


def place_sealed_name(case, name):
    """封の名前のファイルを「開かずに」置く（別名で作って名前だけ変える。中身は空）"""
    (case / "tmp_empty").write_text("", encoding="utf-8")
    os.rename(case / "tmp_empty", case / name)


SEALED_03 = "03_仮説_" + "封.md"


def test_3は封を最後に02bから03の順で置き現場メモを渡さない(tmp_path):
    case = make_case(tmp_path)
    place_sealed_name(case, SEALED_03)
    prompt, items = r.build("3", case, case, str(r.PROMPTS),
                            sealed_texts=[("02b", "人間の見立ての本文"), ("03", "AIの仮説の本文")])
    names = [Path(n).name for n, _ in items]
    assert names[3:] == ["04_現場分析.md", "01i_外形カード_内部用.md"]   # 手順3つの後、04→01i（02 は無い）
    assert "現場メモ.md" not in names
    i04, i02b, i03 = prompt.index("【添付】" + str(case / "04_現場分析.md")), prompt.index("人間の見立ての本文"), prompt.index("AIの仮説の本文")
    assert i04 < i02b < i03
    assert prompt.rstrip().endswith("AIの仮説の本文\n`````")
    assert "{ここに" not in prompt          # 雛形の貼り場所は案内に置き換わる


def test_3の封は照合が合うまで待ち基準を外しクリップボードを空にする():
    clips = iter(["関係ない文章", FAKE_03.replace("テスト", "別の会社"), FAKE_03])
    said, cleared = [], []
    body = r.take_sealed("03", "仮説", "株式会社テスト", read_clip=lambda: next(clips),
                         clear=lambda: cleared.append(1), poll=0, say=lambda m, **k: said.append(m))
    assert "H1 在庫が多い可能性" in body and "〔p〕" not in body and "0.8" not in body
    assert len(cleared) >= 2                    # 照合 NG のときと、受け取った後（どの終わり方でも空にする）
    assert any("照合 NG" in m for m in said)
    assert not any("在庫" in m for m in said)   # 中身は画面に出さない


def test_3の封は届かなければAIを呼ばずに止める():
    with pytest.raises(SystemExit, match="届かなかった"):
        r.take_sealed("03", "仮説", "株式会社テスト", read_clip=lambda: "", clear=lambda: None,
                      timeout=0.01, poll=0, say=lambda m, **k: None)


def test_seal_の有無は名前だけで見る(tmp_path):
    case = make_case(tmp_path)
    assert r.sealed_present("3", case) == []    # 封のファイルは作っていない（開かずに exists だけ）
    (case / "01i_外形カード_内部用.md").write_text("> 注意\n# 会社外形カード｜事実編｜株式会社テスト【架空】\n", encoding="utf-8")
    assert r.company_of(case) == "株式会社テスト"


def test_3は03が無ければ止める(tmp_path):
    case = make_case(tmp_path)
    with pytest.raises(SystemExit, match="が無い"):
        r.build("3", case, case, str(r.PROMPTS))


def test_3で02bが無ければ案内を無いに置き換える(tmp_path):
    case = make_case(tmp_path)
    place_sealed_name(case, SEALED_03)
    prompt, _ = r.build("3", case, case, str(r.PROMPTS), sealed_texts=[("03", "AIの仮説の本文")])
    assert "この案件に 02b はありません" in prompt
    assert "【封の添付：02b】に載せています" not in prompt


def test_3は03と02bを見出しの語で取り違えない():
    both = "# 【封】仮説と見立て｜株式会社テスト\n本文\n"
    with pytest.raises(SystemExit, match="届かなかった"):
        r.take_sealed("03", "仮説", "株式会社テスト", read_clip=lambda: both, clear=lambda: None,
                      timeout=0.01, poll=0, say=lambda m, **k: None)


def test_3の会社名は完全一致():
    longer = FAKE_03.replace("株式会社テスト", "株式会社テスト製作所")
    with pytest.raises(SystemExit, match="届かなかった"):
        r.take_sealed("03", "仮説", "株式会社テスト", read_clip=lambda: longer, clear=lambda: None,
                      timeout=0.01, poll=0, say=lambda m, **k: None)


def test_雛形に封の見出しがあれば止める(tmp_path):
    t = tmp_path / "old.txt"
    t.write_text("指示\n# 【封】仮説｜株式会社テスト\nH1\n", encoding="utf-8")
    with pytest.raises(SystemExit, match="封の中身らしい見出し"):
        r.instruction(str(t), "## ③")


def test_出力先がgitに上がる場所なら止める(tmp_path):
    with pytest.raises(SystemExit, match="git に上がる場所"):
        r.check_out(r.REPO / "runner" / "out")
    r.check_out(tmp_path)                       # リポジトリの外はよい
    r.check_out(r.REPO / "案件" / "_x")          # 案件/ の下はよい（gitignore）


def test_B1の理由の欄は決まりの語だけ写す(tmp_path):
    import k_runs as k
    b = tmp_path / "B-1.md"
    b.write_text("| §1 | 1 | 一部 | L3 | 工場長が言った生の文 |\n| §1 | 2 | なし | | メモに無い数字 |\n", encoding="utf-8")
    rows = k.b1_rows(b)
    assert rows[0][3] == "（決まりの語でない）"
    assert rows[1][3] == "メモに無い数字"


def test_AIは道具なしで呼ぶ():
    src = (Path(r.__file__)).read_text(encoding="utf-8")
    assert '"--tools", ""' in src and '"--setting-sources", ""' in src
