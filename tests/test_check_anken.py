"""check_anken.py の挙動を固定する（段3。スクリプトは変えない）。

★合成の案件フォルダだけを使う。封ファイルは「在る」ことだけを作り、中身は空（開かない）。
★--repo（フックの配線・写し）は一時リポジトリにスクリプトを写して確かめる。
"""
import os
import shutil
import subprocess
import sys

import pytest

from conftest import REPO, SCRIPTS, load_script, run_script

CA = load_script("check_anken")
ALL_READS = sorted({r for need in CA.READERS.values() for r in need})


def make_anken(root, files=ALL_READS):
    """合成の案件フォルダを作る。封の名前のファイルは空で置くだけ（中身は無い）。"""
    a = root / "案件" / "案件Z"
    for rel in files:
        p = a / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        if "_封" in p.name:
            # ★封の名前は seal_guard が開かせないので、別プロセスの touch で空ファイルを置く
            subprocess.run(["touch", str(p)], check=True)
        else:
            p.write_text("合成\n", encoding="utf-8")
    return a


@pytest.fixture
def check(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)   # 禁止語彙のメッセージは cwd の 案件/ から見た相対パス
    def _run(anken):
        return CA.check(str(anken.relative_to(tmp_path)))
    return _run


def test_complete_anken_has_no_findings(tmp_path, check):
    errs, warns, notes = check(make_anken(tmp_path))
    assert (errs, warns, notes) == ([], [], [])


def test_duplicate_number_is_ng(tmp_path, check):
    a = make_anken(tmp_path)
    (a / "04_現場分析_v2.md").write_text("x", encoding="utf-8")
    errs, _, _ = check(a)
    assert any("番号 04" in e for e in errs)


@pytest.mark.parametrize("prefix", ["_保留_", "_なんとか_", "_旧_", "_a__b_"])
def test_duplicate_detected_through_any_prefix(prefix):
    """接頭辞の一覧に頼らない（#24）。"""
    assert CA.strip_num(f"{prefix}04_現場分析.md") == "04"


@pytest.mark.parametrize("prefix", ["_a_b_", "_なんとか_別_", "_旧_保留_x_"])
def test_chained_prefix(prefix):
    """以前の既知の穴 Z7：_ を共有して連なる接頭辞を剥がせなかった（09-29 に直した）。"""
    assert CA.strip_num(f"{prefix}04_現場分析.md") == "04"


def test_chained_prefix_duplicate_is_ng(tmp_path, check):
    a = make_anken(tmp_path)
    (a / "_材料" / "_a_b_04_現場分析.md").write_text("x", encoding="utf-8")
    errs, _, _ = check(a)
    assert any("番号 04" in e for e in errs)


@pytest.mark.parametrize("name,num", [
    ("01i_外形カード_内部用.md", "01i"), ("02b_主任診断士の見立て_封.md", "02b"),
    ("現場メモ.md", None), ("_材料", None)])
def test_strip_num(name, num):
    assert CA.strip_num(name) == num


@pytest.mark.parametrize("name", ["_旧_メモ.md", "_保留_x.md", "_保管", "_前回_x.md", "x.md.bak"])
def test_banned_vocabulary_is_ng(tmp_path, check, name):
    a = make_anken(tmp_path)
    target = a / "_材料" / name
    if name.endswith((".md", ".bak")):
        target.write_text("x", encoding="utf-8")
    else:
        target.mkdir()
    errs, _, _ = check(a)
    assert any("禁止語彙" in e for e in errs)


def test_quarantine_folder_inside_anken_is_ng(tmp_path, check):
    a = make_anken(tmp_path)
    (a / "_ゴミ").mkdir()
    errs, _, _ = check(a)
    assert any("`_ゴミ/`" in e for e in errs)


def test_materials_folder_is_allowed(tmp_path, check):
    errs, _, _ = check(make_anken(tmp_path))
    assert not errs


def test_two_pdfs_is_ng_one_is_ok(tmp_path, check):
    a = make_anken(tmp_path)
    (a / "a.pdf").write_bytes(b"%PDF")
    assert not check(a)[0]
    (a / "b.PDF").write_bytes(b"%PDF")
    assert any("PDF が 2 個" in e for e in check(a)[0])


@pytest.mark.parametrize("stage", list(CA.READERS))
def test_missing_reader_file_is_warn(tmp_path, check, stage):
    need = CA.READERS[stage]
    target = next(r for r in need if r not in CA.FALLBACK)
    a = make_anken(tmp_path, [r for r in ALL_READS if r != target])
    errs, warns, _ = check(a)
    assert not errs and any(target in w for w in warns)


def test_01i_falls_back_to_01_with_note(tmp_path, check):
    files = [r for r in ALL_READS if r != "01i_外形カード_内部用.md"] + ["01_外形カード_事実編.md"]
    errs, warns, notes = check(make_anken(tmp_path, files))
    assert not errs and not warns
    assert notes and all("代用" in n for n in notes)


def test_contamination_record_is_noted(tmp_path, check):
    """CHECK #2：`_汚染記録.md` がある案件は NOTE で知らせる（NG ではない。配管の検証には使える）。"""
    a = make_anken(tmp_path)
    (a / "_汚染記録.md").write_text("合成\n", encoding="utf-8")
    errs, warns, notes = check(a)
    assert not errs and not warns
    assert any("_汚染記録.md" in n for n in notes)


def test_cli_single_target_exit_code(tmp_path):
    a = make_anken(tmp_path)
    (a / "_ゴミ").mkdir()
    code, ng, _ = run_script("check_anken", "案件/案件Z", cwd=tmp_path)
    assert code == 1 and any("_ゴミ" in l for l in ng)


def test_cli_also_runs_the_card_checks(tmp_path):
    """①の出力の形（tests/card_checks.py）は、保存時のフック（notice.py）だけでなく、段の前に流すこのコマンドでも止める。
    2026-11-26：Claude Code を別のフォルダで開いていてフックが動かず、R18・R19・S267 が②まで素通りした。"""
    a = make_anken(tmp_path)            # 構造は完全。01i の中身は「合成」1行だけ＝形が足りない
    assert CA.check(str(a)) == ([], [], [])                # 構造の検査（check）は何も言わない
    code, ng, _ = run_script("check_anken", "案件/案件Z", cwd=tmp_path)
    assert code == 1 and any("①の出力の形" in l for l in ng)


# ── --repo（フックの配線・写し／#43）──────────────────────


@pytest.mark.skipif(subprocess.run(["git", "-C", str(REPO), "config", "--get", "core.hooksPath"],
                                   capture_output=True, text=True).stdout.strip() != ".githooks",
                    reason="この clone ではまだ git config core.hooksPath .githooks をしていない")
def test_repo_check_passes_on_this_repo():
    code, ng, _ = run_script("check_anken", "--repo")
    assert code == 0, ng


@pytest.fixture
def fake_repo(tmp_path):
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    shutil.copy(SCRIPTS["check_anken"], tmp_path / "check_anken.py")
    hooks = tmp_path / ".githooks"
    hooks.mkdir()
    (hooks / "pre-commit").write_text("#!/bin/sh\n", encoding="utf-8")
    os.chmod(hooks / "pre-commit", 0o755)
    subprocess.run(["git", "-C", str(tmp_path), "config", "core.hooksPath", ".githooks"], check=True)
    return tmp_path


def _repo(root):
    r = subprocess.run([sys.executable, str(root / "check_anken.py"), "--repo"],
                       capture_output=True, text=True, cwd=root)
    return r.returncode, r.stdout


def test_fake_repo_ok(fake_repo):
    assert _repo(fake_repo)[0] == 0


def test_ng_when_hooks_path_not_set(fake_repo):
    subprocess.run(["git", "-C", str(fake_repo), "config", "--unset", "core.hooksPath"], check=True)
    code, out = _repo(fake_repo)
    assert code == 1 and "配線" in out


@pytest.mark.skipif(sys.platform.startswith("win"), reason="Windows には実行権限が無い（git もフックの実行権限を見ない）")
def test_ng_when_hook_not_executable(fake_repo):
    os.chmod(fake_repo / ".githooks" / "pre-commit", 0o644)
    code, out = _repo(fake_repo)
    assert code == 1 and "実行できない" in out


@pytest.mark.parametrize("copy", [".agents", "AGENTS.md", ".Codex", ".codex",
                                  ".github/copilot-instructions.md"])
def test_ng_when_copy_for_other_tool_exists(fake_repo, copy):
    p = fake_repo / copy
    p.parent.mkdir(parents=True, exist_ok=True)
    if "." in p.name.lstrip("."):
        p.write_text("x", encoding="utf-8")
    else:
        p.mkdir()
    code, out = _repo(fake_repo)
    assert code == 1 and "写し" in out
