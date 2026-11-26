"""SKILL.md のローカル参照検査を決定論的に固定する。"""
import os

from pathlib import Path


def load_verify_structure():
    import importlib.util

    path = Path(__file__).resolve().parent.parent / "scripts" / "verify_structure.py"
    spec = importlib.util.spec_from_file_location("verify_structure", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_existing_skill_references_are_valid():
    module = load_verify_structure()
    root = Path(__file__).resolve().parent.parent
    assert module.verify(root, root / ".claude" / "skills") == []


def test_missing_asset_is_reported_with_source_line(tmp_path):
    module = load_verify_structure()
    skills = tmp_path / ".claude" / "skills" / "demo"
    skills.mkdir(parents=True)
    (skills / "SKILL.md").write_text("テンプレート：`assets/missing.md`\n", encoding="utf-8")

    findings = module.verify(tmp_path, tmp_path / ".claude" / "skills")

    assert len(findings) == 1
    assert "demo/SKILL.md:1" in findings[0]
    assert "assets/missing.md" in findings[0]


def test_dynamic_anken_paths_and_urls_are_ignored(tmp_path):
    module = load_verify_structure()
    skills = tmp_path / ".claude" / "skills" / "demo"
    skills.mkdir(parents=True)
    (skills / "SKILL.md").write_text(
        "`案件/{会社名}/04_現場分析.md`\n"
        "`https://example.com/missing.md`\n"
        "`assets/ok.md`\n",
        encoding="utf-8",
    )
    (skills / "assets").mkdir()
    (skills / "assets" / "ok.md").write_text("ok\n", encoding="utf-8")

    assert module.verify(tmp_path, tmp_path / ".claude" / "skills") == []


def test_reference_content_is_not_opened(tmp_path):
    module = load_verify_structure()
    skills = tmp_path / ".claude" / "skills" / "demo"
    (skills / "assets").mkdir(parents=True)
    sealed = skills / "assets" / "03_仮説_封.md"
    blank = skills / "assets" / "blank.md"
    blank.touch()
    os.replace(blank, sealed)          # 作るだけ。開かない（Windows の touch は open を通る）
    (skills / "SKILL.md").write_text("`assets/03_仮説_封.md`\n", encoding="utf-8")

    assert module.verify(tmp_path, tmp_path / ".claude" / "skills") == []