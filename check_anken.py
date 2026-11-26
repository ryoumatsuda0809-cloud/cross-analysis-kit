#!/usr/bin/env python3
"""check_anken.py ｜ 案件フォルダの構造検査（実走ログ #24）

  使い方
    python3 check_anken.py                 # 案件/ 配下すべて
    python3 check_anken.py 案件/案件D      # 1案件だけ

  なぜ要るか
    2026-09-20、#23 の「隔離時はファイル名にも接頭辞」という恒久ルールが
    翌日に破れた。ルールは付け忘れる。**これは機械で検出する。**

  検査するもの
    1. 同一案件フォルダ内でのベース名の重複（同じ番号が2つある状態）
    2. ②③④が読むファイルの存在（読む先が無ければ止まる）
    3. 案件フォルダ内に隔離フォルダを作っていないか（_使わない/ の外に置いていないか）
    4. 「使わない」を意味する禁止語彙（_旧_ _保留_ _保管_ _前回_ .bak）
    5. ①の出力（01・01i）の形（tests/card_checks.py。フックが動かない環境でも止める）
"""
import os, re, sys, glob
from pathlib import Path

ANKEN_ROOT = "案件"
ARCHIVE = os.path.join(ANKEN_ROOT, "_使わない")
BANNED_PREFIX = ("_旧", "_保留", "_保管", "_前回", "_to_delete")
BANNED_SUFFIX = (".bak",)
# ②③④が読むもの（cross-run/SKILL.md Stage 3〜5 の表と一致させること）
READERS = {
    "② genba-ops":    ["01i_外形カード_内部用.md", "02_現場で確認すべき問い.md",
                       "_材料/B_現場/現場メモ.md"],
    "③ shinin-hansho":["04_現場分析.md", "01i_外形カード_内部用.md", "02_現場で確認すべき問い.md",
                       "02b_主任診断士の見立て_封.md", "03_仮説_封.md"],
    "④ tougou-report":["05_反証レポート.md", "01i_外形カード_内部用.md", "04_現場分析.md"],
}
# #14（定規化）以前の案件は 01i が無い。01 で代用してよいが、04 に明記させる
FALLBACK = {"01i_外形カード_内部用.md": "01_外形カード_事実編.md"}

def strip_num(name):
    """先頭の接頭辞を「何であれ」剥いでから番号を読む。

    ★接頭辞の一覧に頼らない。禁止語リストは『知っている名前』しか守れない
      （2026-09-20、push済み履歴の社名漏れが `lint_01.py --leak` を素通りしたのと同じ穴）。
      `_保留_04_...` も `_なんとか_04_...` も、等しく 04 として数える。
    """
    # 先頭の _xxx_ を何重でも剥ぐ。`_a_b_04_…` のように _ を共有して連なっても剥がす（Z7・09-29）
    m = re.match(r"^(?:_(?:[^_/]*_)+?)?(\d+[a-z]?i?)_", name)
    return m.group(1) if m else None

def check(anken):
    errs, warns, notes = [], [], []
    name = os.path.basename(anken)

    # 0. 汚染記録（CHECK.md §1。実走ログにしか書かないと、次のAIが「まだきれい」と誤認する → 3-58）
    if os.path.exists(os.path.join(anken, "_汚染記録.md")):
        notes.append("`_汚染記録.md` がある → この案件はクロス分析として成立しない（配管の検証にだけ使う）。先に読む")

    # 1. 同一案件内のベース名（番号）重複
    seen = {}
    for root, dirs, files in os.walk(anken):
        dirs[:] = [d for d in dirs if d != ".git"]
        for f in files:
            if not f.endswith(".md"): continue
            n = strip_num(f)
            if n: seen.setdefault(n, []).append(os.path.relpath(os.path.join(root, f), anken))
    for n, paths in sorted(seen.items()):
        if len(paths) > 1:
            errs.append(f"番号 {n} のファイルが {len(paths)} 個ある → " + " / ".join(paths))

    # 2. 禁止語彙
    for root, dirs, files in os.walk(anken):
        dirs[:] = [d for d in dirs if d != ".git"]
        for e in list(dirs) + files:
            if e.startswith(BANNED_PREFIX) or e.endswith(BANNED_SUFFIX):
                errs.append(f"禁止語彙：{os.path.relpath(os.path.join(root, e), ANKEN_ROOT)}"
                            f"（使わないものは {ARCHIVE}/ へ。接頭辞は付けない）")

    # 3. 案件フォルダ内の隔離フォルダ（_材料 以外のアンダースコア始まりフォルダ）
    for d in os.listdir(anken):
        p = os.path.join(anken, d)
        if os.path.isdir(p) and d.startswith("_") and d != "_材料":
            errs.append(f"案件フォルダの中に `{d}/` がある → {ARCHIVE}/{name}_{{日付}}_{{理由}}/ へ出す")

    # 3.5 PDF（提出物）は1案件に1つ（実走ログ #40）
    pdfs = [f for f in os.listdir(anken) if f.lower().endswith(".pdf")]
    if len(pdfs) > 1:
        errs.append(f"PDF が {len(pdfs)} 個ある（提出物は1つ。前と今を両方置かない）→ " + " / ".join(sorted(pdfs)))

    # 4. ②③④が読む先の存在
    for stage, need in READERS.items():
        for rel in need:
            if os.path.exists(os.path.join(anken, rel)): continue
            fb = FALLBACK.get(os.path.basename(rel))
            if fb and os.path.exists(os.path.join(anken, fb)):
                notes.append(f"{stage}：`{rel}` が無い → `{fb}` で代用可。"
                             f"★その場合 `04` の冒頭に「定規は #14 以前の版を代用。ズレ検出力が落ちている」と明記する")
            else:
                warns.append(f"{stage}：`{rel}` が無い（その段はまだ回せない）")

    return errs, warns, notes

def repo_check():
    """リポジトリ全体の検査（実走ログ #43）。
    ★フックが「在る」ことと「動く」ことは別。09-20〜09-25、tools/pre-commit は
    core.hooksPath=.githooks のせいで一度も動いていなかった。だから配線を見る。"""
    import subprocess
    root = os.path.dirname(os.path.abspath(__file__))
    errs = []
    try:
        hp = subprocess.run(["git", "-C", root, "rev-parse", "--git-path", "hooks"],
                            capture_output=True, text=True).stdout.strip()
    except Exception:
        hp = ""
    if hp != ".githooks":
        errs.append(f"フックの配線が違う（git が見ている場所：{hp or '不明'}）→ git config core.hooksPath .githooks")
    hook = os.path.join(root, ".githooks", "pre-commit")
    if not os.access(hook, os.X_OK):
        errs.append("`.githooks/pre-commit` が無いか実行できない → chmod +x .githooks/pre-commit")
    for m in (".agents", "AGENTS.md", ".Codex", ".codex", ".github/copilot-instructions.md"):
        if os.path.exists(os.path.join(root, m)):
            errs.append(f"別ツール用の写しがある：`{m}`（CLAUDE.md §1-0。外のツールが作った可能性。消して、作った元を探す）")
    return errs

def card_check(anken):
    """5. ①の出力（01・01i）の形（tests/card_checks.py）。
    保存時に notice.py（.claude/settings.json のフック）でも出るが、フックは Claude Code をこのフォルダで
    開いたときしか動かない。2026-11-26 の通しでは別のフォルダで開いていて、R18・R19・S267 が②まで素通りした。
    段の前に毎回流すこのコマンドに入れて、フックが動かない環境でも止まるようにする。
    check() は構造だけを見る（tests/test_check_anken.py が前提にしている）ので、ここは別にしている。"""
    if not any(os.path.exists(os.path.join(anken, f)) for f in ("01_外形カード_事実編.md", "01i_外形カード_内部用.md")):
        return []
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "tests"))
    import card_checks as C
    return [f"①の出力の形：{C.describe(v)}" for v in C.check_case(Path(anken))]

def main():
    if sys.argv[1:] == ["--repo"]:
        errs = repo_check()
        for e in errs: print(f"  NG   {e}")
        if not errs: print("  OK   リポジトリ（フックの配線・写し）")
        sys.exit(1 if errs else 0)
    rerrs = repo_check()
    print("=== リポジトリ ===")
    for e in rerrs: print(f"  NG   {e}")
    if not rerrs: print("  OK   フックの配線・写し")
    print()
    targets = sys.argv[1:] or sorted(
        d for d in glob.glob(os.path.join(ANKEN_ROOT, "*")) 
        if os.path.isdir(d) and os.path.basename(d) != "_使わない")
    bad = 0
    for t in targets:
        errs, warns, notes = check(t)
        errs += card_check(t)
        print(f"=== {t} ===")
        for e in errs:  print(f"  NG   {e}")
        for w in warns: print(f"  WARN {w}")
        for n in notes: print(f"  NOTE {n}")
        if not (errs or warns or notes): print("  OK   問題なし")
        bad += len(errs)
        print()
    bad += len(rerrs)
    print(f"NG 合計：{bad}")
    sys.exit(1 if bad else 0)

if __name__ == "__main__":
    main()
