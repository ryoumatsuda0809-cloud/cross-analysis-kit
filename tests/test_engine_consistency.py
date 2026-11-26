"""エンジン側の整合テスト A1〜A8（段4。移行台帳 §3-2 A）。

同じ一覧が「コード」と「md（エージェントが読む指示）」の2か所にあるものを突き合わせる。
ずれたら落ちる＝二重管理のずれを、誰かが詰まる前に捕まえる。

★追跡ファイルだけを読む。案件/ は git check-ignore（A7）で名前を当てるだけで、何も開かない。
★このテストは md もスクリプトも書き換えない。落ちたら移行台帳 §4 に「ずれ」として載せ、直すかは本人が決める。
"""
import os
import re
import shutil
import subprocess
import sys

import pytest

from conftest import REPO, SCRIPTS, load_script

SK = REPO / ".claude" / "skills"
CROSS_RUN = SK / "cross-run" / "SKILL.md"
PROMPTS = SK / "cross-run" / "assets" / "subagent-prompts.md"


def read(p):
    return p.read_text(encoding="utf-8")


def norm(s):
    """見出しと参照を比べるための正規化（★・太字・空白・スラッシュの全角半角を無視）。"""
    s = s.replace("**", "").replace("★", "").replace("／", "/")
    return re.sub(r"\s+", "", s)


# ── A1｜check_anken.READERS と cross-run「渡すもの」表 ───────────────


def _token(name):
    if "現場メモ" in name:
        return "現場メモ"
    m = re.match(r"(\d+[a-z]?)", os.path.basename(name))
    return m.group(1) if m else name


def cross_run_pass_table():
    """cross-run Stage 3〜5 の表：段 → 「渡すもの」列に出てくるファイル。"""
    out = {}
    for line in read(CROSS_RUN).splitlines():
        m = re.match(r"^\|\s*([②③④])\s*\S+\s*\|(.*?)\|(.*?)\|\s*$", line)
        if not m:
            continue
        cell = m.group(2)
        toks = set(re.findall(r"`(\d+[a-z]?)`", cell))
        if "現場メモ" in cell:
            toks.add("現場メモ")
        out[m.group(1)] = toks
    return out


def test_a1_readers_match_cross_run_table():
    table = cross_run_pass_table()
    readers = {k[0]: {_token(r) for r in v} for k, v in load_script("check_anken").READERS.items()}
    assert set(table) == set(readers) == {"②", "③", "④"}, table
    for stage in readers:
        assert readers[stage] == table[stage], f"{stage}: READERS={readers[stage]} cross-run={table[stage]}"


# ── A2｜断定語：check_report.ASSERTIVE と shinin-hansho の列挙 ─────────


def test_a2_assertive_words_match_shinin_hansho():
    line = next(l for l in read(SK / "shinin-hansho" / "SKILL.md").splitlines() if "断定語の原本" in l)
    paren = re.search(r"ASSERTIVE`[^（]*（(.*?)）", line).group(1)
    listed = re.findall(r"`([^`]+)`", paren)
    assert sorted(listed) == sorted(load_script("check_report").ASSERTIVE)


# ── A3｜固定タグ5つ ─────────────────────────────────


TAG_FILES = [SK / "market-recon" / "SKILL.md", SK / "genba-ops" / "SKILL.md",
             SK / "genba-ops" / "assets" / "04-genba-analysis-template.md",
             SK / "shinin-hansho" / "SKILL.md", PROMPTS]


def tag_lists(path):
    """`#xx` がバッククォートで3つ以上並ぶ行＝タグの列挙。"""
    out = []
    for line in read(path).splitlines():
        tags = re.findall(r"`(#[^`\s]+)`", line)
        if len(tags) >= 3:
            out.append(tuple(tags))
    return out


@pytest.mark.parametrize("path", TAG_FILES, ids=lambda p: p.relative_to(SK).as_posix())
def test_a3_fixed_tags_same_everywhere(path):
    canon = ("#市場", "#現場オペ", "#財務", "#組織", "#DX")
    lists = tag_lists(path)
    assert lists, "タグの列挙が見つからない"
    for tags in lists:
        assert tags == canon, f"{tags} ≠ {canon}"


# ── A4｜check_report.REQUIRED の必須節がテンプレの見出しにある（B-1） ─────


def test_a4_required_sections_exist_in_report_template():
    heads = "\n".join(re.findall(r"^#{1,3}\s+(.+)$", read(SK / "tougou-report" / "assets" / "report-template.md"), re.M))
    missing = [k for k, _ in load_script("check_report").REQUIRED if k not in heads]
    assert not missing, f"テンプレに無い必須節：{missing}（④がテンプレ通りに書くと必ず NG になる）"


# ── A5｜SKILL の §N「名前」参照と、見出しの番号・名前 ──────────────


REF = re.compile(r"(`CLAUDE\.md`\s*)?§(\d+(?:-\d+)?)「([^」]+)」")


def all_refs():
    for p in sorted(SK.rglob("*.md")):
        for i, line in enumerate(read(p).splitlines(), 1):
            for m in REF.finditer(line):
                yield p, i, bool(m.group(1)), m.group(2), m.group(3)


def heading_index():
    """(節番号, 見出し名)。番号の無い小見出しは、直前の番号付き節の番号で登録する（§1 の中の「数字が…とき」など）。"""
    idx = set()
    for p in SK.rglob("*.md"):
        cur = None
        for h in re.findall(r"^#{1,4}\s+(.+)$", read(p), re.M):
            m = re.match(r"^[★\s]*§?(\d+(?:-\d+)?)\.\s*(.+)$", h)
            if m:
                cur = m.group(1)
                idx.add((cur, norm(m.group(2))))
            elif cur is not None:
                idx.add((cur.split("-")[0], norm(h)))
    return idx


def claude_md_item(sec_item):
    """CLAUDE.md §4-3 ＝ 「## 4.」節の3番目の番号付き項目。"""
    sec, item = sec_item.split("-")
    body = re.search(rf"^## {sec}\. .*?(?=^## )", read(REPO / "CLAUDE.md"), re.M | re.S).group(0)
    m = re.search(rf"^{item}\.\s+(.+)$", body, re.M)
    return norm(m.group(1)) if m else ""


# 既知のずれ（移行台帳 §4）。直ったら XPASS で落ちるので外す。Z10 は段8 R4 で済
KNOWN_DRIFT = {}


def _ref_param(r):
    p, l, to_claude, num, name = r
    marks = [pytest.mark.xfail(strict=True, reason=KNOWN_DRIFT[(num, name)])] if (num, name) in KNOWN_DRIFT else []
    return pytest.param(*r, marks=marks, id=f"{p.relative_to(SK).as_posix()}:{l}")


REFS = [_ref_param(r) for r in all_refs()]


@pytest.mark.parametrize("path,line,to_claude,num,name", REFS)
def test_a5_section_reference_resolves(path, line, to_claude, num, name):
    if to_claude:
        assert claude_md_item(num).startswith(norm(name)), f"CLAUDE.md §{num} が「{name}」でない"
        return
    idx = heading_index()
    hit = any(n == num and h.startswith(norm(name)) for n, h in idx)
    assert hit, f"§{num}「{name}」という見出しがどのテンプレにも無い"


# ── A6｜「7つの反証テスト」の数と、実際に並んでいる数 ───────────────


def count_numbered_after(text, marker):
    """marker の直後から、最初の番号付きリストの項目数を数える（次の見出しまで）。"""
    rest = text.split(marker, 1)[1]
    rest = re.split(r"^#{1,4} ", rest, maxsplit=1, flags=re.M)[0]
    return len(re.findall(r"^\d+\.\s", rest, re.M))


def test_a6_seven_tests_in_skill():
    text = read(SK / "shinin-hansho" / "SKILL.md")
    assert count_numbered_after(text, "## Stage 2 ｜ 7つの反証テスト") == 7


def test_a6_seven_tests_in_05_template():
    """Z8（段8 R4 で済）：テンプレにも 0. 前提テスト を並べて7本。"""
    text = read(SK / "shinin-hansho" / "assets" / "05-hansho-template.md")
    assert count_numbered_after(text, "**7つの反証テスト**") == 7


# ── A7｜案件の成果物が git から外れている（CHECK §9） ───────────────


@pytest.mark.parametrize("rel", [
    "案件/新しい会社/03_仮説_封.md",
    "案件/新しい会社/02b_主任診断士の見立て_封.md",
    "案件/新しい会社/_材料/B_現場/現場メモ.md",
    "案件/新しい会社/06_課題仮説レポート.md",
    "案件/新しい会社/Office_新しい会社様_現状の整理_20260101.pdf",
    "案件/_禁止語_ローカル専用.txt",
    "診断結果/何か.md",
])
def test_a7_anken_is_gitignored(rel):
    """check-ignore はパスの名前だけを見る。ファイルを作りも開きもしない。"""
    r = subprocess.run(["git", "-C", str(REPO), "check-ignore", "-q", "--no-index", rel])
    assert r.returncode == 0, f"{rel} が gitignore されていない"


# ── A8｜pre-commit の項目が実際に止める（#43：在るのと動くのは別） ─────────


def _git(root, *a, check=True):
    return subprocess.run(["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@t", *a],
                          capture_output=True, text=True, check=check)


@pytest.fixture
def hook_repo(tmp_path):
    """本物の .githooks/pre-commit と、それが呼ぶスクリプトを一時リポジトリに写す。"""
    root = tmp_path / "r"
    root.mkdir()
    _git(root, "init", "-q")
    for src, rel in [(REPO / ".githooks" / "pre-commit", ".githooks/pre-commit"),
                     (SCRIPTS["check_anken"], "check_anken.py"),
                     (SCRIPTS["lint_01"], ".claude/skills/market-recon/scripts/lint_01.py")]:
        dst = root / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(src, dst)
    os.chmod(root / ".githooks" / "pre-commit", 0o755)
    _git(root, "config", "core.hooksPath", ".githooks")
    # ★新しい端末の既定（quotepath=on）を明示する。フックがこの設定に頼っていないことを確かめるため（Z9）
    _git(root, "config", "core.quotepath", "true")
    (root / "案件").mkdir()
    (root / "案件" / "_禁止語_ローカル専用.txt").write_text("架空工業\n", encoding="utf-8")
    (root / ".gitignore").write_text("案件/\n", encoding="utf-8")
    (root / "README.md").write_text("x\n", encoding="utf-8")
    _git(root, "add", "-A")
    r = _git(root, "commit", "-q", "-m", "init", check=False)
    assert r.returncode == 0, "きれいな状態で commit できない：" + r.stdout + r.stderr
    return root


def _try_commit(root):
    (root / "README.md").write_text(read(root / "README.md") + "y\n", encoding="utf-8")
    _git(root, "add", "README.md")
    r = _git(root, "commit", "-q", "-m", "t", check=False)
    return r.returncode, r.stdout + r.stderr


def test_a8_clean_commit_passes(hook_repo):
    code, out = _try_commit(hook_repo)
    assert code == 0 and "8項目すべて通過" in out


def test_a8_1_blocks_anken_path(hook_repo):
    p = hook_repo / "案件" / "案件Z" / "04_現場分析.md"
    p.parent.mkdir(parents=True)
    p.write_text("合成\n", encoding="utf-8")
    _git(hook_repo, "add", "-f", str(p))
    code, out = _try_commit(hook_repo)
    assert code != 0 and "顧客の診断結果" in out


def test_a8_2_blocks_banned_word_in_diff(hook_repo):
    (hook_repo / "README.md").write_text("架空工業\n", encoding="utf-8")
    code, out = _try_commit(hook_repo)
    assert code != 0 and "禁止語が含まれている" in out


def test_a8_3_blocks_leak_in_already_tracked_file(hook_repo):
    """差分に無くても、追跡中のファイルに禁止語があれば止める（lint_01 --leak）。"""
    (hook_repo / "old.md").write_text("架空工業\n", encoding="utf-8")
    _git(hook_repo, "add", "old.md")
    _git(hook_repo, "commit", "-q", "--no-verify", "-m", "過去に紛れた")
    code, out = _try_commit(hook_repo)
    assert code != 0 and "社名漏れ検査が NG" in out


def test_a8_4_blocks_broken_anken_structure(hook_repo):
    (hook_repo / "案件" / "案件Z" / "_ゴミ").mkdir(parents=True)
    code, out = _try_commit(hook_repo)
    assert code != 0 and "check_anken.py が NG" in out


@pytest.mark.parametrize("mirror", ["AGENTS.md", ".agents"])
def test_a8_5_blocks_mirror_even_untracked(hook_repo, mirror):
    p = hook_repo / mirror
    p.mkdir() if mirror == ".agents" else p.write_text("x", encoding="utf-8")
    code, out = _try_commit(hook_repo)
    assert code != 0 and "写し" in out


@pytest.mark.parametrize("pdf,blocked", [("x/レポート.pdf", True), ("対外資料/デモ_A/デモ.pdf", False)])
def test_a8_6_pdf_allowlist(hook_repo, pdf, blocked):
    p = hook_repo / pdf
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(b"%PDF")
    _git(hook_repo, "add", pdf)
    code, out = _try_commit(hook_repo)
    assert (code != 0) == blocked, out



@pytest.mark.parametrize("rel", ["案件/案件Z/04_現場分析.md", "診断結果/x.md", "x/レポート.pdf"])
def test_a8_blocks_japanese_paths_on_fresh_clone(hook_repo, rel):
    """Z9（09-26 修正済み）：quotepath=on の端末でも 案件/・PDF を止める。"""
    p = hook_repo / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(b"x")
    _git(hook_repo, "add", "-f", rel)
    code, _ = _try_commit(hook_repo)
    assert code != 0


# ── cross-run #80：エンジン側は git が履歴を持つので .bak を作らない（09-28） ──

BACKUP = re.compile(r"\.(bak|orig|old)$|~$", re.I)


def backup_files(root):
    """root の下の控えファイル（.bak・.orig・.old・~）。案件/・診断結果/・.git/ は見ない（名前も開かない）。"""
    out = []
    for d, dirs, files in os.walk(root):
        dirs[:] = [x for x in dirs if x not in {".git", "案件", "診断結果", "node_modules", "__pycache__", ".pytest_cache"}]
        out += [os.path.relpath(os.path.join(d, f), root) for f in files if BACKUP.search(f)]
    return sorted(out)


def test_no_backup_files_in_engine():
    assert backup_files(REPO) == []


@pytest.mark.parametrize("name", ["SKILL.md.bak", "01-facts-template.md.orig", "CLAUDE.md~", "x.OLD"])
def test_backup_file_is_caught(tmp_path, name):
    (tmp_path / ".claude").mkdir()
    (tmp_path / ".claude" / name).write_text("x", encoding="utf-8")
    assert backup_files(tmp_path) == [os.path.join(".claude", name)]


def test_backup_inside_anken_is_not_looked_at(tmp_path):
    (tmp_path / "案件" / "Z").mkdir(parents=True)
    (tmp_path / "案件" / "Z" / "05.md.bak").write_text("x", encoding="utf-8")
    assert backup_files(tmp_path) == []


# ── cross-run #115：実走ログの詰まりに7分類を付ける（09-28） ──

SEVEN = ("スキルの穴", "テンプレの穴", "手順の抜け", "汚染", "データの誤り", "見立ての誤り", "技術的限界")
# 7分類の外の値を使った過去の記録。実走ログは追記専用なので書き換えない（台帳 §8・09-28）
KNOWN_LOG = {27, 28, 52, 53, 56, 57}


def log_category_violations(src):
    """詰まりの表（先頭列「#」・2列目「分類」）で、分類が7つのどれも含まない行 → {実走番号}。
    「分類｜内容」の2列表（教訓1 など）と箇条書きは見ない。再発の行（—）は通す。空欄は違反。"""
    import anken_checks as A
    lines = src.splitlines()
    heads = [(i, l) for i, l in enumerate(lines) if l.startswith("## 実走")]
    out = set()
    for k, (i, h) in enumerate(heads):
        j = heads[k + 1][0] if k + 1 < len(heads) else len(lines)
        m = re.search(r"#(\d+)", h)
        for t in A.tables([(x + 1, lines[x]) for x in range(i, j)]):
            if A.col(t, "分類") != 1 or t[0][1][0].strip() != "#":
                continue
            for _, c in A.rows(t):
                v = A.cell(c, 1).replace("*", "").strip()
                if v not in ("—", "-") and not any(s in v for s in SEVEN):
                    out.add(int(m.group(1)) if m else -1)
    return out


@pytest.mark.skipif(not (REPO / "実走ログ.md").exists(), reason="実走ログ.md は公開版に含めていない")
def test_log_categories_are_the_seven():
    got = log_category_violations(read(REPO / "実走ログ.md"))
    assert got <= KNOWN_LOG, f"実走 {sorted(got - KNOWN_LOG)} の詰まりに7分類の外の分類"
    assert got == KNOWN_LOG, f"実走 {sorted(KNOWN_LOG - got)} は直った。KNOWN_LOG から外す"


LOG_OK = "## 実走 #90（2099-01-01）｜架空\n\n| # | 分類 | 何が | 誰が |\n|---|---|---|---|\n"


@pytest.mark.parametrize("cat", ["スキルの穴", "**テンプレの穴**", "汚染（疑い）", "データの誤り／手順の抜け", "—"])
def test_log_category_ok(cat):
    assert log_category_violations(LOG_OK + f"| 90-1 | {cat} | a | ② |\n") == set()


@pytest.mark.parametrize("cat", ["検査の穴", "設計の穴", "データ（TEST の限界）", ""])
def test_log_category_ng(cat):
    got = log_category_violations(LOG_OK + f"| 90-1 | {cat} | a | ② |\n")
    assert got == {90}   # 空欄も「分類を付けていない」


def test_log_two_column_table_is_not_checked():
    src = "## 実走 #91（2099）\n\n| 分類 | 内容 |\n|---|---|\n| 教訓1 | a |\n"
    assert log_category_violations(src) == set()


# ── 質の検証.md（失敗の条件）を②③④が読む所に書かない（09-29 本人決定）──
# ③が基準を知ると、基準に合わせて書く。`08_質の検証.md`（案件ごとの結果）の名前は CLAUDE.md §3 にあってよい。

CRITERIA = re.compile(r"(?<!\d_)質の検証\.md")


def criteria_refs(root):
    """CLAUDE.md と .claude/skills/ の下（②③④と司令塔が読むもの）で、質の検証.md を指している所。"""
    targets = [root / "CLAUDE.md", *sorted((root / ".claude" / "skills").rglob("*.md"))]
    return [str(p.relative_to(root)) for p in targets if p.exists() and CRITERIA.search(p.read_text(encoding="utf-8"))]


def test_quality_criteria_not_in_agent_reads():
    assert criteria_refs(REPO) == []


def test_quality_criteria_ref_is_caught(tmp_path):
    (tmp_path / ".claude" / "skills" / "x").mkdir(parents=True)
    (tmp_path / "CLAUDE.md").write_text("08_質の検証.md は結果\n", encoding="utf-8")
    (tmp_path / ".claude" / "skills" / "x" / "SKILL.md").write_text("基準は 質の検証.md を見る\n", encoding="utf-8")
    assert criteria_refs(tmp_path) == [os.path.join(".claude", "skills", "x", "SKILL.md")]
