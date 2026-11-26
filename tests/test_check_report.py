"""check_report.py の挙動を固定する（段3。スクリプトは変えない）。

★合成データだけを使う。実在の 06 は読まない。
★B-1（正しく書いた 06 を原理的に通さなかった）と #47（テンプレの項目名を太字と数えた）を
  二度と起こさないため、「通るべきものが通る」側を必ず一緒に確かめる。
"""
import pytest

from conftest import load_script, run_script

REQUIRED = ["この診断が見た範囲", "この診断の限界", "本レポートで踏み込んでいない領域",
            "一緒に確かめたい問い", "次の一歩"]


def report(extra_body="", comment=True, drop=None):
    secs = []
    for h in REQUIRED:
        if h == drop:
            continue
        secs.append(f"## {h}\n\n{h}について、伺った範囲で整理しました。\n")
    memo = "<!-- 内部メモ：棄却した説明は判定表 H3a を参照。封・定規・実走ログ -->\n" if comment else ""
    return "# 現状の整理\n\n" + memo + "\n".join(secs) + extra_body


@pytest.fixture
def check(tmp_path):
    def _run(text, *flags):
        p = tmp_path / "06.md"
        p.write_text(text, encoding="utf-8")
        return run_script("check_report", *flags, p)
    return _run


# ── 通るべきものが通る（B-1）──────────────────────────


def test_clean_report_passes_as_submission(check):
    code, ng, out = check(report(comment=False))
    assert code == 0 and not ng, ng
    assert "OK   問題なし" in out


def test_draft_tolerates_comments_with_internal_words(check):
    """内部メモの中は検査しない。④の生の出力は必ずコメントを持つ（B-1）。"""
    code, ng, out = check(report(), "--draft")
    assert code == 0 and not ng, ng
    assert "WARN" in out and "内部メモ" in out


@pytest.mark.parametrize("line", [
    "**何が起きているか**：",
    "- **一次情報**",
    "1. **現場の声**",
    "> **確かめたいこと**",
])
def test_label_only_bold_lines_not_counted(check, line):
    """#47：項目名だけの太字は見出しと同じ構造。数えない。"""
    body = "\n## 補足\n\n" + "\n".join([line] * 4) + "\n"
    code, ng, _ = check(report(body, comment=False))
    assert code == 0, ng


def test_label_followed_by_colon_inline_not_counted(check):
    body = "\n## 補足\n\n**背景**：受注が増えた。**対応**：人を増やした。\n"
    assert check(report(body, comment=False))[0] == 0


# ── 止めるべきものが止まる ─────────────────────────────


def test_submission_ng_when_comment_left(check):
    code, ng, _ = check(report())
    assert code == 1 and any("内部メモ" in l for l in ng)


@pytest.mark.parametrize("drop", REQUIRED)
def test_ng_when_required_section_missing(check, drop):
    """16-1：業際の節を丸ごと落とした。"""
    code, ng, _ = check(report(comment=False, drop=drop), "--draft")
    assert code == 1 and any(drop in l for l in ng)


def test_required_section_must_be_a_heading(check):
    """本文に語があっても、見出しでなければ無いのと同じ。"""
    text = report(comment=False, drop="次の一歩") + "\n次の一歩は本文にだけ書いた。\n"
    assert check(text, "--draft")[0] == 1


@pytest.mark.parametrize("word", load_script("check_report").INTERNAL)
def test_ng_on_each_internal_word(check, word):
    code, ng, _ = check(report(f"\n本文に {word} が残った。\n", comment=False))
    assert code == 1 and any(f"「{word}」" in l for l in ng)


@pytest.mark.parametrize("word", load_script("check_report").ASSERTIVE)
def test_ng_on_each_assertive_word(check, word):
    code, ng, _ = check(report(f"\nこれは{word}である。\n", comment=False))
    assert code == 1 and any("断定語" in l for l in ng)


@pytest.mark.parametrize("word", load_script("check_report").SINCERITY)
def test_ng_on_each_sincerity_word(check, word):
    code, ng, _ = check(report(f"\n{word}。\n", comment=False))
    assert code == 1 and any("誠実さ" in l for l in ng)


@pytest.mark.parametrize("text,why", [
    ("理由は（H3a）の通り。", "採番"),
    ("X5 を見ると分かる。", "採番"),
    ("〔04・05 参照〕", "01〜07"),
    ("〔3・7・9〕", "羅列"),
    ("05 の採用によれば", "判定への参照"),
    ("02b_主任 を参照", "ファイル名"),
    ("`build.sh` を使う", "バッククォート"),
])
def test_ng_on_structural_leaks(check, text, why):
    """B-6：語リストに頼らない構造検査。"""
    code, ng, _ = check(report(f"\n{text}\n", comment=False))
    assert code == 1 and any(why in l for l in ng), ng


def test_ng_on_two_inline_bolds_in_one_section(check):
    """#44：文中の太字は1節に1か所まで。"""
    body = "\n## 補足\n\n受注は**増えた**が、人は**増えていない**。\n"
    code, ng, _ = check(report(body, comment=False))
    assert code == 1 and any("太字が 2 か所" in l for l in ng)


def test_one_inline_bold_per_section_ok(check):
    body = "\n## 補足\n\n受注は**増えた**が、人は増えていない。\n"
    assert check(report(body, comment=False))[0] == 0


def test_ng_on_long_bold(check):
    body = "\n## 補足\n\n**" + "あ" * 21 + "**という話があった。\n"
    code, ng, _ = check(report(body, comment=False))
    assert code == 1 and any("21字" in l for l in ng)


def test_bold_sentence_on_own_line_is_counted(check):
    """句点を含む太字は項目名ではなく文（pdf-migaki モードB）。"""
    body = "\n## 補足\n\n**人が足りない。**\n**機械も古い。**\n"
    code, ng, _ = check(report(body, comment=False))
    assert code == 1 and any("太字" in l for l in ng)


def test_placeholder_ng_in_submission_warn_in_draft(check):
    text = report("\n## はじめに\n\n{本人が書く欄}\n", comment=False)
    assert check(text)[0] == 1
    code, ng, out = check(text, "--draft")
    assert code == 0 and "未記入" in out


def test_short_braces_are_not_placeholders(check):
    assert check(report("\n{abc}\n", comment=False))[0] == 0


def test_name_flag_replaces_display_only(check):
    code, _, out = check(report(comment=False), "--name", "表示名")
    assert code == 0 and "表示名" in out.splitlines()[0]


def test_no_args_exits_2():
    assert run_script("check_report")[0] == 2


# ── 事前の基準・p・確率（2026-10-03。03・02b テンプレの「06 には書かない」を門で見る）──


@pytest.mark.parametrize("line", ["課題1（当たる見込みが高い）", "この点は p＝0.8 程度です", "80%の確率で起きています",
                                  "8割の見込みです", "〔p〕0.5", "的中率は7割", "Brier スコア"])
def test_prior_words_ng_in_body(check, line):
    code, ng, _ = check(report(f"\n## 補足\n\n{line}\n", comment=False))
    assert code == 1 and any("社内だけ" in l for l in ng), ng


@pytest.mark.parametrize("line", ["1人当たりの受注処理が多い可能性があります", "社員の8割が月末に残業", "可能性があります",
                                  "前年比 80% でした", "2割の取引先", "対策の当たりを付けました"])
def test_prior_normal_text_passes(check, line):
    """止めすぎない（B-1）：割合の事実・「当たり」の普通の使い方は通す。"""
    code, ng, _ = check(report(f"\n## 補足\n\n{line}\n", comment=False))
    assert code == 0, ng


def test_prior_inside_internal_memo_is_not_checked(check):
    text = report("\n<!-- 内部メモ：〔p〕0.8・当たる見込み -->\n", comment=False)
    code, ng, _ = check(text, "--draft")
    assert code == 0, ng
