"""封の保全テスト（CLAUDE.md §1-1・§3／条件②「独立に取る」）。

確かめること
  A｜.claude/settings.json の deny が封を実際に塞いでいるか（パターンを実パスに当てる）
  B｜check_seal.py が「封が外れた設定」を本当に NG にするか（本体は書き換えず、読む先だけ差し替える）
  C｜既知の穴（xfail）。直ったら XPASS で落ちるので、そのとき xfail を外す

★封の中身は読まない。案件/ はファイル名を列挙するだけ（conftest の seal_guard が保証）。
★settings.json を書き換えない。編集は本人だけ（check_seal.py の docstring・実走ログ 19-1）。
"""
import importlib
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

from conftest import REPO, SealOpenError

SETTINGS = REPO / ".claude" / "settings.json"
LOCAL_SETTINGS = REPO / ".claude" / "settings.local.json"

# 封の実在する名前の型（CLAUDE.md §3 パイプライン）
SEAL_SAMPLES = [
    "案件/案件X/03_仮説_封.md",
    "案件/案件X/02b_主任診断士の見立て_封.md",
    "案件/_使わない/案件X_20260101_理由/02b_主任診断士の見立て_封.md",
    "案件/_TEST_配管検証/03_仮説_封.md",
]
# ②が読む必要があるもの。塞いだら配管が止まる
OPEN_SAMPLES = [
    "案件/案件X/01i_外形カード_内部用.md",
    "案件/案件X/01_外形カード_事実編.md",
    "案件/案件X/02_現場で確認すべき問い.md",
    "案件/案件X/04_現場分析.md",
    "案件/案件X/_材料/B_現場/現場メモ.md",
]


# ── 道具 ──────────────────────────────────────────────


def load_settings(path: Path = SETTINGS) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


RULE_RE = re.compile(r"^(?P<tool>\w+)\((?P<spec>.*)\)$")


def parse_rule(rule: str):
    m = RULE_RE.match(rule)
    return (m["tool"], m["spec"]) if m else (rule, None)


def glob_to_regex(pattern: str) -> re.Pattern:
    """gitignore 風：`**/` は0個以上のディレクトリ、`*` は / をまたがない。"""
    p = pattern[2:] if pattern.startswith("./") else pattern
    out, i = "", 0
    while i < len(p):
        if p.startswith("**/", i):
            out += r"(?:.*/)?"
            i += 3
        elif p.startswith("**", i):
            out += r".*"
            i += 2
        elif p[i] == "*":
            out += r"[^/]*"
            i += 1
        elif p[i] == "?":
            out += r"[^/]"
            i += 1
        else:
            out += re.escape(p[i])
            i += 1
    return re.compile(rf"^{out}$")


def read_deny_specs(settings: dict):
    specs = []
    for rule in settings.get("permissions", {}).get("deny", []):
        tool, spec = parse_rule(rule)
        if tool == "Read" and spec:
            specs.append(spec)
    return specs


def denied(relpath: str, specs) -> bool:
    return any(glob_to_regex(s).match(relpath) for s in specs)


@pytest.fixture
def check_seal(monkeypatch, tmp_path):
    """check_seal.py を改変せずに読み込み、読む settings.json だけ一時ファイルへ差し替える。"""
    mod = importlib.import_module("check_seal")

    def point_to(data):
        f = tmp_path / "settings.json"
        f.write_text(data if isinstance(data, str) else json.dumps(data, ensure_ascii=False),
                     encoding="utf-8")
        monkeypatch.setattr(mod, "SETTINGS", f)
        return mod

    point_to.module = mod
    return point_to


# ── 0｜ガード自体が効いているか ─────────────────────────


def test_guard_blocks_opening_seal_named_file(tmp_path):
    with pytest.raises(SealOpenError):
        open(tmp_path / "ダミー_封.md", "w")
    with pytest.raises(SealOpenError):
        (tmp_path / "03_仮説_封.md").read_text()


# ── A｜settings.json の deny ─────────────────────────────


def test_settings_is_valid_json():
    assert isinstance(load_settings(), dict)


@pytest.mark.parametrize("path", SEAL_SAMPLES)
def test_deny_blocks_seal_paths(path):
    specs = read_deny_specs(load_settings())
    assert denied(path, specs), f"Read の deny が {path} を塞いでいない"


@pytest.mark.parametrize("prefix", ["./", ""])
@pytest.mark.parametrize("name", ["03_仮説_封.md", "02b_*_封.md"])
def test_deny_has_both_path_forms(prefix, name):
    """実走ログ 3-59：./ 付き・無しの2系統が両方要る。"""
    specs = read_deny_specs(load_settings())
    assert f"{prefix}案件/**/{name}" in specs


@pytest.mark.parametrize("path", OPEN_SAMPLES)
def test_deny_does_not_block_what_genba_ops_needs(path):
    specs = read_deny_specs(load_settings())
    assert not denied(path, specs), f"{path} まで塞いでいる。②が動けなくなる"


def test_every_seal_file_on_disk_is_denied():
    """実在する *_封* ファイルが全部 deny に掛かるか。名前が型から外れた封を捕まえる。
    ★rglob はファイル名を列挙するだけで、中身は開かない。"""
    anken = REPO / "案件"
    if not anken.is_dir():
        pytest.skip("案件/ が無い（この端末では診断していない）")
    specs = read_deny_specs(load_settings())
    seals = [p.relative_to(REPO).as_posix() for p in anken.rglob("*_封*") if p.is_file()]
    if not seals:
        pytest.skip("封ファイルが1つも無い")
    leaked = [s for s in seals if not denied(s, specs)]
    assert not leaked, f"deny に掛からない封がある：{leaked}"


@pytest.mark.parametrize("path", [SETTINGS, LOCAL_SETTINGS, Path.home() / ".claude" / "settings.json"],
                         ids=["project", "project-local", "user"])
def test_no_allow_rule_reopens_seal(path):
    if not path.exists():
        pytest.skip(f"{path} が無い")
    allow = load_settings(path).get("permissions", {}).get("allow", []) or []
    bad = [r for r in allow if "封" in r or ("Read" in r and "案件" in r and "*" in r)]
    assert not bad, f"allow が封を開けうる：{bad}"


# ── B｜check_seal.py の挙動 ──────────────────────────────


def test_check_seal_cli_passes_on_real_settings():
    r = subprocess.run([sys.executable, str(REPO / "check_seal.py")],
                       capture_output=True, text=True, cwd=REPO)
    assert r.returncode == 0, r.stdout + r.stderr
    assert r.stdout.startswith("✓")


def test_check_seal_ok_on_current_rules(check_seal):
    assert check_seal(load_settings()).main() == 0


@pytest.mark.parametrize("drop", ["03_仮説_封.md", "02b_*_封.md"])
def test_check_seal_ng_when_one_seal_removed(check_seal, drop):
    s = load_settings()
    s["permissions"]["deny"] = [r for r in s["permissions"]["deny"] if drop not in r]
    assert check_seal(s).main() == 1


@pytest.mark.parametrize("data", [
    {"permissions": {"deny": []}},
    {"permissions": {}},
    {},
], ids=["empty-deny", "no-deny", "empty"])
def test_check_seal_ng_when_deny_empty(check_seal, data):
    assert check_seal(data).main() == 1


def test_check_seal_ng_on_broken_json(check_seal):
    assert check_seal("{ not json").main() == 1


def test_check_seal_ng_when_settings_missing(check_seal, monkeypatch, tmp_path):
    mod = check_seal.module
    monkeypatch.setattr(mod, "SETTINGS", tmp_path / "無い.json")
    assert mod.main() == 1


def test_check_seal_does_not_write_settings(check_seal):
    """確認だけで、書き換えないこと（docstring の約束）。"""
    mod = check_seal(load_settings())
    before = mod.SETTINGS.read_bytes()
    mod.main()
    assert mod.SETTINGS.read_bytes() == before


# ── C｜以前の既知の穴（2026-09-26 に xfail で固定 → 09-29 に直した）─────────


def test_check_seal_requires_read_tool(check_seal):
    """Read 以外（Edit など）の deny では封にならない。部分文字列だけで ✓ を出さない（09-29）。"""
    s = {"permissions": {"deny": ["Edit(./案件/**/03_仮説_封.md)", "Edit(./案件/**/02b_*_封.md)"]}}
    assert check_seal(s).main() == 1


def test_check_seal_ng_when_only_one_pattern_is_read(check_seal):
    s = {"permissions": {"deny": ["Read(./案件/**/03_仮説_封.md)", "Edit(./案件/**/02b_*_封.md)"]}}
    assert check_seal(s).main() == 1


def _seal_guard_matchers(s):
    """PreToolUse で seal_guard.py を呼んでいる matcher（段6。09-26 本人が settings.json に登録）。"""
    return [h.get("matcher", "") for h in s.get("hooks", {}).get("PreToolUse", [])
            if any("seal_guard.py" in x.get("command", "") for x in h.get("hooks", []))]


def test_bash_reads_of_seal_are_blocked():
    """以前の既知の穴：deny は Read ツールだけで、Bash の cat / grep -r で封が読めた → seal_guard で閉じた。"""
    s = load_settings()
    bash_deny = [r for r in s.get("permissions", {}).get("deny", [])
                 if r.startswith("Bash(") and "封" in r]
    assert bash_deny or any("Bash" in m and "Grep" in m for m in _seal_guard_matchers(s))


def test_deny_independent_of_cwd():
    """以前の既知の穴：deny のパターンは cwd 基準で、案件/案件D から起動すると掛からない可能性があった。
    → seal_guard が Read をファイル名で止める（cwd 非依存）ので閉じた。deny だけで閉じていても可。"""
    s = load_settings()
    specs = read_deny_specs(s)
    # cwd が 案件/案件X のとき、Claude Code から見た相対パスはファイル名だけになる
    by_deny = denied("03_仮説_封.md", specs) and denied("02b_主任診断士の見立て_封.md", specs)
    assert by_deny or any("Read" in m for m in _seal_guard_matchers(s))


def test_check_seal_is_wired_into_pre_commit():
    """段6（09-26）で pre-commit の項目7に入れた。以前は手で叩くだけ（CHECK.md §1）だった。"""
    hook = (REPO / ".githooks" / "pre-commit").read_text(encoding="utf-8")
    assert "check_seal.py" in hook
