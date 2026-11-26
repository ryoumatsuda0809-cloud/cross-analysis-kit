"""仕分け表（tests/仕分け表.md）と CHECK.md の突き合わせ。段9・移行台帳 §10。

★分母を黙って変えさせない：CHECK.md の項目と表の行が1対1でなければ落ちる。
★「済」と書いたテストが実在しなければ落ちる。
★達成率（済 ÷ M）が FLOOR を下回ったら落ちる。FLOOR は上げるだけ（下げるなら理由を台帳 §8 へ）。

  python3 tests/test_rtm.py     # 達成率と、未・一部の一覧を出す
"""
import ast
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CHECK = REPO / "CHECK.md"
TABLE = REPO / "tests" / "仕分け表.md"
TABLE_SKILL = REPO / "tests" / "仕分け表_SKILL.md"

FLOOR = 0.93   # 58/62（09-28 B8 拡張で #77 を済に）。上げるだけ
FLOOR_SKILL = 0.97   # 146/150（09-29 #403a を一部に・#62〔Z7〕を済に → 台帳 §8）。上げるだけ

MARK = re.compile(r"[*`★]")


def check_items():
    """[(章, 照合用の本文, 🤖 があるか)]。"""
    out, sec = [], None
    for line in CHECK.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^## (\d+b?)\.", line)
        if m:
            sec = m.group(1)
        m = re.match(r"^\s*- \[ \] (.*)", line)
        if m:
            out.append((sec, MARK.sub("", m.group(1)).strip(), "🤖" in line))
    return out


def rows(table=TABLE):
    """仕分け表の行。[{id, num, sub, sec, cls, st, tests, anchor, memo}]（SKILL 版では sec＝スキル名）。
    id は表の # そのまま（`12`・`12a`）。num はその数字、sub は分割の字（無ければ空）。"""
    out = []
    for line in table.read_text(encoding="utf-8").splitlines():
        if not re.match(r"^\| \d+[a-z]? \|", line):
            continue
        cells = [c.strip() for c in re.split(r"(?<!\\)\|", line)[1:-1]]
        num, sec, cls, st, tests, anchor, memo = cells
        base, sub = re.fullmatch(r"(\d+)([a-z]?)", num).groups()
        out.append(dict(id=num, num=int(base), sub=sub, sec=sec, cls=cls, st=st,
                        tests=re.findall(r"`([^`]+)`", tests),
                        anchor=anchor.replace("\\|", "|"), memo=memo))
    return out


def defined_tests():
    names = set()
    for p in (REPO / "tests").glob("test_*.py"):
        for node in ast.walk(ast.parse(p.read_text(encoding="utf-8"))):
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                names.add(f"{p.name}::{node.name}")
    return names


def coverage(rs):
    m = [r for r in rs if r["cls"] == "M"]
    done = [r for r in m if r["st"] == "済"]
    return len(done), len(m)


# ── テスト ─────────────────────────────────────────────


def test_every_check_item_has_exactly_one_row():
    items, rs = check_items(), rows()
    assert not [r["id"] for r in rs if r["sub"]], "CHECK.md 版は分割しない（1項目＝1行）"
    assert [r["num"] for r in rs] == list(range(1, len(rs) + 1)), "# が 1 から連番になっていない"
    assert len(rs) == len(items), f"CHECK.md の項目 {len(items)} 件 ／ 表 {len(rs)} 行。足した項目を表にも足す"
    for r, (sec, text, _) in zip(rs, items):
        assert r["sec"] == sec and text.startswith(r["anchor"]), \
            f"#{r['num']}：表の照合「{r['anchor']}」（§{r['sec']}）が CHECK.md の {r['num']} 番目（§{sec}）と合わない"
        same = [t for s, t, _ in items if s == sec and t.startswith(r["anchor"])]
        assert len(same) == 1, f"#{r['num']}：照合「{r['anchor']}」が §{sec} で {len(same)} 件に当たる"


def test_class_and_state_are_valid():
    for r in rows():
        assert r["cls"] in {"M", "G", "H", "N"}, f"#{r['num']}：分類 {r['cls']}"
        if r["cls"] == "M":
            assert r["st"] in {"済", "一部", "未"}, f"#{r['num']}：M なのに状態が {r['st']!r}"
            assert (r["st"] == "未") == (not r["tests"]), f"#{r['num']}：状態 {r['st']} と検査欄が合わない"
        else:
            assert not r["st"] and not r["tests"], f"#{r['num']}：{r['cls']} に状態・検査がある（M だけ）"


def test_listed_tests_exist():
    names = defined_tests()
    for r in rows():
        for t in r["tests"]:
            assert t in names, f"#{r['num']}：{t} というテストが無い"


def test_robot_mark_matches_table():
    for r, (_, _, robot) in zip(rows(), check_items()):
        if robot:
            assert r["tests"], f"#{r['num']}：CHECK.md に 🤖 があるのに表に検査が無い"
        if r["tests"]:
            assert robot, f"#{r['num']}：表に検査があるのに CHECK.md に 🤖 が無い（人が手で見続ける）"


def test_coverage_does_not_fall():
    done, total = coverage(rows())
    assert done / total >= FLOOR, f"達成率 {done}/{total} = {done/total:.0%} が下限 {FLOOR:.0%} を下回った"


# ── SKILL.md 版（分母は skill_units.py が決める）────────────────
#
# 数え方（09-27 本人決定・移行台帳 §10）：
#   ・1単位に規則が2つ以上あれば `12a`・`12b`…に分ける（a から連続・2行以上）。
#     先頭の行の照合は本文の頭、2行目以降の照合は本文のどこかに在ること
#   ・理由・例・背景は N、ほかの行の繰り返しは R。R はメモ欄に「参照：原本 #n」（n は M・G・H の行）
#   ・N・R・? は分母に入らない（coverage は M だけを数える）

REF = re.compile(r"参照：原本 #(\d+[a-z]?)")


def skill_table_errors(rs, us, names):
    """表 rs と単位 us（[(スキル, 行, 種類, 本文)]）の食い違い。names は実在するテスト名。"""
    errs, groups = [], {}
    for r in rs:
        groups.setdefault(r["num"], []).append(r)
    if list(groups) != list(range(1, len(us) + 1)):
        errs.append(f"# の数字が 1〜{len(us)} の順に並んでいない（SKILL.md の単位 {len(us)} 件）")
    for n, g in groups.items():
        subs = [r["sub"] for r in g]
        if subs != [""] and subs != [chr(ord("a") + i) for i in range(len(g))] or subs == ["a"]:
            errs.append(f"#{n}：分割は a から連続で2行以上（今は {[r['id'] for r in g]}）")
        if not 1 <= n <= len(us):
            continue
        skill, line, _, text = us[n - 1]
        for i, r in enumerate(g):
            hit = text.startswith(r["anchor"]) if i == 0 else (r["anchor"] and r["anchor"] in text)
            if r["sec"] != skill or not hit:
                errs.append(f"#{r['id']}：表（{r['sec']}「{r['anchor']}」）と {skill}/SKILL.md:{line} が合わない")
    by_id = {r["id"]: r for r in rs}
    for r in rs:
        if r["cls"] not in {"M", "G", "H", "N", "R", "?"}:
            errs.append(f"#{r['id']}：分類 {r['cls']}")
        if r["cls"] == "M":
            if r["st"] not in {"済", "一部", "未"}:
                errs.append(f"#{r['id']}：M なのに状態が {r['st']!r}")
            elif (r["st"] == "未") != (not r["tests"]):
                errs.append(f"#{r['id']}：状態 {r['st']} と検査欄が合わない")
        elif r["st"] or r["tests"]:
            errs.append(f"#{r['id']}：{r['cls']} に状態・検査がある（M だけ）")
        if r["cls"] == "R":
            m = REF.search(r["memo"])
            to = by_id.get(m.group(1)) if m else None
            if not m:
                errs.append(f"#{r['id']}：R なのにメモに「参照：原本 #n」が無い")
            elif to is None or to is r or to["cls"] not in {"M", "G", "H"}:
                errs.append(f"#{r['id']}：参照先 #{m.group(1)} が M・G・H の別の行ではない")
        errs += [f"#{r['id']}：{t} というテストが無い" for t in r["tests"] if t not in names]
    return errs


def test_skill_table_matches_units():
    from skill_units import all_units
    errs = skill_table_errors(rows(TABLE_SKILL), all_units(), defined_tests())
    assert not errs, "\n".join(errs[:20])


def test_skill_coverage_does_not_fall():
    done, total = coverage(rows(TABLE_SKILL))
    assert done / total >= FLOOR_SKILL, f"SKILL.md の達成率 {done}/{total} = {done/total:.0%} が下限 {FLOOR_SKILL:.0%} を下回った"


# ── 判定そのものの確認（合成の表。実物の表は使わない）──────────────


US = [("s", 1, "list", "Aし、Bする"), ("s", 2, "list", "Cしない"), ("s", 3, "text", "Aし、と前に書いたとおり")]


def row(num, cls="G", st="", tests=(), anchor="", memo="list"):
    base, sub = re.fullmatch(r"(\d+)([a-z]?)", num).groups()
    return dict(id=num, num=int(base), sub=sub, sec="s", cls=cls, st=st,
                tests=list(tests), anchor=anchor, memo=memo)


def test_split_and_reference_pass():
    rs = [row("1a", "M", "未", anchor="Aし"), row("1b", "G", anchor="Bする"),
          row("2", "N", anchor="Cしない"), row("3", "R", anchor="Aし、と", memo="text／参照：原本 #1a")]
    assert skill_table_errors(rs, US, set()) == []


def test_split_and_reference_catch_mistakes():
    def errs(rs):
        return skill_table_errors(rs, US, set())
    ok2, ok3 = row("2", anchor="Cしない"), row("3", anchor="Aし、と")
    assert errs([row("1a", anchor="Aし"), ok2, ok3]), "分割が1つだけ（1b が無い）"
    assert errs([row("1a", anchor="Aし"), row("1c", anchor="Bする"), ok2, ok3]), "a の次が c"
    assert errs([row("1a", anchor="Aし"), row("1b", anchor="Xする"), ok2, ok3]), "分割の照合が本文に無い"
    assert errs([row("1", anchor="Bする"), ok2, ok3]), "照合が本文の頭と合わない"
    assert errs([row("1", anchor="Aし"), ok2, row("3", "R", anchor="Aし、と", memo="text")]), "R に参照が無い"
    assert errs([row("1", anchor="Aし"), ok2, row("3", "R", anchor="Aし、と", memo="参照：原本 #9")]), "参照先が無い"
    assert errs([row("1", "N", anchor="Aし"), ok2, row("3", "R", anchor="Aし、と", memo="参照：原本 #1")]), "参照先が N"
    assert errs([row("1", anchor="Aし"), ok2, row("3", "R", anchor="Aし、と", memo="参照：原本 #3")]), "自分を参照"
    assert errs([row("1", "R", "済", ["x"], anchor="Aし", memo="参照：原本 #2"), ok2, ok3]), "R に状態・検査"
    assert coverage([row("1a", "M", "済", ["t"]), row("1b", "M", "未"), row("2", "R"), row("3", "N")]) == (1, 2)


if __name__ == "__main__":
    rs = rows()
    done, total = coverage(rs)
    print(f"達成率 {done}/{total} = {done/total:.0%}（目標 90% ＝ {-(-total * 9 // 10)} 件）")
    for st in ("未", "一部"):
        for r in rs:
            if r["cls"] == "M" and r["st"] == st:
                print(f"  {st:2} #{r['num']:>3} §{r['sec']:<3} {r['memo']}")
    sk = rows(TABLE_SKILL)
    left = sum(r["cls"] == "?" for r in sk)
    done, total = coverage(sk)
    kinds = {c: sum(r["cls"] == c for r in sk) for c in "MGHNR"}
    print(f"SKILL.md：{len(sk)} 行（単位 {len({r['num'] for r in sk})}）のうち未仕分け {left} 件"
          f"／{kinds}／M {total} 件のうち済 {done} 件")
