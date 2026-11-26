"""①の出力（01・01i）と案件フォルダの状態の検査（段9。CHECK.md・仕分け表の R・S の番号）。

★pytest（tests/test_check_md.py）と通知のフック（.claude/hooks/notice.py）の両方がここを呼ぶ。
  以前は test_check_md.py の中にあり、pytest を流す pre-commit でしか走らなかった。
  `案件/` は commit しないので、①を回しても誰も流さなかった（台帳 §8・09-28 の配線の穴）。
★返すのは「ルール名」だけ。本文もファイル名も出さない。封（*_封.md）は開かない。読むのは 01・01i・04 と、名前・フォルダの構成だけ。
"""
import re
from pathlib import Path

import anken_checks as A

F01, F01I = "01_外形カード_事実編.md", "01i_外形カード_内部用.md"
SPLIT = re.compile(r"^-{3,}\s*\n-{3,}\s*$", re.M)   # lint_01 と同じ切り離し線


def _read(p):
    return p.read_text(encoding="utf-8")


def _front_back(src):
    m = SPLIT.search(src)
    return (src[:m.start()], src[m.end():]) if m else (src, src)


# ── 案件フォルダ単位 ─────────────────────────────────


def r15_source_log(d):
    """#15：①を回した案件に `_材料/A_公開/取得ログ_*.md` がある（捏造・誤同定を後から grep で捕まえるため）。"""
    if not ((d / F01).exists() or (d / F01I).exists()):
        return []
    return [] if list((d / "_材料" / "A_公開").glob("取得ログ_*.md")) else ["R15"]


def _three_mark_rows(src):
    """「どこに／種類／いつ」の列がある表の行で、その3列のどれかが空のもの。"""
    bad = []
    for t in A.tables([(i + 1, l) for i, l in enumerate(src.splitlines())]):
        idx = [A.col(t, k) for k in ("どこに", "種類", "いつ")]
        if None in idx:
            continue
        for n, c in A.rows(t):
            if any(not A.cell(c, i).replace("*", "").strip() for i in idx):
                bad.append(n)
    return bad


def r18_three_marks(d):
    """#18：01（切り離し線から上）と 01i の3印の列が、どの行も空でない（取れなければ「不明」と書く）。"""
    out = []
    if (d / F01).exists() and _three_mark_rows(_front_back(_read(d / F01))[0]):
        out.append("R18-01")
    if (d / F01I).exists() and _three_mark_rows(_read(d / F01I)):
        out.append("R18-01i")
    return out


KINDS = ("貴社の発信", "行政への届出", "公的DBの登録", "第三者媒体", "実測値")   # market-recon SKILL #267
YEAR_MONTH = re.compile(r"(?:19|20)\d\d\s*[-/.年]\s*(\d{1,2})(?!\d)|(?:令和|平成|昭和)\s*(?:\d{1,2}|元)\s*年\s*(\d{1,2})\s*月")


def _is_year_month(v):
    """年月が1つ以上あり、どれも月が1〜12（2026-99・2026年13月は通さない。09-29）。"""
    months = [int(a or b) for a, b in YEAR_MONTH.findall(v)]
    return bool(months) and all(1 <= m <= 12 for m in months)


def _mark_value_rows(src):
    """3印の表の行で、種類が5つの1つ（か「不明」）でないもの・いつが年月（か「不明」）でないもの。→ ([行], [行])"""
    bad_kind, bad_time = [], []
    for t in A.tables([(i + 1, l) for i, l in enumerate(src.splitlines())]):
        ki, ti = A.col(t, "種類"), A.col(t, "いつ")
        if None in (A.col(t, "どこに"), ki, ti):
            continue
        for n, c in A.rows(t):
            dash = {"—", "－", "-", "―"} if any("不明" in x for x in c) else set()   # 値そのものが不明の行（法人番号 不明（未特定） など）は「—」も通す
            k = re.sub(r"[*`\s]", "", A.cell(c, ki))
            if k and k != "不明" and k not in dash and k not in KINDS:   # 語を含むだけでは通さない（09-29）
                bad_kind.append(n)
            v = A.cell(c, ti).replace("*", "").strip()
            if v and "不明" not in v and v not in dash and not _is_year_month(v):
                bad_time.append(n)
    return bad_kind, bad_time


def r18_mark_values(d):
    """#18（SKILL #267・#268）：01（切り離し線から上）の「種類」が5つのどれか、「いつ」が年月。取れなければ「不明」。空欄は R18。"""
    if not (d / F01).exists():
        return []
    k, t = _mark_value_rows(_front_back(_read(d / F01))[0])
    return (["R18k-01"] if k else []) + (["R18t-01"] if t else [])


def _sections(front):
    """{節番号: 本文の長さ}（「## N.」単位）。"""
    parts = re.split(r"^##\s*(\d+)\.", front, flags=re.M)
    return {int(parts[i]): len(parts[i + 1]) for i in range(1, len(parts) - 1, 2)}


def r21_section2_thickest(d):
    """#21：01（切り離し線から上）で §2（御社が発信されていること）が一番厚い。"""
    if not (d / F01).exists():
        return []
    secs = _sections(_front_back(_read(d / F01))[0])
    if 2 not in secs:
        return ["R21"]
    return [] if secs[2] >= max(secs.values()) else ["R21"]


def _after_site(d):
    return (d / A.MEMO).exists() or (d / A.F04).exists()


def r31_frozen(d):
    """#31：現場の後なら、01 は切り離し線の下（社内メモ）に、01i はどこかに凍結宣言がある。"""
    if not _after_site(d):
        return []
    out = []
    if (d / F01).exists() and "凍結" not in _front_back(_read(d / F01))[1]:
        out.append("R31-01")
    if (d / F01I).exists() and "凍結" not in _read(d / F01I):
        out.append("R31-01i")
    return out


def r111_fallback_declared(d):
    """#111：01i が無く 01 で代用して②を回したなら、04 の冒頭（§1 より前）に代用と書いてある。"""
    if (d / F01I).exists() or not (d / F01).exists() or not (d / A.F04).exists():
        return []
    head = re.split(r"^##\s*1\.", _read(d / A.F04), maxsplit=1, flags=re.M)[0]
    return [] if "代用" in head else ["R111"]


UNKNOWN_NO = re.compile(r"不明|未特定|特定でき(?:ませ|な)")   # 「特定できませんでした」は 01 の敬語（表記の揺れは通す）


def _plain(s):
    return s.replace("*", "").strip()


def _sec_range(lines, num):
    """「## N.」（§ あり・なし）から次の「## 」の手前まで。(開始, 終わり) の添字。無ければ None。"""
    head = re.compile(rf"^##\s*§?{num}\.")
    start = next((i for i, l in enumerate(lines) if head.match(l)), None)
    if start is None:
        return None
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    return start, end


def _numbered(lines, lo=0, hi=None):
    return [(i + 1, lines[i]) for i in range(lo, len(lines) if hi is None else hi)]


def _corp_no(lines):
    """§1 の表の「法人番号」の行 → (行番号, 値)。無ければ None。"""
    r = _sec_range(lines, 1)
    if not r:
        return None
    for t in A.tables(_numbered(lines, *r)):
        for n, c in A.rows(t):
            if _plain(A.cell(c, 0)) == "法人番号":
                return n, _plain(A.cell(c, 1))
    return None


def _unknown(v):
    return not re.search(r"\d{13}", v) and bool(UNKNOWN_NO.search(v))


def _card_areas(d):
    """[(接尾辞, 行の一覧, 相手に見せる側の範囲, 社内メモの範囲)]。01 は切り離し線で割る（無ければ全体を両方に）。01i は全体。"""
    out = []
    if (d / F01).exists():
        src = _read(d / F01)
        lines = src.splitlines()
        m = SPLIT.search(src)
        cut = src[:m.end()].count("\n") + 1 if m else None
        front = (0, src[:m.start()].count("\n")) if m else (0, len(lines))
        out.append(("01", lines, front, (cut, len(lines)) if m else (0, len(lines))))
    if (d / F01I).exists():
        lines = _read(d / F01I).splitlines()
        out.append(("01i", lines, (0, len(lines)), (0, len(lines))))
    return out


def _is_reason(line):
    """法人番号の理由の行か。表の行は項目（先頭の列）が法人番号で、ほかの列に中身があるもの
    （「gBizINFO 一式 | 法人番号が未特定」は理由ではない）。地の文は見出し以外で、法人番号の語のほかに中身があるもの。"""
    s = line.strip()
    if s.startswith("|"):
        cells = [_plain(c) for c in s.strip("|").split("|")]
        return "法人番号" in cells[0] and any(re.sub(r"[\s:\-—]", "", c) for c in cells[1:])
    return "法人番号" in s and not s.startswith("#") and bool(re.sub(r"[\s*>\-]|法人番号", "", s))


def s267_corp_no_filled(d):
    """SKILL #273：法人番号の欄が空でない（13桁か「不明（未特定）」）。未特定なら理由の行が
    01 は社内メモに、01i はどこかにある（§1 の法人番号の行そのものは数えない。理由の中身は人が見る）。"""
    out = []
    for suf, lines, _, memo in _card_areas(d):
        row = _corp_no(lines)
        if not row or not (re.search(r"\d{13}", row[1]) or _unknown(row[1])):
            out.append(f"S267-{suf}")
            continue
        if not _unknown(row[1]):
            continue
        if not any(_is_reason(l) for n, l in _numbered(lines, *memo) if n != row[0]):
            out.append(f"S267-{suf}")
    return out


SOURCE_COLS = ("出典", "どこに")


def r19_gbiz_blank(d):
    """#19（SKILL #274）：法人番号が未特定なら、gBizINFO 由来の欄が空。
    見るのは相手に見せる側（01 は切り離し線から上・01i は全体）の表で、出典の列に gBizINFO とある行と、
    01i §4（公的DB）の件数の列。§5 の TODO・§6 の出典一覧・「誤って当たった情報」の記録は表の出典の列でないので数えない。"""
    out = []
    for suf, lines, front, _ in _card_areas(d):
        row = _corp_no(lines)
        if not row or not _unknown(row[1]):
            continue
        bad = False
        for t in A.tables(_numbered(lines, *front)):
            idx = [i for i, h in enumerate(t[0][1]) if any(k in h for k in SOURCE_COLS)]
            bad |= any("gbiz" in A.cell(c, i).lower() for _, c in A.rows(t) for i in idx)
        sec4 = _sec_range(lines, 4) if suf == "01i" else None
        if sec4:
            for t in A.tables(_numbered(lines, *sec4)):
                i = A.col(t, "件数")
                bad |= i is not None and any(_plain(A.cell(c, i)) for _, c in A.rows(t))
        if bad:
            out.append(f"R19-{suf}")
    return out


def s299_first_ten(d):
    """market-recon #299：02 に「初回訪問で聞く10問」の表があり、問いと元番号の埋まった行がちょうど10行。
    どの問いを選んだか（選び方の基準）は人が見る（CHECK #28 は H）。"""
    p = d / A.F02
    if not p.exists():
        return []
    for t in A.tables(A.section_named(_read(p), "10問") or []):
        qi, oi = A.col(t, "問い"), A.col(t, "元番号")
        if qi is None or oi is None:
            continue
        filled = [c for _, c in A.rows(t) if A.cell(c, qi).replace("*", "").strip() and A.cell(c, oi).replace("*", "").strip()]
        return [] if len(filled) == 10 else ["S299"]
    return ["S299"]


def s269_corp_no_todo(d):
    """SKILL #275：法人番号が未特定なら、TODO の表（「次にどこを見るか」の列がある表。01 は社内メモ）に
    項目が法人番号で「所在地」から引き直す行がある。"""
    out = []
    for suf, lines, _, memo in _card_areas(d):
        row = _corp_no(lines)
        if not row or not _unknown(row[1]):
            continue
        ok = any("法人番号" in _plain(A.cell(c, 0)) and "所在地" in "".join(c)
                 for t in A.tables(_numbered(lines, *memo)) if A.col(t, "次にどこ") is not None
                 for _, c in A.rows(t))
        if not ok:
            out.append(f"S269-{suf}")
    return out


CASE_RULES = [r15_source_log, r18_three_marks, r18_mark_values, r19_gbiz_blank, r21_section2_thickest, r31_frozen,
              r111_fallback_declared, s267_corp_no_filled, s269_corp_no_todo, s299_first_ten]


def check_case(d):
    return sorted(v for r in CASE_RULES for v in r(d))


RULE_NAMES = {   # 通知で本人に見せる1行の説明（本文は出さない）
    "R15": "取得ログ（_材料/A_公開/取得ログ_*.md）が無い",
    "R18": "3印（どこに・種類・いつ／出典・性質・時点）の空欄がある",
    # ★ID（S267・R19 など）は付けた時点の番号で、固定の名前として扱う。仕分け表_SKILL の行番号は SKILL.md の加筆でずれる（2026-11-26 に +6）。
    "R18k": "「種類」が5つ（貴社の発信／行政への届出／公的DBの登録／第三者媒体／実測値）のどれでもない",
    "R18t": "「いつの情報か」が年月でも「不明」でもない",
    "R19": "法人番号が未特定なのに gBizINFO 由来の欄が埋まっている",
    "R21": "§2（御社が発信されていること）が一番厚くない",
    "R31": "現場の後なのに凍結宣言が無い",
    "R111": "01i が無く 01 で代用したのに、04 の冒頭に代用と書いていない",
    "S267": "法人番号の欄が13桁でも「不明（未特定）」でもない／未特定の理由の行が無い",
    "S299": "02 の「初回訪問で聞く10問」の表が10行（問い・元番号あり）になっていない",
    "S269": "法人番号が未特定なのに、TODO に「所在地から引き直す」行が無い",
}


def describe(v):
    """「R18-01i」→「R18-01i 3印…の空欄がある」。"""
    return f"{v} {RULE_NAMES.get(v.split('-')[0], '')}".rstrip()

