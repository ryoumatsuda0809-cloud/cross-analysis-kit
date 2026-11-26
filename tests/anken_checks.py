"""案件の出力（04〜07・現場メモ）の形を検査する B1〜B33（段5。移行台帳 §3-2 B。B15〜B33 は移行後の延長）。

★返すのは「ファイル:行 ルール名」だけ。本文は1文字も返さない（移行台帳 §1 ルール5）。
  05 には 03 の引用が入っている。テストが落ちたときに画面へ出すと、それが封の漏れになる。
★封（*_封.md）は開かない。読むのは 04・05・06・07・現場メモだけ。
★ここは「形」だけを見る。中身の良し悪し（分析の質）は見ない（§3-3 G・H）。
★ルールの原本はテンプレと SKILL。ここはその写しではなく、書かれた出力がテンプレの必須欄を埋めているかの検査。
"""
import os
import re

FIXED_TAGS = {"#市場", "#現場オペ", "#財務", "#組織", "#DX"}
CHECKED = re.compile(r"\[[xX]\]|☑|✅|■|✓|✔")
PLACEHOLDER = re.compile(r"\{[^}]{2,}\}")
COMMENT = re.compile(r"<!--.*?-->", re.S)

F04 = "04_現場分析.md"
F05 = "05_反証レポート.md"
F06 = "06_課題仮説レポート.md"
F07 = "07_主任診断士への申し送り.md"
MEMO = os.path.join("_材料", "B_現場", "現場メモ.md")


def _read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def _blank_comments(src):
    """内部メモを空行にする（行番号を保つ）。"""
    return COMMENT.sub(lambda m: "\n" * m.group(0).count("\n"), src)


def section(src, num):
    """「## N. …」から次の「## 」まで。返り値は [(行番号, 行)]。無ければ None。"""
    lines = src.splitlines()
    start = None
    for i, l in enumerate(lines):
        if start is None:
            if re.match(rf"^##\s+§?{re.escape(num)}\.\s", l):
                start = i
        elif re.match(r"^##\s", l):
            return [(j + 1, lines[j]) for j in range(start, i)]
    return None if start is None else [(j + 1, lines[j]) for j in range(start, len(lines))]


def section_named(src, key):
    """見出しに key を含む「## 」節（番号は問わない。テンプレの改番に強い）。"""
    lines = src.splitlines()
    for i, l in enumerate(lines):
        if re.match(r"^##\s", l) and key in l:
            j = next((k for k in range(i + 1, len(lines)) if re.match(r"^##\s", lines[k])), len(lines))
            return [(k + 1, lines[k]) for k in range(i, j)]
    return None


def tables(numbered):
    """[(行番号, 行)] から表を切り出す。表 = [(行番号, [セル…])]、先頭が見出し行。区切り行は除く。"""
    out, cur = [], []
    for n, l in numbered:
        s = l.strip()
        if s.startswith("|") and s.endswith("|"):
            if re.match(r"^\|[\s:|-]+\|$", s):
                continue
            cur.append((n, [c.strip() for c in s[1:-1].split("|")]))
        elif cur:
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    return out


def col(table, *keys):
    head = table[0][1]
    for i, h in enumerate(head):
        if all(k in h for k in keys):
            return i
    return None


def rows(table):
    """見出しを除き、中身のある行だけ（テンプレの空行は数えない）。
    先頭列が「#」（通し番号）の表は、番号だけ入った行も空行とみなす。"""
    skip = 1 if table[0][1] and table[0][1][0].strip() == "#" else 0
    return [(n, c) for n, c in table[1:] if any(x.replace("*", "").strip() for x in c[skip:])]


def cell(cells, i):
    return cells[i] if i is not None and i < len(cells) else ""


def _v(fname, line, rule):
    return f"{fname}:{line} {rule}"


def _is_template_choice(v, *opts):
    """テンプレの選択肢がそのまま残っている（「強／中／弱」など、候補が2つ以上並んだまま）。"""
    return sum(1 for o in opts if o in v) >= 2


# ── 04 ─────────────────────────────────────────────


def b1_04_independence(src):
    """B1：§0 独立性の宣言が書かれている（チェックが入り、{日付} などが残っていない）。"""
    sec = section_named(src, "独立性")
    if sec is None:
        return [_v(F04, 1, "B1 独立性の宣言の節が無い")]
    body = [(n, l) for n, l in sec[1:] if l.strip() and not l.lstrip().startswith(">")]
    out = []
    if not any(CHECKED.search(l) for _, l in body):
        out.append(_v(F04, sec[0][0], "B1 §0 にチェックが1つも入っていない"))
    for n, l in body:
        if PLACEHOLDER.search(l):
            out.append(_v(F04, n, "B1 §0 に未記入の欄"))
    return out


def b2_04_states(src):
    """B2：ベンチマーク表の「状態」、ズレ表の「同じものを測っているか」に空欄・選択肢の残りが無い。"""
    out = []
    for t in tables([(i + 1, l) for i, l in enumerate(src.splitlines())]):
        i = col(t, "状態")
        if i is not None and col(t, "ベンチマーク") is not None:
            for n, c in rows(t):
                v = cell(c, i)
                if not v.replace("*", "").strip() or _is_template_choice(v, "比較できた", "比較不能", "片側欠測"):
                    out.append(_v(F04, n, "B2 ベンチマーク表の「状態」が空"))
        j = col(t, "同じものを測っているか")
        if j is not None:
            for n, c in rows(t):
                v = cell(c, j)
                # 選択肢の残りは「はい／いいえ」と並んだ形だけ。「いいえ（並べてはいけない）」の「てはい」を「はい」と読まない（#57）
                if not v.replace("*", "").strip() or re.search(r"はい\s*[／/]\s*いいえ", v.replace("*", "")):
                    out.append(_v(F04, n, "B2 ズレ表の「同じものを測っているか」が空"))
    return out


def b3_04_strength(src):
    """B3：真因の芽に強度（強・中・弱のどれか1つ）と情報源の役割数（数字）がある。"""
    sec = section(src, "1")
    if sec is None:
        return [_v(F04, 1, "B3 §1 真因の芽リストが無い")]
    out = []
    for t in tables(sec):
        si, ri = col(t, "強度"), col(t, "役割数")
        if si is None:
            continue
        if ri is None:
            out.append(_v(F04, t[0][0], "B3 真因の芽の表に「情報源の役割数」列が無い"))
        for n, c in rows(t):
            # 括弧から先は注記（「中（定義上は「強」も成り立つ → §6）」）。値は括弧の前だけで見る
            s = re.split(r"[（(]", cell(c, si).replace("*", ""), maxsplit=1)[0]
            if sum(1 for k in "強中弱" if k in s) != 1:
                out.append(_v(F04, n, "B3 強度が「強／中／弱」の1つになっていない"))
            # 「不明」も書かれた値（CLAUDE.md §4-2「不明は不明と書く。推測で埋めない」。話者の無い記述では数えられない → #57）
            if ri is not None and not re.search(r"\d|[一二三四五六七八九十]|不明", cell(c, ri)):
                out.append(_v(F04, n, "B3 情報源の役割数が書かれていない"))
    return out


# ── 05 ─────────────────────────────────────────────


def _template_cells(rel, key):
    """テンプレの表の2列目（行の見出し → 既定の文言）。未記入の判定に使う。"""
    here = os.path.dirname(os.path.abspath(__file__))
    t = _read(os.path.join(here, "..", ".claude", "skills", rel))
    sec = section_named(t, key) or []
    return {c[0]: c[1] for tb in tables(sec) for _, c in tb[1:] if len(c) > 1}


def b4_05_opening(src):
    """B4：§0 開封記録の各行が埋まっている（空欄・☐ だけの行が無い）。"""
    sec = section(src, "0")
    if sec is None:
        return [_v(F05, 1, "B4 §0 開封記録が無い")]
    tmpl = _template_cells(os.path.join("shinin-hansho", "assets", "05-hansho-template.md"), "開封記録")
    out = []
    for t in tables(sec):
        for n, c in t[1:]:
            v = cell(c, 1)
            if not v.strip():
                out.append(_v(F05, n, "B4 §0 開封記録に空欄"))
            elif v.count("☐") >= 2 and not CHECKED.search(v):   # テンプレの選択肢が並んだまま。☐1つ＋説明は意図した記録
                out.append(_v(F05, n, "B4 §0 開封記録の選択肢が選ばれていない"))
            elif "☐" in v and v == tmpl.get(c[0]):             # ☐1つでもテンプレの文言のまま（「順序は正しいか」）
                out.append(_v(F05, n, "B4 §0 開封記録がテンプレの文言のまま"))
    return out


def _sec4_rows(src):
    sec = section(src, "4")
    if sec is None:
        return None
    for t in tables(sec):
        qi, di = col(t, "問い"), col(t, "行き先")
        if qi is not None and di is not None:
            return [(n, cell(c, qi), cell(c, di)) for n, c in rows(t)]
    return []


def b5_05_destination(src):
    """B5：§4 の全問いの「行き先」が 顧客可／社内のみ のどちらか1つ。"""
    r = _sec4_rows(src)
    if r is None:
        return [_v(F05, 1, "B5 §4 決定的な問いが無い")]
    if not r:   # 表が無い／「行き先」列が無い（箇条書きの問いは行き先を検査できない）
        return [_v(F05, section(src, "4")[0][0], "B5 §4 に「行き先」列つきの問いの表が無い")]
    out = []
    for n, _, d in r:
        if ("顧客可" in d) == ("社内のみ" in d):
            out.append(_v(F05, n, "B5 §4 の問いの行き先が「顧客可／社内のみ」の1つになっていない"))
    return out


def b6_05_new_hypotheses(src):
    """B6：「③が新しく作った仮説の申告」節が空でない（無ければ「なし」と書く）。節は名前で探す。"""
    sec = section_named(src, "新しく作った仮説")
    if sec is None:
        return [_v(F05, 1, "B6 「③が新しく作った仮説の申告」の節が無い")]
    for t in tables(sec):
        i = col(t, "解釈")
        if i is not None and any(cell(c, i).replace("*", "").strip() for _, c in rows(t)):
            return []
    # 「なし」は表の外の行だけで探す（対抗仮説の欄の「なし」を申告なしと読まない）
    text = "\n".join(l for _, l in sec[1:] if not l.lstrip().startswith((">", "|")))
    if re.search(r"(該当|申告)?なし|ありません", text.replace("該当なしの場合も「なし」と書く", "")):
        return []
    return [_v(F05, sec[0][0], "B6 新規仮説の申告が空（該当なしなら「なし」と書く）")]


def _norm(s):
    return re.sub(r"[\s*`「」『』。、？?！!]", "", s)


def b7_internal_questions_not_in_06(src05, src06):
    """B7：05 §4 の「社内のみ」の問いが 06 本文に載っていない（6-29）。言い換えられたものは捕まえられない（下限の検査）。"""
    r = _sec4_rows(src05) or []
    body = _norm(_blank_comments(src06))
    out = []
    for n, q, d in r:
        if "社内のみ" in d and "顧客可" not in d:
            k = _norm(q)
            if len(k) >= 8 and k in body:
                out.append(_v(F06, "-", f"B7 05:{n} の「社内のみ」の問いが 06 本文にそのまま載っている"))
    return out


def b11_05_human_section(src):
    """B11：「人間の判断が必要な論点」が 05 の独立した節になっている（3-44。CHECK #68）。
    見出しは「人間」で探す（Z10 の前の版は「人間（主任診断士）への引き渡し」）。"""
    if section_named(src, "人間") is None:
        return [_v(F05, 1, "B11 「人間の判断が必要な論点」の節が無い")]
    return []


TEST_MARKS = "⓪①②③④⑤⑥"


def b12_05_rejection_reason(src):
    """B12：§3 判定表で棄却した行に「落ちたテスト」が書いてある（テンプレの7本の並びのままは未記入。CHECK #69）。"""
    out = []
    for t in tables(section_named(src, "判定表") or []):
        ji, fi = col(t, "判定"), col(t, "落ちたテスト")
        if ji is None or fi is None:
            continue
        for n, c in rows(t):
            v = cell(c, ji)
            if "棄却" not in v or _is_template_choice(v, "採用", "要検証", "棄却", "判定不能"):
                continue
            f = cell(c, fi).replace("*", "").strip()
            if not f or sum(1 for k in TEST_MARKS if k in f) == len(TEST_MARKS):
                out.append(_v(F05, n, "B12 棄却した仮説に「落ちたテスト」（理由）が無い"))
    return out


def _sec9(src):
    """05「比べていないもの」節：(節があるか, 中身のある行数, 「なし」と書いたか)。
    テンプレの行（先頭列が空・「例：」）は数えない。"""
    sec = section_named(src, "比べていないもの")
    if sec is None:
        return False, 0, False
    n = 0
    for t in tables(sec):
        for _, c in rows(t):
            first = c[0].replace("*", "").strip() if c else ""
            if first and not first.startswith("例"):
                n += 1
    text = "\n".join(l for _, l in sec[1:] if not l.lstrip().startswith((">", "|")))
    nashi = bool(re.search(r"(該当|比べていないものは)?なし|ありません", text.replace("該当なしの場合も「なし」と書く", "")))
    return True, n, nashi


def b13_05_not_compared(src):
    """B13：「比べていないもの」節が埋まっている（無ければ「なし」と書く。CHECK #70）。"""
    has, n, nashi = _sec9(src)
    if not has:
        return [_v(F05, 1, "B13 「比べていないもの」の節が無い")]
    if not n and not nashi:
        return [_v(F05, section_named(src, "比べていないもの")[0][0], "B13 「比べていないもの」が空（該当なしなら「なし」と書く）")]
    return []


def b14_limits_in_06(src05, src06):
    """B14：05 に比べていないものがあれば、06 の「限界」の節が空でない（CHECK #83）。"""
    if not _sec9(src05)[1]:
        return []
    sec = section_named(_blank_comments(src06), "限界")
    body = [l for _, l in (sec or [])[1:] if l.strip() and not l.startswith("#")]
    if not body:
        return [_v(F06, (sec or [(1, "")])[0][0], "B14 05 に比べていないものがあるのに 06 の「限界」が空")]
    return []


# ── 06・07・現場メモ ─────────────────────────────────


def _where(memo_src):
    # ★太字の欄名（テンプレは `| **どこで** | 値 | 書き方 |`）を許し、2列目だけを取る（点検で発見。3列目の説明文の「現地」を拾っていた）
    m = re.search(r"^\|\s*\**どこで[^|]*\|\s*([^|]*?)\s*\|", memo_src, re.M)
    return m.group(1) if m else None


def on_site(where):
    """「どこで」欄に、否定されていない「現地」があるか。
    ★「現地」を含むかだけでは決めない：案件Dは「遠隔…、現地には…ない」と書いてあり、含むかで見ると
      観察ありと読み違える。★最初の語でも決めない：テンプレは「両方なら両方書く」ので
      「遠隔…、現地（工場見学）」は観察あり（移行台帳 §8・09-26）。"""
    for m in re.finditer("現地", where):
        tail = re.split(r"[、。,，／/）)]", where[m.end():], maxsplit=1)[0][:12]
        if not re.search(r"ない|なし|無し|未|せず|不可", tail):
            return True
    return False


def b8_observation_zero(memo_src, src06):
    """B8：現場メモの「どこで」が現地でない（観察ゼロ）なら、06 は観察ゼロの型（tougou-report 出力仕様(0)）。"""
    w = _where(memo_src)
    if w is None or on_site(w):
        return []
    body = _blank_comments(src06)
    out = []
    first = next(((i + 1, l) for i, l in enumerate(body.splitlines()) if l.startswith("# ")), None)
    if first and "課題仮説レポート" in first[1]:
        out.append(_v(F06, first[0], "B8 観察ゼロなのに文書名が「課題仮説レポート」"))
    for i, l in enumerate(body.splitlines(), 1):
        if re.match(r"^#{1,3}\s", l) and "見えてきた本質的な課題" in l:
            out.append(_v(F06, i, "B8 観察ゼロなのに見出しが「見えてきた本質的な課題」"))
        if re.search(r"課題である(?![とか])", l):   # 「課題であると断定する段階ではない」は出力仕様(0)に沿った書き方
            out.append(_v(F06, i, "B8 観察ゼロなのに「課題である」と書いている"))
    # 09-28：出力仕様(0)の決まり文句（tougou-report #500・CHECK #77）。言い回しの細部と問いの並べ順は人が見る
    sec = _issue_section(body)
    if sec and not any("断定ではなく" in l for _, l in _text_lines(sec)[:2]):
        out.append(_v(F06, sec[0][0], "B8 観察ゼロなのに課題の節の冒頭に「断定ではなく…という段階」が無い"))
    if not re.search(r"拝見して(いない|いません|おりません)|見て確かめたもの", body):   # 06 は敬体
        out.append(_v(F06, 1, "B8 観察ゼロなのに「現場を拝見していない／見て確かめたものは含まれていない」が無い"))
    if "訪問" in body and "機会をいただける" not in body:
        out.append(_v(F06, 1, "B8 観察ゼロなのに訪問を「機会をいただけるのであれば」と書いていない"))
    return out


def _count_sec8(src05):
    sec = section(src05, "8")
    if not sec:
        return 0
    for t in tables(sec):
        i = col(t, "論点")
        if i is not None:
            return sum(1 for _, c in rows(t) if cell(c, i).replace("*", "").strip())
    return 0


def _count_07(src07):
    sec = section(src07, "1")
    if not sec:
        return 0
    return sum(len([r for r in rows(t) if any(x.replace("*", "").strip() for x in r[1][1:])]) for t in tables(sec))


def b9_07_exists_and_complete(anken, src05):
    """B9：06 があれば 07 もある。05 §8 の論点数 ≤ 07 §1 の転記数（3-44）。"""
    if not os.path.exists(os.path.join(anken, F06)):
        return []
    p07 = os.path.join(anken, F07)
    if not os.path.exists(p07):
        return [_v(F07, "-", "B9 06 があるのに 07 が無い")]
    if src05 is None:
        return []
    n5, n7 = _count_sec8(src05), _count_07(_read(p07))
    if n5 > n7:
        return [_v(F07, "-", f"B9 05 §8 の論点 {n5} 件に対し 07 §1 の転記が {n7} 件")]
    return []


def b10_tags(fname, src):
    """B10：タグ列のタグが固定の5つだけ。"""
    out = []
    for t in tables([(i + 1, l) for i, l in enumerate(src.splitlines())]):
        i = col(t, "タグ")
        if i is None:
            continue
        for n, c in rows(t):
            for tag in re.findall(r"#[^\s`|、,／/・。（）()]+", cell(c, i)):
                if tag not in FIXED_TAGS:
                    out.append(_v(fname, n, "B10 固定リストに無いタグ"))
    return out


# ── B15〜B22：節の有無と件数の突き合わせ（移行後の B 群の延長。仕分け表_SKILL.md の M の未） ──


JUDGES = ("判定不能", "要検証", "採用", "棄却")   # 「判定不能」を先に見る（「判定」だけの語と混ぜない）


def _judge(v):
    """セルの判定語。いちばん先に出てくるものを取る（「採用（要検証寄り）」は採用）。選択肢が並んだままなら None。"""
    v = v.replace("*", "")
    if sum(1 for k in JUDGES if k in v) >= 3:   # テンプレの「採用/要検証/棄却/判定不能」が残っている（2語なら注記つきの判定）
        return None
    hits = [(v.find(k), k) for k in JUDGES if k in v]
    if not hits:
        return None
    first = min(i for i, _ in hits)
    return next(k for i, k in sorted(hits, key=lambda x: (x[0], -len(x[1]))) if i == first)


def _col_exact(table, name):
    for i, h in enumerate(table[0][1]):
        if h.replace("*", "").strip() == name:
            return i
    return None


def _text_lines(sec):
    """節の中の本文行（見出し・引用・表・空行・中身の無い箇条書き・{…} だけの行を除く）。"""
    out = []
    for n, l in (sec or [])[1:]:
        s = l.strip()
        if not s or s.startswith(("#", ">", "|")) or re.fullmatch(r"(-|\*|\d+\.)\s*", s) or s == "---":
            continue
        if not PLACEHOLDER.sub("", s).strip(" -*（）()"):
            continue
        out.append((n, s))
    return out


def _filled_rows(sec):
    """節の中の表で、先頭列（見出し・通し番号）以外に中身がある行。"""
    out = []
    for t in tables(sec or []):
        for n, c in t[1:]:
            if any(PLACEHOLDER.sub("", x).replace("*", "").strip() for x in c[1:]):
                out.append((n, c))
    return out


def b15_04_sections(src):
    """B15：04 に「人間が現場で確認すべき点」と「カバレッジ」の節があり、空でない（genba-ops #187・#188）。
    カバレッジは「問い番号」列に1つでも番号があるか、「02 なし」と書いてあれば埋まっている（テンプレの ✓／△／✗ だけでは埋まっていない）。"""
    out = []
    sec = section_named(src, "確認すべき点")
    if sec is None:
        out.append(_v(F04, 1, "B15 「人間が現場で確認すべき点」の節が無い"))
    elif not _text_lines(sec) and not _filled_rows(sec):
        out.append(_v(F04, sec[0][0], "B15 「人間が現場で確認すべき点」が空"))
    sec = section_named(src, "カバレッジ")
    if sec is None:
        out.append(_v(F04, 1, "B15 「カバレッジ」の節が無い"))
    else:
        body = "\n".join(l for _, l in sec[1:] if not l.lstrip().startswith(">"))
        numbered = any(cell(c, col(t, "問い番号")).replace("*", "").strip()
                       for t in tables(sec) if col(t, "問い番号") is not None for _, c in rows(t))
        if not numbered and not re.search(r"`?02`?\s*なし", body):
            out.append(_v(F04, sec[0][0], "B15 「カバレッジ」が空（02 が無ければ「02 なし」と書く）"))
    return out


F05_SECTIONS = [("クロス表", "§1 クロス表"), ("反証サマリー", "§2 反証サマリー"), ("判定表", "§3 判定表"),
                ("頼りすぎ", "§5 AIに頼りすぎ注意"), ("02b", "§7 02b との突き合わせ")]


CROSS_COLS = ("03", "04", "結論", "機序", "解釈")


def _has_body(sec):
    """本文行があるか、先頭列が埋まった表の行があるか（テンプレの「あり／なし」だけの行は数えない）。"""
    return bool(_text_lines(sec)) or any(c and c[0].replace("*", "").strip() for t in tables(sec or []) for _, c in rows(t))


def b16_05_sections(src):
    """B16：05 に §1・§2・§3・§5・§7 の節がある（shinin-hansho #404〜#411。名前で探す）。
    §1 は列（03・04・結論・機序・解釈）、§3 は「前提が崩れた仮説」の専用表（### の名前は「前提が崩れた」か「Stage 2-0」）、§5・§7 は中身（該当なしなら「なし」と書く）まで見る。"""
    heads = [l for l in src.splitlines() if re.match(r"^##\s", l)]
    out = [_v(F05, 1, f"B16 「{label}」の節が無い") for key, label in F05_SECTIONS
           if not any(key in h for h in heads)]
    sec = section_named(src, "クロス表")
    if sec and not any(all(col(t, k) is not None for k in CROSS_COLS) for t in tables(sec)):
        out.append(_v(F05, sec[0][0], "B16 §1 クロス表に 03・04・結論・機序・解釈 の列が揃っていない"))
    sec = section_named(src, "判定表")
    if sec and not any(re.match(r"^###\s", l) and ("前提が崩れた" in l or "Stage 2-0" in l) for _, l in sec):
        out.append(_v(F05, sec[0][0], "B16 §3 に「前提が崩れた仮説」の専用表（###）が無い"))
    for key, label in (("頼りすぎ", "§5 AIに頼りすぎ注意"), ("02b", "§7 02b との突き合わせ")):
        sec = next((section_named(src, h[3:]) for h in heads if key in h), None)
        if sec and not _has_body(sec):
            out.append(_v(F05, sec[0][0], f"B16 「{label}」が空（該当なしなら「なし」と書く）"))
    return out


def _judgements(src):
    """§3 判定表の判定の件数 {判定: 件数}。最初の判定表だけを数える
    （「### 前提が崩れた仮説」の表にも「判定」「仮説」の列があり、数えると二重になる。案件D で実際に起きた）。"""
    got = {k: 0 for k in JUDGES}
    for t in tables(section_named(src, "判定表") or []):
        ji = _col_exact(t, "判定")
        if ji is None or col(t, "仮説") is None:
            continue
        for _, c in rows(t):
            j = _judge(cell(c, ji))
            if j:
                got[j] += 1
        break
    return got


def b17_05_summary_matches(src):
    """B17：§2 反証サマリーの件数が §3 判定表の判定の数と合う（shinin-hansho #405）。"""
    sec = section_named(src, "反証サマリー")
    if sec is None:
        return []   # 節の有無は B16
    said, line = {}, sec[0][0]
    for t in tables(sec):
        ci = col(t, "件数")
        if ci is None:
            continue
        for n, c in t[1:]:
            j = _judge(c[0]) if c else None
            m = re.search(r"\d+", cell(c, ci))
            if j and m:
                said[j] = int(m.group(0))
    if not said:
        return [_v(F05, line, "B17 §2 反証サマリーの件数が空")]
    missing = [k for k in JUDGES if k not in said]
    if missing:   # 4つ全部を並べる（採用 n／要検証 n／棄却 n／判定不能 n）。欠けた行を 0 件と読まない
        return [_v(F05, line, f"B17 §2 に「{k}」の件数が無い") for k in missing]
    got = _judgements(src)
    bad = [k for k in JUDGES if said.get(k, 0) != got[k]]
    return [_v(F05, line, f"B17 §2 の「{k}」{said.get(k, 0)} 件が §3 の判定 {got[k]} 件と合わない") for k in bad]


def b18_05_no_self_approval(src):
    """B18：§6「③が新しく作った仮説」を③が「採用」にしていない（shinin-hansho #426：自分の推論を自分で承認しない）。"""
    out = []
    for t in tables(section_named(src, "新しく作った仮説") or []):
        ji, ii = _col_exact(t, "判定"), col(t, "解釈")
        if ji is None or ii is None:
            continue
        for n, c in rows(t):
            if cell(c, ii).replace("*", "").strip() and _judge(cell(c, ji)) == "採用":
                out.append(_v(F05, n, "B18 ③が作った仮説を③自身が「採用」にしている"))
    return out


def _issue_section(src06):
    return section_named(src06, "見えてきた本質的な課題") or section_named(src06, "お話から見えてきたこと")


def b19_06_sections(src06):
    """B19：06 にエグゼクティブサマリー・御社の現状・課題の節・出典があり、空でない（tougou-report #483・#487〜#489・#502）。
    課題の節の名前は観察の有無で変わる（出力仕様(0)）。"""
    body = _blank_comments(src06)
    out = []
    for key in ("エグゼクティブサマリー", "御社の現状", "出典"):
        sec = section_named(body, key)
        if sec is None:
            out.append(_v(F06, 1, f"B19 「{key}」の節が無い"))
        elif not _text_lines(sec) and not _filled_rows(sec):
            out.append(_v(F06, sec[0][0], f"B19 「{key}」が空"))
        elif key == "エグゼクティブサマリー" and len(_text_lines(sec)) > 3:   # 3行で突く（#487）
            out.append(_v(F06, sec[0][0], f"B19 エグゼクティブサマリーが {len(_text_lines(sec))} 行（3行以内）"))
    sec = _issue_section(body)
    if sec is None:
        out.append(_v(F06, 1, "B19 課題の節（見えてきた本質的な課題／お話から見えてきたこと）が無い"))
    elif not _text_lines(sec):
        out.append(_v(F06, sec[0][0], "B19 課題の節が空（単一ソースでも空にしない）"))
    return out


def _issue_heads(sec):
    return [(n, l) for n, l in (sec or [])[1:] if re.match(r"^###\s", l)]


def b20_06_at_most_three(src06):
    """B20：課題の見出し（課題の節の ###）が3つ以下（tougou-report #456）。"""
    heads = _issue_heads(_issue_section(_blank_comments(src06)))
    if len(heads) > 3:
        return [_v(F06, heads[3][0], f"B20 課題の見出しが {len(heads)} 個（3つまで。超えたら束ねる）")]
    return []


def b21_06_evidence_table(src06):
    """B21：課題が2つ以上なら、課題の節に根拠の種類の表（列：異なっていた点／数字／まだ決めていないこと）がある（tougou-report #467・#468）。"""
    sec = _issue_section(_blank_comments(src06))
    if len(_issue_heads(sec)) < 2:
        return []
    first = _issue_heads(sec)[0][0]
    for t in tables(sec):
        if all(col(t, k) is not None for k in ("異なっていた", "数字", "決めていない")):
            if t[0][0] < first:
                return []
            return [_v(F06, t[0][0], "B21 根拠の種類の表が課題の見出しより後にある（見出しの前に置く）")]
    return [_v(F06, sec[0][0], "B21 課題が2つ以上なのに根拠の種類の表（3列）が無い")]


def _count_05_sec6(src05):
    return sum(1 for t in tables(section_named(src05, "新しく作った仮説") or []) if col(t, "解釈") is not None
               for _, c in rows(t) if cell(c, col(t, "解釈")).replace("*", "").strip())


def _count_05_internal(src05):
    return sum(1 for _, _, d in (_sec4_rows(src05) or []) if "社内のみ" in d and "顧客可" not in d)


def _count_07_sec(src07, num):
    return len(_filled_rows(section(src07, num)))


def b22_07_transfers(anken, src05):
    """B22：05 §6 の新仮説の件数 ≤ 07 §3 の転記数、05 §4 の「社内のみ」の件数 ≤ 07 §4 の転記数
    （tougou-report #550・shinin-hansho #419。B9 と同じ形）。"""
    p07 = os.path.join(anken, F07)
    if src05 is None or not os.path.exists(p07):
        return []   # 07 が無いことは B9
    s07 = _read(p07)
    out = []
    for n5, num, label in ((_count_05_sec6(src05), "3", "05 §6 の新仮説"), (_count_05_internal(src05), "4", "05 §4 の「社内のみ」の問い")):
        n7 = _count_07_sec(s07, num)
        if n5 > n7:
            out.append(_v(F07, "-", f"B22 {label} {n5} 件に対し 07 §{num} の転記が {n7} 件"))
    return out


ISSUE_ITEMS = ("何が起きているか", "なぜか", "根拠", "放置すると")


def b23_06_issue_items(src06):
    """B23：各課題（課題の節の ###）に4項目「何が起きているか／なぜか（仮説）／根拠／放置するとどうなるか」がある（tougou-report #489）。"""
    sec = _issue_section(_blank_comments(src06)) or []
    heads = _issue_heads(sec)
    out = []
    for k, (n, _) in enumerate(heads):
        end = heads[k + 1][0] if k + 1 < len(heads) else sec[-1][0] + 1
        text = "\n".join(l for m, l in sec if n < m < end)
        for item in ISSUE_ITEMS:
            if item not in text:
                out.append(_v(F06, n, f"B23 課題に「{item}」の項目が無い"))
    return out


def b24_07_counter_hypothesis(anken):
    """B24：07 §3（③が新しく作った仮説）の各行に対抗仮説がある（tougou-report #550「その対抗仮説」）。"""
    p07 = os.path.join(anken, F07)
    if not os.path.exists(p07):
        return []
    out = []
    for t in tables(section(_read(p07), "3") or []):
        ii, ci = col(t, "解釈"), col(t, "対抗")
        if ii is None or ci is None:
            continue
        for n, c in rows(t):
            if cell(c, ii).replace("*", "").strip() and not cell(c, ci).replace("*", "").strip():
                out.append(_v(F07, n, "B24 ③が作った仮説に対抗仮説が無い"))
    return out


ISSUE_ALIASES = ("見えてきた本質的な課題", "お話から見えてきたこと")   # 観察の有無で名前が変わる（出力仕様(0)）


def template_heads_06():
    """06 のテンプレ（report-template.md）の「## 」見出し。括弧から先は除く。テンプレが変われば検査も追う。"""
    here = os.path.dirname(os.path.abspath(__file__))
    t = _read(os.path.join(here, "..", ".claude", "skills", "tougou-report", "assets", "report-template.md"))
    return [re.split(r"[（(]", l[3:], maxsplit=1)[0].strip() for l in t.splitlines() if l.startswith("## ")]


def b25_06_matches_template(src06):
    """B25：06 がテンプレの「## 」見出しを全部持つ（tougou-report #505「必ずテンプレと節を照合する」）。
    テンプレの見出しを毎回読むので、テンプレに節が足されたら古い 06 はここで落ちる。"""
    heads = [l for l in _blank_comments(src06).splitlines() if l.startswith("## ")]
    out = []
    for key in template_heads_06():
        keys = ISSUE_ALIASES if key in ISSUE_ALIASES else (key,)
        if not any(k in h for h in heads for k in keys):
            out.append(_v(F06, 1, f"B25 テンプレの節「{key}」が無い"))
    # 「はじめに」は冒頭（最初の ## 節）に置く（tougou-report #525a）
    if heads and any("はじめに" in h for h in heads) and "はじめに" not in heads[0]:
        out.append(_v(F06, 1, "B25 「はじめに」が冒頭（最初の ## 節）に無い"))
    return out


# ── B26〜B28：05 の形（shinin-hansho #436・#379・#417。仕分け表_SKILL.md の M の未） ──


def _says_no_04(src):
    """「現場側が無い状態での格付け」の明記（shinin-hansho #364）：その語があるか、§0 の「04 の有無」で「なし」を選んでいる。"""
    if re.search(r"現場側が(無|な)い", _blank_comments(src)):
        return True
    for t in tables(section(src, "0") or []):
        for _, c in t[1:]:
            if "04" in c[0] and "有無" in c[0]:
                v = cell(c, 1)
                if re.search(rf"(?:{CHECKED.pattern})\s*\**\s*なし", v) or ("☐" not in v and "なし" in v):
                    return True
    return False


def b26_05_no_adopt_without_04(src):
    """B26：04 が無い案件の 05。「採用」を出していない（shinin-hansho #436。§3 判定表で数える。§2 との一致は B17）、
    「現場側が無い状態での格付け」であることを明記している（#364）。"""
    out = []
    sec = section_named(src, "判定表")
    if sec and _judgements(src)["採用"]:
        out.append(_v(F05, sec[0][0], "B26 04 が無いのに §3 で「採用」を出している"))
    if not _says_no_04(src):
        out.append(_v(F05, 1, "B26 04 が無いのに「現場側が無い状態での格付け」の明記が無い"))
    return out


def b27_05_cross_03_column(src):
    """B27：§1 クロス表の 03 列が空でない。B軸のみの行は「（①には無い）」と書く（shinin-hansho #379）。
    表記の揺れ（「①には〜無い」など）は通す：「①」と「には無い／にはない」があればよい。"""
    out = []
    for t in tables(section_named(src, "クロス表") or []):
        i3, ic = col(t, "03"), col(t, "結論")
        if i3 is None or ic is None:
            continue
        for n, c in rows(t):
            v = PLACEHOLDER.sub("", cell(c, i3)).replace("*", "").strip()
            if not v:
                out.append(_v(F05, n, "B27 §1 の 03 列が空（B軸のみは「（①には無い）」と書く）"))
            elif "B軸のみ" in cell(c, ic) and not ("①" in v and re.search(r"には(無|な)い", v)):
                out.append(_v(F05, n, "B27 §1 の B軸のみの行の 03 列に「（①には無い）」が無い"))
        break
    return out


NO_ORIGIN = ("③が作成", "02b")   # 元の番号が無い行（③が突き合わせから作った／人間の見立てにしかない）


def b29_05_cross_keeps_numbers(src):
    """B29：§1 クロス表の各行に元の番号が残っている（shinin-hansho #377。統合・分割しても追跡できるように）。
    中身のある側（03 列・04 列）に数字が1つはある。H・芽の頭の文字は問わない（04 §2 の「#3」を指す行もある）。
    見ない側：B軸のみの 03・A軸のみの 04（片側が無いのが定義）／③が作成・02b のみの行（元の番号が無い）／「②に該当なし」。"""
    out = []
    for t in tables(section_named(src, "クロス表") or []):
        i3, i4, ic = col(t, "03"), col(t, "04"), col(t, "結論")
        if None in (i3, i4, ic):
            continue
        for n, c in rows(t):
            a, b, k = cell(c, i3).replace("*", ""), cell(c, i4).replace("*", ""), cell(c, ic)
            if any(x in a for x in NO_ORIGIN):
                continue
            need = []
            if "B軸のみ" not in k and "①" not in a and PLACEHOLDER.sub("", a).strip():   # 空は B27
                need.append(("03", a))
            if "A軸のみ" not in k and not re.search(r"該当\s*なし", b):
                need.append(("04", b))
            for name, v in need:
                if not re.search(r"\d", PLACEHOLDER.sub("", v)):
                    out.append(_v(F05, n, f"B29 §1 の {name} 列に元の番号が無い（統合・分割しても番号を残す）"))
        break
    return out


# ── B30〜B33：入力が無いときの扱い（genba-ops #174・#177／tougou-report #448b・#459） ──

F01 = "01_外形カード_事実編.md"
F01I = "01i_外形カード_内部用.md"
F02 = "02_現場で確認すべき問い.md"


def b30_04_no_02(src04):
    """B30：02 が無い案件の 04 のカバレッジ欄に「02 なし」（genba-ops #174。空欄だと聞き漏らしと区別できない）。"""
    sec = section_named(_blank_comments(src04), "カバレッジ")
    if sec is None:
        return []   # 節の有無は B15
    if re.search(r"`?02`?\s*なし", "\n".join(l for _, l in sec)):
        return []
    return [_v(F04, sec[0][0], "B30 02 が無いのにカバレッジ欄に「02 なし」が無い")]


def b31_04_no_01(src04):
    """B31：01 も 01i も無い案件の 04（genba-ops #177）。ズレ一覧は作れない旨を本文に明記し、ズレ一覧に行を立てない（真因の芽だけ）。
    明記は「01 … 無い／ない／なし」の本文行があるか（引用・表・内部メモは数えない）。"""
    src = _blank_comments(src04)
    out = []
    if not any("01" in s and re.search(r"無い|ない|なし", s) for _, s in _text_lines([(0, "")] + list(enumerate(src.splitlines(), 1)))):
        out.append(_v(F04, 1, "B31 01 も 01i も無いのに、その旨（ズレ一覧は作れない）の明記が無い"))
    sec = section_named(src, "ズレ一覧")
    first = tables(sec or [])[:1]   # 建前の表だけ（「### 市場ベンチマークとのズレ」は別の表。狭い方の読み）
    filled = [(n, c) for t in first for n, c in t[1:] if any(PLACEHOLDER.sub("", x).replace("*", "").strip() for x in c[1:])]
    if filled:
        out.append(_v(F04, filled[0][0], "B31 01 も 01i も無いのに、ズレ一覧に行がある（比較対象が無い）"))
    return out


def b32_07_01i_substitute(anken):
    """B32：01i が無く 01 で代用した案件の 07 に、その残リスクが書いてある（tougou-report #448b）。
    「01i」と「代用／無い／ない／なし」が同じ行にあるか（内部メモは数えない）。"""
    p = os.path.join(anken, F07)
    if not os.path.exists(p):
        return []   # 07 の有無は B9
    if any("01i" in l and re.search(r"代用|無い|ない|なし", l) for l in _blank_comments(_read(p)).splitlines()):
        return []
    return [_v(F07, 1, "B32 01i が無く 01 で代用したのに、07 に残リスクとして書いていない")]


def b33_07_bundling_left_to_human(anken, src05):
    """B33：採用が3件を超えた（④が束ねる）案件の 07 §6 に「束ね方は本人が決める」（tougou-report #459）。
    「束ね」と「本人」が §6 の同じ行にあるか（本人が決めた後の記録もこの形になる）。"""
    p = os.path.join(anken, F07)
    if not os.path.exists(p) or _judgements(src05)["採用"] <= 3:
        return []
    sec = section(_blank_comments(_read(p)), "6")
    if sec and any("束ね" in l and "本人" in l for _, l in sec):
        return []
    return [_v(F07, sec[0][0] if sec else 1, "B33 採用が3件を超えたのに、07 §6 に「束ね方は本人が決める」が無い")]


HYP_ID = re.compile(r"H\d+[a-z]?|芽\s*\d+|N\d+")


def _hyp_ids(v, parent=False):
    """番号（H1・H1a・芽2・N1）。parent=True なら枝番 H1a を H1 としても数える
    （§3 側だけ。§4 が枝番を付けずに H1 と書いたとき、H1 の枝の判定を全部集めるため）。"""
    out = set()
    for m in HYP_ID.findall(v.replace("*", "")):
        m = re.sub(r"\s", "", m)
        out.add(m)
        if parent and re.fullmatch(r"H\d+[a-z]", m):
            out.add(m[:-1])
    return out


def b28_05_rejected_question_internal(src):
    """B28：棄却した仮説から出た §4 の問いの行き先が「社内のみ」（shinin-hansho #417）。
    機械で決まる場合だけを見る：§4 の出所の番号が全部、§3 で棄却の行にしか出てこないのに「顧客可」。
    分割（H4a 要検証・H4b 棄却）で出所が H4 のとき・採用と棄却の番号が混ざるときは判断（H）なので見ない。"""
    verdicts = {}
    for t in tables(section_named(src, "判定表") or []):
        ji, hi = _col_exact(t, "判定"), col(t, "仮説")
        if ji is None or hi is None:
            continue
        for _, c in rows(t):
            j = _judge(cell(c, ji))
            if j:
                for i in _hyp_ids(c[0], parent=True) | _hyp_ids(cell(c, hi), parent=True):
                    verdicts.setdefault(i, set()).add(j)
        break
    rejected = {i for i, s in verdicts.items() if s == {"棄却"}}
    out = []
    for t in tables(section(src, "4") or []):
        oi, di = col(t, "出所"), col(t, "行き先")
        if oi is None or di is None:
            continue
        for n, c in rows(t):
            ids = _hyp_ids(cell(c, oi))
            if ids and ids <= rejected and "顧客可" in cell(c, di):
                out.append(_v(F05, n, "B28 §4 の問いの出所が棄却した仮説だけなのに行き先が「顧客可」"))
        break
    return out


# ── B34〜B38：09-28 の再点検で「一部」に落とした行の、機械で見られる残り ──


DATE = re.compile(r"(20\d\d)[-/.](\d{1,2})[-/.](\d{1,2})(?:[\sT・]*(\d{1,2}):(\d{2}))?")


def _when(v):
    """セルの最初の日時 → (日付, 時刻 or None)。日付が無ければ None。「22:1x」のような時刻は日付だけで読む。"""
    m = DATE.search(v.replace("*", ""))
    if not m:
        return None
    d = tuple(int(x) for x in m.group(1, 2, 3))
    return d, (int(m.group(4)), int(m.group(5))) if m.group(4) else None


def _sec0_row(src, *keys):
    for t in tables(section(src, "0") or []):
        for n, c in t[1:]:
            h = c[0].replace("*", "").replace("`", "") if c else ""
            if all(k in h for k in keys):
                return n, cell(c, 1)
    return None


def b34_05_opening_order(src):
    """B34：§0 の「03 を開封した日時」が「04 を読んだ日時」より前でない（shinin-hansho #403a・CHECK #59）。
    両方に日付があれば日付で、両方に時刻もあれば時刻まで比べる。同じ日で時刻が片方にしか無いときは比べられないので通す。
    04 が無い案件（04 の行が「なし」）は 03 の行だけ見る。"""
    sec = section(src, "0")
    if sec is None:
        return []   # 節の有無は B4
    out = []
    r03 = _sec0_row(src, "03", "開封")
    if r03 is None:
        return [_v(F05, sec[0][0], "B34 §0 に「03 を開封した日時」の行が無い")]
    w03 = _when(r03[1])
    if w03 is None:
        out.append(_v(F05, r03[0], "B34 §0 の「03 を開封した日時」に日付が無い"))
    r04 = _sec0_row(src, "04", "読んだ")
    if r04 is None or re.search(r"なし|無い|ない", r04[1]) and _when(r04[1]) is None:
        return out   # 04 が無い案件。その旨の記載は B26
    w04 = _when(r04[1])
    if w04 is None:
        return out + [_v(F05, r04[0], "B34 §0 の「04 を読んだ日時」に日付が無い")]
    if w03 is None:
        return out
    (d4, t4), (d3, t3) = w04, w03
    if d3 < d4 or (d3 == d4 and t3 and t4 and t3 < t4):
        out.append(_v(F05, r03[0], "B34 §0 で 03 の開封が 04 を読むより前になっている"))
    return out


def _rejected_texts(src05):
    """§3 判定表（最初の表）で「棄却」の仮説の文言。番号（H1・芽2）と括弧の注記は外す。"""
    out = []
    for t in tables(section_named(src05, "判定表") or []):
        ji, hi = _col_exact(t, "判定"), col(t, "仮説")
        if ji is None or hi is None:
            continue
        for n, c in rows(t):
            if _judge(cell(c, ji)) == "棄却":
                v = re.sub(r"[（(][^）)]*[）)]", "", HYP_ID.sub("", cell(c, hi)))
                out.append((n, v))
        break
    return out


def b35_rejected_not_in_06(src05, src06):
    """B35：05 §3 で棄却した仮説の文言が 06 本文にそのまま載っていない（CHECK #75・#103／cross-run #121）。
    B7 と同じ下限の検査：言い換えたものは捕まえない。"""
    body = _norm(_blank_comments(src06))
    out = []
    for n, v in _rejected_texts(src05):
        k = _norm(v)
        if len(k) >= 8 and k in body:
            out.append(_v(F06, "-", f"B35 05:{n} で棄却した仮説が 06 本文にそのまま載っている"))
    return out


NOT_COMPARED = ("比較不能", "片側欠測")


def _count_04_not_compared(src04):
    """04 §2 の市場ベンチマークの表で、状態が比較不能・片側欠測の行の数（テンプレの選択肢のままは数えない）。"""
    n = 0
    for t in tables(section(src04, "2") or []):
        si = col(t, "状態")
        if si is None:
            continue
        for _, c in rows(t):
            v = cell(c, si)
            if any(k in v for k in NOT_COMPARED) and not _is_template_choice(v, "比較できた", *NOT_COMPARED):
                n += 1
    return n


def b36_05_takes_over_not_compared(src04, src05):
    """B36：04 §2 の比較不能・片側欠測が、05「比べていないもの」に1行ずつ引き継がれている（shinin-hansho #373b・#413）。
    「なし」で済ませていないか、行の数が 04 より少なくないかだけを見る。どの行がどれに対応するかは人が見る。"""
    k = _count_04_not_compared(src04)
    if not k:
        return []
    has, n, _ = _sec9(src05)
    if not has:
        return []   # 節の有無は B13
    if n < k:
        line = section_named(src05, "比べていないもの")[0][0]
        return [_v(F05, line, f"B36 04 §2 の比較不能・片側欠測 {k} 件に対し「比べていないもの」が {n} 行")]
    return []


IJOU_NASHI = re.compile(r"異常(?:は|が)?(?:なし|無し|ない|ありません|ございません|見られません|みられません|認められません|見当たりません)(?!か)")


def b37_06_no_ijou_nashi(src06):
    """B37：06 本文に「異常なし」と書いていない（tougou-report #473。内部メモは除く）。
    06 は敬体なので「異常はありません」などの形も見る。「異常がないか」（問い）は通す（09-29）。"""
    return [_v(F06, i + 1, "B37 06 に「異常なし」と書いている")
            for i, l in enumerate(_blank_comments(src06).splitlines()) if IJOU_NASHI.search(l.replace("*", ""))]


def b39_05_states_02b(src):
    """B39：§0 開封記録に 02b の有無が書いてある（shinin-hansho #358。テンプレ §0 に行は無いが SKILL が求める → 台帳 §8）。"""
    sec = section(src, "0")
    if sec is None or any("02b" in l for _, l in sec):
        return []   # 節の有無は B4
    return [_v(F05, sec[0][0], "B39 §0 に 02b の有無が無い")]


def _count_06_questions(src06):
    sec = section_named(_blank_comments(src06), "確かめたい問い") or []
    items = sum(1 for _, l in sec[1:] if re.match(r"^\s*(-|\*|\d+\.)\s+\S", l))
    return items + sum(len(rows(t)) for t in tables(sec))


def b40_06_all_customer_questions(src05, src06):
    """B40：05 §4 の「顧客可」の問いの数 ≤ 06「一緒に確かめたい問い」の数（tougou-report #513：全件載せる）。
    ④は言い換えるので文言では照合しない。件数の下限だけ。"""
    k = sum(1 for _, _, d in (_sec4_rows(src05) or []) if "顧客可" in d and "社内のみ" not in d)
    n = _count_06_questions(src06)
    return [_v(F06, "-", f"B40 05 §4 の顧客可 {k} 件に対し 06 の問いが {n} 件")] if n < k else []


def b41_06_no_grading(src06):
    """B41：06 に格付け（強・中・弱）を書いていない（tougou-report #469）。表のセルが強／中／弱だけのもの、「強度」「格付け」の語。"""
    body = _blank_comments(src06)
    out = [_v(F06, i + 1, "B41 06 に「強度」「格付け」と書いている")
           for i, l in enumerate(body.splitlines()) if re.search(r"強度|格付け", l)]
    for t in tables([(i + 1, l) for i, l in enumerate(body.splitlines())]):
        for n, c in t:
            if any(x.replace("*", "").strip() in ("強", "中", "弱") for x in c):
                out.append(_v(F06, n, "B41 06 の表に強・中・弱の格付け"))
    return out


PLAIN_END = re.compile(r"(である|だ|ない|た|だろう|る|う)。$")   # る・う（〜ている。〜と考える。〜と思う。）は 09-29
POLITE_END = re.compile(r"(ます|です|ません|でした|ました|ましょう|でしょう)。$")
QUOTE = re.compile(r"「[^」]*」")   # 「」の中は相手の言葉。文末の形を見ない（09-29）


def b42_06_polite_style(src06):
    """B42：06 は敬体・相手は「御社」・「可能性」を3文以上続けない（tougou-report #533）。
    表・見出し・引用・内部メモは見ない。断定語は check_report（ASSERTIVE）、言い切れる事実を言い切ったかは人。"""
    body = "\n".join(l for l in _blank_comments(src06).splitlines() if not l.lstrip().startswith(("|", "#", ">")))
    sents = [x.strip().replace("*", "") for x in re.split(r"(?<=。)", QUOTE.sub("「」", body)) if x.strip()]
    out = []
    if any(PLAIN_END.search(x) and not POLITE_END.search(x) for x in sents):
        out.append(_v(F06, "-", "B42 06 に常体の文（〜である。〜だ。）がある"))
    run = 0
    for x in sents:
        run = run + 1 if "可能性" in x else 0
        if run == 3:
            out.append(_v(F06, "-", "B42 06 で「可能性」が3文続いている"))
    if "貴社" in body:
        out.append(_v(F06, "-", "B42 06 で相手を「貴社」と呼んでいる（「御社」）"))
    return out


def b38_04_every_row_tagged(src):
    """B38：04 のタグ列のある表で、中身のある行のタグ列が空でない（genba-ops #182・#185a。タグの種類は B10）。"""
    out = []
    for t in tables([(i + 1, l) for i, l in enumerate(src.splitlines())]):
        i = col(t, "タグ")
        if i is None:
            continue
        for n, c in rows(t):
            if not re.search(r"#\S", cell(c, i)):
                out.append(_v(F04, n, "B38 タグ列が空の行"))
    return out


# ── まとめて ────────────────────────────────────────


def check_anken(anken):
    """1案件の出力を全部見る。返り値：違反の一覧（「ファイル:行 ルール名」だけ）。"""
    p = lambda f: os.path.join(anken, f)
    s04 = _read(p(F04)) if os.path.exists(p(F04)) else None
    s05 = _read(p(F05)) if os.path.exists(p(F05)) else None
    s06 = _read(p(F06)) if os.path.exists(p(F06)) else None
    memo = _read(p(MEMO)) if os.path.exists(p(MEMO)) else None
    out = []
    if s04 is not None:
        out += b1_04_independence(s04) + b2_04_states(s04) + b3_04_strength(s04) + b10_tags(F04, s04)
        out += b15_04_sections(s04) + b38_04_every_row_tagged(s04)
        if not os.path.exists(p(F02)):
            out += b30_04_no_02(s04)
        if not os.path.exists(p(F01)) and not os.path.exists(p(F01I)):
            out += b31_04_no_01(s04)
    if s05 is not None:
        out += b4_05_opening(s05) + b5_05_destination(s05) + b6_05_new_hypotheses(s05) + b10_tags(F05, s05)
        out += b11_05_human_section(s05) + b12_05_rejection_reason(s05) + b13_05_not_compared(s05)
        out += b16_05_sections(s05) + b17_05_summary_matches(s05) + b18_05_no_self_approval(s05)
        out += b27_05_cross_03_column(s05) + b28_05_rejected_question_internal(s05) + b29_05_cross_keeps_numbers(s05)
        out += b34_05_opening_order(s05) + b39_05_states_02b(s05)
        if s04 is None:
            out += b26_05_no_adopt_without_04(s05)
        else:
            out += b36_05_takes_over_not_compared(s04, s05)
        if s06 is not None:
            out += b7_internal_questions_not_in_06(s05, s06) + b14_limits_in_06(s05, s06) + b35_rejected_not_in_06(s05, s06)
            out += b40_06_all_customer_questions(s05, s06)
    if s06 is not None:
        out += b19_06_sections(s06) + b20_06_at_most_three(s06) + b21_06_evidence_table(s06) + b23_06_issue_items(s06) + b25_06_matches_template(s06)
        out += b37_06_no_ijou_nashi(s06) + b41_06_no_grading(s06) + b42_06_polite_style(s06)
    if memo is not None and s06 is not None:
        out += b8_observation_zero(memo, s06)
    out += b9_07_exists_and_complete(anken, s05) + b22_07_transfers(anken, s05) + b24_07_counter_hypothesis(anken)
    if os.path.exists(p(F01)) and not os.path.exists(p(F01I)):
        out += b32_07_01i_substitute(anken)
    if s05 is not None:
        out += b33_07_bundling_left_to_human(anken, s05)
    return out
