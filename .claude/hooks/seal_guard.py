#!/usr/bin/env python3
"""seal_guard.py ｜ PreToolUse フック：Read 以外の経路から封（*_封*）を読ませない（移行 段6）

  なぜ要るか（tests/test_seal_security.py の既知の穴 C）
    settings.json の deny は Read ツールだけに効く。Bash の `cat` / `grep -r`、Grep ツールで
    封の本文が読めた。deny のパターンは起動した場所（cwd）基準で、案件/案件D から起動すると掛からない可能性もあった。
    → ツールの入力を見て、封に触れうるものを止める（exit 2）。**名前で見るので cwd に依存しない。**

  ★これは事故を防ぐための柵であって、わざと破る相手を止める壁ではない（シェルの書き方は無限にある）。
    封の本体は今までどおり「②に存在を知らせない」運用と deny（CLAUDE.md §1-1）。
  ★止めるだけで、何も読まない。封の中身にも案件の中身にも触れない。

  止めるもの
    Read  ：ファイル名に _封 を含む
    Grep  ：path が _封、または 案件/ のディレクトリ（ファイルを1つ指定するなら可）
    Bash  ：コマンドに _封 を含む（ls / find で名前を見るだけなら可）
            案件/ に対する再帰検索（grep -r・rg・ag）、案件/ の中でワイルドカードを付けて中身を出すもの（cat 案件/x/* 等）
            cwd が 案件/ の中なら、コマンドに 案件 と書いていなくても 案件/ に対するものとして扱う
            案件/ を含む場所（リポジトリ直下・その親・~）からの再帰検索（grep -r・rg・ag・ack、find に -exec／xargs）。
            コマンドに 案件 と書いていなくても入るため（台帳 §8・09-30。本物の grep で直下から 03 に当たった）。
            --exclude-dir=案件・rg -g '!案件'・find -path …案件… -prune で除外していれば通す。git grep は追跡ファイルだけなので通す。
            本体もサブエージェントも同じに止める（09-30 本人決定）

  サブエージェント（入力に agent_id がある＝②③④と B-1 の検証役）にだけ、さらに止めるもの（実走 62-1）
    08_質の検証（B-1 の判定表）と _プロンプト.md（TEST の回したプロンプト）を、上と同じ3経路で。
    ②をやり直すとき、前の B-1 の指摘を読めば指摘に合わせて書ける（59-11 と同じ型）。
    質の検証.md（失敗の条件）と 案件/_使わない/（前の回の 05・06・07 は 03 の中身を含むのに名前に _封 が無い）も同じ。
    司令塔（本体）は止めない：B-1 の表を 08 に貼る・_プロンプト.md を一字一句使うのは司令塔の仕事。
    deny にしないのはこのため（deny は本体にも効く）。
"""
import json
import os
import re
import shlex
import sys

SEAL = "_封"
READERS = r"(cat|head|tail|less|more|sed|awk|strings|xxd|od|nl|bat|tac|cut|sort|uniq|wc|diff|cmp|base64|python3?|perl|ruby|node)"
NAMES_ONLY = re.compile(r"^\s*(ls|find)\b")
DANGER = re.compile(r"[|;&`]|\$\(|-exec|-ok\b|-delete|xargs|-print0|>")
SUB_CLOSED = ("08_質の検証", "_プロンプト.md", "質の検証.md", "_使わない")
SUB_WHY = ("司令塔だけが読むもの（08 の B-1 の判定・_プロンプト.md・質の検証.md の失敗の条件・"
           "_使わない/ の前の回の出力＝03 の中身を含む）。②③④と検証役は開かない（実走 62-1）")


SEARCHERS = {"grep", "egrep", "fgrep", "ugrep", "rg", "ag", "ack"}
ALWAYS_RECURSIVE = {"rg", "ag", "ack"}
ARG_OPTS = set("efmABCdDgtTM")          # 次の語を値に取る短いオプション（grep・rg の主なもの）
EXCLUDE = re.compile(r"--exclude-dir[= ]\s*['\"]?[^'\"\s]*案件[^'\"\s]*['\"]?"
                     r"|(-g|--glob|--iglob)[= ]\s*['\"]?![^'\"\s]*案件[^'\"\s]*['\"]?"
                     r"|-path\s+['\"]?[^'\"\s]*案件[^'\"\s]*['\"]?\s+-prune")
FIND_READS = re.compile(r"-exec|-ok\b|xargs")


def _norm(p):
    """比べる前に区切りを / に揃える（Windows は \\。揃えないと 案件/ の判定が素通りする）。"""
    return os.path.normpath(p).replace("\\", "/")


def anken_dirs(cwd):
    """cwd から上にたどって見つかる 案件/（と CLAUDE_PROJECT_DIR の 案件/）。名前を見るだけで中は開かない。"""
    found, d = set(), os.path.abspath(cwd or ".")
    for base in [os.environ.get("CLAUDE_PROJECT_DIR", "")] + [d]:
        while base:
            if os.path.isdir(os.path.join(base, "案件")):
                found.add(_norm(os.path.join(base, "案件")))
            parent = os.path.dirname(base)
            base = "" if parent == base else parent
    return found


def reaches_anken(target, cwd):
    t = _norm(os.path.join(cwd or "", os.path.expanduser(target)))
    return any(a == t or a.startswith(t.rstrip("/") + "/") for a in anken_dirs(cwd))


def _words(seg):
    try:
        w = shlex.split(seg)
    except ValueError:
        w = seg.split()
    while w and (w[0] in ("command", "env", "sudo", "nice", "time", "xargs") or "=" in w[0]):
        w = w[1:]                                      # 前に付く語（command grep・xargs grep 等）を外す
    return w


def _find_targets(args, seg):
    """find は中身を読むとき（-exec・xargs）だけ検索と見る。名前を見るだけなら None。"""
    if not FIND_READS.search(seg):
        return None
    paths = []
    for x in args:
        if x.startswith(("-", "(", "!")):
            break
        paths.append(x)
    return paths or ["."]


def _grep_targets(name, args):
    """grep・rg などが再帰なら、対象（場所なしは「.」）。再帰でなければ None。"""
    pos, has_e, recursive, skip = [], False, name in ALWAYS_RECURSIVE, False
    for x in args:
        if skip:
            skip = False
        elif x.startswith("--"):
            recursive |= x in ("--recursive", "--dereference-recursive", "--directories=recurse")
            has_e |= x.startswith(("--regexp", "--file"))
        elif x.startswith("-") and len(x) > 1:
            recursive |= x[1] not in ARG_OPTS and any(c in "rR" for c in x[1:])
            has_e |= x[1] in "ef"
            skip = len(x) == 2 and x[1] in ARG_OPTS
        else:
            pos.append(x)
    if not recursive:
        return None
    return (pos if has_e else pos[1:]) or ["."]      # -e が無ければ最初の語は検索語


def search_targets(seg, rest=""):
    """1区切りのコマンドが中身を読む再帰検索なら、その対象を返す。違えば None。
    rest は後ろに続くコマンド（find … | xargs grep の xargs を見るため）。"""
    w = _words(seg)
    if not w:
        return None
    name = os.path.basename(w[0])
    if name == "find":
        return _find_targets(w[1:], seg + rest)
    return _grep_targets(name, w[1:]) if name in SEARCHERS else None


def root_search_reaches_anken(cmd, cwd):
    """案件/ を含む場所からの再帰検索か（コマンドに 案件 と書いていなくても）。除外していれば通す。"""
    segs = re.split(r"\|\||&&|[|;&]", cmd)
    for i, seg in enumerate(segs):
        targets = search_targets(seg, " ".join(segs[i + 1:i + 2]))
        if targets and not EXCLUDE.search(seg) and any(reaches_anken(t, cwd) for t in targets):
            return True
    return False


def sub_closed(s):
    return any(n in (s or "") for n in SUB_CLOSED)


def in_anken(path, cwd):
    p = _norm(os.path.join(cwd or "", (path or "").replace("\\", "/")))
    return ("/案件/" in p + "/") or p.startswith("案件")


def check(tool, inp, cwd, sub=False):
    if tool == "Read":
        if SEAL in os.path.basename((inp.get("file_path") or "").replace("\\", "/")):
            return "封（_封）のファイルは読まない（CLAUDE.md §3・条件②）"
        if sub and sub_closed(inp.get("file_path", "")):          # _使わない はフォルダなのでパス全体で見る
            return SUB_WHY
        return None

    if tool == "Grep":
        path = inp.get("path") or ""
        if SEAL in path or SEAL in (inp.get("glob") or ""):
            return "封（_封）を Grep しない"
        if sub and (sub_closed(path) or sub_closed(inp.get("glob"))):
            return SUB_WHY
        target = os.path.join(cwd or "", path)
        if in_anken(path, cwd) and not os.path.isfile(target):
            return "案件/ のフォルダを Grep すると封の本文が結果に出る。ファイルを1つ指定するか、Read で読む"
        return None

    if tool == "Bash":
        cmd = inp.get("command", "")
        if SEAL in cmd and not (NAMES_ONLY.match(cmd) and not DANGER.search(cmd)):
            return "コマンドが封（_封）に触れている。名前を見るだけなら ls / find を単独で使う"
        if sub and (sub_closed(cmd) or sub_closed(cwd)) and not (NAMES_ONLY.match(cmd) and not DANGER.search(cmd)):
            return SUB_WHY
        if root_search_reaches_anken(cmd, cwd):
            return ("案件/ を含む場所から再帰検索すると封の本文まで入る。"
                    "git grep を使うか、--exclude-dir=案件（rg は -g '!案件'）を付けるか、対象のフォルダを指定する")
        under = "案件" in EXCLUDE.sub("", cmd) or in_anken("", cwd)
        if not under:
            return None
        if re.search(r"\bgrep\b[^|;&]*\s-[a-zA-Z]*[rR]", cmd) or re.search(r"\b(rg|ag|ack)\b", cmd):
            return "案件/ を再帰検索すると封の本文が出る。ファイルを指定する"
        if re.search(rf"\b{READERS}\b[^|;&]*[*?]", cmd):
            return "案件/ の中身をワイルドカードで出すと封が混ざる。ファイル名を1つずつ指定する"
        return None
    return None


def main():
    try:
        data = json.loads(sys.stdin.buffer.read().decode("utf-8"))   # 端末の文字コードに依らず UTF-8 で読む
    except Exception:
        return 0            # 入力が読めないときは止めない（フックの故障で作業を止めない）
    why = check(data.get("tool_name", ""), data.get("tool_input") or {}, data.get("cwd", ""),
                sub=bool(data.get("agent_id")))
    if why:
        sys.stderr.buffer.write(f"✋ seal_guard：{why}（.claude/hooks/seal_guard.py）\n".encode("utf-8"))
        sys.stderr.flush()
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
