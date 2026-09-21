"""Skills library seeding for the knowledge base.

Domain knowledge about vulnerability classes (how to detect and exploit them)
lives as a set of markdown files under ``saga/skills/`` rather than inline in the
agent system prompts. At run start these files are loaded into the run's
``KnowledgeBase`` under the ``skills/`` prefix, and the DAST/exploitation agents are
instructed to read the relevant skill before probing.

The files are seeded via :meth:`KnowledgeBase.store` — **not** by writing them
directly into the on-disk backing directory. ``KnowledgeBase.get`` reads the
in-memory store only, so a file dropped straight onto disk would be visible to
``kb_list_dir`` (which reads disk) but return "Not found" from ``kb_get`` (which
reads memory). Seeding through ``store`` populates memory; when the API later calls
``set_root`` the write-through flush persists the skills to
``saga_runs/{run_id}/knowledge_base/skills/`` as well, so each run also records the
exact skills it used.
"""

import logging
from pathlib import Path

from knowledge_base import KnowledgeBase

logger = logging.getLogger(__name__)

# saga/src/skills.py -> saga/skills/
DEFAULT_SKILLS_DIR = Path(__file__).resolve().parent.parent / "skills"

# KB prefix under which every skill is stored (e.g. "skills/sql_injection.md").
SKILLS_PREFIX = "skills"


def seed_skills(kb: KnowledgeBase, skills_dir: Path = DEFAULT_SKILLS_DIR) -> int:
    """Load every ``skills_dir/*.md`` file into ``kb`` under the ``skills/`` prefix.

    Each file is stored via :meth:`KnowledgeBase.store` at key
    ``skills/<filename>`` (e.g. ``skills/sql_injection.md``). A missing or empty
    directory is a no-op (a warning is logged for a missing directory).

    Args:
        kb: The knowledge base to seed.
        skills_dir: Directory holding the skill markdown files. Defaults to the
            built-in ``saga/skills/`` library.

    Returns:
        The number of skill files seeded.
    """
    if not skills_dir.is_dir():
        logger.warning("Skills directory not found, skipping seeding: %s", skills_dir)
        return 0

    count = 0
    for path in sorted(skills_dir.glob("*.md")):
        kb.store(f"{SKILLS_PREFIX}/{path.name}", path.read_text(encoding="utf-8"))
        count += 1

    logger.info("Seeded %d skill(s) into the knowledge base from %s", count, skills_dir)
    return count
