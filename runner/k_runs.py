#!/usr/bin/env python3
"""runner/k_runs.py ｜ ②→check_genba_ref→B-1 を k 回まわし、ぶれの幅を出す（実走 #79・79-3）

  使い方
    python3 runner/k_runs.py --case 案件/_TEST_配管検証 --out {出力先} --k 3 --model opus [--prompt 案件/_TEST_配管検証/_プロンプト.md]

  なぜ要るか
    ②は1回ごとにぶれる（#75 で③のぶれが大きいと分かった）。1回同士を比べると、差が版のせいか
    ぶれのせいか分からない。k 回の幅で見る（外部の調査の施策1 と同じ考え）。

  出すもの
    {出力先}/r1 … rk（各回の 04・B-1.md・実行記録）と {出力先}/_ぶれ.md（回ごとの件数と、どの回でも「あり」でない行）
    ★_ぶれ.md には件数と行の # だけを書く（04 やメモの本文は書かない＝守秘・B-1 の雛形と同じ）
"""
import argparse, re, shutil, subprocess, sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
MEMO = "_材料/B_現場/現場メモ.md"
VERDICTS = ("あり", "一部", "なし")
REASONS = ("メモに無い人物", "メモに無い数字", "メモに無い出来事", "その他")   # これ以外は写さない（守秘・点検 #7）


def one(i, a, case, out):
    d = out / f"r{i}"
    common = (["--model", a.model] if a.model else [])
    r = subprocess.run([sys.executable, str(HERE / "run_stage.py"), "2", "--case", str(case), "--out", str(d),
                        "--prompt", a.prompt] + common, capture_output=True, text=True)
    if r.returncode != 0:
        return i, f"② 失敗：{(r.stderr or r.stdout).strip()[-200:]}"
    (d / MEMO).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(case / MEMO, d / MEMO)           # check_genba_ref は 04 の隣のメモを読む
    ref = subprocess.run([sys.executable, str(REPO / "check_genba_ref.py"), str(d / "04_現場分析.md")],
                         capture_output=True, text=True)
    (d / "_check_genba_ref.txt").write_text(ref.stdout, encoding="utf-8")
    if ref.returncode != 0:
        return i, "check_genba_ref NG（B-1 は回していない）"
    r = subprocess.run([sys.executable, str(HERE / "run_stage.py"), "B1", "--case", str(d), "--out", str(d)] + common,
                       capture_output=True, text=True)
    return i, None if r.returncode == 0 else f"B-1 失敗：{(r.stderr or r.stdout).strip()[-200:]}"


def b1_rows(path):
    """B-1 の表 → [(節, #, 判定, 理由の種類)]"""
    rows = []
    for ln in Path(path).read_text(encoding="utf-8").splitlines():
        c = [x.strip() for x in ln.strip().strip("|").split("|")]
        if len(c) >= 3 and c[2] in VERDICTS:
            why = c[4] if len(c) > 4 else ""
            rows.append((c[0], c[1], c[2], why if why in REASONS or not why else "（決まりの語でない）"))
    return rows


def summarize(out, k, errors):
    lines = ["# ②のぶれ（k 回）", "", "| 回 | 芽（§1 の行） | ズレ（§2 の行） | あり | 一部 | なし | 一部・なしの行 |", "|---|---|---|---|---|---|---|"]
    tally = Counter()
    for i in range(1, k + 1):
        b = out / f"r{i}" / "B-1.md"
        if errors.get(i) or not b.exists():
            lines.append(f"| r{i} | — | — | — | — | — | {errors.get(i, 'B-1 が無い')} |")
            continue
        rows = b1_rows(b)
        n = Counter(v for _, _, v, _ in rows)
        bad = "・".join(f"{s}#{no}（{v}：{why}）" for s, no, v, why in rows if v != "あり")
        tally.update(n)
        lines.append(f"| r{i} | {sum(1 for s, *_ in rows if '1' in s)} | {sum(1 for s, *_ in rows if '2' in s)} | "
                     f"{n['あり']} | {n['一部']} | {n['なし']} | {bad or '—'} |")
    ok = sum(1 for i in range(1, k + 1) if not errors.get(i) and (out / f"r{i}" / "B-1.md").exists())
    lines += ["", f"回せた回数：{ok}/{k}。合計：あり{tally['あり']}・一部{tally['一部']}・なし{tally['なし']}。",
              "★行の # は回ごとに中身が違う（同じ # が同じ芽とは限らない）。同じ芽かは各回の 04 を見て本人が判断する。"]
    (out / "_ぶれ.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--k", type=int, default=3)
    ap.add_argument("--model")
    ap.add_argument("--prompt", default=str(REPO / ".claude/skills/cross-run/assets/subagent-prompts.md"))
    a = ap.parse_args()
    case, out = Path(a.case).resolve(), Path(a.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=a.k) as ex:
        errors = dict(ex.map(lambda i: one(i, a, case, out), range(1, a.k + 1)))
    print(summarize(out, a.k, {i: e for i, e in errors.items() if e}))


if __name__ == "__main__":
    main()
