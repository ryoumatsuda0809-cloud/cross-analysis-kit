#!/usr/bin/env python3
"""lint_01.py ｜ 外形カード（01＝提出用）の機械検査

  ★対象は `01_外形カード_事実編.md`（提出用）だけ。
    `01i_外形カード_内部用.md`（定規）には掛けない。
    01i は「定規」「建前」「自己申告」「仮説」といった内部語を正当に含むので、
    掛けると全部エラーになる（2026-09-20・01/01i の2本立て化に伴う注記）。

  使い方
    python3 lint_01.py 案件/案件D/01_外形カード_事実編.md   # 提出用カード1枚を検査
    python3 lint_01.py --leak                                # push対象への社名漏れを検査

  なぜ要るか（実走ログ #14／#15）
    - `01` は相手に見せる紙。見立て・内部語が1語でも混ざったら出せない
    - 数字の行は「どこに／種類／いつ」の3点セットで初めて定規になる
    - `実走ログ.md` やスキルは push される。社名・実数が混ざると守秘が破れる
"""
import re, sys, os, subprocess

# 1. 見立て（Dの混入）
BANNED_PREDICATES = [
    "可能性がある", "可能性が高い", "と思われる", "だろう", "おそらく",
    "が課題", "課題である", "が弱い", "が遅れて", "べきである", "すべきだ",
    "改善余地", "ボトルネック", "属人化",
]
# 2. 読者を取り違えた語（相手が読む紙に載せない）
BANNED_WORDS = ["実態", "自己申告", "建前", "定規", "仮説", "封", "棄却", "見立て"]
# 3. 必須の列見出し
REQUIRED_HEADERS = ["どこに", "種類", "いつ"]
# 4. 切り離し線から上に出てはいけない内部語
INTERNAL_ONLY = ["社内メモ", "社内用", "TODO", "genba-ops", "shinin-hansho",
                 "market-recon", "実走ログ", "SKILL.md", "CHECK.md", "gitignore"]
SPLIT = re.compile(r"^-{3,}\s*\n-{3,}\s*$", re.M)

def lint_card(path):
    src = open(path, encoding="utf-8").read()
    errs, warns = [], []

    m = SPLIT.search(src)
    if not m:
        warns.append("切り離し線（--- の2行）が無い。社内メモをどこで切るか分からない")
        front = src
    else:
        front = src[:m.start()]

    for w in BANNED_PREDICATES:
        for i, line in enumerate(front.splitlines(), 1):
            if w in line:
                errs.append(f"L{i} 見立てが混ざっている：「{w}」 → 03 へ")
    for w in BANNED_WORDS:
        for i, line in enumerate(front.splitlines(), 1):
            if w in line:
                errs.append(f"L{i} 内部語が混ざっている：「{w}」")
    for w in INTERNAL_ONLY:
        for i, line in enumerate(front.splitlines(), 1):
            if w in line:
                errs.append(f"L{i} 切り離し線より上に内部語：「{w}」")

    if re.search(r"案件[A-Z]", front):
        errs.append("切り離し線より上にコード名（案件X）がある。提出時は実名にする")

    for h in REQUIRED_HEADERS:
        if h not in front:
            errs.append(f"必須の列見出しが無い：「{h}」 → 15-2")

    # 分からなかったことの節が空でないか
    m4 = re.search(r"##\s*4\..*?\n(.*?)(?=\n##|\Z)", front, re.S)
    if not m4 or len(re.findall(r"^\|.*\|\s*$", m4.group(1), re.M)) < 3:
        warns.append("§4『公開情報では分からなかったこと』が空か、ほぼ空。"
                     "ここが『お話を伺わないと分かりません』の根拠になる")

    # §2 が §3 より厚いか
    def seclen(n):
        mm = re.search(rf"##\s*{n}\..*?\n(.*?)(?=\n##\s*\d\.|\Z)", front, re.S)
        return len(mm.group(1)) if mm else 0
    if seclen(2) < seclen(3):
        warns.append("§2（御社が発信されていること）より §3 の方が厚い。定規が薄い")

    return errs, warns

def lint_leak(root="."):
    ng = os.path.join(root, "案件", "_禁止語_ローカル専用.txt")
    if not os.path.exists(ng):
        return ["禁止語リストが無い: " + ng], []
    words = [w.strip() for w in open(ng, encoding="utf-8") if w.strip()]
    try:
        # ★quotepath=off と -z（Z9）。無いと日本語名が "\345…" にエスケープされて isfile() が偽になり、
        #   中身を検査しないまま通る（この Mac は .git/config で off だったので気づかなかった）
        files = [f for f in subprocess.check_output(
            ["git", "-c", "core.quotepath=off", "ls-files", "-z"], cwd=root, text=True).split("\0") if f]
    except Exception as e:
        return [f"git ls-files に失敗: {e}"], []
    errs = []
    for f in files:
        p = os.path.join(root, f)
        if not os.path.isfile(p):
            continue
        try:
            body = open(p, encoding="utf-8", errors="ignore").read()
        except Exception:
            continue
        for w in words:
            if w in body:
                errs.append(f"{f} に禁止語「{w}」が混ざっている（このファイルは push される）")
    return errs, []

def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(2)
    if sys.argv[1] == "--leak":
        errs, warns = lint_leak(sys.argv[2] if len(sys.argv) > 2 else ".")
        title = "社名漏れ検査"
    else:
        errs, warns = lint_card(sys.argv[1])
        title = sys.argv[1]
    print(f"=== lint_01 ｜ {title} ===")
    for e in errs:  print("  NG   " + e)
    for w in warns: print("  WARN " + w)
    if not errs and not warns:
        print("  OK   問題なし")
    sys.exit(1 if errs else 0)

if __name__ == "__main__":
    main()
