#!/usr/bin/env python3
"""check_genba_ref.py ｜ 04 の根拠が、現場メモの行を正しく引いているかを機械検査する

  使い方
    python3 check_genba_ref.py 案件/{社名}/04_現場分析.md
    （現場メモは同じ案件の _材料/B_現場/現場メモ.md を読む）

  なぜ要るか（実走 #58）
    ②が 04 の根拠に、メモに無い役割を書いた（「誰が言ったか」がメモに無い）。③はその役割数を
    採用の材料（代表性）に使うので、採用が強く出すぎる入口になる。
    しかも今の書き方では Python で見られなかった（58-3）。
    → 現場メモの各行の頭に【役割】、04 の根拠に【役割】L行番号 を書く（09-29 本人決定）。
      そうすれば次の4つは機械で見られる：
      1. 引いた行があるか（行番号がメモに実在し、【役割】の印がある行か）
      2. その行の役割か（04 に書いた【役割】が、メモのその行の印と同じか）
      3. 役割数が合うか（情報源の役割数 ＝ 引いた行の役割の種類。【不明】は数えない）
      4. 役割数に「（つないだ）」とある芽が「強」でないか（別々の話をつないだ芽は中まで → 62-4）
    ★見ないもの：根拠を「広げた・つないだ・強めた」か（意味の判断。4 は②が自分で添えた印だけを見る）。それは B-1 の検証役（cross-run）。

  見る所：04 §1 真因の芽リストの「根拠」列（1〜3）と、§2 建前と現場のズレ一覧の「現場の事実」列（1・2）。

  cross-run は②の後・③の前にこれを実行する。NG（exit 1）なら③を起動しない。
  ★出すのは節・行の番号とルール名だけ。本文・役割名は出さない（守秘）。
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check_genba_mark import body_lines  # noqa: E402  本文の行の決め方を1か所にする（写しを作らない）

MEMO_REL = os.path.join("_材料", "B_現場", "現場メモ.md")
TAG = re.compile(r"【([^】]+)】")
TOKEN = re.compile(r"【([^】]+)】|L(\d+)")
SEP = re.compile(r"^\|[\s:|-]+\|$")
UNKNOWN = "不明"
JOINED = "つないだ"   # 役割数の括弧の注記。②が別々の話をつないだ芽（→ 62-4）
KANJI = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9, "十": 10}


def memo_tags(src):
    """{行番号: {役割…}}。★本文の行（check_genba_mark が【役割】を求める行）だけ。
    引用の注記・見出し・★出所の表にある【…】は、発言の行ではないので引けない（② が見つけた穴：【架空】L27 が1役割として通った）。"""
    return {n: {t.strip() for t in TAG.findall(l)} for n, l in body_lines(src) if TAG.search(l)}


def section(src, num):
    """「## N. …」から次の「## 」まで。[(行番号, 行)]。無ければ None。"""
    lines, start = src.splitlines(), None
    for i, l in enumerate(lines):
        if start is None:
            if re.match(rf"^##\s+§?{num}\.\s", l):
                start = i
        elif re.match(r"^##\s", l):
            return [(j + 1, lines[j]) for j in range(start, i)]
    return None if start is None else [(j + 1, lines[j]) for j in range(start, len(lines))]


def tables(numbered):
    """表 = [(行番号, [セル…])]、先頭が見出し行。区切り行は除く。"""
    out, cur = [], []
    for n, l in numbered:
        s = l.strip()
        if s.startswith("|") and s.endswith("|"):
            if not SEP.match(s):
                cur.append((n, [c.strip() for c in s[1:-1].split("|")]))
        elif cur:
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    return out


def col(head, key):
    return next((i for i, h in enumerate(head) if key in h), None)


def pairs(text):
    """「【工場長】L12・L15／【事務】L20」→ ([(12, 工場長), (15, 工場長), (20, 事務)], 役割の無い行番号があるか)。"""
    out, role, orphan = [], None, False
    for m in TOKEN.finditer(text):
        if m.group(1) is not None:
            role = m.group(1).strip()
        elif role is None:
            orphan = True
        else:
            out.append((int(m.group(2)), role))
    return out, orphan


def role_count(text):
    """情報源の役割数の値。数字 → int、「不明」→ None、読めなければ False。括弧から先は注記。"""
    s = re.split(r"[（(]", text.replace("*", ""), maxsplit=1)[0]
    m = re.search(r"\d+", s)
    if m:
        return int(m.group(0))
    k = next((KANJI[c] for c in s if c in KANJI), None)
    if k is not None:
        return k
    return None if UNKNOWN in s else False


def check_rows(sec_name, table, key, tags, errs, count_key=None):
    head = table[0][1]
    ci = col(head, key)
    ni = col(head, count_key) if count_key else None
    if ci is None:
        return
    for n, c in table[1:]:
        if not any(x.replace("*", "").strip() for x in c[1:]):
            continue   # テンプレの空行
        rid = c[0].replace("*", "").strip() or f"({n}行目)"
        where = f"§{sec_name} #{rid}"
        ps, orphan = pairs(c[ci] if ci < len(c) else "")
        if not ps:
            errs.append(f"根拠にメモの行番号が無い：{where}　← 【役割】L12 の形で、メモのどの行かを書く")
            continue
        if orphan:
            errs.append(f"行番号の前に【役割】が無い：{where}")
        for line, role in ps:
            if line not in tags:
                errs.append(f"引いた行がメモに無い：{where} L{line}（行が無いか、その行に【役割】の印が無い）")
            elif role not in tags[line]:
                errs.append(f"その行の役割ではない：{where} L{line}（04 の【役割】とメモのその行の印が違う）")
        if ni is not None:
            want = len({r for _, r in ps if r != UNKNOWN})
            got = role_count(c[ni] if ni < len(c) else "")
            if got is False:
                errs.append(f"情報源の役割数が読めない：{where}")
            elif (got is None and want > 0) or (got is not None and got != want):
                errs.append(f"役割数が合わない：{where}（引いた行の役割は {want} 種類。【不明】は数えない）")
            elif any(r == UNKNOWN for _, r in ps) and UNKNOWN not in (c[ni] if ni < len(c) else ""):
                # 63-2：【不明】は数えないので、添えないと③には話者の分からない根拠が見えない
                errs.append(f"【不明】の行を引いたのに役割数に書いていない：{where}（例：1役割（＋不明1行））")
            si = col(head, "強度")
            if si is not None and si < len(c) and JOINED in c[ni] and c[si].replace("*", "").strip() == "強":
                # 62-4：役割が複数でも誰もその因果を述べていない。強のままだと③が「2役割が裏付けた」と読む
                errs.append(f"つないだ芽が「強」：{where}（別々の話をつないだ芽は中まで）")


def check(path04):
    errs = []
    memo_path = os.path.join(os.path.dirname(os.path.abspath(path04)), MEMO_REL)
    if not os.path.exists(memo_path):
        return [f"現場メモが無い：{MEMO_REL}"]
    tags = memo_tags(open(memo_path, encoding="utf-8").read())
    src = open(path04, encoding="utf-8").read()

    s1 = section(src, "1")
    t1 = [t for t in tables(s1 or []) if col(t[0][1], "根拠") is not None]
    if not t1:
        errs.append("§1 真因の芽リストの表（根拠の列）が無い")
    for t in t1:
        check_rows("1", t, "根拠", tags, errs, count_key="役割数")

    s2 = section(src, "2")
    for t in tables(s2 or [])[:1]:     # 建前と現場のズレ一覧（最初の表）。ベンチマークの表は見ない
        check_rows("2", t, "現場の事実", tags, errs)
    return errs


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    path = sys.argv[1]
    errs = check(path)
    print(f"=== check_genba_ref ｜ {path} ===")
    for e in errs:
        print("  NG   " + e)
    if errs:
        print("  → 04 の根拠が現場メモの行と合うまで、③を起動しない")
        sys.exit(1)
    print("  OK   04 の根拠は、現場メモの【役割】の行を引いていて、役割数も合っています")
    sys.exit(0)


if __name__ == "__main__":
    main()
