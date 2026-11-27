#!/usr/bin/env python3
"""check_report.py ｜ 提出レポート（06）の検査

  python3 check_report.py <06.md>            提出版として検査（コメントが残っていたら NG）
  python3 check_report.py --draft <06.md>    提出前版として検査（内部メモは許容）
  python3 check_report.py <一時.md> --name <表示名>   表示だけ差し替える（build.sh 用）

  ★2つのモードがある理由（実走ログ 29-3 #1／B-1）
    `report-template.md` は内部メモ（HTMLコメント）を**必須**にしている。
    だから④の生の出力は原理的に「コメントあり」であり、
    旧版はそれを NG にしていたので **④の出力は絶対に検査を通らず、PDF が作れなかった。**
    → 通常は `--draft` で書き進め、PDF を作るときだけ提出版として検査する。
      `build.sh` はコメントを機械的に除去してから提出版検査を掛ける（B-7）。

  ★内部メモの中は、どちらのモードでも検査対象から外す（B-1）
    内部メモには「棄却」「判定表」などの内部語が**入っていて当然**。
    そこを NG にすると、正しく書いたものが落ちる。**見るのは本文だけ。**

  何を見るか（`tougou-report/SKILL.md` §出力仕様）
    1. 必須節が落ちていないか  ← 2026-09-19 に業際の節を丸ごと落とした（16-1）
    2. 内部語が本文に残っていないか
    3. ★内部の採番・参照が本文に漏れていないか（**語リストに依存しない構造検査**／B-6）
    4. 「誠実さの宣言」が入っていないか（AIっぽさの最大の原因／16-2）
    5. 本人が書く欄が埋まっているか
    6. ★太字を撒いていないか（実走ログ #44。案件Dで本文の行の38%に太字＝どこも目立たない）
       文中の太字は 1節に1か所・20字まで。項目名（「**何が起きているか**：」）は数えない
    7. ★事前の基準・p・確率が本文に出ていないか（10-01 の事前の基準。p も当たり外れも社内だけ）
       H1 の形は 3 で捕まるので、ここは語と数の形だけ（「1人当たり」「社員の8割」「前年比80%」は拾わない）
"""
import re, sys, io

BOLD_PER_SEC = 1    # 文中の太字は1節に1か所まで（#44）
BOLD_MAX_LEN = 20   # 太字は20字まで（#44）

# 1. 必須節（部分一致で照合。順序は問わない）
REQUIRED = [
    ("この診断が見た範囲", "誰に何人聞いたかの線引き"),
    ("この診断の限界",     "会えていない人・取れていない数字。差別化そのもの"),
    ("本レポートで踏み込んでいない領域", "★業際（弁護士法72条・税理士法52条・社労士法27条・行政書士法1条の2）"),
    ("一緒に確かめたい問い", "伴走の入口"),
    ("次の一歩",           "押し売りしない締め"),
]

# 2. 本文に残ってはいけない語
#    ★これはブロックリストなので fail-open（知らない語を通す）。
#      実際 2026-09-21 に「判定表」が載っておらず素通りした（31-2／B-6）。
#      → 下の STRUCTURAL（構造検査）と併用する。語リストだけに頼らない。
INTERNAL = ["実態", "自己申告", "定規", "棄却", "見立て", "内部メモ",
            "_材料", "実走ログ", "SKILL.md", "README_これは", "genba-ops",
            "shinin-hansho", "market-recon", "tougou-report", "封",
            # --- 2026-09-21 追加（B-6／31-2）---
            "判定表", "クロス表", "格付け表", "真因の芽", "採用・要検証", "格付け"]

# 3. ★内部の採番・参照（構造で見る。語を知らなくても捕まる／B-6）
#    2026-09-21 実測：06 のコメント内にのみ出現、提出水準のデモには 0 件。誤検出しない。
STRUCTURAL = [
    (re.compile(r"[（(]\s*[A-Z]\d+[a-z]?\s*[)）]"), "内部の採番（（H3a）（X1）の形）が本文にある"),
    (re.compile(r"(?<![A-Za-z])[HX]\d+[a-z]?(?![A-Za-z0-9])"), "内部の採番（H1・X5 の形）が本文にある"),
    (re.compile(r"〔[^〕]*\b0[1-7][a-zA-Z]?\b[^〕]*〕"), "〔〕の中に 01〜07 の採番がある"),
    (re.compile(r"〔[^〕]*\d+(?:[・,、]\s*\d+)+[^〕]*〕"), "〔〕の中に番号の羅列がある"),
    (re.compile(r"(?<![0-9])0[1-9][a-z]?\s*の\s*(採用|要検証|棄却|判定)"), "他ファイルの判定への参照がある"),
    # --- 2026-09-25 追加（実走ログ #47。pdf-migaki が案件Dで検出：本文に社内のファイル名がそのまま出ていた）---
    (re.compile(r"(?<![0-9A-Za-z])0[1-7][a-z]?_\S"), "社内のファイル名（01_・02b_ の形）が本文にある", "顧客向けの言い方にする（例：事前にお渡しした問い）"),
    (re.compile(r"`[^`]+`"), "コード表示（バッククォート）が本文にある", "顧客の紙に要らない。記号を外す"),
]

# 4. 誠実さの宣言（16-2）
SINCERITY = ["正直に書きます", "正直にお伝えします", "隠さずに", "誠実だと考え",
             "弱みを隠さない", "包み隠さず"]

# 4b. ★断定語（2026-09-22 追加／C-6・実走ログ 29-3 #7）
#     ③の問い文と④の本文で語彙を揃えるための**唯一の原本**。③の SKILL.md もここを見る。
#     ③が「確認済みですか」と書き、④がそのまま転記して禁止語が入った。
ASSERTIVE = ["確認済み", "実証", "明らかにな", "判明"]

# 4c. ★事前の基準・p・確率（2026-10-03 追加。03・02b テンプレの「06 には書かない」を見る物が無かった）
PRIOR = [
    (re.compile(r"〔\s*(当たり|外れ|いつ|手段|[pPｐＰ])\s*〕"), "事前の基準の印が本文にある"),
    (re.compile(r"当たる見込み|当たりの条件|外れの条件"), "事前の基準の語が本文にある"),
    (re.compile(r"(?<![A-Za-z])[pPｐＰ]\s*[=＝:：]\s*0?[.．]\d"), "p の値が本文にある"),
    (re.compile(r"\d{1,3}\s*[%％]\s*の(確率|見込み|可能性)|確率\s*[は=＝:：]?\s*0?[.．]\d"
                r"|[0-9０-９一二三四五六七八九]\s*割\s*の(確率|見込み)"), "確率・見込みの数が本文にある"),
    (re.compile(r"[Bb]rier|ブライア|的中率"), "採点の語が本文にある"),
]

# 5. 埋めていない欄
PLACEHOLDER = re.compile(r"\{[^}]{4,}\}")
COMMENT = re.compile(r"<!--.*?-->", re.S)

def strip_comments(src):
    """内部メモを空行に置き換える（行番号を保つため改行は残す）"""
    return COMMENT.sub(lambda m: "\n" * m.group(0).count("\n"), src)

def main():
    argv = sys.argv[1:]
    draft = "--draft" in argv
    disp = None
    if "--name" in argv:                      # 表示名（build.sh が一時ファイルを検査するため）
        i = argv.index("--name"); disp = argv[i+1]; argv = argv[:i] + argv[i+2:]
    args = [a for a in argv if not a.startswith("--")]
    if not args:
        print(__doc__); sys.exit(2)
    path = args[0]
    src = io.open(path, encoding="utf-8").read()
    body = strip_comments(src)          # ★以降の検査はすべて本文だけを見る
    lines = body.splitlines()
    errs, warns = [], []

    heads = "\n".join(re.findall(r"^#{1,3}\s+(.+)$", body, re.M))
    for key, why in REQUIRED:
        if key not in heads:
            errs.append(f"必須節が無い：「{key}」　← {why}")

    for i, line in enumerate(lines, 1):
        for w in INTERNAL:
            if w in line:
                errs.append(f"L{i} 内部語が本文に残っている：「{w}」")
        for rx, why, *h in STRUCTURAL:
            hint = h[0] if h else "対応表は内部メモにだけ書く（B-6）"
            m = rx.search(line)
            if m:
                errs.append(f"L{i} {why}：「{m.group(0)}」　← {hint}")
        for w in ASSERTIVE:
            if w in line:
                errs.append(f"L{i} 断定語が本文にある：「{w}」　← 証拠の強さを超える（定義-1／C-6）")
        for w in SINCERITY:
            if w in line:
                errs.append(f"L{i} 誠実さを宣言している：「{w}」　← 書きぶりで示す（16-2）")
        for rx, why in PRIOR:
            m = rx.search(line)
            if m:
                errs.append(f"L{i} {why}：「{m.group(0)}」　← p も当たり外れも社内だけ。06 では確からしさを数で言わない")

    if COMMENT.search(src):
        n = len(COMMENT.findall(src))
        if draft:
            warns.append(f"内部メモ {n} 件（提出前版なので可）。**PDFを作る前に除去する** → build.sh が自動でやる")
        else:
            errs.append(f"内部メモ（HTMLコメント）が {n} 件残っている。提出版では必ず削除する")

    # 6. 太字（節ごとに数える。節＝見出し h1〜h3 の区切り）
    BOLD = re.compile(r"\*\*(.+?)\*\*")
    sec, sec_line, cnt = "（冒頭）", 1, []
    def flush():
        if len(cnt) > BOLD_PER_SEC:
            errs.append(f"L{sec_line} 節「{sec[:20]}」の文中の太字が {len(cnt)} か所（1節に{BOLD_PER_SEC}か所まで）："
                        + "／".join(t[:12] for t in cnt[:4]) + ("…" if len(cnt) > 4 else ""))
    for i, line in enumerate(lines, 1):
        h = re.match(r"^#{1,3}\s+(.+)$", line)
        if h:
            flush(); sec, sec_line, cnt = h.group(1), i, []
            continue
        # ★1行に項目名だけの太字（「**何が起きているか**」「1. **一次情報**」）は見出しと同じ構造なので数えない
        #   （実走ログ #47。テンプレの書き方を #44 の検査が文中の太字と数え、案件Dの 06 が NG 45件で PDF を作れなかった
        #    ＝B-1・B-6 と同じ「指示と検査の食い違い」3例目）。20字を超えるものは項目名ではなく文なので数える
        #   ★句点・読点・疑問符を含むものは文なので項目名にしない（1行に置いた文ごとの太字が素通りしていた／pdf-migaki モードB）
        lab = re.match(r"^\s*(?:[-*]\s+|\d+\.\s+|>\s*)?\*\*([^*]+)\*\*[：:]?\s*$", line)
        if lab and len(lab.group(1)) <= BOLD_MAX_LEN and not re.search(r"[。、？！?!]", lab.group(1)):
            continue
        for m in BOLD.finditer(line):
            t = m.group(1)
            nxt = line[m.end():m.end()+1]               # ★行末だと "" になり、"" in "：:" は True（空文字は必ず含まれる）
            if nxt and nxt in "：:" and not line.lstrip().startswith("|"):
                continue                                  # 項目名は構造なので数えない
            cnt.append(t)
            if len(t) > BOLD_MAX_LEN:
                errs.append(f"L{i} 太字が{len(t)}字（{BOLD_MAX_LEN}字まで。文ではなく語句を太くする）：「{t[:24]}…」")
    flush()

    for m in PLACEHOLDER.finditer(body):
        # ★提出版に未記入の欄が残るのは壊れた提出物（#44：④のやり直しで「はじめに」が空欄に戻るのを止める）
        (warns if draft else errs).append(f"未記入の欄：{m.group(0)[:46]}")

    n = len(body)
    if n > 5000:   # 2026-11-27 本人決定（tougou-report 出力仕様(2)）。16,000 から下げた
        warns.append(f"本文 {n:,} 字（上限 5,000）。削らずに移す：8つ目以降の問いと、本文に出ない数字の 9-2 を 07 へ"
                     "（課題・限界・採っていない説明の中身は削らない／C-7）")

    mode = "提出前版(--draft)" if draft else "提出版"
    print(f"=== check_report ｜ {disp or path}　[{mode}] ===")
    for e in errs:  print("  NG   " + e)
    for w in warns: print("  WARN " + w)
    if not errs and not warns:   print("  OK   問題なし")
    elif not errs:               print("  OK   必須節と禁止語は問題なし（WARN は確認のうえ進めてよい）")
    sys.exit(1 if errs else 0)

if __name__ == "__main__":
    main()
