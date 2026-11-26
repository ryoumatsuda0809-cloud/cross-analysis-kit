"""SKILL.md から「規則の単位」を機械で取り出す（段9・仕分け表_SKILL.md の分母）。

★分母を人が選ばない：抽出はこの関数だけが決める。SKILL.md の文章が変われば抽出も変わり、
  tests/test_rtm.py が「表を更新せよ」と落ちる（CHECK.md の項目と同じ仕組み）。
★単位：コードブロックと見出しを除いた行のうち
  1. 箇条書き・番号付きの項目
  2. 表の本文の行（見出し行・区切り行は除く）
  3. 地の文・引用の行で、指示の言い回し（DIRECTIVE）を含むもの
  説明だけの行は3に拾われないことがある。拾った行が規則でなければ、表で N（規則ではない）にする。
"""
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILLS = REPO / ".claude" / "skills"
MARK = re.compile(r"[*`★]")
DIRECTIVE = re.compile(r"必ず|禁止|しない|しません|するな|させない|ないこと|ない。|てはいけない|なければ|すること|絶対|のみ|だけを|だけに|だけ。")
SEP = re.compile(r"^\|[\s:|-]+\|$")


def norm(s):
    return MARK.sub("", re.sub(r"^(>\s*)+", "", s.strip())).strip()


def units(path):
    """[(行番号, 種類, 照合用の本文)]。種類は list／table／text。"""
    lines = path.read_text(encoding="utf-8").splitlines()
    out, fence = [], False
    for i, l in enumerate(lines):
        s = l.strip()
        if s.startswith("```"):
            fence = not fence
            continue
        if fence or not s or s.startswith("#") or SEP.match(s):
            continue
        if s.startswith("|"):
            if i + 1 < len(lines) and SEP.match(lines[i + 1].strip()):
                continue   # 表の見出し行
            out.append((i + 1, "table", " ／ ".join(norm(c) for c in s.strip("|").split("|")).strip()))
        elif re.match(r"^(>\s*)*(- |\* |\d+\. )", s):
            out.append((i + 1, "list", norm(re.sub(r"^(>\s*)*(- |\* |\d+\. )", "", s))))
        elif DIRECTIVE.search(s):
            out.append((i + 1, "text", norm(s)))
    return out


def all_units():
    """[(スキル名, 行番号, 種類, 本文)]（スキル名の順）。"""
    return [(p.parent.name, *u) for p in sorted(SKILLS.glob("*/SKILL.md")) for u in units(p)]


if __name__ == "__main__":
    from collections import Counter
    us = all_units()
    for k, v in sorted(Counter((s, t) for s, _, t, _ in us).items()):
        print(k, v)
    print("合計", len(us))
