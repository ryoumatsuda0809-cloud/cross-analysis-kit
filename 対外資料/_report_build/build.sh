#!/usr/bin/env bash
# build.sh ｜ レポートの md を PDF にする（何回やっても同じ結果にする）
#
#   ./build.sh ../デモ_20260919/見本_課題仮説レポート.md
#   ./build.sh ../../案件/案件D/06_課題仮説レポート.md
#
# ★PDF は「入力の .md と同じ場所」に出る。ここ（_report_build/）には出ない。
#   出してよい場所は 案件/・診断結果/・対外資料/デモ_*/・リポジトリの外 のみ。
#   それ以外を指定すると止まる（許可リスト方式。知らないパスは止める側に倒す）。
#
# ★体裁は style.css の1箇所だけで決まる。ここを触る。md には体裁を書かない。

set -euo pipefail
cd "$(dirname "$0")"

# ★リポジトリの健全性（実走ログ #43）。PDF は作るが、問題があれば必ず目に入るように出す
PY=$(for p in python3 python py; do "$p" -c "import sys" >/dev/null 2>&1 && { echo "$p"; break; }; done)
[ -n "$PY" ] || { echo "✗ Python が見つかりません"; exit 1; }
if ! "$PY" ../../check_anken.py --repo > /tmp/_repo.log 2>&1; then
  echo "⚠️  リポジトリに問題がある（PDF は作る。commit は止まる）"
  sed 's/^/  /' /tmp/_repo.log
  echo
fi

SRC="${1:?使い方: ./build.sh <レポートの.md> [出力.pdf]}"
# ★出力は「入力の .md と同じ場所」が既定（実走ログ 30-1／B-5）
#   以前は $PWD（＝このスクリプトのある 対外資料/_report_build/）に出していた。
#   そこは gitignore されていないので、顧客の診断結果が push 対象の場所に生成されていた。
# ★出力名（実走ログ #40）
#   出力先のフォルダに既に PDF が1つあれば、**それを上書きする**（前と今を両方作らない）。
#   2026-09-23、既定名を「.md と同じ名前」にしていたため、既存の
#   `{事務所名}_案件D_現状の整理.pdf` の横に `06_課題仮説レポート.pdf` が新しく作られ、2つ並んだ。
#   2つ以上あるときは、どれが正か分からないので止める。
if [ -z "${2:-}" ]; then
  _dir="$(dirname "$SRC")"
  _n=$(find "$_dir" -maxdepth 1 -name '*.pdf' | wc -l | tr -d ' ')
  if [ "$_n" -gt 1 ]; then
    echo "✗ $_dir に PDF が $_n 個ある。どれが最新か分からないので作らない。"
    find "$_dir" -maxdepth 1 -name '*.pdf' | sed 's/^/    /'
    echo "  → 古いものを 案件/_使わない/ へ移すか、出力名を2つ目の引数で指定する"
    exit 1
  elif [ "$_n" -eq 1 ]; then
    OUT="$(find "$_dir" -maxdepth 1 -name '*.pdf')"
    echo "  既存の PDF を上書きする：$(basename "$OUT")"
  else
    # ★初回は名前を必ず渡す（STATUS F-2・09-25 本人承認）
    #   以前は `06_課題仮説レポート.pdf` を既定にしていたが、社内のファイル名が顧客に渡る。
    #   社名・文書名は機械では決められないので、推測せず止める。
    echo "✗ $_dir に PDF がまだ無い。提出用の名前を2つ目の引数で渡す。"
    echo "  形：{事務所名}_{会社}様_{文書名}_{日付}.pdf（社名は 案件/_社名対応表_ローカル専用.md）"
    echo "  → ./build.sh $SRC \"$_dir/{事務所名}_{会社}様_{文書名}_{YYYY-MM-DD}.pdf\""
    exit 1
  fi
else
  OUT="$2"
fi

# --- 0. 出力先の検査（★許可した場所以外には出さない）-------------------
#   ブロックリストではなく**許可リスト**にする。
#   知らないパスは「通す」ではなく「止める」側に倒す（実走ログ #24〜26 の教訓）。
OUT_ABS="$(cd "$(dirname "$OUT")" 2>/dev/null && pwd)/$(basename "$OUT")" || {
  echo "✗ 出力先のディレクトリが存在しません: $(dirname "$OUT")"; exit 1; }
REPO="$(git rev-parse --show-toplevel 2>/dev/null || echo "")"
if [ -n "$REPO" ]; then
  REL="${OUT_ABS#"$REPO"/}"
  case "$REL" in
    案件/*|診断結果/*)   ;;   # gitignore 済み。顧客の診断結果はここ
    対外資料/デモ_*/*)   ;;   # 架空化済みのデモ。追跡してよい
    "$OUT_ABS")          ;;   # リポジトリの外。関与しない
    *)
      echo "✗ そこには出力しません: $REL"
      echo "  顧客の診断結果が git 追跡下に出ると CLAUDE.md §5（顧客データは push しない）に違反します。"
      echo "  出してよいのは：案件/ 配下・診断結果/ 配下・対外資料/デモ_*/ 配下・リポジトリの外 だけ。"
      echo "  → ./build.sh ../../案件/{社名}/06_課題仮説レポート.md"
      exit 1 ;;
  esac
fi

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# --- 1. ★内部メモを機械的に除去して「提出版」を作る（実走ログ 30-3／B-7）---
#      以前は行番号を手で指定して消していた。次の案件では通用しない。
#      06 本体には内部メモを残したまま、PDF に入るものからだけ落とす。
"$PY" - "$SRC" "$TMP/submit.md" <<'STRIP'
import io,re,sys
src=io.open(sys.argv[1],encoding='utf-8').read()
n=len(re.findall(r'<!--.*?-->', src, re.S))
body=re.sub(r'<!--.*?-->', lambda m:'\n'*m.group(0).count('\n'), src, flags=re.S)
io.open(sys.argv[2],'w',encoding='utf-8').write(body)
print(f"  内部メモ {n} 件を除去した（元ファイルは触っていない）")
STRIP

# --- 2. 必須節と禁止語の検査（通らなければ PDF を作らない）-------------
#      ★検査は「提出版」に掛ける。内部メモの中は見ない（B-1）
"$PY" check_report.py "$TMP/submit.md" --name "${SRC}（内部メモ除去後）" || { echo ""; echo "✗ 検査に通らなかったので PDF は作っていません。"; exit 1; }

# --- 3. 依存の確認 -----------------------------------------------------
command -v pandoc >/dev/null || { echo "✗ pandoc がありません（Mac：brew install pandoc／Windows：winget install pandoc）"; exit 1; }

CHROME="${CHROME:-}"
for c in \
  "$CHROME" \
  "/c/Program Files/Google/Chrome/Application/chrome.exe" \
  "/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe" \
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  "/Applications/Chromium.app/Contents/MacOS/Chromium" \
  "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge" \
  "/opt/pw-browsers/chromium-1194/chrome-linux/chrome" \
  "$(command -v chromium || true)" "$(command -v google-chrome || true)"
do [ -x "$c" ] && CHROME="$c" && break; done
[ -n "$CHROME" ] || { echo "✗ Chrome / Chromium が見つかりません"; exit 1; }

# --- 4. 箇条書きの前に空行を入れる（pandoc が list と認識するため）-----
"$PY" - "$TMP/submit.md" "$TMP/src.md" <<'PY'
import io,re,sys
src,dst=sys.argv[1],sys.argv[2]
out=[]
for l in io.open(src,encoding='utf-8').read().split('\n'):
    if re.match(r'^\s*(-|\d+\.)\s', l) and out and out[-1].strip():
        if not re.match(r'^\s*(-|\d+\.)\s', out[-1]) and not out[-1].lstrip().startswith('>'):
            out.append('')
    out.append(l)
io.open(dst,'w',encoding='utf-8').write('\n'.join(out))
PY

# --- 5. md → html → pdf -----------------------------------------------
DOCTITLE="$(grep -m1 '^# ' "$TMP/src.md" | sed -e 's/^# *//' -e 's/｜.*$//' -e 's/"/”/g')"
[ -n "$DOCTITLE" ] || DOCTITLE="レポート"
pandoc "$TMP/src.md" -f markdown+hard_line_breaks -t html5 -o "$TMP/body.html"
{ printf '<!DOCTYPE html><html lang="ja"><head><meta charset="utf-8">'
  # ★文書名は h1 から取る（PDF の Title 欄に社内のファイル名 06_課題仮説レポート が出ていた／実走ログ #47）
  #   「｜」より前だけを使う（宛名はヘッダーに出さない）
  printf '<title>%s</title><link rel="stylesheet" href="style.css">' "$DOCTITLE"
  printf '<style>@page{ @top-right{ content:"%s"; } } @page :first{ @top-right{ content:none; } }</style></head><body>\n' "$DOCTITLE"
  cat "$TMP/body.html"
  printf '</body></html>'
} > "$TMP/out.html"
cp style.css "$TMP/style.css"

"$CHROME" --headless --disable-gpu --no-sandbox --no-pdf-header-footer \
  --print-to-pdf="$OUT_ABS" --virtual-time-budget=8000 "$TMP/out.html" 2>/dev/null

echo "✓ $OUT_ABS"
"$PY" - "$OUT_ABS" <<'PY' 2>/dev/null || true
import sys
from pypdf import PdfReader
n=len(PdfReader(sys.argv[1]).pages)
print(f"  {n} ページ（上限は置かない。長さで削ってよいのは重複と体裁だけ → tougou-report §出力仕様(2)）")
PY
