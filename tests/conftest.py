"""tests/ 共通設定。

★テストは封（*_封.md）の中身を1バイトも読まない（CLAUDE.md §3・条件②）。
下の seal_guard が全テストに自動で掛かり、_封 を含むファイルを開こうとした瞬間に落とす。
見てよいのは settings.json・既存スクリプト・ファイル名（パス）だけ。
"""
import builtins
import io
import os
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))


class SealOpenError(AssertionError):
    """テストが封を開こうとした。テストの書き方が間違っている。"""


def _is_seal(path) -> bool:
    try:
        return "_封" in os.path.basename(os.fspath(path))
    except TypeError:  # int の fd など
        return False


@pytest.fixture(autouse=True)
def seal_guard(monkeypatch):
    real_open = builtins.open
    real_os_open = os.open

    def guarded_open(file, *args, **kwargs):
        if _is_seal(file):
            raise SealOpenError(f"テストが封を開こうとした：{file}")
        return real_open(file, *args, **kwargs)

    def guarded_os_open(path, *args, **kwargs):
        if _is_seal(path):
            raise SealOpenError(f"テストが封を開こうとした：{path}")
        return real_os_open(path, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", guarded_open)
    monkeypatch.setattr(io, "open", guarded_open)
    monkeypatch.setattr(os, "open", guarded_os_open)
    # pathlib は io.open を内部で掴んでいるので Path.open も塞ぐ
    real_path_open = pathlib.Path.open

    def guarded_path_open(self, *args, **kwargs):
        if _is_seal(self):
            raise SealOpenError(f"テストが封を開こうとした：{self}")
        return real_path_open(self, *args, **kwargs)

    monkeypatch.setattr(pathlib.Path, "open", guarded_path_open)
    yield


@pytest.fixture
def repo() -> pathlib.Path:
    return REPO


# ── 既存の検査スクリプト（段3）。CLI（引数・NG 行・終了コード）は約束事なので、外から叩いて確かめる
SCRIPTS = {
    "check_anken": REPO / "check_anken.py",
    "check_genba_mark": REPO / "check_genba_mark.py",
    "check_genba_ref": REPO / "check_genba_ref.py",
    "check_report": REPO / "対外資料" / "_report_build" / "check_report.py",
    "lint_01": REPO / ".claude" / "skills" / "market-recon" / "scripts" / "lint_01.py",
    "strip_kijun": REPO / ".claude" / "skills" / "cross-run" / "scripts" / "strip_kijun.py",
}


os.environ.setdefault("PYTHONUTF8", "1")     # 子プロセスの入出力を UTF-8 に（Windows の既定は cp932）


def run_script(name, *args, cwd=None):
    """スクリプトを別プロセスで叩く。返り値は (終了コード, NG 行のリスト, 標準出力)。"""
    import subprocess
    r = subprocess.run([sys.executable, str(SCRIPTS[name]), *map(str, args)],
                       capture_output=True, text=True, encoding="utf-8", cwd=cwd or REPO)
    ng = [l.strip()[len("NG"):].strip() for l in r.stdout.splitlines() if l.strip().startswith("NG ")]
    return r.returncode, ng, r.stdout


def load_script(name):
    import importlib.util
    spec = importlib.util.spec_from_file_location(f"_t_{name}", SCRIPTS[name])
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod
