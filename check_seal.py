#!/usr/bin/env python3
"""check_seal.py ｜ settings.json の deny に封(03/02b)が入っているかだけを確認する。

★このスクリプトは封を「外す」ことも「入れる」こともしない。確認だけ。
settings.json を編集してよいのは本人だけ（CLAUDE.md §1-1・実走ログ 19-1）。

使い方：python3 check_seal.py
"""
import json
import sys
from pathlib import Path

SETTINGS = Path(__file__).parent / ".claude" / "settings.json"

# 封として必須のパターン（実走ログ 3-59 で確定した2系統。./ 付き・無し両方を見る）
REQUIRED_SUBSTRINGS = [
    "03_仮説_封.md",
    "02b_*_封.md",
]


def main() -> int:
    if not SETTINGS.exists():
        print(f"✗ {SETTINGS} が見つかりません")
        return 1

    try:
        data = json.loads(SETTINGS.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"✗ settings.json が JSON として読めません：{e}")
        return 1

    deny = data.get("permissions", {}).get("deny", [])

    # Read の deny でなければ封にならない（Edit などの deny では読める。09-29）
    missing = [s for s in REQUIRED_SUBSTRINGS
               if not any(rule.startswith("Read(") and s in rule for rule in deny)]

    if missing:
        print("✋ 封が外れています。settings.json の permissions.deny に以下が無い：")
        for m in missing:
            print(f"    {m}")
        print("  → 本人が settings.json を直接編集して戻すこと。AIには編集させない。")
        return 1

    print(f"✓ 封は入っています（{len(deny)}件の deny ルール中、03/02b の2パターンを確認）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
