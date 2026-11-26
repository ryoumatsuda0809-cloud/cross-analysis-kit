#!/bin/sh
# フックを動かす Python を選ぶ。Mac/Linux は python3、Windows は python か py。
# 見つからなければ 2 で止める（封を守るフックが黙って素通りしないように）。
for p in python3 python py; do
  if "$p" -c "import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)" >/dev/null 2>&1; then
    PYTHONUTF8=1 exec "$p" "$@"
  fi
done
echo "✋ hook：Python 3.9 以上が見つからない" >&2
exit 2
