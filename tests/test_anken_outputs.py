"""案件出力テスト B1〜B10（段5）。

前半：合成データで「検査そのものが正しく判定するか」（通るべきものが通る／止めるべきものが止まる）。
後半：この端末の 案件/ に当てる。案件/ が無ければ skip（Windows・CI では走らない）。

★落ちたときに出すのは「ファイル:行 ルール名」だけ（anken_checks が本文を返さない）。
  pytest の比較表示で本文が出ないよう、実案件は pytest.fail に安全な文字列だけを渡す。
★封は開かない（conftest の seal_guard が保証）。
"""
import os
import re
from pathlib import Path

import pytest

import anken_checks as A
from conftest import REPO

# ── 合成データ ─────────────────────────────────────


GOOD_04 = """# 04｜現場分析｜架空

## 0. 独立性の宣言

- [x] `03_仮説_封.md` を**読んでいない**
- [x] `01` と `02` のみ参照した

## 1. 真因の芽リスト

| # | 真因の芽 | 根拠 | **強度** | **情報源の役割数** | 整合 | タグ |
|---|---|---|---|---|---|---|
| 1 | 段取り替えが長い | 課長 | 中 | **1役割** | | `#現場オペ` |
| 2 | | | | | | |

## 2. 建前と現場のズレ一覧

| # | 建前 | 現場の事実 | 差分 | **同じものを測っているか** | タグ |
|---|---|---|---|---|---|
| 1 | 不良率0.1% | 工程内で止めた数 | — | **いいえ（層が違う）** | `#現場オペ` |

### 市場ベンチマークとのズレ

| ベンチマーク（`01`§3） | 現場の数字 | **状態** | 差 |
|---|---|---|---|
| 平均残業 | なし | **片側欠測（現場の数字なし）** | |

## 3. 人間が現場で確認すべき点（次のヒアリング用）

1. 段取り替えの記録はどこにあるか

## 4. カバレッジ（`02` の問いはどこまで潰せたか）

| 区分 | 問い番号 | 状態 |
|---|---|---|
| 答えが取れた | Q1・Q3 | ✓ |
| 聞けなかった | | ✗（理由： ） |
"""

GOOD_05 = """# 05｜反証レポート｜架空

## 0. 開封記録

| 項目 | 記録 |
|---|---|
| `04` を読んだ日時 | 2026-01-01 10:00 |
| `03` を開封した日時 | 2026-01-01 10:30 |
| 順序は正しいか | ☑ 04を先に読んだ |
| `02b` の記入欄 | ☐ 空欄のまま（理由を §7 に） |

## 1. クロス表（★ここが本体）

| # | `03`の仮説（外から） | `04`の現場所見（中から） | **結論** | **機序** | 解釈（決着させない） |
|---|---|---|---|---|---|
| 1 | H1 | 芽1 | 一致 | — | 同じ |

## 2. 反証サマリー

| 判定 | 件数 |
|---|---|
| 採用 | 1 |
| 要検証 | 0 |
| 棄却 | 1 |
| **判定不能**（材料が足りず判定自体ができない） | 0 |

## 3. 仮説ごとの判定表

| # | 仮説 | 判定 | 根拠の強さ | 落ちたテスト |
|---|---|---|---|---|
| 1 | 段取り替えが長い | 採用 | 中 | |
| 2 | 前社長の方針が残っている | 棄却 | 弱 | ②代表性 |

### ★前提が崩れた仮説（Stage 2-0 の結果）

なし

## 4. 現場で確認すべき決定的な問い

| # | 問い | 出所 | **行き先** | なぜ |
|---|---|---|---|---|
| 1 | 段取り替えは1回何分かかっていますか | 芽1 | 顧客可 | 採用 |
| 2 | 前社長の方針は今も生きていると思いますか | H3 | **社内のみ** | 棄却から出た |

## 5. AIに頼りすぎ注意

- 業界の一般論に寄りかかった箇所は無い

## 6. ★③が新しく作った仮説の申告

| # | ③が作った解釈 | なぜ | 対抗仮説 | 判定 |
|---|---|---|---|---|
| 1 | | | | |

なし

## 7. `02b`（主任診断士の見立て）との突き合わせ

`02b` は無い。

## 8. ★人間の判断が必要な論点（主任診断士への引き渡し）

| # | 判断が必要な論点 | 理由 | 行き先 |
|---|---|---|---|
| 1 | 後継の話をどう切り出すか | 対人 | `07` |

## 9. ★比べていないもの

| 項目 | ベンチマーク側 | 現場側 | 状態 | `06` に書くか |
|---|---|---|---|---|
| 不良率 | あり | なし | 片側欠測 | 書く |
"""

GOOD_06 = """# 現状の整理と、確かめたいこと｜架空 御中

## はじめに

本人が書いた文。

## エグゼクティブサマリー

段取り替えの長さが、うかがったお話の中心でした。

## 御社の現状（外から見えること）

公開情報では金属加工。

## お話から見えてきたこと（1点）

断定ではなく、お話からはそう見えるという段階です。

うかがったお話ではこう見えます。

## 一緒に確かめたい問い

- 段取り替えは1回何分かかっていますか

## この診断が見た範囲

- 課長1名に遠隔で。見て確かめたものは1件も含まれていません

## この診断の限界

- 不良率は、まだ比べていません

## 本レポートで踏み込んでいない領域

- 法令の適合の判定

## 次の一歩

- 続けるかは御社が決める

## 出典

- 御社ウェブサイト（2026-01 閲覧）
"""

GOOD_07 = """# 07

## 1. 人間の判断が必要な論点

| # | 論点 | 理由 |
|---|---|---|
| 1 | 後継の話をどう切り出すか | 対人 |

## 3. ★③が新しく作った仮説

| # | ③が作った解釈 | 対抗仮説 | `06` での扱い |
|---|---|---|---|
| 1 | | | |

## 4. ★「社内のみ」の問い

| # | 問い | 出所（棄却された仮説） | なぜ社内のみか |
|---|---|---|---|
| 1 | 前社長の方針は今も生きていると思いますか | H3 | 棄却由来 |
"""

MEMO_REMOTE = "| 話者 | 課長 |\n| いつ | 2026-01-01 |\n| どこで（現地／遠隔） | 遠隔（Zoom） |\n| 誰から | 直接 |\n"


@pytest.fixture
def anken(tmp_path):
    def make(**files):
        d = tmp_path / "案件Z"
        (d / "_材料" / "B_現場").mkdir(parents=True, exist_ok=True)
        names = {"s01": A.F01, "s01i": A.F01I, "s02": A.F02,
                 "s04": A.F04, "s05": A.F05, "s06": A.F06, "s07": A.F07, "memo": A.MEMO}
        for k, v in files.items():
            if v is not None:
                (d / names[k]).write_text(v, encoding="utf-8")
        return str(d)
    return make


def rules(violations):
    return sorted({v.split(" ", 1)[1].split(" ", 1)[0] for v in violations})


def test_good_set_passes(anken):
    d = anken(s01="x", s01i="x", s02="x", s04=GOOD_04, s05=GOOD_05, s06=GOOD_06, s07=GOOD_07, memo=MEMO_REMOTE)
    assert A.check_anken(d) == []


def test_violation_strings_carry_no_body_text(anken):
    """★本文を返さない：違反文字列に合成データの語が1つも入らない。"""
    bad05 = GOOD_05.replace("顧客可 | 採用", " | 採用")
    bad06 = GOOD_06 + "\n前社長の方針は今も生きていると思いますか\n"
    d = anken(s04=GOOD_04.replace("| 中 |", "| |"), s05=bad05, s06=bad06, s07=GOOD_07, memo=MEMO_REMOTE)
    out = "\n".join(A.check_anken(d))
    assert out
    for word in ["段取り", "前社長", "課長", "後継", "不良率", "架空"]:
        assert word not in out


# B1
@pytest.mark.parametrize("mut", [
    lambda s: s.replace("[x]", "[ ]"),
    lambda s: s.replace("## 0. 独立性の宣言", "## 0. 独立性の宣言\n\n- [ ] 現場メモは {日付} に取得"),
    lambda s: s.replace("## 0. 独立性の宣言", "## 0. 別の節"),
])
def test_b1_ng(mut):
    assert "B1" in rules(A.b1_04_independence(mut(GOOD_04)))


# B2
@pytest.mark.parametrize("old,new", [
    ("**いいえ（層が違う）**", ""),
    ("**いいえ（層が違う）**", "**はい**／**いいえ（層が違う）**"),
    ("**片側欠測（現場の数字なし）**", ""),
    ("**片側欠測（現場の数字なし）**", "比較できた／比較不能（両側なし）"),
])
def test_b2_ng(old, new):
    assert rules(A.b2_04_states(GOOD_04.replace(old, new))) == ["B2"]


def test_b2_nai_containing_hai_is_not_a_template_choice():
    """#57：「いいえ（層が違う。並べてはいけない）」は答え。「てはい」の「はい」で選択肢の残りと読まない。"""
    s = GOOD_04.replace("**いいえ（層が違う）**", "**いいえ（層が違う。並べてはいけない）**")
    assert A.b2_04_states(s) == []


@pytest.mark.parametrize("v", ["はい／いいえ", "はい/いいえ", "**はい**／**いいえ**"])
def test_b2_template_choice_left_is_ng(v):
    assert "B2" in rules(A.b2_04_states(GOOD_04.replace("**いいえ（層が違う）**", v)))


def test_b2_ok():
    assert A.b2_04_states(GOOD_04) == []


# B3
@pytest.mark.parametrize("old,new", [("| 中 |", "| |"), ("| 中 |", "| 強／中／弱 |"), ("**1役割**", "")])
def test_b3_ng(old, new):
    assert rules(A.b3_04_strength(GOOD_04.replace(old, new))) == ["B3"]


def test_b3_unknown_role_count_is_a_written_value():
    """#57：話者の無い記述では役割数を数えられない。「不明」は空欄ではない（CLAUDE.md §4-2）。"""
    assert A.b3_04_strength(GOOD_04.replace("**1役割**", "不明（話者の記載なし）")) == []


def test_b3_blank_role_count_is_still_ng():
    assert "B3" in rules(A.b3_04_strength(GOOD_04.replace("**1役割**", "")))


@pytest.mark.parametrize("new", ["| **中**（1役割。定義上は「強」も成り立つ → §6 付記） |", "| 中（強とも読める） |"])
def test_b3_note_in_brackets_is_not_a_second_value(new):
    """段8 R2 で②が強度に注記を添えた。括弧の中の「強」を2つ目の値と数えない。"""
    assert A.b3_04_strength(GOOD_04.replace("| 中 |", new)) == []


@pytest.mark.parametrize("new", ["| 強／中／弱（未記入） |", "| （中） |"])
def test_b3_note_does_not_hide_missing_value(new):
    """括弧の前に値が1つ無ければ、注記があっても NG。"""
    assert rules(A.b3_04_strength(GOOD_04.replace("| 中 |", new))) == ["B3"]


# B4
@pytest.mark.parametrize("old,new", [
    ("2026-01-01 10:00", ""),
    ("☑ 04を先に読んだ", "☐ 04を先に読んだ ／ ☐ 逆"),
])
def test_b4_ng(old, new):
    assert rules(A.b4_05_opening(GOOD_05.replace(old, new))) == ["B4"]


def test_b4_single_unchecked_box_with_reason_is_a_record():
    """「☐ 空欄のまま（理由）」は意図した記録。未記入ではない（_TEST_案件C で誤検出した）。"""
    assert A.b4_05_opening(GOOD_05) == []


# B5
@pytest.mark.parametrize("new", ["", "顧客可／**社内のみ**"])
def test_b5_ng(new):
    assert rules(A.b5_05_destination(GOOD_05.replace("| 顧客可 |", f"| {new} |"))) == ["B5"]


def test_b5_ng_when_no_destination_column():
    s = GOOD_05.replace("| # | 問い | 出所 | **行き先** | なぜ |", "| # | 問い | 出所 | 優先 | なぜ |")
    assert rules(A.b5_05_destination(s)) == ["B5"]


def test_b5_ng_when_questions_are_a_list():
    s = GOOD_05.split("## 4.")[0] + "## 4. 問い\n\n1. 何分ですか\n\n## 6." + GOOD_05.split("## 6.")[1]
    assert rules(A.b5_05_destination(s)) == ["B5"]


# B6
def test_b6_ng_when_empty():
    assert rules(A.b6_05_new_hypotheses(GOOD_05.replace("\nなし\n", "\n"))) == ["B6"]


def test_b6_ok_with_row():
    s = GOOD_05.replace("\nなし\n", "\n").replace("| 1 | | | | |", "| 1 | 別の筋 | 突き合わせ | 偶然 | 要検証 |")
    assert A.b6_05_new_hypotheses(s) == []


def test_b6_found_by_name_not_number():
    assert A.b6_05_new_hypotheses(GOOD_05.replace("## 6. ★③", "## 9. ★③")) == []


def test_b6_ng_when_section_missing():
    s = GOOD_05.replace("## 6. ★③が新しく作った仮説の申告", "## 6. 別の節")
    assert rules(A.b6_05_new_hypotheses(s)) == ["B6"]


# B7
def test_b7_ng_when_internal_question_copied_to_06():
    s06 = GOOD_06 + "- 前社長の方針は、今も生きていると思いますか？\n"
    assert rules(A.b7_internal_questions_not_in_06(GOOD_05, s06)) == ["B7"]


def test_b7_ignores_internal_memo_in_06():
    s06 = GOOD_06 + "<!-- 前社長の方針は今も生きていると思いますか -->\n"
    assert A.b7_internal_questions_not_in_06(GOOD_05, s06) == []


def test_b7_customer_questions_may_appear():
    assert A.b7_internal_questions_not_in_06(GOOD_05, GOOD_06) == []


# B8
@pytest.mark.parametrize("s06", [
    GOOD_06.replace("# 現状の整理と、確かめたいこと", "# 課題仮説レポート"),
    GOOD_06 + "\n## 見えてきた本質的な課題\n",
    GOOD_06 + "\nこれが課題である。\n",
])
def test_b8_ng_on_observation_zero(s06):
    assert rules(A.b8_observation_zero(MEMO_REMOTE, s06)) == ["B8"]


@pytest.mark.parametrize("where,site", [
    ("現地", True), ("現地（工場に入った）", True), ("遠隔（Zoom）。現地には入っていない", False),
    ("遠隔", False), ("不明（記憶が曖昧）", False), ("現地と遠隔の両方（初回は現地）", True),
    ("遠隔（Zoom）、現地（工場見学）", True),          # テンプレ「両方なら両方書く」
    ("遠隔（書面）／現地訪問なし", False), ("遠隔。現地は未訪問", False)])
def test_b8_on_site_is_unnegated_genchi(where, site):
    """否定されていない「現地」があれば観察あり。含むかだけ（案件Dで誤読）でも、最初の語だけ（両方書く、で誤読）でもない。"""
    assert A.on_site(where) is site


def test_b8_does_not_apply_when_on_site():
    memo = MEMO_REMOTE.replace("遠隔（Zoom）", "現地")
    assert A.b8_observation_zero(memo, "# 課題仮説レポート\nこれが課題である。\n") == []


# B9
def test_b9_ng_when_07_missing(anken):
    d = anken(s05=GOOD_05, s06=GOOD_06)
    assert rules(A.b9_07_exists_and_complete(d, GOOD_05)) == ["B9"]


def test_b9_ng_when_07_has_fewer_items(anken):
    s05 = GOOD_05.replace("| 1 | 後継の話をどう切り出すか | 対人 | `07` |",
                          "| 1 | 後継の話をどう切り出すか | 対人 | `07` |\n| 2 | 値上げの伝え方 | 対人 | `07` |")
    d = anken(s05=s05, s06=GOOD_06, s07=GOOD_07)
    assert rules(A.b9_07_exists_and_complete(d, s05)) == ["B9"]


def test_b9_no_06_no_requirement(anken):
    assert A.b9_07_exists_and_complete(anken(s05=GOOD_05), GOOD_05) == []


# B10
def test_b10_ng_on_new_tag():
    assert rules(A.b10_tags(A.F04, GOOD_04.replace("`#現場オペ` |\n| 2", "`#人材` |\n| 2"))) == ["B10"]


# ── この端末の実案件 ─────────────────────────────────


ANKEN = REPO / "案件"
# テンプレより前に作られた成果物（検査が正しく、成果物が古い）。案件名 → 許すルールと理由
KNOWN = {
    "_TEST_案件C": ({"B5", "B6", "B13", "B16", "B21", "B25", "B32", "B33"}, "B32・B33：07 は 08-19 作成。01i の代用を 07 に書く規則は 09-20（97e7728）、束ね方は本人が決めるは 09-25（5c3c154）に入った。B25：06 は 09-19 作成なのに、08-30（fe5074e）にテンプレに入った「本レポートで踏み込んでいない領域」が無い。実走 #16 と同じ根（古い 06 を土台にした）。TEST なので直さない。B16：§1 の機序の列と §3 の前提の専用表は 08-20（3a1c59b）にテンプレに入った。B21：06 は 09-19 作成、根拠の種類の表は 09-23（320fcd1・C-4）にテンプレに入った。05 は 08-19 作成。B13（比べていないもの）の節もテンプレに入る前。§4 の「行き先」列（08-20 0ed94cb）と「③が新しく作った仮説の申告」節"
                                  "（08-20 3a1c59b）はその翌日にテンプレに入った。この TEST 自身が後者の欠落を見つけた（05 §7 #4）"),
    "案件D": ({"B42"}, "B42：「はじめに」（本人が書く欄）に常体の文（〜させる。）が1つ。09-29 に B42 が「る・う」の文末も見るようにして初めて出た。"
                       "デモで提出しない（09-27 本人）ので後から書き換えない（09-27 の取得ログ・凍結宣言と同じ扱い）"),
}


def _cases():
    if not ANKEN.is_dir():
        return []
    out = []
    for d in sorted(ANKEN.iterdir()):
        if d.is_dir() and d.name != "_使わない" and any((d / f).exists() for f in (A.F04, A.F05, A.F06)):
            out.append(d.name)
    return out


CASES = _cases()


@pytest.mark.skipif(not CASES, reason="案件/ に出力のある案件が無い（この端末では診断していない）")
@pytest.mark.parametrize("name", CASES or ["-"])
def test_real_anken_outputs(name):
    allowed, why = KNOWN.get(name, (set(), ""))
    found = A.check_anken(str(ANKEN / name))
    got = set(rules(found))
    bad = [v for v in found if rules([v])[0] not in allowed]
    if bad:
        pytest.fail(f"{name}：" + " ／ ".join(bad), pytrace=False)
    if allowed - got:
        pytest.fail(f"{name}：既知の {sorted(allowed - got)} が出なくなった。KNOWN から外す（{why}）", pytrace=False)


# ── 段5の点検（別エージェント）で見つかった穴の再発防止 ─────────────

MEMO_TEMPLATE_ROW = "| **どこで** | {v} | **`現地`**（工場・事務所に入った）／**`遠隔`**（Zoom・電話・書面）。両方なら両方書く |\n"


@pytest.mark.parametrize("v,site", [("遠隔（Zoom）", False), ("現地", True)])
def test_b8_reads_template_format_memo(v, site):
    """テンプレは太字の欄名＋3列。2列目だけを読む（3列目の説明文の「現地」を拾わない）。"""
    assert A.on_site(A._where(MEMO_TEMPLATE_ROW.format(v=v))) is site


def test_b8_applies_to_template_format_memo():
    memo = MEMO_TEMPLATE_ROW.format(v="遠隔（Zoom）")
    assert rules(A.b8_observation_zero(memo, "# 課題仮説レポート\n")) == ["B8"]


def test_b8_negated_kadai_is_allowed():
    s06 = GOOD_06 + "\nこれが課題であると断定する段階ではありません。\n"
    assert A.b8_observation_zero(MEMO_REMOTE, s06) == []


def test_b4_template_text_left_as_is_is_ng():
    s = GOOD_05.replace("| 順序は正しいか | ☑ 04を先に読んだ |",
                        "| **順序は正しいか** | ☐ 04を先に読み、03を後に開封した |")
    assert rules(A.b4_05_opening(s)) == ["B4"]


def test_b6_nashi_inside_table_cell_is_not_a_declaration():
    s = GOOD_05.replace("\nなし\n", "\n").replace("| 1 | | | | |", "| 1 | | | なし | |")
    assert rules(A.b6_05_new_hypotheses(s)) == ["B6"]


@pytest.mark.parametrize("cell", ["`#財務`。", "(#財務)", "（#組織）"])
def test_b10_punctuation_is_not_part_of_tag(cell):
    s = GOOD_04.replace("| `#現場オペ` |\n| 2", f"| {cell} |\n| 2")
    assert A.b10_tags(A.F04, s) == []


# ── 既存の検査スクリプトを実案件に当てる（段7。CHECK.md の 🤖 印の裏付け）──────────
# ★NG 行には本文の断片が入りうる（check_genba_mark は値を40字まで出す）。
#   ここでは「：」「（」より前のルール名だけを残し、値は出さない。

import re as _re

from conftest import run_script

SCRIPT_ON = [  # (スクリプト, 案件内のファイル, 追加の引数)
    ("check_genba_mark", A.MEMO, []),
    ("check_genba_ref", A.F04, []),
    ("lint_01", "01_外形カード_事実編.md", []),
    ("check_report", A.F06, ["--draft"]),
]
# テンプレ・ルールより前に作られた成果物（検査が正しく、成果物が古い）。(案件, スクリプト) → 理由
_OLD_TEST = "ルールより前に作られた TEST の成果物。段8で _TEST_配管検証 を作り直して通し直すとき、NG が消えたら外す"
KNOWN_SCRIPT = {
    ("_TEST_案件C", "check_genba_mark"): "メモは 08-19 作成。4印（09-22）より前",
    ("_TEST_案件C", "lint_01"): "01 の最終更新は 09-19（定規化 #14 と同日。以後の lint の強化を受けていない）。" + _OLD_TEST,
    ("_TEST_案件C", "check_report"): "06 の最終更新は 09-19。太字・構造検査（#44・#47・09-24〜25）より前。" + _OLD_TEST,
    ("_TEST_配管検証", "lint_01"): "01 は 08-07 作成。定規化（#14・09-19）より前。" + _OLD_TEST,
    ("_TEST_案件C", "check_genba_ref"): "04 は 08-19 作成。現場メモの各行の【役割】と 04 の【役割】L行番号は 09-29（実走 #58 の対策 (b)）から。" + _OLD_TEST,
    ("案件D", "check_genba_mark"): "メモの最終更新は 09-22。現場メモの各行の【役割】と 04 の【役割】L行番号は 09-29（実走 #58 の対策 (b)）から。デモで回し直さない（09-27 本人）",
    ("案件D", "check_genba_ref"): "04 の最終更新は 09-20。現場メモの各行の【役割】と 04 の【役割】L行番号は 09-29（実走 #58 の対策 (b)）から。デモで回し直さない（09-27 本人）",
}


def _rule_only(line):
    return _re.split(r"[：（「]", _re.sub(r"^L\d+\s*", "", line), maxsplit=1)[0].strip()


def _script_cases():
    out = []
    for name in CASES:
        for script, rel, extra in SCRIPT_ON:
            if (ANKEN / name / rel).exists():
                out.append((name, script, rel, extra))
    return out


SCRIPT_CASES = _script_cases()


@pytest.mark.skipif(not SCRIPT_CASES, reason="案件/ に対象ファイルが無い")
@pytest.mark.parametrize("name,script,rel,extra", SCRIPT_CASES or [("-", "-", "-", [])],
                         ids=[f"{n}:{s}" for n, s, *_ in SCRIPT_CASES] or ["-"])
def test_real_anken_scripts(name, script, rel, extra):
    code, ng, _ = run_script(script, *extra, ANKEN / name / rel)
    known = KNOWN_SCRIPT.get((name, script))
    if code != 0 and not known:
        rules_ = sorted({_rule_only(l) for l in ng})
        pytest.fail(f"{name}/{rel}：{script} が NG {len(ng)} 件（{' ／ '.join(rules_)}）", pytrace=False)
    if code == 0 and known:
        pytest.fail(f"{name}：{script} の既知の NG が出なくなった。KNOWN_SCRIPT から外す（{known}）", pytrace=False)


# ── 段9：CHECK.md の M 項目を移す（仕分け表 #68・#69・#70・#83）───────────

# B11（#68）
def test_b11_ng_when_human_section_missing():
    s = GOOD_05.replace("## 8. ★人間の判断が必要な論点（主任診断士への引き渡し）", "## 8. 別の節")
    assert rules(A.b11_05_human_section(s)) == ["B11"]


def test_b11_accepts_old_heading_before_z10():
    s = GOOD_05.replace("人間の判断が必要な論点（主任診断士への引き渡し）", "人間（主任診断士）への引き渡し")
    assert A.b11_05_human_section(s) == []


# B12（#69）
@pytest.mark.parametrize("reason", ["", "⓪前提 ①証拠 ②代表性 ③因果 ④対抗 ⑤反証条件 ⑥AI依存"])
def test_b12_ng_when_rejection_has_no_reason(reason):
    s = GOOD_05.replace("| 棄却 | 弱 | ②代表性 |", f"| 棄却 | 弱 | {reason} |")
    assert rules(A.b12_05_rejection_reason(s)) == ["B12"]


def test_b12_template_choice_row_is_not_a_rejection():
    s = GOOD_05.replace("| 棄却 | 弱 | ②代表性 |", "| 採用/要検証/棄却/判定不能 | | |")
    assert A.b12_05_rejection_reason(s) == []


# B13（#70）
def test_b13_ng_when_empty():
    s = GOOD_05.replace("| 不良率 | あり | なし | 片側欠測 | 書く |", "| | あり／なし | あり／なし | 比較不能／片側欠測 | 書く |")
    assert rules(A.b13_05_not_compared(s)) == ["B13"]


def test_b13_ok_when_nashi():
    s = GOOD_05.replace("| 不良率 | あり | なし | 片側欠測 | 書く |", "| | | | | |") + "\nなし\n"
    assert A.b13_05_not_compared(s) == []


def test_b13_example_row_does_not_count():
    s = GOOD_05.replace("| 不良率 | あり | なし | 片側欠測 | 書く |", "| 例：客先流出の不良率 | a | b | c | d |")
    assert rules(A.b13_05_not_compared(s)) == ["B13"]


def test_b13_ng_when_section_missing():
    assert rules(A.b13_05_not_compared(GOOD_05.replace("## 9. ★比べていないもの", "## 9. 別の節"))) == ["B13"]


# B14（#83）
def test_b14_ng_when_limits_empty():
    s06 = GOOD_06.replace("- 不良率は、まだ比べていません\n", "")
    assert rules(A.b14_limits_in_06(GOOD_05, s06)) == ["B14"]


def test_b14_ng_when_limits_only_in_comment():
    s06 = GOOD_06.replace("- 不良率は、まだ比べていません", "<!-- 不良率は、まだ比べていません -->")
    assert rules(A.b14_limits_in_06(GOOD_05, s06)) == ["B14"]


def test_b14_not_required_when_nothing_uncompared():
    s05 = GOOD_05.replace("| 不良率 | あり | なし | 片側欠測 | 書く |", "| | | | | |") + "\nなし\n"
    assert A.b14_limits_in_06(s05, GOOD_06.replace("- 不良率は、まだ比べていません\n", "")) == []


# ── B15〜B22（移行後の B 群の延長） ─────────────────


def _one(rule, found):
    return rule in rules(found)


@pytest.mark.parametrize("mut", [
    lambda s: s.replace("1. 段取り替えの記録はどこにあるか", "1.\n2."),
    lambda s: s.replace("## 3. 人間が現場で確認すべき点", "## 3. 別の節"),
    lambda s: s.replace("Q1・Q3", ""),
    lambda s: s.replace("## 4. カバレッジ", "## 4. 別の節"),
])
def test_b15_ng(mut):
    assert _one("B15", A.b15_04_sections(mut(GOOD_04)))


def test_b15_ok_when_no_02():
    s = GOOD_04.replace("Q1・Q3", "").replace("| 聞けなかった |", "`02` なし\n\n| 聞けなかった |")
    assert A.b15_04_sections(s) == []


@pytest.mark.parametrize("head", ["## 1. クロス表", "## 2. 反証サマリー", "## 3. 仮説ごとの判定表", "## 5. AIに頼りすぎ注意", "## 7. `02b`"])
def test_b16_ng_when_section_missing(head):
    assert _one("B16", A.b16_05_sections(GOOD_05.replace(head, "## 別の節")))


@pytest.mark.parametrize("old, new", [("| 採用 | 1 |", "| 採用 | 2 |"), ("| 棄却 | 1 |", "| 棄却 | 0 |"), ("| 要検証 | 0 |", "| 要検証 | 1 |")])
def test_b17_ng_when_counts_differ(old, new):
    assert _one("B17", A.b17_05_summary_matches(GOOD_05.replace(old, new)))


def test_b17_ng_when_summary_blank():
    s = GOOD_05
    for k in ("| 採用 | 1 |", "| 要検証 | 0 |", "| 棄却 | 1 |", "判定自体ができない） | 0 |"):
        s = s.replace(k, k.rsplit("|", 2)[0] + "| |")
    assert _one("B17", A.b17_05_summary_matches(s))


def test_b17_premise_table_is_not_counted_twice():
    s = GOOD_05.replace("\n## 4. 現場で確認すべき決定的な問い", "\n### ★前提が崩れた仮説\n\n| # | 仮説 | 崩れた前提 | 判定 |\n|---|---|---|---|\n| 2 | 前社長の方針 | 人数 | 棄却 |\n\n## 4. 現場で確認すべき決定的な問い")
    assert A.b17_05_summary_matches(s) == []


def test_b17_first_word_decides():
    s = GOOD_05.replace("| 段取り替えが長い | 採用 |", "| 段取り替えが長い | 採用（要検証寄り） |")
    assert A.b17_05_summary_matches(s) == []


NEW_HYP = "| 1 | 後継が決まらない | 芽1×H2 | なし | {j} |"


def test_b18_ng_when_self_approved():
    s = GOOD_05.replace("| 1 | | | | |\n\nなし", NEW_HYP.format(j="採用"))
    assert _one("B18", A.b18_05_no_self_approval(s))


def test_b18_ok_when_to_be_verified():
    s = GOOD_05.replace("| 1 | | | | |\n\nなし", NEW_HYP.format(j="**要検証**（原則）"))
    assert A.b18_05_no_self_approval(s) == []


@pytest.mark.parametrize("key", ["## エグゼクティブサマリー", "## 御社の現状", "## 出典", "## お話から見えてきたこと"])
def test_b19_ng_when_section_missing(key):
    assert _one("B19", A.b19_06_sections(GOOD_06.replace(key, "## 別の節")))


@pytest.mark.parametrize("filler", ["- ", "<!-- 内部メモ：05 判定表 1 -->"])
def test_b19_ng_when_sources_empty(filler):
    assert _one("B19", A.b19_06_sections(GOOD_06.replace("- 御社ウェブサイト（2026-01 閲覧）", filler)))


def _06_with(n, table=True):
    ev = ("| | 御社の発信と、お話が異なっていた点 | 数字でうかがえたもの | まだ決めていないこと |\n"
          "|---|---|---|---|\n| 1 | 1点 | なし | — |\n\n") if table else ""
    body = f"## お話から見えてきたこと（{n}点）\n\n{ev}" + "".join(f"### 課題{i}：見出し{i}\n\n- 何が起きているか\n\n" for i in range(1, n + 1))
    return GOOD_06.replace("## お話から見えてきたこと（1点）\n\n断定ではなく、お話からはそう見えるという段階です。\n\nうかがったお話ではこう見えます。\n", body)


def test_b20_ng_when_four_issues():
    assert _one("B20", A.b20_06_at_most_three(_06_with(4)))


def test_b20_ok_with_three():
    assert A.b20_06_at_most_three(_06_with(3)) == []


def test_b21_ng_when_two_issues_without_table():
    assert _one("B21", A.b21_06_evidence_table(_06_with(2, table=False)))


def test_b21_ok_with_table_and_single_issue_needs_none():
    assert A.b21_06_evidence_table(_06_with(2)) == []
    assert A.b21_06_evidence_table(_06_with(1, table=False)) == []


def test_b22_ng_when_internal_question_not_transferred(anken):
    s07 = GOOD_07.replace("| 1 | 前社長の方針は今も生きていると思いますか | H3 | 棄却由来 |", "| 1 | | | |")
    d = anken(s04=GOOD_04, s05=GOOD_05, s06=GOOD_06, s07=s07, memo=MEMO_REMOTE)
    assert _one("B22", A.check_anken(d))


def test_b22_ng_when_new_hypothesis_not_transferred(anken):
    s05 = GOOD_05.replace("| 1 | | | | |\n\nなし", NEW_HYP.format(j="要検証"))
    d = anken(s04=GOOD_04, s05=s05, s06=GOOD_06, s07=GOOD_07, memo=MEMO_REMOTE)
    assert _one("B22", A.check_anken(d))


# ── RC の厳密化（09-28）：済にした行の「機械で判定できる部分」を全部見る ─────


@pytest.mark.parametrize("mut, why", [
    (lambda s: s.replace("| **結論** | **機序** |", "| **結論** | 何か |"), "§1 の列"),
    (lambda s: s.replace("### ★前提が崩れた仮説（Stage 2-0 の結果）", "### 別の表"), "前提の専用表"),
    (lambda s: s.replace("- 業界の一般論に寄りかかった箇所は無い", "-"), "§5 が空"),
    (lambda s: s.replace("`02b` は無い。", ""), "§7 が空"),
])
def test_b16_rigor_ng(mut, why):
    assert _one("B16", A.b16_05_sections(mut(GOOD_05))), why


def test_b16_premise_heading_by_stage_name():
    s = GOOD_05.replace("### ★前提が崩れた仮説（Stage 2-0 の結果）", "### ★前提の表（Stage 2-0 の結果）")
    assert A.b16_05_sections(s) == []


def test_b17_ng_when_a_judgement_row_is_missing():
    s = GOOD_05.replace("| **判定不能**（材料が足りず判定自体ができない） | 0 |\n", "")
    assert _one("B17", A.b17_05_summary_matches(s))


def test_b19_ng_when_summary_over_three_lines():
    s = GOOD_06.replace("段取り替えの長さが、うかがったお話の中心でした。", "一。\n二。\n三。\n四。")
    assert _one("B19", A.b19_06_sections(s))


def test_b19_three_lines_ok():
    s = GOOD_06.replace("段取り替えの長さが、うかがったお話の中心でした。", "一。\n二。\n三。")
    assert A.b19_06_sections(s) == []


def test_b21_ng_when_table_after_first_heading():
    s = _06_with(2)
    table = s[s.index("| | 御社の発信と、お話が異なっていた点"):s.index("### 課題1")]
    s = s.replace(table, "").replace("- 何が起きているか\n\n### 課題2", "- 何が起きているか\n\n" + table + "### 課題2")
    assert _one("B21", A.b21_06_evidence_table(s))


ITEMS = "- **何が起きているか**：a\n- **なぜか（仮説）**：b\n- **根拠**：c\n- **放置するとどうなるか**：d\n"


def test_b23_ok_with_four_items():
    s = _06_with(2).replace("- 何が起きているか\n", ITEMS)
    assert A.b23_06_issue_items(s) == []


@pytest.mark.parametrize("drop", ["- **根拠**：c\n", "- **放置するとどうなるか**：d\n"])
def test_b23_ng_when_item_missing(drop):
    s = _06_with(2).replace("- 何が起きているか\n", ITEMS.replace(drop, ""))
    assert _one("B23", A.b23_06_issue_items(s))


def test_b23_no_issue_heading_no_requirement():
    assert A.b23_06_issue_items(GOOD_06) == []


def test_b24_ng_when_counter_hypothesis_blank(anken):
    s07 = GOOD_07.replace("| 1 | | | |\n\n## 4.", "| 1 | 後継が決まらない | | 載せていない |\n\n## 4.")
    d = anken(s04=GOOD_04, s05=GOOD_05, s06=GOOD_06, s07=s07, memo=MEMO_REMOTE)
    assert _one("B24", A.check_anken(d))


def test_b24_ok_with_counter_hypothesis(anken):
    s07 = GOOD_07.replace("| 1 | | | |\n\n## 4.", "| 1 | 後継が決まらない | 人手不足 | 載せていない |\n\n## 4.")
    d = anken(s04=GOOD_04, s05=GOOD_05, s06=GOOD_06, s07=s07, memo=MEMO_REMOTE)
    assert not _one("B24", A.check_anken(d))


def test_b25_template_heads_are_read_from_template():
    heads = A.template_heads_06()
    for h in ("はじめに", "エグゼクティブサマリー", "出典", "見えてきた本質的な課題"):
        assert h in heads


def test_b25_ng_when_hajimeni_not_first():
    s = GOOD_06.replace("## はじめに\n\n本人が書いた文。\n\n", "").replace("## 出典", "## はじめに\n\n本人が書いた文。\n\n## 出典")
    assert _one("B25", A.b25_06_matches_template(s))


@pytest.mark.parametrize("head", ["## 次の一歩", "## この診断が見た範囲", "## 本レポートで踏み込んでいない領域"])
def test_b25_ng_when_template_section_missing(head):
    assert _one("B25", A.b25_06_matches_template(GOOD_06.replace(head, "## 別の節")))


def test_b25_ok_with_observation_zero_issue_name():
    assert A.b25_06_matches_template(GOOD_06) == []


def test_b25_heading_only_inside_memo_is_missing():
    s = GOOD_06.replace("## 次の一歩", "<!--\n## 次の一歩\n-->")
    assert _one("B25", A.b25_06_matches_template(s))



# ── B26〜B28：05 の形（shinin-hansho #444・#379・#417） ─────────


def test_b26_ng_when_adopted_without_04(anken):
    d = anken(s05=GOOD_05, s06=GOOD_06, s07=GOOD_07, memo=MEMO_REMOTE)
    assert _one("B26", A.check_anken(d))


def test_b26_not_applied_when_04_exists(anken):
    d = anken(s04=GOOD_04, s05=GOOD_05, s06=GOOD_06, s07=GOOD_07, memo=MEMO_REMOTE)
    assert not _one("B26", A.check_anken(d))


def test_b26_ok_without_adoption():
    s = GOOD_05.replace("| 段取り替えが長い | 採用 |", "| 段取り替えが長い | 要検証 |") + "\n現場側が無い状態での格付け。\n"
    assert A.b26_05_no_adopt_without_04(s) == []


B_ONLY = "| 1 | H1 | 芽1 | 一致 | — | 同じ |\n| 2 | {v} | 芽2 | **B軸のみ** | — | 捨てない |"


def test_b27_ok_good():
    assert A.b27_05_cross_03_column(GOOD_05) == []


@pytest.mark.parametrize("v", ["**（①には無い）**", "（①の仮説には無い。現場だけ）", "（①にはない）"])
def test_b27_ok_b_axis_marked(v):
    assert A.b27_05_cross_03_column(GOOD_05.replace("| 1 | H1 | 芽1 | 一致 | — | 同じ |", B_ONLY.format(v=v))) == []


@pytest.mark.parametrize("v", ["—", "H2", "{①には無い、と書く}"])
def test_b27_ng_b_axis_not_marked(v):
    s = GOOD_05.replace("| 1 | H1 | 芽1 | 一致 | — | 同じ |", B_ONLY.format(v=v))
    assert _one("B27", A.b27_05_cross_03_column(s))


@pytest.mark.parametrize("v", ["", "**", "{03 の仮説}"])
def test_b27_ng_when_03_blank(v):
    s = GOOD_05.replace("| 1 | H1 | 芽1 |", f"| 1 | {v} | 芽1 |")
    assert _one("B27", A.b27_05_cross_03_column(s))


REJ = "| {n} | 前社長の方針が残っている | 棄却 |"
Q2 = "| 2 | 前社長の方針は今も生きていると思いますか | {o} | {d} | 棄却から出た |"


def _b28(n="H3", o="H3", d="顧客可", extra=""):
    s = GOOD_05.replace("| 2 | 前社長の方針が残っている | 棄却 |", REJ.format(n=n) + extra)
    return s.replace("| 2 | 前社長の方針は今も生きていると思いますか | H3 | **社内のみ** | 棄却から出た |", Q2.format(o=o, d=d))


def test_b28_ok_good():
    assert A.b28_05_rejected_question_internal(GOOD_05) == []


def test_b28_ng_rejected_to_customer():
    assert _one("B28", A.b28_05_rejected_question_internal(_b28()))


def test_b28_ok_rejected_to_internal():
    assert A.b28_05_rejected_question_internal(_b28(d="**社内のみ**")) == []


def test_b28_ng_when_id_in_hypothesis_column():
    s = _b28(n="2").replace("| 前社長の方針が残っている | 棄却 |", "| H3：前社長の方針が残っている | 棄却 |")
    assert _one("B28", A.b28_05_rejected_question_internal(s))


SPLIT = "\n| H3a | 前社長の方針の一部 | 要検証 | 弱 | |"


def test_b28_split_parent_is_judgement():
    """H3a 要検証・H3b 棄却で、出所が枝番なしの H3 → 判断（H）なので見ない。"""
    assert A.b28_05_rejected_question_internal(_b28(n="H3b", o="H3", extra=SPLIT)) == []


def test_b28_ng_when_rejected_branch_cited():
    assert _one("B28", A.b28_05_rejected_question_internal(_b28(n="H3b", o="H3b", extra=SPLIT)))


def test_b28_mixed_sources_is_judgement():
    """出所に棄却でない番号（芽1）が混ざる → 判断（H）なので見ない。"""
    assert A.b28_05_rejected_question_internal(_b28(o="H3・芽1")) == []


# B26 の続き（#364：「現場側が無い状態での格付け」の明記）

NO04 = GOOD_05.replace("| 段取り替えが長い | 採用 |", "| 段取り替えが長い | 要検証 |")
ROW04 = "| 順序は正しいか | ☑ 04を先に読んだ |\n| `04` の有無 | {v} |"


def _no04(v):
    return NO04.replace("| 順序は正しいか | ☑ 04を先に読んだ |", ROW04.format(v=v))


def test_b26_ng_when_not_stated():
    assert _one("B26", A.b26_05_no_adopt_without_04(NO04))


@pytest.mark.parametrize("v", ["☐ あり ／ ☑ **なし（＝無料診断フック段階）**", "[x] なし", "なし（無料診断フック段階）"])
def test_b26_ok_when_selected_in_sec0(v):
    assert A.b26_05_no_adopt_without_04(_no04(v)) == []


def test_b26_ng_when_template_choice_left():
    assert _one("B26", A.b26_05_no_adopt_without_04(_no04("☐ あり ／ ☐ **なし（＝無料診断フック段階）**")))


def test_b26_ok_when_stated_in_text():
    assert A.b26_05_no_adopt_without_04(NO04 + "\n現場側が無い状態での格付け（暫定）。\n") == []


def test_b26_stated_only_in_comment_is_missing():
    assert _one("B26", A.b26_05_no_adopt_without_04(NO04 + "\n<!-- 現場側が無い状態での格付け -->\n"))


# B29（#377：元の番号を残す）

CROSS1 = "| 1 | H1 | 芽1 | 一致 | — | 同じ |"


def _cross(*rows_):
    return GOOD_05.replace(CROSS1, "\n".join(rows_))


def test_b29_ok_good():
    assert A.b29_05_cross_keeps_numbers(GOOD_05) == []


@pytest.mark.parametrize("row", [
    "| 1 | H1＋H3 の統合 | 04 §2 #3 | 一致 | — | a |",        # 芽ではなく §2 の行を指す
    "| 1 | **（①には無い）** | 芽8 | B軸のみ | — | a |",
    "| 1 | H5 | （現場には無い。①のみ） | A軸のみ | — | a |",   # A軸のみの 04 は番号なし
    "| 1 | H5 | **（②に該当なし）** | 食い違い | — | a |",
    "| 1 | **（③が作成）** | — | — | — | a |",
    "| 1 | （`02b`のみ） | — | — | — | a |",
])
def test_b29_ok(row):
    assert A.b29_05_cross_keeps_numbers(_cross(row)) == []


@pytest.mark.parametrize("row", [
    "| 1 | 段取りの仮説 | 芽1 | 一致 | — | a |",
    "| 1 | H1 | 段取りの話 | 一致 | — | a |",
    "| 1 | H1 | {芽の番号} | 一致 | — | a |",
])
def test_b29_ng(row):
    assert _one("B29", A.b29_05_cross_keeps_numbers(_cross(row)))


# ── B30〜B33：入力が無いときの扱い（genba-ops #174・#177／tougou-report #456b・#459） ──

FULL = dict(s01="x", s01i="x", s02="x", s04=GOOD_04, s05=GOOD_05, s06=GOOD_06, s07=GOOD_07, memo=MEMO_REMOTE)


def _set(**kw):
    d = dict(FULL)
    d.update(kw)
    return d


def test_b30_ng_when_no_02_and_not_stated(anken):
    assert _one("B30", A.check_anken(anken(**_set(s02=None))))


def test_b30_ok_when_no_02_stated(anken):
    s04 = GOOD_04.replace("| 聞けなかった |", "`02` なし\n\n| 聞けなかった |")
    assert not _one("B30", A.check_anken(anken(**_set(s02=None, s04=s04))))


def test_b30_not_applied_when_02_exists(anken):
    assert not _one("B30", A.check_anken(anken(**FULL)))


def test_b30_stated_only_in_comment_is_missing():
    s04 = GOOD_04.replace("| 聞けなかった |", "<!-- 02 なし -->\n\n| 聞けなかった |")
    assert _one("B30", A.b30_04_no_02(s04))


DIFF_ROW = "| 1 | 不良率0.1% | 工程内で止めた数 | — | **いいえ（層が違う）** | `#現場オペ` |"
NO_DIFF = GOOD_04.replace(DIFF_ROW, "| 1 | | | | | |")
STATED = "\n`01` も `01i` も無いので、ズレ一覧は作れない。真因の芽だけを出す。\n"
H3 = "## 3. 人間が現場で確認すべき点"


def test_b31_ok_when_stated_and_no_rows():
    assert A.b31_04_no_01(NO_DIFF.replace(H3, STATED + "\n" + H3)) == []


def test_b31_ng_when_not_stated():
    assert _one("B31", A.b31_04_no_01(NO_DIFF))


def test_b31_ng_when_diff_rows_exist():
    assert _one("B31", A.b31_04_no_01(GOOD_04.replace(H3, STATED + "\n" + H3)))


def test_b31_quote_is_not_a_statement():
    assert _one("B31", A.b31_04_no_01(NO_DIFF.replace(H3, "\n> `01` が無いときはこう書く\n\n" + H3)))


def test_b31_applied_only_when_both_missing(anken):
    assert _one("B31", A.check_anken(anken(**_set(s01=None, s01i=None))))
    assert not _one("B31", A.check_anken(anken(**_set(s01i=None))))


def test_b32_ng_when_substitute_not_recorded(anken):
    assert _one("B32", A.check_anken(anken(**_set(s01i=None))))


def test_b32_ok_when_recorded(anken):
    s07 = GOOD_07 + "\n- `01i` が無い案件なので `01` で代用した（残リスク）\n"
    assert not _one("B32", A.check_anken(anken(**_set(s01i=None, s07=s07))))


def test_b32_not_applied_when_01i_exists(anken):
    assert not _one("B32", A.check_anken(anken(**FULL)))


REJ_ROW = "| 2 | 前社長の方針が残っている | 棄却 | 弱 | ②代表性 |"
S05_4 = GOOD_05.replace(REJ_ROW, REJ_ROW + "\n" + "\n".join(f"| {i} | 仮説{i} | 採用 | 中 | |" for i in range(3, 6)))
S05_4 = S05_4.replace("| 採用 | 1 |", "| 採用 | 4 |")


def test_b33_ng_when_bundling_not_left_to_human(anken):
    assert _one("B33", A.check_anken(anken(**_set(s05=S05_4))))


def test_b33_ok_when_left_to_human(anken):
    s07 = GOOD_07 + "\n## 6. ④が迷った箇所と、その判断\n\n- 束ね方と見出しの名前は本人が決める（束ねた案を渡す）\n"
    assert not _one("B33", A.check_anken(anken(**_set(s05=S05_4, s07=s07))))


def test_b33_not_applied_up_to_three(anken):
    assert not _one("B33", A.check_anken(anken(**FULL)))


def test_b33_line_outside_sec6_is_not_enough(anken):
    s07 = GOOD_07.replace("## 1. 人間の判断が必要な論点", "## 1. 人間の判断が必要な論点\n\n- 束ね方は本人が決める", 1)
    assert _one("B33", A.check_anken(anken(**_set(s05=S05_4, s07=s07))))


# ── B34〜B38（09-28 の再点検で「一部」に落とした行） ──

R04 = "| `04` を読んだ日時 | 2026-01-01 10:00 |"
R03 = "| `03` を開封した日時 | 2026-01-01 10:30 |"


@pytest.mark.parametrize("r04, r03", [
    (R04, "| `03` を開封した日時 | 2026-01-01 09:59 |"),                 # 同じ日で時刻が前
    (R04, "| `03` を開封した日時 | 2025-12-31 23:00 |"),                 # 日付が前
    ("| `04` を読んだ日時 | 2026-01-02・**最初に読んだ** |", "| **`03_仮説_封.md` を開封した日時** | **2026-01-01（最後）** |"),
])
def test_b34_ng_when_03_before_04(r04, r03):
    assert _one("B34", A.b34_05_opening_order(GOOD_05.replace(R04, r04).replace(R03, r03)))


@pytest.mark.parametrize("r04, r03", [
    (R04, R03),
    ("| `04` を読んだ日時 | 2026-01-01 22:1x 直前 |", "| `03` を開封した日時 | 2026-01-01 22:12 |"),   # 時刻が片方だけ → 日付だけで比べる
    ("| `04` を読んだ日時 | 2026-01-01・最初 |", "| `03` を開封した日時 | 2026-01-01・最後 |"),
    ("| `04` を読んだ日時 | 2026/1/1 10:00 |", "| `03` を開封した日時 | 2026/1/1 10:00 |"),        # 同じ分は前ではない
])
def test_b34_ok(r04, r03):
    assert A.b34_05_opening_order(GOOD_05.replace(R04, r04).replace(R03, r03)) == []


@pytest.mark.parametrize("r03", ["", "| `03` を開封した日時 | 最後に開けた |"])
def test_b34_ng_when_03_row_missing_or_undated(r03):
    assert _one("B34", A.b34_05_opening_order(GOOD_05.replace(R03 + "\n", r03 + ("\n" if r03 else ""))))


def test_b34_ng_when_04_undated():
    assert _one("B34", A.b34_05_opening_order(GOOD_05.replace(R04, "| `04` を読んだ日時 | 先に読んだ |")))


def test_b34_ok_when_no_04():
    assert A.b34_05_opening_order(GOOD_05.replace(R04, "| `04` を読んだ日時 | なし（無料診断フック段階） |")) == []


REJECTED = "前社長の方針が残っている"


def test_b35_ng_when_rejected_hypothesis_in_06():
    assert _one("B35", A.b35_rejected_not_in_06(GOOD_05, GOOD_06 + f"\n- {REJECTED}。\n"))


@pytest.mark.parametrize("s06", [
    GOOD_06,
    GOOD_06 + "\n- 前社長の考え方は、今回は扱っていません\n",          # 言い換え（下限の検査なので捕まえない）
    GOOD_06 + f"\n<!-- 内部メモ：{REJECTED} は棄却 -->\n",       # 内部メモは build.sh が除く
])
def test_b35_ok(s06):
    assert A.b35_rejected_not_in_06(GOOD_05, s06) == []


def test_b35_ignores_ids_and_notes():
    s05 = GOOD_05.replace(f"| {REJECTED} | 棄却", f"| H3 {REJECTED}（②代表性で落ちた） | 棄却")
    assert _one("B35", A.b35_rejected_not_in_06(s05, GOOD_06 + f"\n{REJECTED}\n"))


def test_b35_adopted_hypothesis_is_not_checked():
    assert A.b35_rejected_not_in_06(GOOD_05, GOOD_06 + "\n段取り替えが長い\n") == []


SEC9_ROW = "| 不良率 | あり | なし | 片側欠測 | 書く |"
BENCH_ROW = "| 平均残業 | なし | **片側欠測（現場の数字なし）** | |"


def test_b36_ok_good():
    assert A.b36_05_takes_over_not_compared(GOOD_04, GOOD_05) == []


def test_b36_ng_when_sec9_says_none():
    s05 = GOOD_05.replace(SEC9_ROW, "| | | | | |") + "\nなし\n"
    assert _one("B36", A.b36_05_takes_over_not_compared(GOOD_04, s05))


def test_b36_ng_when_fewer_rows_than_04():
    s04 = GOOD_04.replace(BENCH_ROW, BENCH_ROW + "\n| 離職率 | あり | **比較不能（両側なし）** | |")
    assert _one("B36", A.b36_05_takes_over_not_compared(s04, GOOD_05))


@pytest.mark.parametrize("state", ["比較できた", "比較できた／**比較不能（両側なし）**／**片側欠測（現場の数字なし）**"])
def test_b36_not_applied_when_04_compared_or_template(state):
    s04 = GOOD_04.replace("**片側欠測（現場の数字なし）**", state)
    s05 = GOOD_05.replace(SEC9_ROW, "| | | | | |") + "\nなし\n"
    assert A.b36_05_takes_over_not_compared(s04, s05) == []


def test_b37_ng_on_ijou_nashi():
    assert _one("B37", A.b37_06_no_ijou_nashi(GOOD_06 + "\n- 不良率は**異常なし**\n"))


@pytest.mark.parametrize("add", ["\n- 温度の記録は異常はありません。\n", "\n不良率に異常は見られませんでした。\n",
                                 "\n在庫は異常がない状態です。\n", "\n出荷に異常はございません。\n"])
def test_b37_ng_on_polite_forms(add):
    """06 は敬体なので「異常なし」はそのままの形では出にくい（09-29）。"""
    assert _one("B37", A.b37_06_no_ijou_nashi(GOOD_06 + add))


def test_b37_ok_on_asking_whether():
    assert A.b37_06_no_ijou_nashi(GOOD_06 + "\n異常がないかを一緒に確かめたいと考えております。\n") == []


def test_b37_ok_in_comment():
    assert A.b37_06_no_ijou_nashi(GOOD_06 + "\n<!-- 異常なし と書かない -->\n") == []


@pytest.mark.parametrize("row", [
    "| 1 | 段取り替えが長い | 課長 | 中 | **1役割** | | `#現場オペ` |",                 # §1 真因の芽
    "| 1 | 不良率0.1% | 工程内で止めた数 | — | **いいえ（層が違う）** | `#現場オペ` |",   # §2 ズレ
])
def test_b38_ng_when_tag_cell_empty(row):
    assert row in GOOD_04
    assert _one("B38", A.b38_04_every_row_tagged(GOOD_04.replace(row, row.replace("`#現場オペ`", ""))))


def test_b34_to_b38_are_wired_into_check_anken(anken):
    """関数だけでなく check_anken から呼ばれていること（配線が外れても関数のテストは通るため）。"""
    row = "| 1 | 段取り替えが長い | 課長 | 中 | **1役割** | | `#現場オペ` |"
    s04 = GOOD_04.replace(row, row.replace("`#現場オペ`", "")).replace(
        BENCH_ROW, BENCH_ROW + "\n| 離職率 | あり | **比較不能（両側なし）** | |")
    s05 = GOOD_05.replace(R03, "| `03` を開封した日時 | 2025-12-31 23:00 |")
    s06 = GOOD_06 + f"\n- {REJECTED}\n- 不良率は異常なし\n"
    got = rules(A.check_anken(anken(**_set(s04=s04, s05=s05, s06=s06))))
    assert {"B34", "B35", "B36", "B37", "B38"} <= set(got)


DANTEI = "断定ではなく、お話からはそう見えるという段階です。\n\n"
MITA = "見て確かめたものは1件も含まれていません"


@pytest.mark.parametrize("old, new", [
    (DANTEI, ""),                                                   # 節冒頭の一文が無い
    (MITA, "課長にうかがいました"),                                   # 拝見していない／見て確かめたもの が無い
    ("- 続けるかは御社が決める", "- 次回は工場を訪問します"),          # 訪問を前提にしている
])
def test_b8_ng_on_missing_stock_phrases(old, new):
    assert old in GOOD_06
    assert _one("B8", A.b8_observation_zero(MEMO_REMOTE, GOOD_06.replace(old, new)))


@pytest.mark.parametrize("old, new", [
    (MITA, "現場は拝見していません"),
    ("- 続けるかは御社が決める", "- 機会をいただけるのであれば、訪問して拝見したい"),
])
def test_b8_ok_stock_phrase_variants(old, new):
    assert A.b8_observation_zero(MEMO_REMOTE, GOOD_06.replace(old, new)) == []


def test_b8_stock_phrases_not_required_on_site():
    memo = MEMO_REMOTE.replace("遠隔（Zoom）", "現地（工場見学）")
    assert A.b8_observation_zero(memo, GOOD_06.replace(DANTEI, "").replace(MITA, "x")) == []


def test_b39_ng_when_02b_not_stated():
    s05 = GOOD_05.replace("| `02b` の記入欄 | ☐ 空欄のまま（理由を §7 に） |\n", "")
    assert _one("B39", A.b39_05_states_02b(s05))


def test_b39_ok_good():
    assert A.b39_05_states_02b(GOOD_05) == []


def test_b40_ng_when_customer_question_dropped():
    s05 = GOOD_05.replace("| 2 | 前社長の方針は今も生きていると思いますか | H3 | **社内のみ** | 棄却から出た |",
                          "| 2 | 月に何回止まりますか | 芽1 | 顧客可 | 採用 |")
    assert _one("B40", A.b40_06_all_customer_questions(s05, GOOD_06))


def test_b40_counts_list_items_not_comments():
    s06 = GOOD_06.replace("- 段取り替えは1回何分かかっていますか", "<!-- - 段取り替えは1回何分かかっていますか -->")
    assert _one("B40", A.b40_06_all_customer_questions(GOOD_05, s06))


def test_b40_ng_when_06_has_more_than_seven_questions():
    """2026-11-27 本人決定：06 の問いは7つまで。8つ目以降は 07§4 へ移す（架空案件で問い14・7,527字になった）。"""
    extra = "".join(f"\n- 追加の確認{i}はどうなっていますか" for i in range(8))
    s06 = GOOD_06.replace("- 段取り替えは1回何分かかっていますか", "- 段取り替えは1回何分かかっていますか" + extra)
    assert _one("B40", A.b40_06_all_customer_questions(GOOD_05, s06))


def test_b40_ok_good_and_rephrased():
    assert A.b40_06_all_customer_questions(GOOD_05, GOOD_06) == []
    s06 = GOOD_06.replace("段取り替えは1回何分かかっていますか", "1回の段取り替えに、何分くらいかかりますか")
    assert A.b40_06_all_customer_questions(GOOD_05, s06) == []


@pytest.mark.parametrize("add", ["\n| 課題 | 強さ |\n|---|---|\n| 段取り | **中** |\n", "\n根拠の強度は中です。\n", "\n格付けは強。\n"])
def test_b41_ng(add):
    assert _one("B41", A.b41_06_no_grading(GOOD_06 + add))


@pytest.mark.parametrize("add", ["\n強い根拠がある\n", "\n| 項目 | 値 |\n|---|---|\n| 中身 | 中小企業 |\n", "\n<!-- 強度：中 -->\n"])
def test_b41_ok(add):
    assert A.b41_06_no_grading(GOOD_06 + add) == []


def test_b39_to_b41_are_wired_into_check_anken(anken):
    s05 = GOOD_05.replace("| `02b` の記入欄 | ☐ 空欄のまま（理由を §7 に） |\n", "").replace(
        "| 2 | 前社長の方針は今も生きていると思いますか | H3 | **社内のみ** | 棄却から出た |",
        "| 2 | 月に何回止まりますか | 芽1 | 顧客可 | 採用 |")
    s06 = GOOD_06 + "\n根拠の強度は中です。\n"
    got = set(rules(A.check_anken(anken(**_set(s05=s05, s06=s06)))))
    assert {"B39", "B40", "B41"} <= got


@pytest.mark.parametrize("add", [
    "\n段取り替えが長いことが原因である。\n",
    "\n段取りは課題だ。\n",
    "\nこれは可能性があります。あれも可能性があります。それも可能性があります。\n",
    "\n貴社のお話では、段取りが長いとのことでした。\n",
    "\n段取り替えに時間がかかっている。\n",          # 〜ている。（09-29）
    "\n記録を見直すことが必要と考える。\n",
    "\n改善の余地があると思う。\n",
])
def test_b42_ng(add):
    assert _one("B42", A.b42_06_polite_style(GOOD_06 + add))


@pytest.mark.parametrize("add", [
    "\n段取り替えが長い可能性があります。記録はまだ見ていません。別の可能性もあります。\n",
    "\n| 根拠の種類 | 貴社の発信 |\n|---|---|\n| a | b |\n",       # 表のラベルは相手の呼び方ではない
    "\n<!-- 内部メモ：これは課題だ。 -->\n",
    "\n> 引用：課題である。\n",
    "\n「毎日確認している。」とのお話でした。\n",      # 「」の中は相手の言葉（09-29）
    "\n今後も確認が必要でしょう。\n",
])
def test_b42_ok(add):
    assert A.b42_06_polite_style(GOOD_06 + add) == []


def test_b42_wired_into_check_anken(anken):
    assert "B42" in rules(A.check_anken(anken(**_set(s06=GOOD_06 + "\n原因である。\n"))))


def test_b38_ok_good_and_number_only_rows():
    assert A.b38_04_every_row_tagged(GOOD_04) == []   # 「| 2 | | … |」の番号だけの行は数えない
