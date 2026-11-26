"""lint_01.py の挙動を固定する（段3。スクリプトは変えない）。

★合成データだけを使う。実在の 01 と禁止語リストは読まない（--leak は一時リポジトリで確かめる）。
"""
import subprocess

import pytest

from conftest import REPO, load_script, run_script

L = load_script("lint_01")

CLEAN = """# 外形カード

## 1. 基本情報

| 項目 | 内容 | どこに | 種類 | いつ |
|---|---|---|---|---|
| 所在地 | 市内 | 公式サイト | 自社発信 | 2026-09 |

## 2. 御社が発信されていること

| 項目 | 内容 | どこに | 種類 | いつ |
|---|---|---|---|---|
| 方針 | 地域に根ざす | 公式サイト | 自社発信 | 2026-09 |
| 採用 | 若手を募集 | 求人票 | 自社発信 | 2026-08 |

## 3. 市場

短い。

## 4. 公開情報では分からなかったこと

| 項目 | 理由 |
|---|---|
| 従業員数 | 公式サイトに記載なし |
| 売上 | 非公開 |

---
---

社内メモ：ここから下は切り離す。仮説・封・genba-ops は書いてよい。
"""


@pytest.fixture
def lint(tmp_path):
    def _run(text):
        p = tmp_path / "01_外形カード_事実編.md"
        p.write_text(text, encoding="utf-8")
        return run_script("lint_01", p)
    return _run


def test_clean_card_passes(lint):
    code, ng, out = lint(CLEAN)
    assert code == 0 and not ng, ng
    assert "OK   問題なし" in out


def test_below_split_line_is_not_checked(lint):
    """切り離し線より下の社内メモは内部語を含んでよい。"""
    assert lint(CLEAN)[0] == 0


def _inject(word):
    return CLEAN.replace("地域に根ざす", f"地域に根ざす{word}")


@pytest.mark.parametrize("word", L.BANNED_PREDICATES)
def test_ng_on_each_judgement_word(lint, word):
    code, ng, _ = lint(_inject(word))
    assert code == 1 and any(f"「{word}」" in l for l in ng)


@pytest.mark.parametrize("word", L.BANNED_WORDS + L.INTERNAL_ONLY)
def test_ng_on_each_internal_word(lint, word):
    code, ng, _ = lint(_inject(word))
    assert code == 1 and any(f"「{word}」" in l for l in ng)


def test_ng_on_code_name(lint):
    code, ng, _ = lint(_inject("（案件D）"))
    assert code == 1 and any("コード名" in l for l in ng)


@pytest.mark.parametrize("header", ["どこに", "種類", "いつ"])
def test_ng_when_three_column_header_missing(lint, header):
    code, ng, _ = lint(CLEAN.replace(header, "出典"))
    assert code == 1 and any(f"「{header}」" in l for l in ng)


def test_warn_only_when_no_split_line(lint):
    text = CLEAN.split("---\n---")[0]
    code, ng, out = lint(text)
    assert code == 0 and "切り離し線" in out


def test_warn_when_section4_nearly_empty(lint):
    text = CLEAN.replace("| 従業員数 | 公式サイトに記載なし |\n| 売上 | 非公開 |\n", "")
    code, _, out = lint(text)
    assert code == 0 and "§4" in out


def test_no_args_exits_2():
    assert run_script("lint_01")[0] == 2


# ── --leak（push 対象への社名漏れ）。一時リポジトリで確かめる ─────────


def _git(root, *a):
    subprocess.run(["git", "-C", str(root), *a], check=True, capture_output=True)


@pytest.fixture
def leak_repo(tmp_path):
    _git(tmp_path, "init", "-q")
    (tmp_path / "案件").mkdir()
    (tmp_path / "案件" / "_禁止語_ローカル専用.txt").write_text("架空工業\n", encoding="utf-8")
    (tmp_path / "README.md").write_text("中身\n", encoding="utf-8")
    _git(tmp_path, "add", "README.md")
    return tmp_path


def test_leak_ok_when_clean(leak_repo):
    assert run_script("lint_01", "--leak", leak_repo)[0] == 0


def test_leak_ng_on_tracked_file(leak_repo):
    (leak_repo / "README.md").write_text("架空工業 の話\n", encoding="utf-8")
    code, ng, _ = run_script("lint_01", "--leak", leak_repo)
    assert code == 1 and any("README.md" in l for l in ng)


def test_leak_ignores_untracked_file(leak_repo):
    (leak_repo / "メモ.md").write_text("架空工業\n", encoding="utf-8")
    assert run_script("lint_01", "--leak", leak_repo)[0] == 0


def test_leak_ng_when_word_list_missing(leak_repo):
    (leak_repo / "案件" / "_禁止語_ローカル専用.txt").unlink()
    code, ng, _ = run_script("lint_01", "--leak", leak_repo)
    assert code == 1 and any("禁止語リストが無い" in l for l in ng)


def test_leak_checks_japanese_named_file_on_fresh_clone(leak_repo):
    """Z9（09-26 修正済み）：quotepath=on でも日本語名の追跡ファイルの中身を検査する。"""
    _git(leak_repo, "config", "core.quotepath", "true")
    f = leak_repo / "実走ログ.md"
    f.write_text("架空工業\n", encoding="utf-8")
    _git(leak_repo, "add", "実走ログ.md")
    code, ng, _ = run_script("lint_01", "--leak", leak_repo)
    assert code == 1 and any("実走ログ.md" in l for l in ng)


# ── #256（market-recon）：テンプレ本体に作業説明を書かない（09-28） ──

TEMPLATE_01 = REPO / ".claude" / "skills" / "market-recon" / "assets" / "01-facts-template.md"
# SKILL.md「テンプレに載せない」の表：「定規である」という説明・行の3分類・文末のルール・自己チェック・判定の考え方
WORK_NOTES = ["定規", "3分類", "三分類", "文末", "自己チェック", "判定"]


def _front(src):
    m = L.SPLIT.search(src)
    return src[:m.start()] if m else src


def work_note_hits(src):
    """切り離し線から上にある作業説明の語と内部メモ。返り値は語の一覧（本文は返さない）。"""
    front = _front(src)
    words = WORK_NOTES + L.BANNED_WORDS + L.INTERNAL_ONLY
    return sorted({w for w in words if w in front} | ({"<!--"} if "<!--" in front else set()))


def test_template_01_has_no_work_notes_above_split():
    src = TEMPLATE_01.read_text(encoding="utf-8")
    assert L.SPLIT.search(src), "01 テンプレに切り離し線が無い"
    assert work_note_hits(src) == []
    code, ng, _ = run_script("lint_01", TEMPLATE_01)
    assert code == 0 and not ng, ng


@pytest.mark.parametrize("note", ["> 文末は4つだけ", "<!-- 書き方：出典を付ける -->", "> この表は定規である", "- [ ] 自己チェック"])
def test_work_note_above_split_is_caught(note):
    assert work_note_hits(CLEAN.replace("## 3. 市場", note + "\n\n## 3. 市場")) != []


def test_work_note_below_split_is_allowed():
    assert work_note_hits(CLEAN + "\n<!-- 文末のルール・自己チェック・判定 -->\n") == []
