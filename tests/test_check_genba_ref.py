"""check_genba_ref.py の挙動を固定する（実走 #58 の対策 (b)・09-29 本人決定）。

★合成データだけを使う。実在の現場メモ・04 は読まない。
★見ているのは4つ：引いた行があるか／その行の役割か／役割数が合うか／「（つないだ）」の芽が強でないか。つないだかどうか（意味の判断）は B-1 の検証役。
"""
import pytest

from conftest import run_script

MEMO = """# 現場メモ

| 欄 | 中身 |
|---|---|
| 話者 | 工場長・事務 |

- 【工場長】品目が増え続けている
- 【工場長】段取り替えが多い日で8回
- 【事務】受注は電話とFAXで受ける
- 【不明】廃棄率は記録していないとのこと
"""
# 行番号：L7 工場長／L8 工場長／L9 事務／L10 不明（L5 は★出所の行で【】が無い）

S04 = """# 04

## 1. 真因の芽リスト

| # | 真因の芽 | 根拠 | 強度 | 情報源の役割数 | 整合 | タグ |
|---|---|---|---|---|---|---|
| 1 | 芽1 | {r1} | {s1} | {n1} | | `#現場オペ` |
| 2 | | | | | | |

## 2. 建前と現場のズレ一覧

| # | 建前 | 現場の事実 | 差分 | 同じものを測っているか | タグ |
|---|---|---|---|---|---|
| 1 | 建前1 | {f1} | 差 | はい | `#現場オペ` |

### 市場ベンチマークとのズレ

| ベンチマーク | 現場の数字 | 状態 | 差 |
|---|---|---|---|
| 業界平均 | なし | 比較不能（両側なし） | |
"""


def make(r1="【工場長】L7・L8／【事務】L9", n1="2役割", f1="段取りが多い（【工場長】L8）", s1="中"):
    return S04.format(r1=r1, n1=n1, f1=f1, s1=s1)


@pytest.fixture
def check(tmp_path):
    def _run(s04, memo=MEMO):
        d = tmp_path / "案件"
        (d / "_材料" / "B_現場").mkdir(parents=True, exist_ok=True)
        (d / "_材料" / "B_現場" / "現場メモ.md").write_text(memo, encoding="utf-8")
        p = d / "04_現場分析.md"
        p.write_text(s04, encoding="utf-8")
        return run_script("check_genba_ref", p)
    return _run


def test_ok_when_refs_roles_and_count_match(check):
    code, ng, out = check(make())
    assert code == 0 and not ng, ng
    assert "OK" in out


def test_no_args_exits_2():
    assert run_script("check_genba_ref")[0] == 2


def test_ng_when_no_line_number(check):
    code, ng, _ = check(make(r1="工場長・事務から"))
    assert code == 1 and any(l.startswith("根拠にメモの行番号が無い") and "§1 #1" in l for l in ng)


def test_ng_when_line_number_has_no_role(check):
    code, ng, _ = check(make(r1="L7／【事務】L9", n1="1役割"))
    assert code == 1 and any(l.startswith("行番号の前に【役割】が無い") for l in ng)


@pytest.mark.parametrize("r1", ["【工場長】L99／【事務】L9", "【工場長】L5／【事務】L9"])
def test_ng_when_cited_line_missing_or_untagged(check, r1):
    """L99 はメモに無い行、L5 は【役割】の無い行（★出所の話者）。"""
    code, ng, _ = check(make(r1=r1))
    assert code == 1 and any(l.startswith("引いた行がメモに無い") for l in ng)


def test_ng_when_role_differs_from_memo(check):
    """58-1：メモに無い役割を 04 が書いた。"""
    code, ng, _ = check(make(r1="【工場長】L7／【営業】L9"))
    assert code == 1 and any(l.startswith("その行の役割ではない") and "L9" in l for l in ng)


def test_ng_when_role_count_differs(check):
    code, ng, _ = check(make(n1="3役割"))
    assert code == 1 and any(l.startswith("役割数が合わない") for l in ng)


def test_unknown_role_is_not_counted(check):
    assert check(make(r1="【工場長】L7／【不明】L10", n1="1役割（＋不明1行）"))[0] == 0
    code, ng, _ = check(make(r1="【工場長】L7／【不明】L10", n1="2役割"))
    assert code == 1 and any(l.startswith("役割数が合わない") for l in ng)


def test_ng_when_unknown_line_is_cited_but_not_noted(check):
    """63-2：【不明】を数えないので、添えないと話者の分からない根拠が③に見えない。"""
    code, ng, _ = check(make(r1="【工場長】L7／【不明】L10", n1="1役割"))
    assert code == 1 and any(l.startswith("【不明】の行を引いたのに") for l in ng)


def test_role_count_unknown_ok_only_when_all_unknown(check):
    assert check(make(r1="【不明】L10", n1="不明"))[0] == 0
    assert check(make(r1="【工場長】L7", n1="不明"))[0] == 1


def test_note_in_brackets_is_not_the_count(check):
    assert check(make(n1="2役割（工場長は当事者）"))[0] == 0


def test_ng_when_sec2_fact_has_no_line_number(check):
    code, ng, _ = check(make(f1="段取りが多い"))
    assert code == 1 and any(l.startswith("根拠にメモの行番号が無い") and "§2 #1" in l for l in ng)


def test_benchmark_table_is_not_checked(check):
    """§2 の2つ目の表（市場ベンチマーク）は見ない。行番号が無くても通る。"""
    assert check(make())[0] == 0


def test_ng_when_memo_missing(tmp_path):
    p = tmp_path / "04_現場分析.md"
    p.write_text(make(), encoding="utf-8")
    code, ng, _ = run_script("check_genba_ref", p)
    assert code == 1 and any("現場メモが無い" in l for l in ng)


def test_output_carries_no_role_names(check):
    """守秘：役割名・本文を出さない（出すのは節・行の番号とルール名）。"""
    _, _, out = check(make(r1="【工場長】L7／【営業】L9", n1="3役割", f1="段取り"))
    assert "工場長" not in out and "営業" not in out and "段取り" not in out


@pytest.mark.parametrize("line", ["> 【工場長】注記の引用", "# 現場メモ【架空】"])
def test_tag_outside_body_cannot_be_cited(check, line):
    """② が見つけた穴（09-29）：引用の注記・見出しの【…】を引くと1役割として通っていた。本文の行だけを引ける。"""
    memo = MEMO + f"\n{line}\n"                      # L11 は空行、L12 がこの行
    role = "工場長" if "工場長" in line else "架空"
    code, ng, _ = check(make(r1=f"【{role}】L12", n1="1役割"), memo=memo)
    assert code == 1 and any(l.startswith("引いた行がメモに無い") for l in ng)


def test_ng_when_joined_seed_is_strong(check):
    """62-4：②が別々の話をつないだ芽は、役割が複数でも中まで。「2役割が裏付けた」と③が読む入口。"""
    assert check(make(n1="2役割（つないだ）", s1="中"))[0] == 0
    assert check(make(n1="2役割", s1="強"))[0] == 0
    code, ng, _ = check(make(n1="2役割（つないだ）", s1="**強**"))
    assert code == 1 and any(l.startswith("つないだ芽が「強」") for l in ng)
