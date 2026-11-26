"""check_genba_mark.py の挙動を固定する（段3。スクリプトは変えない）。

★合成データだけを使う。実在の現場メモは読まない。
★見ているのは「4印の形」（実走ログ 20-2・21・27-5・B-4）。欄が埋まっているだけでは通さない。
"""
import pytest

from conftest import run_script


def memo(**over):
    marks = {"話者": "製造課長", "いつ": "2026-09-20", "どこで（現地／遠隔）": "現地",
             "誰から（直接／伝聞／書面）": "直接"}
    marks.update(over)
    rows = "\n".join(f"| {k} | {v} |" for k, v in marks.items() if v is not None)
    return f"# 現場メモ\n\n| 欄 | 中身 |\n|---|---|\n{rows}\n\n【製造課長】本文（合成）\n"


@pytest.fixture
def check(tmp_path):
    def _run(text):
        p = tmp_path / "現場メモ.md"
        p.write_text(text, encoding="utf-8")
        return run_script("check_genba_mark", p)
    return _run


def test_ok_when_four_marks_have_shape(check):
    code, ng, out = check(memo())
    assert code == 0 and not ng
    assert "OK" in out


@pytest.mark.parametrize("where", ["遠隔（Zoom）", "不明（本人の記憶が曖昧）"])
def test_ok_for_other_allowed_where(check, where):
    assert check(memo(**{"どこで（現地／遠隔）": where}))[0] == 0


def test_no_args_exits_2():
    assert run_script("check_genba_mark")[0] == 2


@pytest.mark.parametrize("mark", ["話者", "いつ", "どこで（現地／遠隔）", "誰から（直接／伝聞／書面）"])
def test_ng_when_mark_row_missing(check, mark):
    code, ng, _ = check(memo(**{mark: None}))
    assert code == 1
    assert any("欄そのものが無い" in l and mark.split("（")[0] in l for l in ng)


def test_ng_when_mark_empty(check):
    code, ng, _ = check(memo(話者=""))
    assert code == 1 and any("空欄" in l for l in ng)


@pytest.mark.parametrize("mark,value", [
    ("いつ", "先週"),                                  # 日付の形でない
    ("どこで（現地／遠隔）", "工場"),                  # 現地／遠隔／不明のどれでもない
    ("誰から（直接／伝聞／書面）", "課長"),            # 直接／伝聞／書面／不明のどれでもない
])
def test_ng_when_filled_but_shapeless(check, mark, value):
    """B-4：埋まっているだけでは通さない。"""
    code, ng, _ = check(memo(**{mark: value}))
    assert code == 1 and any("形になっていない" in l for l in ng)


def test_ng_on_legacy_three_mark_format(check):
    """旧3印（いつ・どこで ／ 直接／伝聞／書面）は2軸が1列に潰れている。"""
    text = ("| 欄 | 中身 |\n|---|---|\n| 話者 | 課長 |\n"
            "| いつ・どこで | 2026-09-20 |\n| 直接／伝聞／書面 | 直接 |\n")
    code, ng, _ = check(text)
    assert code == 1 and any("旧3印形式" in l for l in ng)


def test_unknown_without_reason_is_note_not_ng(check):
    code, ng, out = check(memo(いつ="不明"))
    assert code == 0 and not ng
    assert "NOTE" in out and "理由" in out


# ── Z13（段5の点検で発見。09-26 修正済み）─────────────────


def template_memo(values):
    """genba-memo-template.md の★出所表（太字の欄名＋3列）に値を入れたもの。"""
    import re
    from conftest import REPO
    t = (REPO / ".claude/skills/genba-ops/assets/genba-memo-template.md").read_text(encoding="utf-8")
    out = []
    for l in t.splitlines():
        m = re.match(r"^\|\s*\**(話者|いつ|どこで|誰から)", l)
        if m and m.group(1) in values:
            l = re.sub(r"^(\|[^|]*\|)\s*\|", rf"\1 {values[m.group(1)]} |", l, count=1)
        out.append(l)
    return "\n".join(out) + "\n"


def test_template_memo_filled_passes(check):
    """Z13（09-26 修正済み）：テンプレどおり（太字の欄名＋3列）に埋めたメモは通る。"""
    code, ng, _ = check(template_memo({"話者": "製造課長", "いつ": "2026-09-20", "どこで": "現地", "誰から": "直接"}))
    assert code == 0, ng


def test_template_memo_left_blank_is_ng(check):
    """★Z13 を直すとき、太字を許すだけだと3列目の説明文（`現地`・`直接`）を値として拾い、空欄が通る。
    このテストは、その直し方をしたら落ちる。"""
    code, _, _ = check(template_memo({}))
    assert code == 1


@pytest.mark.parametrize("field,val", [("いつ", "先週"), ("どこで", "工場"), ("誰から", "課長")])
def test_template_memo_shapeless_value_is_ng(check, field, val):
    """テンプレ形式でも、2列目の値の形を見る（3列目の説明文で救わない）。"""
    vals = {"話者": "製造課長", "いつ": "2026-09-20", "どこで": "現地", "誰から": "直接"}
    vals[field] = val
    code, ng, _ = check(template_memo(vals))
    assert code == 1 and any("形になっていない" in l for l in ng)


# ── 本文の各行に【役割】（実走 #58 の対策 (b)・09-29 本人決定）─────────────


def test_ng_when_body_line_has_no_role(check):
    code, ng, out = check(memo() + "\n- 【工場長】段取りが多い\n- 品目が増えている\n")
    assert code == 1 and any(l.startswith("本文の行に【役割】が無い：1行") for l in ng)
    assert "L13" in out and "品目" not in out          # 守秘：行番号だけ出す


@pytest.mark.parametrize("line", ["- 【工場長】段取りが多い", "- 【不明】廃棄率は記録していない",
                                  "- 困っている作業：【事務】FAXの転記", "| 品目数 | 【工場長】約150 |"])
def test_ok_when_body_line_has_role(check, line):
    assert check(memo() + f"\n{line}\n")[0] == 0


def test_ng_when_table_body_row_has_no_role(check):
    code, ng, _ = check(memo() + "\n| 項目 | 値 |\n|---|---|\n| 品目数 | 約150 |\n")
    assert code == 1 and any(l.startswith("本文の行に【役割】が無い") for l in ng)


def test_prompt_only_and_quote_lines_are_not_checked(check):
    """テンプレの問いだけの行（「…：」で終わる）・引用・見出しは見ない。★出所の4印の行も見ない。"""
    body = "\n## B. 現場の生の声\n- 毎日「面倒だ」と感じる作業：\n> 補足の引用\n- \n"
    assert check(memo() + body)[0] == 0


def test_ng_when_plain_answer_line_has_no_role(check):
    """問い（太字）＋答え（地の文）の形。答えの行に【役割】が無ければ NG（箇条書きだけ見ると素通りする）。"""
    code, ng, _ = check(memo() + "\n**困っていることは？**\n段取り替えが多い\n\n---\n")
    assert code == 1 and any(l.startswith("本文の行に【役割】が無い：1行") for l in ng)
    assert check(memo() + "\n**困っていることは？**\n【工場長】段取り替えが多い\n\n---\n")[0] == 0
