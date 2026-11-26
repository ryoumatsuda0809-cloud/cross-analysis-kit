#!/usr/bin/env python3
"""runner/run_stage.py ｜ ②〜④を「道具を持たない AI」に渡して回す（10-18 本人決定・STATUS §2 1b）

  使い方
    python3 runner/run_stage.py 2  --case 案件/_TEST_配管検証 --out {出力先} [--prompt 案件/_TEST_配管検証/_プロンプト.md]
    python3 runner/run_stage.py B1 --case {出力先} --out {出力先}      （②の 04 を見る。memo は --case から）
    python3 runner/run_stage.py 3  --case 案件/_TEST_配管検証 --out {出力先} [--prompt {③のプロンプト}.txt]
      → 実行中に「▶ 03 をコピーしてください」と出る。本人がエディタで 03（あれば先に 02b）を全選択→コピーする

  なぜこの形か
    今の cross-run は「何でも読める AI を deny で止める」。ここでは AI に道具を一切持たせず
    （claude -p --tools ""）、ファイルはこのプログラムが読んで文章として渡す。
    ★封＝渡さない。渡す物は下の STAGES の表だけ。AI 側に開く手段が無いので、モデルを替えても封は崩れない。
    ★このプログラム自身も封のファイルを開かない。名前に「封」があるファイルは読む前に止める。
    ★③の 02b・03 だけは、本人がコピーした中身をこのプログラムがクリップボードから直接受け取る（10-18 本人決定）。
      見出しで案件を照合し、事前の基準を strip_kijun で外し、受け取ったらクリップボードを空にする。
      中身は画面にも記録にも出さない（司令塔の会話に入らない＝pbpaste を司令塔が受けていた 10-03 の形より固い）。
      ③には 04→01i→02 の後、最後に 02b→03 の順で添付する（78-3：03 が先に目に入らない）。
    指示の本文は今と同じ雛形（cross-run の assets、または案件の _プロンプト.md・前回の .txt）から取り、写しを作らない。

  出すもの（--out）
    {出力ファイル}・_報告_{段}.md（AI の報告）・_実行記録_{段}.json（モデル・費用・渡したファイルと sha256）
    ★出力先は案件フォルダの外にする（今の版の出力を上書きしない・check_anken の「案件内の _ フォルダ」を作らない）
"""
import argparse, glob, hashlib, json, os, re, shutil, subprocess, sys, tempfile, time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PROMPTS = REPO / ".claude/skills/cross-run/assets/subagent-prompts.md"
MEMO = "_材料/B_現場/現場メモ.md"
OUT_BEGIN, OUT_END = "<<<出力ここから>>>", "<<<出力ここまで>>>"
FALLBACK_01 = {"01i_外形カード_内部用.md": "01_外形カード_事実編.md"}   # #14 以前の案件（check_anken の FALLBACK と同じ）

sys.path.insert(0, str(REPO / ".claude/skills/cross-run/scripts"))
from strip_kijun import strip  # noqa: E402

# ★渡す物の表（cross-run/SKILL.md の受け渡し表をコードにしたもの）。ここに無い物は AI に届かない。
STAGES = {
    "2": dict(
        heading="## ②",
        output="04_現場分析.md",
        repo_files=[".claude/skills/genba-ops/SKILL.md",
                    ".claude/skills/genba-ops/assets/04-genba-analysis-template.md",
                    "CLAUDE.md"],
        case_files=["01i_外形カード_内部用.md", MEMO, "02_現場で確認すべき問い.md"],
        fallback=FALLBACK_01,
        listings=[".claude/skills/_shared/industries"],
        sealed=[],
        required=[MEMO, "01i_外形カード_内部用.md"],          # 現場メモが無いのに②を回さない（cross-run Stage 0）
    ),
    "B1": dict(
        heading="## ②の後",
        output="B-1.md",
        repo_files=[],
        case_files=[MEMO, "04_現場分析.md"],
        fallback={},
        listings=[],
        sealed=[],
        required=[MEMO, "04_現場分析.md"],
    ),
    "3": dict(
        heading="## ③",
        output="05_反証レポート.md",
        repo_files=[".claude/skills/shinin-hansho/SKILL.md",
                    ".claude/skills/shinin-hansho/assets/05-hansho-template.md",
                    "CLAUDE.md"],
        case_files=["04_現場分析.md", "01i_外形カード_内部用.md", "02_現場で確認すべき問い.md"],   # 現場メモは渡さない（75-15）
        fallback=FALLBACK_01,
        listings=[],
        # (呼び名, ファイル名, 見出しにある語) ★この順で最後に添付する：人間の見立て → AI の仮説
        sealed=[("02b", "02b_主任診断士の見立て_封.md", "見立て"), ("03", "03_仮説_封.md", "仮説")],
        required=["04_現場分析.md", "01i_外形カード_内部用.md", "03_仮説_封.md"],   # 04 の無い③・03 の無い③は回さない
    ),
}


def find_claude():
    if os.environ.get("CLAUDE_BIN"):
        return os.environ["CLAUDE_BIN"]
    if shutil.which("claude"):
        return shutil.which("claude")
    hits = sorted(glob.glob(os.path.expanduser(
        "~/.vscode/extensions/anthropic.claude-code-*/resources/native-binary/claude")))
    if hits:
        return hits[-1]
    sys.exit("claude が見つからない（CLAUDE_BIN で指定する）")


def instruction(prompt_md, heading):
    """雛形の md から、見出し heading の節の最初の ``` ブロックを取り出す。.txt は全文がプロンプト"""
    guard(prompt_md, "雛形")
    src = Path(prompt_md).read_text(encoding="utf-8")
    if str(prompt_md).endswith(".txt"):
        body = src
    else:
        i = next((m.start() for m in re.finditer(rf"^{re.escape(heading)}(\s|$)", src, re.M)), None)
        if i is None:
            sys.exit(f"雛形に見出しが無い：{heading}（{prompt_md}）")
        nxt = re.search(r"^## ", src[i + 1:], re.M)
        sect = src[i: i + 1 + nxt.start()] if nxt else src[i:]
        m = re.search(r"^```\n(.*?)^```", sect, re.S | re.M)
        if not m:
            sys.exit(f"見出しの節にプロンプトのブロックが無い：{heading}")
        body = m.group(1)
    # 前の版のプロンプトに封の中身が埋め込まれたまま残っていることがある（点検 #1）
    if re.search(r"^\s*#\s*【封】|【封の添付", body, re.M):
        sys.exit(f"✋ 雛形の本文に封の中身らしい見出しがある：{Path(prompt_md).name}。AI は呼ばない")
    return body


def is_sealed(path):
    p = Path(path)
    return "封" in p.name or (p.exists() and "封" in p.resolve().name)


def guard(path, stage):
    """★読む前に止める。このプログラムは封のファイルを一度も開かない（中身の突き合わせもしない）"""
    if is_sealed(path):
        sys.exit(f"✋ 封のファイルを渡そうとした：{Path(path).name}（段 {stage}）。AI は呼ばない")


def gather(stage, case, memo_case):
    """渡すファイルを集める。戻り値：[(表示名, 本文)]・欠けの一覧"""
    st = STAGES[stage]
    items, missing = [], []
    for rel in st["repo_files"]:
        p = REPO / rel
        guard(p, stage)
        items.append((str(p), p.read_text(encoding="utf-8")))
    for rel in st["case_files"]:
        base = memo_case if rel == MEMO else case
        p = base / rel
        guard(p, stage)
        if not p.exists() and rel in st["fallback"]:
            p = base / st["fallback"][rel]
            guard(p, stage)
        if not p.exists():
            if rel in st["required"]:
                sys.exit(f"✋ 段 {stage} に要る {rel} が無い。AI は呼ばない")
            missing.append(rel)
            continue
        items.append((str(p), p.read_text(encoding="utf-8")))
    for rel in st["required"]:
        if rel not in st["case_files"] and not (case / rel).exists():   # 封は名前で有無だけ見る
            sys.exit(f"✋ 段 {stage} に要る {rel} が無い。AI は呼ばない")
    for rel in st["listings"]:
        d = REPO / rel
        names = sorted(x.name for x in d.iterdir() if not x.name.startswith("."))
        items.append((f"{d}/ の一覧（ls の結果）", "\n".join(names)))
    return items, missing


def sealed_present(stage, case):
    """この案件にある封（名前で見るだけ。開かない）"""
    return [s for s in STAGES[stage]["sealed"] if (case / s[1]).exists()]


def sealed_pointer(kind):
    return f"（この文章の最後の【封の添付：{kind}】に載せています。a〜c の添付を読み終えてから読んでください）"


def build(stage, case, memo_case, prompt_md, sealed_texts=None):
    """sealed_texts：[(呼び名, 基準を外した本文)]。③だけ。添付の一番最後に、この順で置く"""
    st = STAGES[stage]
    body = instruction(prompt_md, st["heading"])
    body = body.replace("{案件}", str(case)).replace("{リポジトリ}", str(REPO)).replace("{社名}", case.name)
    # 雛形の「{ここに…03…}」は中身ではなく、最後の添付への案内に置き換える（78-3）
    have = {k for k, _ in (sealed_texts or [])} if sealed_texts is not None else {k for k, *_ in sealed_present(stage, case)}
    body = re.sub(r"\{ここに[^}]*?(02b|03)[^}]*\}",
                  lambda m: sealed_pointer(m.group(1)) if m.group(1) in have else f"（この案件に {m.group(1)} はありません）", body)
    items, missing = gather(stage, case, memo_case)
    head = (
        "■■ この実行のしくみ（プログラムから）■■\n"
        "あなたはファイルを開く道具も、書き込む道具も持っていません。\n"
        "下の指示で「Read してください」「ls してください」「読んでください」とあるファイルは、"
        "この文章の最後に【添付】として全文を載せています。添付に無いファイルは、あなたには渡されていません。\n"
    )
    if stage != "B1":
        head += (f"保存はこのプログラムが行います。{st['output']} の本文は、"
                 f"{OUT_BEGIN} の行と {OUT_END} の行の間に全文を書いてください。"
                 "報告（指示の「最後に報告してほしいこと」）はその後に書いてください。\n")
    if missing:
        head += "渡していないファイル（この案件に無い）：" + "・".join(missing) + "\n"
    if st["sealed"]:
        got = [k for k, _ in (sealed_texts or [])]
        absent = [k for k, *_ in st["sealed"] if k not in got]
        if absent:
            head += "この案件に無い封：" + "・".join(absent) + "\n"
        head += ("封の中身は、ファイルとしてではなく、本人がコピーしたものをこのプログラムが受け取り、"
                 "事前の基準を外してから、添付の一番最後に置いています。\n")
    att = "".join(f"\n\n【添付】{name}\n`````\n{text}\n`````" for name, text in items)
    for kind, text in sealed_texts or []:
        att += f"\n\n【封の添付：{kind}】\n`````\n{text}\n`````"
    return head + "\n" + body + att, items


def heading_company(h):
    return h.rsplit("｜", 1)[-1].replace("【架空】", "").replace("御中", "").strip() or None


def company_of(case):
    """01i（無ければ 01）の見出しから会社名を取る。見出しの照合に使う"""
    for name in ("01i_外形カード_内部用.md", "01_外形カード_事実編.md"):
        p = case / name
        if p.exists():
            for ln in p.read_text(encoding="utf-8").splitlines():
                if ln.startswith("# "):
                    return heading_company(ln)
    return None


def _clip_cmds():
    """(読む, 空にする) のコマンド。Mac は pbpaste、Windows は PowerShell、Linux は wl-paste か xclip。"""
    if sys.platform == "darwin":
        return ["pbpaste"], ["pbcopy"]
    if sys.platform.startswith("win"):
        ps = ["powershell", "-NoProfile", "-Command"]
        return (ps + ["[Console]::OutputEncoding=[Text.Encoding]::UTF8; Get-Clipboard -Raw"],
                ps + ["Set-Clipboard -Value $null"])
    if shutil.which("wl-paste"):
        return ["wl-paste", "--no-newline"], ["wl-copy", "--clear"]
    return ["xclip", "-selection", "clipboard", "-o"], ["xclip", "-selection", "clipboard", "-i"]


def read_clipboard():
    r = subprocess.run(_clip_cmds()[0], capture_output=True)
    return r.stdout.decode("utf-8", errors="replace").replace("\r\n", "\n")


def clear_clipboard():
    subprocess.run(_clip_cmds()[1], input=b"")
    if read_clipboard():
        print("⚠ クリップボードを空にできなかった。本人が別の文字をコピーして上書きしてください", flush=True)


LABELS = ("仮説", "見立て")


def take_sealed(kind, label, company, read_clip=read_clipboard, clear=clear_clipboard,
                timeout=900, poll=2.0, say=print):
    """本人がコピーした封をクリップボードから受け取る。★中身は返り値だけ。画面・記録には出さない
    どの終わり方（受け取った・照合 NG・時間切れ・中断）でも、クリップボードは空にする"""
    try:
        return _take(kind, label, company, read_clip, clear, timeout, poll, say)
    finally:
        clear()


def _take(kind, label, company, read_clip, clear, timeout, poll, say):
    say(f"▶ {kind} をエディタで開き、全選択→コピーしてください（{int(timeout // 60)}分待ちます。中身は表示しません）",
        flush=True)
    seen, last = None, None
    deadline = time.time() + timeout
    while time.time() < deadline:
        t = read_clip()
        if t != seen:
            seen = t
            h = next((ln for ln in t.splitlines() if ln.startswith("# ")), "")
            other = [x for x in LABELS if x != label]
            if label in h and not any(x in h for x in other):
                if heading_company(h) != company:
                    msg = f"✗ {kind} らしいものが届いたが、見出しの会社名がこの案件と違う（照合 NG）。正しい案件の {kind} をコピーし直してください"
                else:
                    body, dropped, cut, left = strip(t)
                    if left:
                        sys.exit(f"✋ {kind} の事前の基準が外し残し {len(left)} 行。AI は呼ばない（本人に知らせる）")
                    say(f"✓ {kind} を受け取った（照合 OK・基準を外した：行ごと {dropped}・一部 {cut}）", flush=True)
                    return body
                if msg != last:
                    say(msg, flush=True)
                    last = msg
                clear()                        # 別案件の封をクリップボードに残さない
        time.sleep(poll)
    sys.exit(f"{kind} が {int(timeout // 60)} 分以内に届かなかった。AI は呼ばない")


def call(prompt, model=None, timeout=1800):
    cmd = [find_claude(), "-p", "--tools", "", "--strict-mcp-config", "--disable-slash-commands",
           "--setting-sources", "", "--no-session-persistence", "--output-format", "json"]
    if model:
        cmd += ["--model", model]
    with tempfile.TemporaryDirectory() as cwd:   # リポジトリの外で呼ぶ（CLAUDE.md・スキル・フックを読ませない）
        r = subprocess.run(cmd, input=prompt, capture_output=True, text=True, cwd=cwd, timeout=timeout)
    if r.returncode != 0:
        sys.exit(f"claude が失敗した（exit {r.returncode}）：{r.stderr[-500:]}")
    return json.loads(r.stdout)


def check_out(out):
    """出力（封やメモの中身を含みうる）を git に上がる場所に書かない（CLAUDE.md §5・点検 #6）"""
    if out.is_relative_to(REPO) and not any(out.is_relative_to(REPO / d) for d in ("案件", "診断結果")):
        sys.exit(f"✋ 出力先がリポジトリの中で git に上がる場所：{out}。案件/ の下かリポジトリの外にする")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=STAGES)
    ap.add_argument("--case", required=True, help="入力を読む案件フォルダ（B1 では 04 のあるフォルダ）")
    ap.add_argument("--memo-case", help="現場メモのある案件フォルダ（既定は --case）")
    ap.add_argument("--out", required=True)
    ap.add_argument("--prompt", default=str(PROMPTS), help="指示の雛形（既定は cross-run の assets）")
    ap.add_argument("--model")
    ap.add_argument("--dry", action="store_true", help="組み立てて検査するだけ。AI は呼ばない・封は受け取らない")
    a = ap.parse_args()

    case, out = Path(a.case).resolve(), Path(a.out).resolve()
    check_out(out)
    memo_case = Path(a.memo_case).resolve() if a.memo_case else case
    prompt, items = build(a.stage, case, memo_case, a.prompt)      # 封の前に、封以外が揃うかを先に確かめる
    sealed = sealed_present(a.stage, case)
    rec = dict(stage=a.stage, case=str(case), prompt_template=a.prompt,
               files=[dict(name=n, sha256=hashlib.sha256(t.encode()).hexdigest()) for n, t in items],
               sealed_expected=[k for k, *_ in sealed], prompt_chars=len(prompt))
    if a.dry:
        print(json.dumps(rec, ensure_ascii=False, indent=1))
        return
    sealed_texts = []
    if sealed:
        company = company_of(case)
        if not company:
            sys.exit("01i／01 の見出しから会社名が取れない（封の照合ができない）。AI は呼ばない")
        for kind, _, label in sealed:
            sealed_texts.append((kind, take_sealed(kind, label, company)))
        prompt, items = build(a.stage, case, memo_case, a.prompt, sealed_texts)
        rec["files"] += [dict(name=f"{k}（クリップボード・基準を外した後）", sha256=hashlib.sha256(t.encode()).hexdigest())
                         for k, t in sealed_texts]
        rec["prompt_chars"] = len(prompt)
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    res = call(prompt, a.model)
    del prompt, sealed_texts
    text = res.get("result") or ""
    rec.update(seconds=round(time.time() - t0), cost_usd=res.get("total_cost_usd"),
               models=list((res.get("modelUsage") or {}).keys()), is_error=res.get("is_error"))
    st = STAGES[a.stage]
    if a.stage == "B1":
        (out / st["output"]).write_text(text, encoding="utf-8")
    else:
        m = re.search(rf"{re.escape(OUT_BEGIN)}\n(.*?)\n{re.escape(OUT_END)}", text, re.S)
        if not m:
            (out / f"_生の返答_{a.stage}.md").write_text(text, encoding="utf-8")
            sys.exit(f"出力の区切りが無い → _生の返答_{a.stage}.md に保存した")
        (out / st["output"]).write_text(m.group(1).rstrip() + "\n", encoding="utf-8")
        (out / f"_報告_{a.stage}.md").write_text(text[m.end():].strip() + "\n", encoding="utf-8")
    (out / f"_実行記録_{a.stage}.json").write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"✓ 段 {a.stage}：{st['output']}・{rec['seconds']}秒・{rec['cost_usd']} USD・{rec['models']}")


if __name__ == "__main__":
    main()
