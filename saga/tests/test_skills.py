"""Unit tests for the skills library seeding — no infrastructure required."""

from pathlib import Path

from knowledge_base import KnowledgeBase
from skills import DEFAULT_SKILLS_DIR, SKILLS_PREFIX, seed_skills

# The vulnerability-class skills expected in the built-in library. Guards against
# accidental deletion/rename of a skill file.
EXPECTED_SKILLS = {
    "sql_injection.md",
    "reflected_xss.md",
    "broken_access_control.md",
    "path_traversal.md",
}


def test_seed_skills_populates_kb(tmp_path: Path):
    """Seeded files are readable via kb.get, proving the store-not-file path.

    KnowledgeBase.get reads memory only, so a file dropped straight onto disk
    would list but not read. seed_skills must go through kb.store.
    """
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    (skills_dir / "alpha.md").write_text("alpha content", encoding="utf-8")
    (skills_dir / "beta.md").write_text("beta content", encoding="utf-8")
    # A non-markdown file must be ignored.
    (skills_dir / "ignore.txt").write_text("nope", encoding="utf-8")

    kb = KnowledgeBase()
    count = seed_skills(kb, skills_dir)

    assert count == 2
    assert set(kb.list_dir(SKILLS_PREFIX)) == {"alpha.md", "beta.md"}
    assert kb.get(f"{SKILLS_PREFIX}/alpha.md") == "alpha content"
    assert kb.get(f"{SKILLS_PREFIX}/beta.md") == "beta content"


def test_seed_skills_missing_dir_is_noop(tmp_path: Path):
    """A missing skills directory returns 0 and raises nothing."""
    kb = KnowledgeBase()
    count = seed_skills(kb, tmp_path / "does_not_exist")
    assert count == 0
    assert kb.list_keys() == []


def test_seed_skills_empty_dir_is_noop(tmp_path: Path):
    """An empty skills directory returns 0."""
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    kb = KnowledgeBase()
    assert seed_skills(kb, skills_dir) == 0


def test_builtin_skills_library_present():
    """The real saga/skills/ library contains exactly the expected skill files."""
    kb = KnowledgeBase()
    count = seed_skills(kb)

    assert count == len(EXPECTED_SKILLS)
    assert set(kb.list_dir(SKILLS_PREFIX)) == EXPECTED_SKILLS


def test_builtin_skills_have_expected_sections():
    """Each built-in skill exposes the sections the agent prompts point at."""
    kb = KnowledgeBase()
    seed_skills(kb)

    # Every class carries an Exploitation section; the three DAST-tested classes
    # also carry a Detection section.
    for name in EXPECTED_SKILLS:
        content = kb.get(f"{SKILLS_PREFIX}/{name}")
        assert content is not None
        assert "## Exploitation" in content, name

    sqli = kb.get(f"{SKILLS_PREFIX}/sql_injection.md")
    assert "## Detection" in sqli
    # Spot-check that detection and exploitation knowledge both landed in the file.
    assert "OR 1=1" in sqli
    assert "updatexml" in sqli


def test_default_skills_dir_points_at_library():
    """DEFAULT_SKILLS_DIR resolves to the packaged saga/skills/ directory."""
    assert DEFAULT_SKILLS_DIR.name == "skills"
    assert DEFAULT_SKILLS_DIR.is_dir()
