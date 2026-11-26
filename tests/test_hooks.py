"""段6のフック（.claude/hooks/）の判定を確かめる。

★フックに渡すのは合成の JSON だけ。封も案件も開かない（seal_guard 自体も名前しか見ない）。
★settings.json は書き換えない。登録案（settings案.json）が正しい形か、登録されたら既知の穴が閉じるかだけを見る。
"""
import json
import subprocess
import sys

import pytest
from pathlib import Path

from conftest import REPO

HOOKS = REPO / ".claude" / "hooks"


def guard(tool, cwd=str(REPO), agent_id=None, **inp):
    data = {"tool_name": tool, "tool_input": inp, "cwd": cwd}
    if agent_id:
        data["agent_id"] = agent_id                    # サブエージェントの中から呼ばれたとき
    r = subprocess.run([sys.executable, str(HOOKS / "seal_guard.py")],
                       input=json.dumps(data), capture_output=True, text=True, encoding="utf-8")
    return r.returncode


BLOCK = [
    ("Read", {"file_path": "/x/案件/案件Z/03_仮説_封.md"}),
    ("Read", {"file_path": "02b_主任診断士の見立て_封.md"}),                    # cwd に依存しない
    ("Grep", {"pattern": "課題", "path": "案件"}),
    ("Grep", {"pattern": "課題", "path": "案件/案件Z"}),
    ("Grep", {"pattern": "課題", "path": ".", "glob": "*_封.md"}),
    ("Bash", {"command": "cat 案件/案件Z/03_仮説_封.md"}),
    ("Bash", {"command": "grep -rn 課題 案件/"}),
    ("Bash", {"command": "grep -Rn 課題 案件/案件Z"}),
    ("Bash", {"command": "rg 課題 案件"}),
    ("Bash", {"command": "cat 案件/案件Z/*"}),
    ("Bash", {"command": "head -5 案件/案件Z/0?_*.md"}),
    ("Bash", {"command": "find 案件 -name '*_封*' -exec cat {} \\;"}),
    ("Bash", {"command": "ls 案件/案件Z/*_封.md | xargs cat"}),
]


@pytest.mark.parametrize("tool,inp", BLOCK, ids=[f"{t}:{list(i.values())[-1]}" for t, i in BLOCK])
def test_seal_guard_blocks(tool, inp):
    assert guard(tool, **inp) == 2


def test_seal_guard_treats_cwd_inside_anken_as_anken():
    assert guard("Bash", cwd=str(REPO / "案件" / "案件Z"), command="cat *") == 2
    assert guard("Bash", cwd=str(REPO / "案件" / "案件Z"), command="grep -r 課題 .") == 2


# 止めてはいけないもの（止めすぎると配管の日常作業が止まる＝B-1 と同じ失敗）
ALLOW = [
    ("Read", {"file_path": "/x/案件/案件Z/04_現場分析.md"}),
    ("Read", {"file_path": "/x/案件/案件Z/01i_外形カード_内部用.md"}),
    ("Grep", {"pattern": "x", "path": ".claude/skills"}),
    ("Bash", {"command": "python3 check_genba_mark.py 案件/案件Z/_材料/B_現場/現場メモ.md"}),
    ("Bash", {"command": "python3 check_anken.py 案件/案件Z"}),
    ("Bash", {"command": "ls -la 案件/案件Z/"}),
    ("Bash", {"command": "ls 案件/案件Z/*_封.md"}),                               # 名前を見るだけ
    ("Bash", {"command": "find 案件 -name '*_封*'"}),
    ("Bash", {"command": "python3 -m pytest tests/ -q"}),
    ("Bash", {"command": "git status -s"}),
    ("Bash", {"command": "grep -rn 封 .claude/skills/"}),                          # 案件の外
    ("Bash", {"command": "cd 対外資料/_report_build && ./build.sh ../../案件/案件Z/06_課題仮説レポート.md"}),
    ("Bash", {"command": "pbpaste | python3 .claude/skills/cross-run/scripts/strip_kijun.py"}),  # Stage 4（10-03）
]


@pytest.mark.parametrize("tool,inp", ALLOW, ids=[f"{t}:{list(i.values())[-1]}" for t, i in ALLOW])
def test_seal_guard_allows(tool, inp):
    assert guard(tool, **inp) == 0


# 実走 62-1：②をやり直すと、前の B-1 の判定（08）に合わせて書ける。サブエージェントにだけ閉じる。
# 司令塔（本体）は B-1 の表を 08 に貼り、_プロンプト.md を一字一句使うので止めない。
SUB_ONLY = [
    ("Read", {"file_path": "/x/案件/案件Z/08_質の検証.md"}),
    ("Read", {"file_path": "/x/案件/_TEST_配管検証/_プロンプト.md"}),
    ("Grep", {"pattern": "一部", "path": ".", "glob": "08_質の検証*"}),
    ("Bash", {"command": "cat 案件/案件Z/08_質の検証.md"}),
    ("Bash", {"command": "sed -n 1,40p 案件/_TEST_配管検証/_プロンプト.md"}),
    ("Bash", {"command": "ls 案件/案件Z/08_質の検証.md | xargs cat"}),
    # 同じ型の穴（台帳 §8・09-30）：失敗の条件と、03 の中身を含む前の回の出力
    ("Read", {"file_path": "/x/質の検証.md"}),
    ("Bash", {"command": "cat 質の検証.md"}),
    ("Read", {"file_path": "/x/案件/_使わない/_TEST_配管検証_20260929_v5/05_反証レポート.md"}),
    ("Bash", {"command": "cat 案件/_使わない/_TEST_配管検証_20260929_v5/06_課題仮説レポート.md"}),
    ("Bash", {"command": "cd 案件/_使わない && sed -n 1,20p x/05_反証レポート.md"}),
]


@pytest.mark.parametrize("tool,inp", SUB_ONLY, ids=[f"{t}:{list(i.values())[-1]}" for t, i in SUB_ONLY])
def test_seal_guard_closes_b1_and_prompt_to_subagents_only(tool, inp):
    assert guard(tool, agent_id="a1", **inp) == 2
    assert guard(tool, **inp) == 0


def test_seal_guard_lets_subagents_do_their_work():
    """止めすぎない：②が読む入力・名前を見るだけの ls は、サブエージェントでも通る。"""
    assert guard("Read", agent_id="a1", file_path="/x/案件/案件Z/_材料/B_現場/現場メモ.md") == 0
    assert guard("Read", agent_id="a1", file_path="/x/案件/案件Z/04_現場分析.md") == 0
    assert guard("Bash", agent_id="a1", command="ls -la 案件/案件Z/") == 0
    assert guard("Bash", agent_id="a1", command="ls 案件/案件Z/08_質の検証.md") == 0
    assert guard("Read", agent_id="a1", file_path="/x/案件/案件Z/03_仮説_封.md") == 2   # 封は今までどおり
    assert guard("Grep", agent_id="a1", pattern="一部", path="案件/案件Z/08_質の検証.md") == 2
    assert guard("Bash", agent_id="a1", cwd="/x/案件/_使わない/y", command="head 05_反証レポート.md") == 2
    assert guard("Bash", agent_id="a1", command="ls 案件/_使わない/") == 0          # 名前を見るだけ


# 台帳 §8（09-30）の③：コマンドに「案件」と書かない再帰検索が、リポジトリ直下などから 案件/ の封まで入る。
# 実測：本物の grep（/usr/bin/grep -rl）を直下で打つと 03 に3件当たった。本体もサブエージェントも同じに止める（09-30 本人決定）
ROOT_BLOCK = [
    (str(REPO), "grep -rn 課題 ."),
    (str(REPO), "grep -rn 課題"),                                   # 場所なし＝今いる所
    (str(REPO), "/usr/bin/grep -rl 仮説一覧 ."),
    (str(REPO), "command grep -R 課題 ."),
    (str(REPO), "grep --recursive 課題 ."),
    (str(REPO), "rg 課題"),
    (str(REPO), "grep -rn 課題 ~"),
    (str(REPO / "tests"), "grep -rn 課題 .."),                      # 親に上がる
    (str(REPO), "find . -type f -exec cat {} +"),
    (str(REPO), "find . -name '*.md' | xargs grep 課題"),
]


@pytest.fixture
def anken_here():
    """案件/ がある状態を作る（新しく clone した所には無い。.gitignore 済みなので commit されない）。"""
    d = REPO / "案件"
    made = not d.exists()
    d.mkdir(exist_ok=True)
    yield d
    if made:
        d.rmdir()


@pytest.mark.parametrize("cwd,cmd", ROOT_BLOCK, ids=[c for _, c in ROOT_BLOCK])
def test_seal_guard_blocks_recursive_search_that_reaches_anken(cwd, cmd, anken_here):
    if cmd.endswith(" ~") and Path.home() not in REPO.parents:
        pytest.skip("この clone はホームの下に無いので、~ からの検索は 案件/ に届かない")
    assert guard("Bash", cwd=cwd, command=cmd) == 2
    assert guard("Bash", cwd=cwd, agent_id="a1", command=cmd) == 2


ROOT_ALLOW = [
    (str(REPO), "grep -rn 課題 --exclude-dir=案件 ."),               # 除外していれば通す
    (str(REPO), "grep -rn 課題 --exclude-dir 案件 ."),
    (str(REPO), "rg 課題 -g '!案件'"),
    (str(REPO), "git grep -n 課題"),                                # 追跡ファイルだけ＝案件/ は入らない
    (str(REPO), "grep -rn 課題 tests/ .claude/"),
    (str(REPO), "grep -r -e . tests"),                             # -e の後の「.」は場所ではない
    (str(REPO / "tests"), "grep -rn 課題 ."),                       # 案件/ を含まない所
    (str(REPO), "grep -n 課題 STATUS.md"),                          # 再帰でない
    (str(REPO), "find . -name '*.md'"),                            # 名前を見るだけ
    (str(REPO), "find . -name '*.md' | wc -l"),                    # 名前を数えるだけ
]


@pytest.mark.parametrize("cwd,cmd", ROOT_ALLOW, ids=[c for _, c in ROOT_ALLOW])
def test_seal_guard_allows_search_that_skips_anken(cwd, cmd):
    assert guard("Bash", cwd=cwd, command=cmd) == 0


def test_seal_guard_does_not_block_on_broken_input():
    r = subprocess.run([sys.executable, str(HOOKS / "seal_guard.py")], input="壊れた", capture_output=True, text=True)
    assert r.returncode == 0


# ── notice.py：本人にだけ見せ、何も止めない ─────────────────────


def notice(kind, payload):
    r = subprocess.run([sys.executable, str(HOOKS / "notice.py"), kind],
                       input=json.dumps(payload), capture_output=True, text=True)
    return r.returncode, r.stdout


def test_notice_report_shows_ng_to_user_only(tmp_path):
    p = tmp_path / "06_課題仮説レポート.md"
    p.write_text("# 表題\n\n本文に棄却が残った。\n", encoding="utf-8")
    code, out = notice("report", {"tool_input": {"file_path": str(p)}})
    assert code == 0
    msg = json.loads(out)
    assert set(msg) == {"systemMessage"}            # ★エージェントへ返す欄（additionalContext・decision）を使わない
    assert "NG" in msg["systemMessage"]


def test_notice_report_ignores_other_files(tmp_path):
    p = tmp_path / "04_現場分析.md"
    p.write_text("x", encoding="utf-8")
    assert notice("report", {"tool_input": {"file_path": str(p)}}) == (0, "")


SECRET = "架空の秘密の製品名"   # 本文の語。通知に出てはいけない

CARD_01 = f"""# 外形カード

## 1. 確認させてください

| 項目 | 公開情報ではこうなっています | どこに | 種類 | いつ |
|---|---|---|---|---|
| 法人番号 | 不明（未特定） | — | — | — |

## 2. 御社が発信されていること

| 項目 | 値 | どこに | 種類 | いつ |
|---|---|---|---|---|
| 主力 | {SECRET} | gBizINFO | 貴社の発信 | 2026-01 |
| 設備 | おそらく新しい | | 貴社の発信 | 2026-01 |

## 4. 公開情報では分からなかったこと

- 架空

---
---

社内メモ
"""

CARD_01I = """# 01i

## §1. 同定（A）

| 項目 | 内容 | 出典 | 性質 | 時点 |
|---|---|---|---|---|
| 法人番号 | 1234567890123 | 法人番号公表サイト | 公的DBの登録 | 2026 |
"""


def _card_case(tmp_path, name, text, log=True):
    d = tmp_path / "案件Z"
    (d / "_材料" / "A_公開").mkdir(parents=True)
    if log:
        (d / "_材料" / "A_公開" / "取得ログ_2026-01-01.md").write_text("x", encoding="utf-8")
    p = d / name
    p.write_text(text, encoding="utf-8")
    return p


def test_notice_card_01_shows_rule_names_to_user_only(tmp_path):
    """①の出力を保存したら①の検査を知らせる（台帳 §8・09-28 の配線の穴）。本人にだけ・本文を出さない。"""
    p = _card_case(tmp_path, "01_外形カード_事実編.md", CARD_01, log=False)
    code, out = notice("report", {"tool_input": {"file_path": str(p)}})
    assert code == 0
    msg = json.loads(out)
    assert set(msg) == {"systemMessage"}
    m = msg["systemMessage"]
    for rule in ("R15", "R18-01", "R19-01", "S267-01", "S269-01", "lint_01 NG"):
        assert rule in m, rule
    assert SECRET not in m


def test_notice_card_01i_clean_says_zero(tmp_path):
    p = _card_case(tmp_path, "01i_外形カード_内部用.md", CARD_01I)
    code, out = notice("report", {"tool_input": {"file_path": str(p)}})
    assert code == 0
    assert "違反 0 件" in json.loads(out)["systemMessage"]


def test_notice_card_ignores_other_files_in_case(tmp_path):
    p = _card_case(tmp_path, "02_現場で確認すべき問い.md", "x")
    assert notice("report", {"tool_input": {"file_path": str(p)}}) == (0, "")


def test_notice_never_blocks_on_error():
    code, out = notice("anken", "壊れた")
    assert code == 0


# ── 登録案 ─────────────────────────────────────────


def test_settings_proposal_points_to_existing_scripts():
    s = json.loads((HOOKS / "settings案.json").read_text(encoding="utf-8"))
    cmds = [h["command"] for ev in s["hooks"].values() for m in ev for h in m["hooks"]]
    assert cmds
    for c in cmds:
        script = c.split("/.claude/hooks/")[1].split()[0].strip('"')
        assert (HOOKS / script).exists(), script
    pre = s["hooks"]["PreToolUse"][0]["matcher"]
    assert all(t in pre for t in ("Bash", "Grep", "Read"))


# Windows：パスの区切りが \ で、フックへの入力は UTF-8 のまま届く。どちらでも封を止める（公開版で追加）
WIN_BLOCK = [
    ("Read", {"file_path": "C:\\Users\\u\\kit\\案件\\案件Z\\03_仮説_封.md"}),
    ("Grep", {"path": "C:\\Users\\u\\kit\\案件\\案件Z", "pattern": "課題"}),
    ("Read", {"file_path": "C:/Users/u/kit/案件/案件Z/02b_主任診断士の見立て_封.md"}),
]


@pytest.mark.parametrize("tool,inp", WIN_BLOCK, ids=[str(i) for _, i in WIN_BLOCK])
def test_seal_guard_blocks_windows_paths(tool, inp):
    assert guard(tool, **inp) == 2


def test_seal_guard_reads_raw_utf8_input():
    """Claude Code は日本語をエスケープせずに渡すことがある。端末の文字コードに依らず読めて、止める。"""
    data = {"tool_name": "Read", "tool_input": {"file_path": "/x/案件/案件Z/03_仮説_封.md"}, "cwd": str(REPO)}
    r = subprocess.run([sys.executable, str(HOOKS / "seal_guard.py")],
                       input=json.dumps(data, ensure_ascii=False).encode("utf-8"), capture_output=True)
    assert r.returncode == 2
    assert "seal_guard" in r.stderr.decode("utf-8")
