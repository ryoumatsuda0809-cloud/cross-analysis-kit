#!/usr/bin/env python3
"""SKILL.md からローカル参照を抽出し、参照先の存在だけを検査する。"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


MARKDOWN_LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
CODE_SPAN = re.compile(r"`([^`]+)`")
PATH_PREFIXES = ("assets/", "references/", "scripts/", "../", "./", ".claude/skills/")
IGNORED_PREFIXES = ("案件/", "{", "_")


class Reference:
    __slots__ = ("source", "line", "text", "target")

    def __init__(self, source: Path, line: int, text: str, target: Path):
        self.source = source
        self.line = line
        self.text = text
        self.target = target


def _clean_target(value: str) -> str:
    """Markdown のリンク先から fragment と表示用の余分な空白を除く。"""
    return value.strip().split("#", 1)[0].split("?", 1)[0].strip("<>")


def _is_local_path(value: str) -> bool:
    value = _clean_target(value)
    if not value or any(char.isspace() for char in value) or value.startswith("http") or any(value.startswith(prefix) for prefix in IGNORED_PREFIXES):
        return False
    if "{" in value or "}" in value or "*" in value or "..." in value:
        return False
    return value.startswith(PATH_PREFIXES)


def _resolve(root: Path, skill_file: Path, value: str) -> Path:
    value = _clean_target(value)
    if value.startswith(".claude/skills/"):
        return root / value
    return skill_file.parent / value


def extract_references(root: Path, skill_file: Path) -> list[Reference]:
    lines = skill_file.read_text(encoding="utf-8").splitlines()
    found: dict[tuple[int, str], Reference] = {}
    for line_number, line in enumerate(lines, 1):
        values = [match.group(1) for match in MARKDOWN_LINK.finditer(line)]
        values.extend(match.group(1) for match in CODE_SPAN.finditer(line))
        for value in values:
            target = _clean_target(value)
            if not _is_local_path(target):
                continue
            key = (line_number, target)
            found[key] = Reference(skill_file, line_number, target, _resolve(root, skill_file, target))
    return sorted(found.values(), key=lambda item: (item.source.as_posix(), item.line, item.text))


def verify(root: Path, skills_root: Path) -> list[str]:
    findings: list[str] = []
    skill_files = sorted(skills_root.rglob("SKILL.md"))
    if not skill_files:
        return [f"SKILL.md が見つからない：{skills_root}"]
    for skill_file in skill_files:
        for reference in extract_references(root, skill_file):
            if not reference.target.exists():
                relative_source = reference.source.relative_to(root)
                relative_target = reference.target.relative_to(root) if reference.target.is_relative_to(root) else reference.target
                findings.append(
                    f"{Path(relative_source).as_posix()}:{reference.line} 参照先が無い：`{reference.text}` → {Path(relative_target).as_posix()}"
                )
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="リポジトリのルート")
    parser.add_argument("--skills-root", type=Path, default=Path(".claude/skills"), help="スキルのルート")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    skills_root = (root / args.skills_root).resolve() if not args.skills_root.is_absolute() else args.skills_root.resolve()
    findings = verify(root, skills_root)
    for finding in findings:
        print(f"  NG   {finding}")
    if not findings:
        print(f"  OK   SKILL.md {len(list(skills_root.rglob('SKILL.md')))} 件の参照先")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())