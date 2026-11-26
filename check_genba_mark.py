#!/usr/bin/env python3
"""check_genba_mark.py ｜ 現場メモの「B軸の4印」を機械検査する

  使い方
    python3 check_genba_mark.py 案件/案件D/_材料/B_現場/現場メモ.md

  なぜ要るか（実走ログ 20-2／21・案件D）
    現場メモに出所が1つも無いと、半年後にB軸の証拠として使えるかを判定する手段が
    本人に聞く以外に無くなる。実際の案件では異動・記憶の曖昧さ・情報源を明かせない事情で、
    聞いても答えが出ないことがある。**印は後から付けられない。取るときに付ける。**

  ★3印 → 4印にした理由（2026-09-22／実走ログ 27-5・B-4・#34）
    旧版は `いつ・どこで` と `直接／伝聞／書面` の2列だった。これは**2軸を1列に潰していた。**
    Zoom通話は「現地か遠隔か」＝遠隔、「直接か伝聞か」＝直接（本人から聞いた）であり、
    1列では決まらない。案件Dで本人が欄をずらして記入し、
    **09-20 の引き継ぎ書が「実際の訪問が行われた」と書く事故が起きた（実際は未訪問）。**
    → `いつ` と `どこで（現地／遠隔）` を分け、`誰から（直接／伝聞／書面）` を独立させた。

  ★存在検査ではなく「中身の形」を見る（#32・#33 と同じ直し方）
    旧版は**セルが空でないかだけ**を見ていた。だから `いつ・どこで | 2026-09-20` は
    **どこでが書かれていないのに通った。** これが B-4 の実害の入口。
    → 各印に「取りうる値」を定め、それが含まれているかを検査する。

  ★本文の各行の頭に【役割】（2026-09-29 本人決定／実走 #58）
    4印はメモ全体に1つなので、どの発言を誰がしたかが残らなかった。②は 04 の根拠に役割を推測で書き、
    ③はその役割数を採用の材料に使った（58-1）。→ 本文の箇条書き・表の本文の各行に【役割】（名前でなく役割）。
    分からない行は【不明】（役割数に数えない）。04 がその行を正しく引いたかは check_genba_ref.py が見る。
    テンプレの問いだけの行（「…：」で終わる）は答えが無いので見ない。★出すのは行番号だけ（守秘）。

  cross-run は②を起動する前に、対象の現場メモに対してこれを実行する。
  NG（exit 1）なら②以降を起動しない。
"""
import re
import sys

# genba-memo-template.md の「★出所」表と対応させる
#   (欄の見出し, 値に含まれていなければNGの候補, 説明)
REQUIRED_MARKS = [
    ("話者",   None,                                  "誰の話か"),
    ("いつ",   [r"\d{4}[-/年]\d{1,2}", r"不明"],       "日付（2026-09-20 の形）または「不明（理由）」"),
    ("どこで", ["現地", "遠隔", "不明"],               "**現地**（工場・事務所に入った）／**遠隔**（Zoom・電話・書面）／不明"),
    ("誰から", ["直接", "伝聞", "書面", "不明"],       "**直接**（本人から）／**伝聞**（人づて）／**書面**／不明"),
]

LEGACY = ["いつ・どこで", "直接／伝聞／書面"]

TAG = re.compile(r"【[^】]+】")
SEP = re.compile(r"^\|[\s:|-]+\|$")
LIST = re.compile(r"^(?:[-*]|\d+\.)\s+(.*)$")
SOURCE_ROW = re.compile(r"^\|\s*\**(話者|いつ|どこで|誰から)")
HR = re.compile(r"^([-*_])\1{2,}$")
BOLD_ONLY = re.compile(r"^\*\*[^*]+\*\*$")


def body_lines(src):
    """本文の行（地の文・箇条書き・表の本文）の [(行番号, 行)]。【役割】を付ける行＝04 が引いてよい行。
    見出し・引用・コード・区切り線・表の見出し行・★出所の4印の行・太字だけの行（問い・話者の見出し）・
    問いだけの行（「…：」で終わる）は見ない。
    ★地の文も見る：問い（太字）＋答え（地の文）の形のメモがある。箇条書きだけ見ると、その形は素通りする（fail-open）"""
    lines = src.splitlines()
    out, fence = [], False
    for i, l in enumerate(lines):
        s = l.strip()
        if s.startswith("```"):
            fence = not fence
            continue
        if fence or not s or s.startswith(("#", ">")):
            continue
        if s.startswith("|"):
            if SEP.match(s) or (i + 1 < len(lines) and SEP.match(lines[i + 1].strip())) or SOURCE_ROW.match(s):
                continue
            if not s.replace("|", "").replace("*", "").strip():
                continue
        else:
            m = LIST.match(s)
            body = (m.group(1) if m else s).strip()
            if not body or re.fullmatch(r"[-*]|\d+\.", s) or HR.match(s) or BOLD_ONLY.match(body) or re.search(r"[：:]$", body):
                continue
        out.append((i + 1, s))
    return out


def untagged_lines(src):
    """本文の行のうち【役割】が無いものの行番号。"""
    return [n for n, s in body_lines(src) if not TAG.search(s)]


def cell(src, mark):
    """「| <mark>（…） | 中身 | 書き方 |」の2列目を返す。欄が無ければ None

    ★Z13（2026-09-26・tests/移行台帳.md）：テンプレの欄名は太字（`| **いつ** | | 書き方 |`）で3列ある。
      旧版は太字を許さず、テンプレどおりに書いたメモを「欄そのものが無い」で NG にしていた（②が起動できない）。
      ★太字を許すだけで直すと、3列目の説明文（`現地`・`直接`）まで値として拾い、空欄が通る。
      だから「太字を許す」と「2列目だけ取る」を同時に入れる（tests/test_check_genba_mark.py が両方を見張る）"""
    rx = re.compile(rf"^\|\s*\**{re.escape(mark)}[^|]*\|\s*([^|]*?)\s*\|", re.M)
    m = rx.search(src)
    return m.group(1).strip() if m else None


def check(path):
    src = open(path, encoding="utf-8").read()
    errs, notes = [], []

    # 旧3印形式の検出（B-4 以前のメモ）
    legacy_hit = [m for m in LEGACY if cell(src, m) is not None]
    if legacy_hit and cell(src, "どこで") is None:
        errs.append(
            "★旧3印形式である（" + "／".join(legacy_hit) + "）。"
            "2軸が1列に潰れているので、現地か遠隔かが決まらない")
        errs.append(
            "  → 欄を4つに分ける：`話者` ／ `いつ` ／ `どこで（現地／遠隔）` ／ `誰から（直接／伝聞／書面）`"
            "（テンプレ：.claude/skills/genba-ops/assets/genba-memo-template.md）")
        return errs, notes

    for mark, allowed, why in REQUIRED_MARKS:
        v = cell(src, mark)
        if v is None:
            errs.append(f"欄そのものが無い：「{mark}」　← {why}")
            continue
        if not v:
            errs.append(f"欄はあるが空欄：「{mark}」　← {why}")
            continue
        if allowed and not any(re.search(a, v) for a in allowed):
            errs.append(
                f"「{mark}」の中身が形になっていない：「{v[:40]}」\n"
                f"       ← {why}。**欄が埋まっているだけでは通さない**（B-4 の実害はここから入った）")
        if "不明" in v and "（" not in v and "(" not in v:
            notes.append(f"「{mark}」が「不明」だが理由が書かれていない。`不明（理由）` の形で書く")

    bare = untagged_lines(src)
    if bare:
        shown = "・".join(f"L{n}" for n in bare[:15]) + ("…" if len(bare) > 15 else "")
        errs.append(
            f"本文の行に【役割】が無い：{len(bare)}行（{shown}）\n"
            f"       ← 各行の頭に話した人の役割（名前でなく役割。例【工場長】）。分からなければ【不明】（実走 #58）")
    return errs, notes


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    path = sys.argv[1]
    errs, notes = check(path)
    print(f"=== check_genba_mark ｜ {path} ===")
    for e in errs:
        print("  NG   " + e)
    for n in notes:
        print("  NOTE " + n)
    if errs:
        print("  → 4印と各行の【役割】が揃うまで、この現場メモをB軸の証拠として使わない（②以降を起動しない）")
        sys.exit(1)
    print("  OK   4印（話者／いつ／どこで／誰から）と、本文の各行の【役割】が揃っています")
    sys.exit(0)


if __name__ == "__main__":
    main()
