#!/usr/bin/env python3
"""strip_kijun.py ｜ ③に埋め込む前に、`03`／`02b` の中身から事前の基準（〔当たり〕〜〔p〕）を外す

  なぜ要るか（10-01 の事前の基準・10-03 本人決定）
    cross-run Stage 4 で、司令塔は `03`・`02b` の中身を③のプロンプトに埋め込む。
    10-01 から各仮説に〔当たり〕〔外れ〕〔いつ〕〔手段〕〔p〕が付いたので、③は p＝0.8 を見て採用に寄りうる（係留）。
    ③が `05` に写せば④が `06` に運ぶ。「写すな」という指示では係留は防げない → ③に渡す前に**コードで**外す。

  ★決まり
    - **標準入力から読み、標準出力に出すだけ。ファイルを開かない・書かない**（引数があれば止まる）。
      `03` の写しをディスクに残さない（#75 のスクラッチパッドの写しと同じことを起こさない）。
    - 何を外したかは件数だけを標準エラーに出す。外した中身は出さない。
    - **外し残しがあれば何も出さずに exit 1**（中途半端な本文を③に渡さない）。

  外すもの
    1. 印（〔当たり〕〔外れ〕〔いつ〕〔手段〕〔p〕）が2つ以上ある行 → 行ごと
    2. 印が1つだけの行 → 印から次の〔 の前まで
    3. テンプレの説明（> で始まる行）のうち、基準に触れる行 → 行ごと
       （③に「基準がある」こと自体を知らせない。②に 03 の存在を知らせないのと同じ考え）
       ★本物のテンプレは「当たり／外れ：…」「手段：…」「社内だけ」の行も持つ（試作はこれを外し残した）

  使い方（Stage 4。本人がエディタで `03` を全選択→コピーした後に、司令塔が）
    pbpaste | python3 .claude/skills/cross-run/scripts/strip_kijun.py
    ★コマンドに中身が入らないので seal_guard とぶつからない（heredoc だと中身の「案件」と ** で止まりうる）
"""
import re
import sys

KEYS = r"(当たり|外れ|いつ|手段|[pPｐＰ])"
MARK = re.compile(rf"〔\s*{KEYS}\s*〕")
SEG = re.compile(rf"〔\s*{KEYS}\s*〕[^〔]*")
PVAL = r"(?<![A-Za-z])[pPｐＰ]\s*[=＝:：]\s*0?[.．]\d"
NOTE = re.compile(rf"事前の基準|当たる見込み|当たり|外れ|社内だけ|{PVAL}|0\.8\s*[／/]\s*0\.5"
                  r"|^>\s*-?\s*(いつ|手段|[pPｐＰ])\s*[：:（(]")
LEFT = re.compile(rf"〔\s*{KEYS}\s*〕|事前の基準|当たる見込み|{PVAL}")


def strip(text):
    """(外した後の本文, 行ごと外した数, 一部を削った数, 外し残しの行番号)"""
    out, dropped, cut = [], 0, 0
    for line in text.splitlines():
        n = len(MARK.findall(line))
        if n >= 2 or (line.lstrip().startswith(">") and NOTE.search(line.lstrip())):
            dropped += 1
            continue
        if n == 1:
            line = SEG.sub("", line).rstrip()
            cut += 1
        out.append(line)
    left = [i for i, l in enumerate(out, 1) if LEFT.search(l)]
    return "\n".join(out) + ("\n" if text.endswith("\n") else ""), dropped, cut, left


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv:
        print("✋ strip_kijun はファイルを開かない。中身を標準入力で渡す（pbpaste | python3 …）", file=sys.stderr)
        return 2
    body, dropped, cut, left = strip(sys.stdin.read())
    if left:
        print(f"✗ 外し残し {len(left)} 行（L{left[0]} など）。何も出さない。③に渡さず本人に知らせる", file=sys.stderr)
        return 1
    sys.stdout.write(body)
    print(f"✓ 事前の基準を外した：行ごと {dropped}・一部 {cut}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
