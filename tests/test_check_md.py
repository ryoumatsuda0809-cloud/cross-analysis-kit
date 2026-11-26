"""CHECK.md の M 項目のうち、案件フォルダ・リポジトリの状態で決まるもの（段9・仕分け表）。

★返すのは「案件のコード名 ルール番号」だけ。本文もファイル名も出さない（PDF の名前には実名が入る）。
★封（*_封.md）は開かない。読むのは 01・01i・04 と、名前・フォルダの構成だけ。
★実案件で今守られていないものは KNOWN に理由つきで置く（strict：直ったら落ちるので外す）。
  直すかどうかは本人が決める（移行台帳 §7「見つけたずれをその場で直さない」）。
"""
import os
import re
from pathlib import Path

import pytest

import anken_checks as A
from card_checks import (F01, F01I, _read, r15_source_log, r18_three_marks, r18_mark_values, r21_section2_thickest, r31_frozen, r111_fallback_declared, s267_corp_no_filled, r19_gbiz_blank, s269_corp_no_todo, s299_first_ten, check_case)
from conftest import REPO, load_script

ANKEN = REPO / "案件"
ARCHIVE = ANKEN / "_使わない"
CA = load_script("check_anken")


def _real_cases():
    if not ANKEN.is_dir():
        return []
    num = re.compile(r"^\d+i?_.*\.md$")
    return sorted(p.name for p in ANKEN.iterdir()
                  if p.is_dir() and p != ARCHIVE and any(num.match(f.name) for f in p.iterdir()))


# 実案件で今守られていないもの（2026-09-27 段9で初めて機械で見た。直していない）
KNOWN_CASE = {
    "_TEST_案件C": ({"R111", "S269-01"}, "08-19 作成。01i（09-20）より前で、04 に代用の明記が無い／"
                                      "法人番号の引き直しの TODO（09-19 bb57de7）より前の 01"),
    "_TEST_配管検証": ({"R15", "R21", "R31-01"},
                     "08-07 作成の 01 を入力として固定している（実走ログ #7「入力を変えたらリグレッションではない」）"),
    "案件A": ({"R15", "R21"}, "汚染記録あり（配管の検証にしか使わない）。08-10 以前の 01"),
    "案件D": ({"R15", "R31-01", "R31-01i"},
             "取得ログを残さず・凍結宣言を書かずに②へ進んだ。CHECK.md §2・§3 の項目は当時からあった（読まれなかった）"),
}


# ── リポジトリ単位 ───────────────────────────────────


def archive_violations(root):
    """#115〜#118：`_使わない/` の中の形。返り値：[(フォルダ名, ルール)]。"""
    out = []
    if not root.is_dir():
        return out
    for d in sorted(p for p in root.iterdir() if p.is_dir()):
        if not re.fullmatch(r".+_\d{8}_.+", d.name):
            out.append((d.name, "R115"))
        if not (d / "_なぜ使わないか.md").exists():
            out.append((d.name, "R118"))
        for p in d.rglob("*"):
            if p.is_dir() and p.name in ("_材料", "B_現場", "A_公開"):
                out.append((d.name, "R116"))
                break
        for p in d.rglob("*"):
            if p.name.startswith(CA.BANNED_PREFIX) or p.name.endswith(CA.BANNED_SUFFIX):
                out.append((d.name, "R117"))
                break
    return out


KNOWN_ARCHIVE = {
    ("案件D_20260926_提出用PDFの前の版", "R118"): "理由はフォルダ名にだけある",
}


def pdf_names_with_code(anken_root):
    """#100：案件フォルダ直下の PDF の名前にコード名（案件X・_TEST_）が入っていないか。返り値：案件名の一覧。"""
    out = []
    if not anken_root.is_dir():
        return out
    for d in sorted(p for p in anken_root.iterdir() if p.is_dir() and p.name != "_使わない"):
        if any(re.search(r"案件[A-Z]|_TEST_", p.name) for p in d.glob("*.pdf")):
            out.append(d.name)
    return out


# ── 合成データのテスト（検査そのものが正しいか）─────────────


def _case(tmp_path, **files):
    d = tmp_path / "案件Z"
    for rel, text in files.items():
        p = d / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    return d


CARD = """# 外形カード

## 1. 同定

| 項目 | 値 | どこに | 種類 | いつ |
|---|---|---|---|---|
| 所在地 | 架空 | 公式 | 貴社の発信 | 2026-01 |
| 法人番号 | 1234567890123 | 法人番号公表サイト | 公的DBの登録 | 2026-01 |

## 2. 御社が発信されていること

| 項目 | 値 | どこに | 種類 | いつ |
|---|---|---|---|---|
| 主力 | 架空の製品 | 公式サイト | 貴社の発信 | 2026-01 |
| 設備 | 架空の設備を持つ | 公式サイト | 貴社の発信 | 2026-01 |

## 4. 公開情報では分からなかったこと

- 架空

---
---

社内メモ：2026-01-01 凍結。
"""


def test_good_case_has_no_findings(tmp_path):
    d = _case(tmp_path, **{F01: CARD, "_材料/A_公開/取得ログ_2026-01-01.md": "x", A.MEMO: "x"})
    assert check_case(d) == []


def test_r15_ng_without_source_log(tmp_path):
    assert r15_source_log(_case(tmp_path, **{F01: CARD})) == ["R15"]


def test_r15_not_required_before_01(tmp_path):
    assert r15_source_log(_case(tmp_path, **{"02_現場で確認すべき問い.md": "x"})) == []


def test_r18_ng_on_empty_mark_cell(tmp_path):
    bad = CARD.replace("| 主力 | 架空の製品 | 公式サイト |", "| 主力 | 架空の製品 | |")
    assert r18_three_marks(_case(tmp_path, **{F01: bad})) == ["R18-01"]


def test_r18_fumei_is_filled(tmp_path):
    ok = CARD.replace("| 主力 | 架空の製品 | 公式サイト | 貴社の発信 | 2026-01 |", "| 主力 | 架空の製品 | 不明 | 不明 | 不明 |")
    assert r18_three_marks(_case(tmp_path, **{F01: ok})) == []


MAIN_ROW = "| 主力 | 架空の製品 | 公式サイト | 貴社の発信 | 2026-01 |"


@pytest.mark.parametrize("kind", ["公式", "貴社の発信／第三者媒体", "—", "{種類}",
                                  "貴社の発信（独自分類）", "第三者媒体など"])   # 5つの語を含むだけでは通さない（09-29）
def test_r18k_ng_on_kind_outside_five(tmp_path, kind):
    bad = CARD.replace(MAIN_ROW, MAIN_ROW.replace("貴社の発信", kind))
    assert r18_mark_values(_case(tmp_path, **{F01: bad})) == ["R18k-01"]


@pytest.mark.parametrize("kind", ["**行政への届出**", "`実測値`", "不明", "公的DBの登録"])
def test_r18k_ok(tmp_path, kind):
    ok = CARD.replace(MAIN_ROW, MAIN_ROW.replace("貴社の発信", kind))
    assert r18_mark_values(_case(tmp_path, **{F01: ok})) == []


@pytest.mark.parametrize("when", ["2026", "最近", "—", "HPより",
                                  "2026-99", "2026-00", "2026年13月", "令和5年13月", "2026-123"])   # 月が1〜12でない（09-29）
def test_r18t_ng_on_not_year_month(tmp_path, when):
    bad = CARD.replace(MAIN_ROW, MAIN_ROW.replace("2026-01", when))
    assert r18_mark_values(_case(tmp_path, **{F01: bad})) == ["R18t-01"]


@pytest.mark.parametrize("when", ["2026年1月", "平成29年3月", "令和元年 5月", "2026/01 閲覧", "不明", "不明（記載なし）",
                                  "2026-12", "2026.9"])
def test_r18t_ok(tmp_path, when):
    ok = CARD.replace(MAIN_ROW, MAIN_ROW.replace("2026-01", when))
    assert r18_mark_values(_case(tmp_path, **{F01: ok})) == []


def test_r18_values_dash_ok_only_when_row_is_unknown(tmp_path):
    assert r18_mark_values(_case(tmp_path, **{F01: CARD_UNKNOWN})) == []


def test_r18_values_are_wired_into_check_case(tmp_path):
    bad = CARD.replace(MAIN_ROW, "| 主力 | 架空の製品 | 公式サイト | 公式 | 最近 |")
    assert {"R18k-01", "R18t-01"} <= set(check_case(_case(tmp_path, **{F01: bad})))


def test_r18_below_split_line_is_not_checked(tmp_path):
    card = CARD + "\n| x | どこに | 種類 | いつ |\n|---|---|---|---|\n| a | | | |\n"
    assert r18_three_marks(_case(tmp_path, **{F01: card})) == []


def test_r21_ng_when_other_section_thicker(tmp_path):
    bad = CARD.replace("- 架空\n", "- 架空\n" + "- 分からなかったことが長い\n" * 30)
    assert r21_section2_thickest(_case(tmp_path, **{F01: bad})) == ["R21"]


def test_r31_ng_when_not_frozen_after_site(tmp_path):
    d = _case(tmp_path, **{F01: CARD.replace("凍結", "メモ"), F01I: "内部用", A.MEMO: "x"})
    assert r31_frozen(d) == ["R31-01", "R31-01i"]


def test_r31_freeze_above_split_line_does_not_count(tmp_path):
    bad = CARD.replace("社内メモ：2026-01-01 凍結。", "社内メモ").replace("# 外形カード", "# 外形カード（凍結）")
    assert r31_frozen(_case(tmp_path, **{F01: bad, A.MEMO: "x"})) == ["R31-01"]


def test_r31_not_required_before_site(tmp_path):
    assert r31_frozen(_case(tmp_path, **{F01: CARD.replace("凍結", "メモ")})) == []


def test_r111_ng_when_fallback_not_declared(tmp_path):
    d = _case(tmp_path, **{F01: CARD, A.F04: "# 04\n\n## 1. 真因の芽\n\n代用\n"})
    assert r111_fallback_declared(d) == ["R111"]


def test_r111_ok_when_declared_before_section1(tmp_path):
    d = _case(tmp_path, **{F01: CARD, A.F04: "# 04\n\n定規は #14 以前の版を代用。\n\n## 1. 真因の芽\n"})
    assert r111_fallback_declared(d) == []


UNKNOWN_ROW = "| 法人番号 | 不明（未特定） | — | — | — |"
TODO_OK = "\n### 取りに行けるもの（A軸のTODO）\n\n| 項目 | なぜ取れていないか | 次にどこを見るか |\n|---|---|---|\n" \
          "| 法人番号 | 同名の別法人に当たった | 法人番号公表サイトで所在地から検索 |\n"
CARD_UNKNOWN = CARD.replace("| 法人番号 | 1234567890123 | 法人番号公表サイト | 公的DBの登録 | 2026-01 |", UNKNOWN_ROW) + TODO_OK
CARD_I = """# 01i

## §1. 同定（A）

| 項目 | 内容 | 出典 | 性質 | 時点 |
|---|---|---|---|---|
| 法人番号 | 不明（未特定） | — | — | — |
| 従業員数 | 30名 | 公式サイト | 貴社の発信 | 2026-01 |

検索で出た法人番号は同名の別法人だった。

## §4. 公的DB上の登録状況（A）

| 項目 | 件数 | 備考 |
|---|---|---|
| 補助金交付 |  |  |

## §5. 埋まらなかった項目

### 5-2. 未取得／未調査

| 項目 | なぜ取れていないか | 次にどこを見るか |
|---|---|---|
| 法人番号 | 同名の別法人 | 法人番号公表サイトで所在地から検索 |
| gBizINFO 一式 | 法人番号が未特定 | 法人番号の確定後 |

## §6. 出典一覧

- gBizINFO 0000000000000 → 同名の別法人。当社ではない
"""


def test_corp_no_unknown_good_card_passes(tmp_path):
    d = _case(tmp_path, **{F01: CARD_UNKNOWN, F01I: CARD_I})
    assert (r19_gbiz_blank(d), s267_corp_no_filled(d), s269_corp_no_todo(d)) == ([], [], [])


def test_corp_no_polite_unknown_counts_as_unknown(tmp_path):
    card = CARD_UNKNOWN.replace("不明（未特定）", "特定できませんでした（同名の別法人がございました）")
    d = _case(tmp_path, **{F01: card.replace(TODO_OK, "")})
    assert s269_corp_no_todo(d) == ["S269-01"]


def test_s267_ng_on_empty_or_dash(tmp_path):
    for v in ("", "—"):
        d = _case(tmp_path, **{F01: CARD.replace("| 1234567890123 |", f"| {v} |"), F01I: CARD_I.replace("| 不明（未特定） |", f"| {v} |")})
        assert s267_corp_no_filled(d) == ["S267-01", "S267-01i"]


def test_s267_ng_without_row(tmp_path):
    d = _case(tmp_path, **{F01: CARD.replace("| 法人番号 | 1234567890123 | 法人番号公表サイト | 公的DBの登録 | 2026-01 |\n", "")})
    assert s267_corp_no_filled(d) == ["S267-01"]


def test_s267_ng_without_reason(tmp_path):
    card_i = CARD_I.replace("検索で出た法人番号は同名の別法人だった。", "").replace(
        "| 法人番号 | 同名の別法人 | 法人番号公表サイトで所在地から検索 |\n", "")
    d = _case(tmp_path, **{F01: CARD_UNKNOWN.replace(TODO_OK, "\n### 法人番号\n"), F01I: card_i})
    assert s267_corp_no_filled(d) == ["S267-01", "S267-01i"]


def test_s267_reason_above_split_line_does_not_count(tmp_path):
    card = CARD_UNKNOWN.replace(TODO_OK, "").replace("## 4. 公開情報では分からなかったこと\n",
                                                     "## 4. 公開情報では分からなかったこと\n\n- 法人番号は同名の別法人があり特定できなかった\n")
    assert s267_corp_no_filled(_case(tmp_path, **{F01: card})) == ["S267-01"]


def test_r19_ng_when_gbiz_source_filled(tmp_path):
    card = CARD_UNKNOWN.replace("| 主力 | 架空の製品 | 公式サイト |", "| 主力 | 架空の製品 | gBizINFO |")
    card_i = CARD_I.replace("| 従業員数 | 30名 | 公式サイト |", "| 従業員数 | 30名 | ★GBIZINFO（職場情報） |")
    assert r19_gbiz_blank(_case(tmp_path, **{F01: card, F01I: card_i})) == ["R19-01", "R19-01i"]


def test_r19_ng_when_public_db_count_filled(tmp_path):
    d = _case(tmp_path, **{F01I: CARD_I.replace("| 補助金交付 |  |  |", "| 補助金交付 | 0件 |  |")})
    assert r19_gbiz_blank(d) == ["R19-01i"]


def test_r19_gbiz_below_split_line_or_known_no_is_not_checked(tmp_path):
    below = CARD_UNKNOWN + "\n| 誤って当たった | 出典 |\n|---|---|\n| 別法人 | gBizINFO |\n"
    known = CARD.replace("| 主力 | 架空の製品 | 公式サイト |", "| 主力 | 架空の製品 | gBizINFO |")
    assert r19_gbiz_blank(_case(tmp_path / "a", **{F01: below})) == []
    assert r19_gbiz_blank(_case(tmp_path / "b", **{F01: known})) == []


def test_s269_ng_without_todo_or_without_address(tmp_path):
    no_addr = CARD_I.replace("法人番号公表サイトで所在地から検索", "法人番号公表サイト")
    d = _case(tmp_path, **{F01: CARD_UNKNOWN.replace(TODO_OK, ""), F01I: no_addr})
    assert s269_corp_no_todo(d) == ["S269-01", "S269-01i"]


def test_s269_todo_above_split_line_does_not_count(tmp_path):
    card = CARD_UNKNOWN.replace(TODO_OK, "").replace("## 4. 公開情報では分からなかったこと\n",
                                                     "## 4. 公開情報では分からなかったこと\n" + TODO_OK)
    assert s269_corp_no_todo(_case(tmp_path, **{F01: card})) == ["S269-01"]


def test_archive_rules(tmp_path):
    root = tmp_path / "_使わない"
    (root / "a_20260101_理由").mkdir(parents=True)
    (root / "a_20260101_理由" / "_なぜ使わないか.md").write_text("x", encoding="utf-8")
    (root / "b_20260101_理由" / "_材料" / "B_現場").mkdir(parents=True)
    (root / "b_20260101_理由" / "_旧_04.md").write_text("x", encoding="utf-8")
    for bad in ("c_理由", "d_2026-01-01_理由", "e_20260101"):
        (root / bad).mkdir()
        (root / bad / "_なぜ使わないか.md").write_text("x", encoding="utf-8")
    assert archive_violations(root) == [("b_20260101_理由", "R118"), ("b_20260101_理由", "R116"),
                                        ("b_20260101_理由", "R117"), ("c_理由", "R115"),
                                        ("d_2026-01-01_理由", "R115"), ("e_20260101", "R115")]


def test_pdf_code_name(tmp_path):
    (tmp_path / "案件Z").mkdir()
    (tmp_path / "案件Z" / "Office_案件Z_現状の整理.pdf").write_bytes(b"")
    (tmp_path / "案件Y").mkdir()
    (tmp_path / "案件Y" / "Office_架空様_現状の整理.pdf").write_bytes(b"")
    assert pdf_names_with_code(tmp_path) == ["案件Z"]


# ── 実物に当てる ───────────────────────────────────


REAL = _real_cases()


@pytest.mark.skipif(not REAL, reason="案件/ に案件が無い（この端末では診断していない）")
@pytest.mark.parametrize("name", REAL or ["-"])
def test_real_case_state(name):
    allowed, why = KNOWN_CASE.get(name, (set(), ""))
    got = set(check_case(ANKEN / name))
    if got - allowed:
        pytest.fail(f"{name}：{sorted(got - allowed)}", pytrace=False)
    if allowed - got:
        pytest.fail(f"{name}：既知の {sorted(allowed - got)} が出なくなった。KNOWN_CASE から外す（{why}）", pytrace=False)


@pytest.mark.skipif(not ARCHIVE.is_dir(), reason="案件/_使わない/ が無い（この端末では使っていない）")
def test_real_archive_state():
    got = set(archive_violations(ARCHIVE))
    assert not (got - set(KNOWN_ARCHIVE)), f"_使わない/ の形の違反：{sorted(got - set(KNOWN_ARCHIVE))}"
    gone = {k for k in set(KNOWN_ARCHIVE) - got if (ARCHIVE / k[0]).is_dir()}   # 別の端末に無いフォルダは数えない
    assert not gone, f"既知の違反が出なくなった。KNOWN_ARCHIVE から外す：{sorted(gone)}"


def test_real_pdf_names_have_no_code_name():
    assert pdf_names_with_code(ANKEN) == []


def test_shindan_kekka_is_not_used():
    """#140：`診断結果/` は廃止（`案件/` に統一）。フォルダが無いか、空。"""
    d = REPO / "診断結果"
    assert not d.exists() or not any(p.is_file() for p in d.rglob("*")), "診断結果/ にファイルがある → 案件/ へ"


def test_subagent_prompt_limits_writes_to_one_output():
    """#45：②③④の雛形に「書き込んでよいのは出力ファイル1つだけ」がある（6-41）。"""
    src = _read(REPO / ".claude" / "skills" / "cross-run" / "assets" / "subagent-prompts.md")
    assert "書き込んでよいのは、あなたの出力ファイル1つだけ" in src


def test_report_style_has_page_numbers():
    """#94：PDF にページ番号が入る（style.css の @page に counter(page)）。"""
    css = _read(REPO / "対外資料" / "_report_build" / "style.css")
    page = re.search(r"@page\s*\{.*?\n\}", css, re.S)
    assert page and "counter(page)" in page.group(0)


# ── この端末の外（#138）────────────────────────────


KNACIT = Path(os.environ["ENGINE_DOCS_DIR"]) if os.environ.get("ENGINE_DOCS_DIR") else Path("/nonexistent")
BANNED = ANKEN / "_禁止語_ローカル専用.txt"
# 禁止語を含む md の数。★名前は書かない。09-27 の内訳：案件の成果物（診断実例）2件＝STATUS §5 の「2件」＋
# 設計文書が案件名を例として書いている8件（クロス分析の写し・台帳・申し送りなど）。直すかは本人（移行台帳 §8）
KNOWN_KNACIT_HITS = 10


@pytest.mark.skipif(not (KNACIT.is_dir() and BANNED.exists()), reason="ENGINE_DOCS_DIR か禁止語リストが無い")
def test_engine_docs_have_no_case_words():
    """#138：エンジン層（ENGINE_DOCS_DIR）に案件の実名・実数が入っていない。★ファイル名も語も出さない。"""
    words = [w.strip() for w in _read(BANNED).splitlines() if w.strip() and not w.startswith("#")]
    hits = 0
    for p in KNACIT.rglob("*.md"):
        try:
            s = _read(p)
        except (UnicodeDecodeError, OSError):
            continue
        if any(w in s or w in p.name for w in words):
            hits += 1
    assert hits == KNOWN_KNACIT_HITS, \
        f"実名・実数を含む md が {hits} 件（既知 {KNOWN_KNACIT_HITS} 件）。増えたなら移す／減ったなら KNOWN を下げる"


# ── market-recon #299：初回訪問で聞く10問（09-28） ──

def _q02(n, orig=True, head="## ★初回訪問で聞く10問（全問は1回で聞けない）"):
    rows_ = "".join(f"| {i} | 問い{i}はどうですか | {'Q' + str(i) if orig else ''} | 答えやすい |\n" for i in range(1, n + 1))
    return f"# 02\n\n## 問い\n\n1. a\n\n{head}\n\n| # | 問い | 元番号 | なぜ最初か |\n|---|---|---|---|\n{rows_}\n## 帰ってきたら\n"


def test_s299_ok_ten(tmp_path):
    assert s299_first_ten(_case(tmp_path, **{A.F02: _q02(10)})) == []


@pytest.mark.parametrize("q", [_q02(9), _q02(11), _q02(10, orig=False), _q02(1), "# 02\n\n## 問い\n\n1. a\n"])
def test_s299_ng(tmp_path, q):
    assert s299_first_ten(_case(tmp_path, **{A.F02: q})) == ["S299"]


def test_s299_not_applied_without_02(tmp_path):
    assert s299_first_ten(_case(tmp_path, **{F01: CARD})) == []


def test_s299_wired_into_check_case(tmp_path):
    assert "S299" in check_case(_case(tmp_path, **{A.F02: _q02(3)}))


# ── client-data-firewall #33・#34：新しい案件を始めるときの確認（09-28） ──
# ★返すのはコード名（伏せ名）と件数だけ。実名・番号は出さない。

TABLE_NAMES = "_社名対応表_ローカル専用.md"
BANNED_NAME = "_禁止語_ローカル専用.txt"
PIPE_FILES = (F01, F01I, A.F02, A.F04, A.F05, A.F06)


def _clean(v):
    return re.sub(r"[*`~]", "", v).strip()


def firewall_violations(anken_root):
    """#33 案件フォルダが対応表のフォルダ名にある／#34 実名（「架空」の行を除く）に禁止語が1つ以上含まれ、
    法人番号・電話番号の値が禁止語リストにある。返り値は「#33 フォルダ名」「#34 コード名」「#34 番号」だけ。"""
    src = _read(anken_root / TABLE_NAMES)
    banned = [w.strip() for w in _read(anken_root / BANNED_NAME).splitlines() if w.strip() and not w.startswith("#")]
    folders, out = set(), []
    for t in A.tables([(i + 1, l) for i, l in enumerate(src.splitlines())]):
        fi, ni, ci = A.col(t, "フォルダ名"), A.col(t, "実名"), A.col(t, "コード")
        if fi is not None and ni is not None:
            for _, c in A.rows(t):
                folders.add(_clean(A.cell(c, fi)).rstrip("/").split("/")[0])
                name = _clean(A.cell(c, ni))
                if "架空" not in name and not any(w in name for w in banned):
                    out.append(f"#34 {_clean(A.cell(c, ci)) or '?'}")
        ki, vi = A.col(t, "項目"), A.col(t, "値")
        if ki is not None and vi is not None:
            for _, c in A.rows(t):
                v = re.sub(r"[*`\s]", "", A.cell(c, vi))
                if re.search(r"法人番号|電話", A.cell(c, ki)) and re.search(r"\d{4}", v) and not any(v in w or w in v for w in banned):
                    out.append("#34 番号")
    cases = sorted(d.name for d in anken_root.iterdir()
                   if d.is_dir() and not d.name.startswith("_") and any((d / f).exists() for f in PIPE_FILES))
    out += [f"#33 {d}" for d in cases if d not in folders]
    return out


@pytest.mark.skipif(not ((ANKEN / TABLE_NAMES).exists() and (ANKEN / BANNED_NAME).exists()), reason="対応表か禁止語リストが無い")
def test_real_firewall_registration():
    got = firewall_violations(ANKEN)
    assert got == [], f"対応表・禁止語リストの登録漏れ：{got}"


FW_TABLE = """# 対応表

| コード | フォルダ名 | 実名 | 業種 | 状態 |
|---|---|---|---|---|
| 案件Z | `案件Z` | 株式会社見本工業（本社） | 製造 | 進行中 |
| 案件Y | _TEST_案件Y | 完全な架空データの会社 | 製造 | 完了 |

### 案件Z

| 項目 | 値 |
|---|---|
| 法人番号 | 1234567890123 |
| 電話番号 | 000-0000-0000 |
"""
FW_BANNED = "見本工業\n1234567890123\n000-0000-0000\n"


@pytest.fixture
def fw(tmp_path):
    def make(table=FW_TABLE, banned=FW_BANNED, dirs=("案件Z",)):
        (tmp_path / TABLE_NAMES).write_text(table, encoding="utf-8")
        (tmp_path / BANNED_NAME).write_text(banned, encoding="utf-8")
        for d in dirs:
            (tmp_path / d).mkdir()
            (tmp_path / d / F01).write_text("x", encoding="utf-8")
        return tmp_path
    return make


def test_firewall_ok(fw):
    assert firewall_violations(fw()) == []


def test_firewall_ng_case_folder_not_in_table(fw):
    assert firewall_violations(fw(dirs=("案件Z", "案件X"))) == ["#33 案件X"]


def test_firewall_folder_without_outputs_is_not_a_case(fw):
    root = fw()
    (root / "メモ置き場").mkdir()
    assert firewall_violations(root) == []


def test_firewall_ng_real_name_not_banned(fw):
    assert firewall_violations(fw(banned="1234567890123\n000-0000-0000\n")) == ["#34 案件Z"]


@pytest.mark.parametrize("drop", ["1234567890123\n", "000-0000-0000\n"])
def test_firewall_ng_number_not_banned(fw, drop):
    assert firewall_violations(fw(banned=FW_BANNED.replace(drop, ""))) == ["#34 番号"]


def test_firewall_output_carries_no_names(fw):
    out = " ".join(firewall_violations(fw(banned="x\n")))
    assert out and "見本工業" not in out and "1234567890123" not in out
